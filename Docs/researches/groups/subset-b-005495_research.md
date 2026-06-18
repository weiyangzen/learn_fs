# Research: subset-b-005495 USB gadget function utilities

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_audio.c -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_audio.c

Purpose: implements the shared ALSA-side helper for USB Audio Class gadget functions. It creates a virtual `snd_card`/PCM device for a `struct g_audio`, moves samples between USB isochronous requests and ALSA DMA buffers, exposes mixer/rate/pitch controls, and exports lifecycle hooks used by UAC1/UAC2 function drivers.

Important APIs, types, and functions:
- `struct uac_rtd_params` is per-stream runtime state. It tracks endpoint enablement, the active ALSA substream, ring-buffer `hw_ptr`, preallocated USB requests, feedback request, pitch, current sample rate, feature-unit volume/mute state, control element IDs, and a spinlock for state read/write from control paths.
- `struct snd_uac_chip` is the ALSA card private data. It owns playback/capture `uac_rtd_params`, `snd_card`, `snd_pcm`, and playback packet scheduling precomputations (`p_residue_mil`, `p_interval`, `p_framesize`).
- `u_audio_iso_complete()` is the main isochronous completion callback. For playback IN packets it calculates adaptive packet length from sample rate, pitch, endpoint interval, frame size, and accumulated fractional residue, then copies ALSA DMA data into request buffers. For capture OUT packets it copies received data into ALSA DMA memory. It advances `hw_ptr`, notifies ALSA periods, and requeues the request.
- `u_audio_iso_fback_complete()` updates and requeues the asynchronous feedback endpoint request with `u_audio_set_fback_frequency()`.
- ALSA PCM callbacks are `uac_pcm_open()`, `uac_pcm_trigger()`, `uac_pcm_pointer()`, and null close/prepare helpers in `uac_pcm_ops`.
- Endpoint lifecycle exports are `u_audio_start_capture()`, `u_audio_stop_capture()`, `u_audio_start_playback()`, `u_audio_stop_playback()`, and `u_audio_suspend()`.
- Control exports are `u_audio_get/set_capture_srate()`, `u_audio_get/set_playback_srate()`, `u_audio_get/set_volume()`, and `u_audio_get/set_mute()`.
- `g_audio_setup()` allocates runtime buffers/requests, registers the ALSA card and PCM, and creates pitch, mute, volume, and volatile rate controls as needed. `g_audio_cleanup()` releases the card and runtime storage.

Control flow:
- Setup starts with caller-filled `g_audio->params`, endpoint max packet sizes, and gadget pointer. `g_audio_setup()` allocates the private chip, initializes capture/playback runtime depending on channel masks, creates the ALSA card/PCM, registers controls according to feedback endpoint and feature-unit flags, sets a managed continuous DMA buffer, and registers the card.
- Host alternate-setting enable in a UAC function calls `u_audio_start_capture()` or `u_audio_start_playback()`. Each function configures the endpoint for current speed, enables it, allocates missing requests, assigns callbacks/buffers, queues all requests, and marks the rate control active. Capture can also enable an IN feedback endpoint.
- Completion callbacks are continuous recycling loops. If ALSA is not actively running, requests are requeued without copying meaningful PCM data. Once ALSA starts, completions copy to/from `runtime->dma_area`, update `hw_ptr`, and call `snd_pcm_period_elapsed()` when a period boundary is crossed.
- Stop paths mark controls inactive, dequeue or free outstanding requests through `free_ep()` / `free_ep_fback()`, disable endpoints, and allow completion callbacks to free requests that could not be dequeued synchronously.

State and persistence:
- Persistent runtime state is kernel memory under `g_audio->uac`. It lasts from `g_audio_setup()` until `g_audio_cleanup()`.
- Stream state includes `srate`, `pitch`, `volume`, `mute`, `active`, endpoint-enabled flags, and request arrays. It is not persisted outside the module.
- ALSA control values are mirrored into `uac_rtd_params`; host-facing UAC control changes are expected to call exported setters, while ALSA user changes invoke `audio_dev->notify()` so the UAC function can report feature-unit changes to USB control state.
- `p_residue_mil` persists across playback completions during one streaming episode to distribute fractional samples across packets.

Dependencies and integration points:
- Depends on ALSA core/PCM/control APIs, USB composite gadget APIs, UAC descriptor constants, and `u_audio.h` / `uac_common.h`.
- UAC1/UAC2 function drivers provide descriptors, endpoints, rate lists, channel masks, sample sizes, feature-unit IDs, and a `notify()` callback.
- Uses `config_ep_by_speed()`, `usb_ep_enable()`, `usb_ep_queue()`, `usb_ep_dequeue()`, and endpoint descriptor interval/maxpacket fields from the gadget framework.
- ALSA user space sees the registered card/PCM and mixer controls. USB control request handlers use exported get/set helpers.

Risks:
- Error handling in `u_audio_start_capture()` has TODO comments: feedback endpoint configuration/enable/allocation failures can leave the OUT endpoint enabled and queued unless the caller tears it down.
- Several allocation failures after endpoint enablement return directly without disabling endpoints or freeing already allocated request state.
- `u_audio_pitch_get()` / `u_audio_pitch_put()` do not take `prm->lock`, unlike most rate/volume/mute paths, so pitch updates can race with feedback and playback packet calculations.
- `u_audio_iso_complete()` uses `req->actual = req->length` for playback before copying; correctness depends on IN requests being prepared as device-to-host payloads.
- Period elapsed detection compares wrapped `hw_ptr` modulo period against `req->actual`; unusual period/request sizing can affect notification cadence.
- Mutable static `u_audio_controls[]` names are overwritten during setup; concurrent setup of multiple cards could race on control template names if multiple gadget instances are created.

Test signals:
- Build with UAC1/UAC2 gadget functions enabled and verify no sparse/lockdep warnings around spinlocks and callback contexts.
- Enumerate a UAC gadget, run ALSA playback and capture at every configured rate/sample size/channel mask, and check for steady `snd_pcm_period_elapsed()` behavior without xruns.
- Exercise host sample-rate control requests and ALSA volatile rate controls; inactive streams should report rate `0`, active streams should notify selected rate.
- Test mute/volume from both host controls and ALSA mixer, confirming `notify()` callbacks and `snd_ctl_notify()` events.
- For asynchronous capture feedback, inspect feedback packet values at full speed and high speed and vary pitch within configured limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_audio.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_audio.h

Purpose: declares the public interface and configuration structures for the USB gadget ALSA audio utility implemented in `u_audio.c`.

Important APIs and types:
- `FBACK_SLOW_MAX` and `FBACK_FAST_MAX` define default feedback pitch deviation bounds in per-mil units.
- `struct uac_fu_params` describes a UAC Feature Unit: unit ID, mute presence, volume presence, and min/max/resolution in 1/256 dB.
- `struct uac_params` holds playback and capture channel masks, zero-terminated sample-rate arrays of length `UAC_MAX_RATES`, sample sizes, feature-unit params, preallocated request count, and feedback maximum drift.
- `struct g_audio` embeds `usb_function`, endpoint pointers, endpoint max packet sizes, UAC control notification callback, private `snd_uac_chip`, and `uac_params`.
- `func_to_g_audio()` converts a `usb_function` to `g_audio`; `num_channels()` counts enabled bits in a channel mask.
- Declares setup/cleanup, stream start/stop, sample-rate get/set, mute/volume get/set, and suspend APIs.

Control flow and integration:
- UAC function drivers allocate/embed `struct g_audio`, fill `params`, descriptors, endpoint max packet sizes, and `notify`, then call `g_audio_setup()`.
- USB alt-setting changes call `u_audio_start_*()` / `u_audio_stop_*()`.
- USB class control request handlers call get/set helpers for current rate and feature-unit state.

State and persistence:
- This header defines only in-memory runtime/configuration contracts. Actual persistent state lives in the `snd_uac_chip` object allocated by `g_audio_setup()`.
- Rate arrays are fixed-size and use `0` as terminator, so callers must initialize them carefully.

Dependencies:
- Includes USB composite APIs and `uac_common.h` for `UAC_MAX_RATES`.
- Depends on ALSA types indirectly through the opaque `struct snd_uac_chip`.

Risks:
- `num_channels(0)` returns `0`; callers use zero channel masks to suppress stream creation.
- Feature-unit IDs must match descriptors owned by UAC function drivers; mismatch breaks host control routing.
- `req_number` directly affects memory pressure and endpoint queue depth.

Test signals:
- Compile users of the header against UAC1/UAC2 configurations.
- Validate that configfs-provided rates fit within `UAC_MAX_RATES` and are zero-terminated before `g_audio_setup()`.
- Confirm `notify()` receives expected unit/control selector values for ALSA-side mute/volume changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ecm.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ecm.h

Purpose: defines configfs/function-instance option storage for the CDC ECM Ethernet gadget function.

Important APIs and types:
- `struct f_ecm_opts` embeds `usb_function_instance`, points to the shared ECM `net_device`, records whether the netdev is already `bound`, tracks `bind_count`, and protects configfs/refcount state with `lock` and `refcnt`.

Control flow and integration:
- The ECM function allocator creates this options object, usually initializes `net` through `u_ether` helpers, and uses `bind_count` to avoid duplicate netdev registration when the same instance is linked into configurations.
- Configfs attributes and symlink lifecycle use `lock` and `refcnt` to reject changes while active.

State and persistence:
- State is per function instance in kernel memory and persists while the configfs function instance exists.
- `bound` distinguishes legacy/shared netdev ownership from function-local registration.

Dependencies:
- Includes USB composite definitions and integrates with `u_ether.c` via `struct net_device` and `gether_*` helpers in ECM implementation files.

Risks:
- Incorrect `bind_count` or `bound` handling can double-register or prematurely unregister the netdev.
- Configfs writes must hold `lock` and respect `refcnt`; otherwise MAC/queue changes can race function binding.

Test signals:
- Create/remove ECM configfs functions repeatedly, link into multiple configurations, and verify netdev registration count.
- Change dev/host address and qmult only while unbound and confirm `-EBUSY` while active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ecm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_eem.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_eem.h

Purpose: defines option storage for the CDC EEM Ethernet gadget function.

Important APIs and types:
- `struct f_eem_opts` mirrors the ECM/subset option pattern: `usb_function_instance`, associated `net_device`, `bound`, `bind_count`, `lock`, and `refcnt`.

Control flow and integration:
- The EEM function uses this object as its configfs instance state, borrowing or registering a `u_ether` netdev and using bind counters to coordinate multi-configuration binding.
- EEM-specific framing is handled by the function driver through `struct gether` wrap/unwrap hooks declared in `u_ether.h`.

State and persistence:
- Kernel-resident configfs instance state; no on-disk persistence.
- `net` points to the Ethernet-over-USB link that outlives individual `usb_function` allocations for the same instance.

Dependencies:
- USB composite APIs and the EEM function implementation's use of `u_ether`.

Risks:
- As with ECM, stale `bound`/`bind_count` state risks netdev lifecycle imbalance.
- EEM framing depends on correct wrap/unwrap configuration outside this header.

Test signals:
- Configfs bind/unbind cycles for EEM with traffic through the created netdev.
- Multi-configuration binding should not produce duplicate network interfaces for one options instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_eem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether.c -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether.c

Purpose: implements the shared Ethernet-over-USB link layer for gadget functions such as ECM, EEM, CDC subset, NCM, and RNDIS. It owns the Linux `net_device`, USB request pools, RX/TX queueing, MAC address helpers, suspend/resume behavior, and connect/disconnect handoff between protocol-specific function drivers and the network stack.

Important APIs, types, and functions:
- `struct eth_dev` is the private netdev state. It contains the active `struct gether *port_usb`, netdev/gadget pointers, request freelists, RX frame queue, queue multiplier, protocol wrap/unwrap hooks, work item for RX memory recovery, ZLP/no-reserve flags, interface-name flag, and MAC addresses.
- `qlen()` scales endpoint request queue depth for high/super speed using `qmult`.
- `rx_submit()`, `rx_complete()`, `rx_fill()`, and `eth_work()` manage OUT endpoint receive buffers, unwrap protocol frames, feed SKBs into `netif_rx()`, and retry after allocation pressure.
- `eth_start_xmit()` applies CDC filters, invokes protocol `wrap()` for outgoing frames, queues IN endpoint requests, handles fixed-size NCM transfers and ZLP policy, and maintains netdev stats.
- `tx_complete()` recycles TX requests and wakes the netdev queue.
- Netdev methods are `eth_open()`, `eth_stop()`, and `eth_start_xmit()` in `eth_netdev_ops`; ethtool reports gadget driver information through `eth_get_drvinfo()`.
- Setup and config helpers include `gether_setup_name()`, `gether_setup_name_default()`, `gether_register_netdev()`, `gether_set/attach/detach_gadget()`, MAC getters/setters, `gether_set/get_qmult()`, and `gether_set/get_ifname()`.
- Link lifecycle exports are `gether_connect()`, `gether_disconnect()`, `gether_suspend()`, `gether_resume()`, and `gether_cleanup()`.

Control flow:
- Setup allocates an Ethernet netdev, initializes locks/lists/work, chooses configured or random device/host MACs, installs netdev and ethtool ops, sets MTU bounds, and registers the netdev or returns an unregistered default netdev for later configfs setup.
- A protocol function fills `struct gether` endpoints, filter/framing fields, and callbacks, then calls `gether_connect()` when USB data endpoints are enabled for the selected configuration. Connect enables endpoints, preallocates RX/TX requests, copies wrap/unwrap/header settings into `eth_dev`, sets `port_usb`, turns carrier on, and starts queues if the netdev is open.
- RX requests allocate SKBs sized from Ethernet header + MTU + protocol header + hardware alignment/fixed-size requirements, queue them on the OUT endpoint, and on completion unwrap to one or more SKBs before handing each to the network stack.
- TX begins from the network stack. It checks carrier/endpoint availability, honors suspend wakeup and CDC packet filters, obtains a TX request, optionally protocol-wraps the SKB, queues it on the IN endpoint, and recycles on completion.
- Disconnect clears `port_usb`, stops carrier/queue, disables endpoints, frees idle request objects, clears endpoint descriptors, and resets wrap/unwrap state.

State and persistence:
- MAC addresses, qmult, ifname override, request queues, and carrier state are held in `eth_dev` while the netdev exists.
- `port_usb` is the current active USB configuration link and is guarded by `dev->lock`.
- Request freelists are guarded by `req_lock`; RX memory retry state is a bit in `todo`.
- Network statistics accumulate in `net_device->stats` until netdev unregister.

Dependencies and integration points:
- Integrates Linux networking (`alloc_etherdev`, SKB APIs, `netif_*`, ethtool, MAC validation), USB composite endpoint APIs, and protocol function drivers through `struct gether`.
- Protocol-specific functions supply CDC filters and optional `wrap()`/`unwrap()` callbacks for RNDIS/EEM/NCM framing.
- Configfs macros in `u_ether_configfs.h` call MAC/qmult/ifname helpers.
- Suspend/resume uses `usb_func_wakeup()` or `usb_gadget_wakeup()` depending on function suspend state.

Risks:
- `get_ether_addr()` assumes parseable pairs and does not explicitly reject `hex_to_bin()` failures before composing bytes; invalid strings generally fall through to random address only after `is_valid_ether_addr()` fails.
- `eth_start_xmit()` reads `dev->port_usb` outside the lock after the initial snapshot in some wrap/fixed-size checks; disconnect races are mostly tolerated but deserve stress testing.
- `eth_stop()` disables and re-enables endpoints to flush pending I/O while preserving descriptors, which is hardware-sensitive.
- `rx_submit()` computes buffer sizes from MTU, header, alignment quirks, and fixed lengths; mistakes can cause truncation or excess memory allocation.
- Multi-frame wrappers can retain SKBs and return NULL; `supports_multi_frame` must be set consistently to avoid false drops.
- Queue-depth tuning via `qmult` can create memory pressure at high/super speed.

Test signals:
- Bring up ECM/EEM/NCM/RNDIS/subset gadgets, check netdev registration, carrier transitions, MAC attributes, MTU limits, and ethtool information.
- Run sustained bidirectional traffic at full/high/super speed with disconnect/reconnect cycles and inspect tx/rx error counters.
- Exercise CDC packet filters for broadcast, multicast, directed, and promiscuous traffic.
- Test suspend/resume while TX requests are in flight and verify wakeup behavior.
- Run with low-memory fault injection around SKB/request allocation and ensure RX retry work recovers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether.h

Purpose: declares the shared Ethernet-over-USB utility API and the `struct gether` contract used by Ethernet-like USB gadget functions.

Important APIs and types:
- `QMULT_DEFAULT` is the default high/super-speed queue multiplier.
- `USB_ETHERNET_MODULE_PARAMETERS()` defines common `qmult`, `dev_addr`, and `host_addr` module parameters for legacy gadgets.
- `struct gether` embeds `usb_function`, holds active `eth_dev`, IN/OUT endpoints, ZLP support, CDC packet filter, protocol header/fixed-size/multi-frame flags, wrap/unwrap callbacks, netdev open/close callbacks, and suspend state.
- `DEFAULT_FILTER` enables broadcast, all-multicast, promiscuous, and directed traffic by default.
- Setup APIs cover named/default netdev allocation, registration, gadget attachment/detachment, MAC address getters/setters, qmult, ifname, cleanup, suspend/resume, connect/disconnect.
- `can_support_ecm()` validates alternate-setting support for CDC ECM.
- `gether_bitrate()` returns theoretical link bitrate for speed-specific descriptors/status notifications.

Control flow and integration:
- Protocol functions allocate their instance-specific options, prepare a shared netdev through `gether_setup*()`, then create `struct gether` functions that call `gether_connect()` after endpoint descriptors are selected.
- `wrap()` and `unwrap()` are the protocol extension points for RNDIS/EEM/NCM or any framing that differs from raw Ethernet frames.
- Configfs attributes use the declared getters/setters to mutate instance state before binding.

State and persistence:
- `struct gether` represents one active USB function binding episode; `eth_dev` and netdev may outlive it.
- `cdc_filter` and `is_suspend` are runtime USB-control state.
- `fixed_*` sizes and `header_len` persist per active function and are copied into `eth_dev` during connect.

Dependencies:
- Linux USB composite, CDC constants, Ethernet/netdevice types, and `u_ether.c`.

Risks:
- Only one physical network link per configuration is supported by design; multiple functions must coordinate at a higher layer.
- Callback contracts require correct locking by `u_ether.c` callers and protocol implementations.
- `can_support_ecm()` only checks alternate-setting support, so controller-specific CDC issues may need additional quirks.

Test signals:
- Compile all Ethernet function drivers using this header.
- Validate protocol wrappers with `supports_multi_frame`, `is_fixed`, and ZLP settings at multiple USB speeds.
- Verify configfs/legacy module parameters produce expected MACs and queue depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether_configfs.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether_configfs.h

Purpose: provides macro-generated configfs item operations and attributes shared by USB Ethernet gadget functions.

Important APIs and types:
- `USB_ETHERNET_CONFIGFS_ITEM(_f_)` creates a configfs release callback that converts the item to `f_<name>_opts` and drops the function instance.
- `USB_ETHERNET_CONFIGFS_ITEM_ATTR_DEV_ADDR`, `HOST_ADDR`, `QMULT`, and `IFNAME` generate show/store attributes backed by `gether_*` helpers.
- `USB_ETHER_CONFIGFS_ITEM_ATTR_U8_RW` generates a generic hex u8 read/write attribute for protocol-specific option bytes.

Control flow:
- Function-specific configfs files include this header, instantiate macros for their option type, and include generated `CONFIGFS_ATTR()` objects in attribute arrays.
- Store paths take `opts->lock`; most reject writes when `opts->refcnt` is nonzero, preventing mutation while a function instance is in use.

State and persistence:
- Does not own state itself. It reads/writes fields in `f_*_opts`, mainly the shared `net_device` and qmult/MAC/ifname fields.

Dependencies:
- Requires each function to provide `struct f_<name>_opts`, `to_f_<name>_opts()`, an `opts->lock`, `opts->refcnt`, and usually `opts->net`.
- Depends on configfs, `u_ether.h` helper APIs, and kernel parsing helpers such as `kstrtou8()`.

Risks:
- Macro expansion hides type requirements; compile errors can be hard to trace if an options struct lacks expected fields.
- Generic u8 attribute does not check `refcnt`, unlike qmult/MAC/ifname attributes; function users must choose it only for fields safe to change live or add external protection.
- `QMULT` stores into `u8 val`, limiting accepted qmult to 0..255 even though `gether_set_qmult()` takes `unsigned`.

Test signals:
- For each Ethernet function, read/write generated configfs attributes before binding and verify `-EBUSY` after binding.
- Confirm generated release drops function-instance references exactly once.
- Fuzz invalid MAC, qmult, ifname, and u8 attribute input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether_configfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_fs.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_fs.h

Purpose: declares internal FunctionFS utility types, state machines, and option structures used by the FunctionFS gadget function.

Important APIs and types:
- `struct ffs_dev` represents a named FunctionFS device/mount with descriptor readiness, mount state, single-device mode, callbacks for ready/closed/acquire/release, and link into a global device list.
- `ffs_lock`, `ffs_dev_lock()`, and `ffs_dev_unlock()` protect global FunctionFS device state. `ffs_name_dev()` and `ffs_single_dev()` assign naming/singleton behavior.
- `enum ffs_state` models descriptor/string reading, active operation, deactivated no-disconnect mode, and closing/error state.
- `enum ffs_setup_state` models pending/cancelled EP0 setup handling.
- `struct ffs_data` is the core FunctionFS runtime state: gadget pointer, EP0 mutex/request/completion, endpoint spinlock, refcount/open count, state/setup_state, event queue, flags, wait queues, active function, descriptor/string storage, endpoint address map, mount superblock, file permissions, eventfd, I/O completion workqueue, no-disconnect flag, reset work, and endpoint files.
- `struct f_fs_opts` embeds `usb_function_instance`, links to `ffs_dev`, tracks refcount, and records whether configfs is bypassed.
- `to_f_fs_opts()` converts a function instance to its options object.

Control flow and state machine:
- FunctionFS starts in `FFS_READ_DESCRIPTORS`, transitions to `FFS_READ_STRINGS`, then `FFS_ACTIVE` after user space supplies descriptors/strings and callbacks succeed.
- If files close with `no_disconnect`, the function can enter `FFS_DEACTIVATED`, remaining visible but refusing transfers/setup until reactivated.
- `FFS_CLOSING` is terminal for unrecoverable errors or all endpoints closed.
- EP0 setup events move between `FFS_NO_SETUP`, `FFS_SETUP_PENDING`, and `FFS_SETUP_CANCELLED`, with comments documenting required locks.

State and persistence:
- All state is in kernel memory tied to the mounted FunctionFS instance and its USB function instance.
- Raw descriptors/strings are stored after user-space writes and drive later binding.
- File permissions and superblock are write-once mount properties.

Dependencies and integration:
- Depends on USB composite, lists, mutexes, workqueues, refcounts, eventfd, superblock/VFS concepts, and endpoint-file implementations elsewhere.
- User-space FunctionFS applications provide descriptors, strings, and endpoint I/O through the FunctionFS filesystem.
- Composite gadget binding uses `f_fs_opts` and `ffs_data->func`.

Risks:
- EP0 setup cancellation races are subtle; comments require use of helper clearing functions rather than direct `setup_state` mutation.
- Descriptor/string buffers have several internal pointers into raw allocation; lifetime bugs can corrupt bind-time descriptor parsing.
- `no_disconnect` deliberately keeps a visible but nonfunctional USB function, which can surprise host-side tests.
- Global `ffs_lock` and per-instance locks must be observed consistently to avoid mount/configfs races.

Test signals:
- FunctionFS smoke tests should mount, write descriptors/strings, bind to a gadget, transfer on endpoints, close/reopen with and without `no_disconnect`, and unmount.
- Race tests around EP0 setup while user space is slow or closes files.
- Validate descriptor count/address map limits up to `FFS_MAX_EPS_COUNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_gether.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_gether.h

Purpose: defines option storage for the CDC subset/generic Ethernet gadget function.

Important APIs and types:
- `struct f_gether_opts` embeds `usb_function_instance`, associated `net_device`, legacy/shared `bound` flag, `bind_count`, `lock`, and `refcnt`.

Control flow and integration:
- The subset function uses this options object to coordinate configfs instance lifetime with the shared `u_ether` netdev.
- Binding increments `bind_count`; unbinding decrements and unregisters/cleans the netdev only when the last binding is gone.

State and persistence:
- Per-instance in-memory configfs state. `net` usually persists across individual `usb_function` allocations.

Dependencies:
- USB composite and the shared Ethernet utility implementation.

Risks:
- Same lifecycle imbalance risks as ECM/EEM: double registration, stale netdev pointers, and live configfs mutation if `lock`/`refcnt` checks are missed.

Test signals:
- Create subset gadget, configure MAC/qmult/ifname before bind, run network traffic, and unbind/rebind repeatedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_gether.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_hid.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_hid.h

Purpose: declares configfs option state and global setup/cleanup APIs for the HID gadget function.

Important APIs and types:
- `struct f_hid_opts` embeds `usb_function_instance` and stores HID minor, subclass, protocol, optional absence of OUT endpoint, report length, report descriptor pointer/length/allocation flag, interrupt interval and user-set flag, plus `lock` and `refcnt`.
- `ghid_setup(struct usb_gadget *g, int count)` and `ghid_cleanup()` initialize/tear down the HID gadget character-device infrastructure for a number of HID instances.

Control flow and integration:
- Configfs writes fill descriptor/protocol/report fields before the function is instantiated.
- HID function bind consumes these options to build descriptors and create the `/dev/hidg*` endpoint interface.
- `report_desc_alloc` tells cleanup whether `report_desc` is owned by the options object.

State and persistence:
- Options persist as long as the configfs function instance exists.
- Minor allocation and character-device infrastructure are global to HID gadget setup.

Dependencies:
- USB composite framework and HID function implementation files.

Risks:
- Report descriptor length/content must match `report_length`; invalid descriptors may enumerate but fail host HID parsing.
- `no_out_endpoint` changes endpoint topology and must match intended report direction.
- Concurrent configfs mutation while bound must be blocked through `lock`/`refcnt`.

Test signals:
- Instantiate keyboard/mouse/custom HID report descriptors, verify host enumeration, IN reports, optional OUT reports, and interval behavior.
- Repeated setup/cleanup should not leak minors or report descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_hid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_midi.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_midi.h

Purpose: declares configfs option state for the legacy USB MIDI gadget function.

Important APIs and types:
- `struct f_midi_opts` embeds `usb_function_instance` and stores ALSA card index/id, interface string, number of IN/OUT virtual MIDI ports, request buffer length, queue length, plus `lock` and `refcnt`.

Control flow and integration:
- Configfs initializes port counts, ALSA identity, and transfer sizing before bind.
- The MIDI function uses these options to create USB MIDI descriptors and an ALSA rawmidi/card interface.

State and persistence:
- Per-function-instance in-memory configuration; strings may be dynamically allocated by configfs store paths in the implementation.

Dependencies:
- USB composite framework and ALSA/MIDI implementation files.

Risks:
- Large `buflen`/`qlen` values increase memory use and endpoint latency; small values can drop/fragment MIDI events.
- Port counts must match descriptor generation and ALSA substream setup.

Test signals:
- Bind with several IN/OUT port combinations, enumerate on host, send MIDI events both directions, and verify ALSA rawmidi devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_midi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_midi2.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_midi2.h

Purpose: declares configuration structures for the USB MIDI 2.0 gadget function, including UMP endpoints and Function Blocks.

Important APIs and types:
- `struct f_midi2_block_info` stores UMP Function Block direction, group ranges, MIDI 1.0 group mapping, UI hint, MIDI-CI version, sysex8 streams, MIDI 1.0 port mode, active flag, and name.
- `struct f_midi2_ep_info` stores endpoint protocol capabilities/default, manufacturer/family/model/software IDs, endpoint name, and product ID.
- `struct f_midi2_card_info` stores card-level processing mode, static-block flag, USB request buffer sizing, request count, and interface name.
- `struct f_midi2_block_opts` and `struct f_midi2_ep_opts` are configfs groups linking blocks to endpoints and endpoints to the root options.
- `struct f_midi2_opts` embeds `usb_function_instance`, lock/refcnt, card info, endpoint count, and up to `MAX_UMP_EPS` endpoint option pointers.
- `MAX_UMP_EPS` is 4 and `MAX_CABLES` is 16.

Control flow and integration:
- Configfs creates endpoint groups and nested block groups, then the MIDI2 function consumes this tree to build descriptors and ALSA UMP interfaces.
- Static Function Blocks can be declared before bind; dynamic processing behavior is controlled by `process_ump`.

State and persistence:
- Nested configfs groups hold all MIDI2 state in memory for the lifetime of the function instance.
- Names are `const char *` pointers expected to be managed by the implementation/configfs layer.

Dependencies:
- USB composite APIs and ALSA UMP constants from `<sound/asound.h>`.

Risks:
- Range fields have protocol-defined bounds documented in comments but not enforced in the header; store paths must validate all values.
- Endpoint/block ownership is pointer-based; removal must avoid stale block pointers in `blks[]`.
- MIDI1 group mapping can overlap invalidly with UMP groups if validation is incomplete.

Test signals:
- Build configfs trees with multiple UMP endpoints and Function Blocks; verify descriptor contents and host MIDI2 enumeration.
- Exercise bounds for group counts, sysex stream counts, manufacturer/model IDs, and static/dynamic blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_midi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ncm.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ncm.h

Purpose: defines configfs option storage for the CDC NCM Ethernet gadget function.

Important APIs and types:
- `struct f_ncm_opts` embeds `usb_function_instance`, associated `net_device`, `bind_count`, configfs/OS descriptor group pointers, `ncm_os_desc`, `ncm_ext_compat_id`, `lock`, `refcnt`, and `max_segment_size`.

Control flow and integration:
- NCM configfs setup uses this state to expose networking attributes plus OS descriptors.
- Bind consumes `max_segment_size` and NCM OS descriptor fields while `u_ether` handles the underlying netdev and fixed-size transfer behavior.

State and persistence:
- Per-instance in-memory state; `net` and OS descriptor groups persist while the configfs function exists.

Dependencies:
- USB composite, configfs group types, USB OS descriptor support, and `u_ether`.

Risks:
- NCM fixed IN/OUT transfer sizing must match the `u_ether` `is_fixed` / fixed length fields configured by the NCM implementation.
- Incorrect OS descriptor strings can affect Windows binding.
- `max_segment_size` needs validation against MTU/NCM descriptor limits.

Test signals:
- Enumerate NCM on Linux and Windows-compatible hosts, verify OS descriptors, segment size, and high-throughput traffic.
- Rebind with different `max_segment_size` before active use and confirm configfs rejects live mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ncm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_phonet.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_phonet.h

Purpose: declares the Phonet USB gadget utility interface and option state.

Important APIs and types:
- `struct f_phonet_opts` embeds `usb_function_instance`, tracks whether the function is `bound`, and points to its `net_device`.
- Declares `gphonet_setup_default()`, `gphonet_set_gadget()`, `gphonet_register_netdev()`, and `gphonet_cleanup()`.

Control flow and integration:
- The Phonet function creates or receives a netdev through `gphonet_setup_default()`, associates it with the gadget, registers it, and cleans it up on instance teardown.
- It parallels `u_ether` patterns but targets Nokia Phonet networking rather than Ethernet framing.

State and persistence:
- In-memory options state per function instance, with netdev lifetime coordinated by bind/unbind.

Dependencies:
- USB composite, CDC constants, and Phonet network implementation outside this header.

Risks:
- Fewer synchronization fields than Ethernet option structs; implementation must externally protect configfs/bind state if mutable.
- Bound/netdev ownership must be unambiguous to avoid netdev leaks.

Test signals:
- Bind Phonet gadget, verify netdev registration and gadget parent assignment, then unbind/cleanup under traffic if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_phonet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_printer.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_printer.h

Purpose: declares configfs option state for the USB printer gadget function.

Important APIs and types:
- `struct f_printer_opts` embeds `usb_function_instance`, stores printer minor, PNP string pointer and ownership flag, request queue length `q_len`, and configfs `lock`/`refcnt`.

Control flow and integration:
- Configfs sets PNP identification and queue depth before bind.
- The printer function uses `minor` to create a printer character device and `q_len` to size USB request queues.

State and persistence:
- Per-instance in-memory options. `pnp_string_allocated` controls ownership cleanup for the PNP string.

Dependencies:
- USB composite framework and printer function implementation.

Risks:
- PNP string lifetime/ownership must be tracked exactly to avoid leaks or freeing static strings.
- Queue depth affects memory and throughput.
- Live changes must respect `refcnt`.

Test signals:
- Create printer gadget with custom PNP string, verify host class detection and bidirectional data path through the character device.
- Repeated bind/unbind should release minors and allocated PNP strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_printer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_rndis.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_rndis.h

Purpose: defines option storage and a netdev borrowing hook for the RNDIS Ethernet gadget function.

Important APIs and types:
- `struct f_rndis_opts` embeds `usb_function_instance`, vendor/manufacturer identity, associated `net_device`, `bind_count`, `borrowed_net`, RNDIS OS descriptor group and descriptor data, class/subclass/protocol bytes, `lock`, and `refcnt`.
- `rndis_borrow_net()` lets a legacy/composite gadget provide a pre-created netdev to an RNDIS function instance.

Control flow and integration:
- RNDIS configfs uses these fields for Microsoft OS descriptors, class codes, and Ethernet attributes.
- Bind uses `borrowed_net` to decide whether the RNDIS function owns netdev registration/cleanup or is sharing a pre-registered netdev.
- The underlying packet transport uses `u_ether` with RNDIS wrap/unwrap callbacks.

State and persistence:
- Per-instance in-memory configfs state. Manufacturer string is a pointer whose lifetime is managed by implementation/configfs.

Dependencies:
- USB composite, configfs, USB OS descriptor support, and shared Ethernet utility.

Risks:
- Windows interoperability depends heavily on OS descriptor compatibility ID and class/subclass/protocol values.
- Incorrect borrowed-net ownership can leak or double-free/register netdevs.
- RNDIS framing allows padding and internal packet boundaries, so `u_ether` buffer sizing and unwrap error handling are important.

Test signals:
- Enumerate RNDIS on Windows/Linux hosts, verify OS descriptor content, MAC addresses, and network traffic.
- Test `rndis_borrow_net()` with legacy multi-function gadgets sharing a netdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_rndis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_serial.c -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_serial.c

Purpose: implements the shared TTY/USB bridge used by serial-like gadget functions such as ACM, generic serial, OBEX-style byte streams, and optional USB gadget console output. It creates `/dev/ttyGS*` devices, buffers data between tty and USB endpoints, and exposes `gserial_*` lifecycle APIs.

Important APIs, types, and functions:
- `struct gs_port` is the per-tty-port nexus. It embeds `tty_port`, holds `port_usb`, optional console state, port number, RX request pools/queue/counters, TX request pool and kfifo buffer, wait queues, suspended/delayed flags, async counters, and CDC line coding.
- `struct gs_console` exists under `CONFIG_U_SERIAL_CONSOLE` and owns a console, work item, lock, one USB request, kfifo, and missed-byte counter.
- `gs_alloc_req()` / `gs_free_req()` allocate/free USB requests with buffers and are exported for serial functions.
- TX path: `gs_write()`, `gs_put_char()`, `gs_flush_chars()`, `gs_send_packet()`, `gs_start_tx()`, and `gs_write_complete()` move tty writes from `port_write_buf` into IN endpoint requests.
- RX path: `gs_start_rx()`, `gs_read_complete()`, and `gs_rx_push()` queue OUT requests, collect completed data, push into tty flip buffers, and refill requests.
- TTY operations are `gs_open()`, `gs_close()`, `gs_write()`, `gs_put_char()`, `gs_flush_chars()`, `gs_write_room()`, `gs_chars_in_buffer()`, `gs_unthrottle()`, `gs_break_ctl()`, and `gs_get_icount()`.
- Line lifecycle exports are `gserial_alloc_line_no_console()`, `gserial_alloc_line()`, `gserial_free_line()`, `gserial_connect()`, `gserial_disconnect()`, `gserial_suspend()`, and `gserial_resume()`.
- Module init/exit registers and unregisters a dynamic raw tty driver named `ttyGS`.

Control flow:
- Module init allocates a tty driver for `MAX_U_SERIAL_PORTS`, configures raw serial defaults, installs tty ops, initializes per-port mutexes, and registers the driver.
- Function drivers request a line through `gserial_alloc_line*()`, which allocates a `gs_port`, initializes queues/work/waits, registers a tty device, and optionally initializes console on port 0.
- When a USB configuration activates, the function calls `gserial_connect()`. It enables IN/OUT endpoints, sets endpoint `driver_data`, links `gserial` and `gs_port`, copies line coding, starts I/O if the tty is already open, calls protocol connect/disconnect callbacks, and connects optional console output.
- TTY open allocates the TX kfifo on first open, links `tty_struct`, and starts USB I/O if already connected and not suspended. TTY close notifies protocol disconnect, waits up to `GS_CLOSE_TIMEOUT` for writes to drain, resets or frees the TX buffer, clears tty linkage, and wakes close waiters.
- RX completions enqueue requests to `read_queue`; delayed work pushes into tty flip buffers unless throttled, returns requests to `read_pool`, and starts more RX.
- Disconnect unlinks tty and USB state under locks, hangs up open tty, disables endpoints, frees idle/queued requests, resets counters, and frees TX kfifo if closed.

State and persistence:
- Global `ports[MAX_U_SERIAL_PORTS]` holds per-line mutex and active `gs_port` pointer.
- Per-port state persists from line allocation to `gserial_free_line()`.
- `port_write_buf` exists while tty is open or while connected with buffered data; it is freed on closed disconnect.
- CDC `port_line_coding` is copied between `gserial` and `gs_port` across disconnect/connect.
- Optional console state persists while enabled through configfs/port 0 setup.

Dependencies and integration:
- Depends on tty core, tty flip buffers, kfifo, wait queues, workqueues, USB composite endpoints, CDC line coding, and optional console subsystem.
- Protocol function drivers embed `struct gserial`, choose endpoints/descriptors, and provide connect/disconnect/send_break callbacks.
- Suspend/resume integrates with USB remote wakeup through `usb_func_wakeup()` / `usb_gadget_wakeup()`.

Risks:
- Locking is complex: global `serial_port_lock`, per-port mutexes, and `port_lock` protect different parts of the graph. Changes must preserve lock ordering.
- `gs_write()` and `gs_flush_chars()` snapshot `port->port_usb` before acquiring `port_lock` for wakeup paths; disconnect races require care.
- Close waits only a bounded 15 seconds for buffered data, then discards remaining data.
- RX can backlog if tty is throttled or flip buffer lacks space, causing USB OUT NAKs.
- Console path uses a single request and kfifo; overflow increments `missed`, so early boot or high-volume console output can lose bytes.
- Request allocation happens with `GFP_ATOMIC` during I/O start and may partially allocate; cleanup must keep `read_allocated`/`write_allocated` consistent.

Test signals:
- Allocate all `MAX_U_SERIAL_PORTS`, open `/dev/ttyGS*`, connect/disconnect USB functions, and transfer data both directions.
- Stress tty close while writes are pending, host disconnect while tty is open, and repeated bind/unbind.
- Exercise throttling/unthrottling and confirm RX resumes.
- Test suspend/resume with pending writes and verify remote wakeup and delayed start behavior.
- With `CONFIG_U_SERIAL_CONSOLE`, enable/disable console and validate output, missed-byte accounting, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_serial.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_serial.h

Purpose: declares the public interface for USB gadget serial/TTY utilities.

Important APIs and types:
- `MAX_U_SERIAL_PORTS` limits dynamic `ttyGS*` ports to 8.
- `struct f_serial_opts` is generic serial configfs option state with `usb_function_instance`, port number, protocol, lock, and instance count.
- `struct gserial` embeds `usb_function`, stores linked `gs_port`, IN/OUT endpoints, CDC line coding, and connect/disconnect/send_break callbacks.
- Exports request helpers `gs_alloc_req()` / `gs_free_req()`.
- Exports line allocation/free, optional console get/set, connect/disconnect, and suspend/resume APIs.

Control flow and integration:
- Serial-like functions allocate a line, bind descriptors/endpoints to a `gserial`, then call `gserial_connect()` on USB activation and `gserial_disconnect()` on deactivation.
- Function-specific control handlers can update or read `port_line_coding` through the `gserial` object.
- TTY devices are managed by `u_serial.c`, not by each individual function.

State and persistence:
- `gserial->ioport` is valid only while connected.
- `port_line_coding` persists across connect/disconnect by copyback in `u_serial.c`.

Dependencies:
- USB composite and CDC line coding definitions.

Risks:
- `MAX_U_SERIAL_PORTS` is fixed; configfs users must handle `-ENXIO`/allocation failure when exhausted.
- Callback execution context can be IRQ-like; callbacks must avoid sleeping unless implementation guarantees context.
- Endpoint pointers must be configured and enabled by speed before connect.

Test signals:
- Compile ACM/gserial/OBEX users.
- Validate line allocation exhaustion, disconnect without connect, and suspend/resume callback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_tcm.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_tcm.h

Purpose: declares option state for the USB TCM/storage target gadget function.

Important APIs and types:
- `struct f_tcm_opts` embeds `usb_function_instance`, optional dependent module pointer, dependency lock, readiness/attach flags, `has_dep`, and callbacks for TCM registration/unregistration.

Control flow and integration:
- Legacy gadgets can set `dependent` so target portal group creation increments a module refcount and dropping it decrements the refcount.
- New programmatic function registration must provide sensible register/unregister callbacks to probe/remove the composite layer.
- `ready` and `can_attach` gate whether a USB function can be bound to a gadget.

State and persistence:
- Per-instance in-memory state, plus module reference state for an optional dependent module.

Dependencies:
- USB composite framework and target core/TCM implementation outside this header.

Risks:
- Incorrect dependent module refcounting can unload storage target code while in use or pin it forever.
- Missing callbacks in programmatic use can leave the composite gadget unprobed or unremoved.
- `can_attach` and `ready` need synchronization through `dep_lock`.

Test signals:
- Create/drop TPGs with and without a dependent module and check module refcounts.
- Bind/unbind TCM function only after `ready`/`can_attach` are set and verify callbacks fire exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_tcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1.h

Purpose: declares defaults and configfs option state for the modern USB Audio Class 1 gadget function that uses `u_audio`.

Important APIs and types:
- Defaults define UAC1 packet size, capture/playback channel masks, sample rates, sample sizes, request counts, interrupt request count, mute/volume presence, and default volume range/resolution.
- `struct f_uac1_opts` embeds `usb_function_instance`, capture/playback channel masks, rate arrays, sample sizes, playback/capture feature-unit mute/volume settings, request count, bound flag, configurable function/terminal/channel/feature-unit names, `lock`, and `refcnt`.

Control flow and integration:
- Configfs fills this options object. The UAC1 function converts it into descriptors and `struct uac_params` for `g_audio_setup()`.
- `bound`/`refcnt` protect descriptor-affecting options from mutation while active.

State and persistence:
- Per-instance in-memory configfs state. Rate arrays are bounded by `UAC_MAX_RATES`.
- Name arrays are fixed-size `USB_MAX_STRING_LEN` buffers.

Dependencies:
- USB composite and `uac_common.h`; integrates with `u_audio.h` in the function implementation.

Risks:
- Rate arrays require validation and zero termination.
- Volume values use 1/256 dB units; configfs conversions must preserve signed bounds and nonzero resolution.
- Endpoint bandwidth depends on channel mask, sample size, and max sample rate.

Test signals:
- Enumerate UAC1 with default and custom capture/playback settings, validate descriptors, ALSA card behavior, and host class control requests.
- Exercise name customization and feature-unit presence toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1_legacy.c -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1_legacy.c

Purpose: implements the legacy UAC1 gadget audio helper that proxies USB audio playback into existing ALSA device files, rather than creating its own virtual ALSA card like `u_audio.c`.

Important APIs and functions:
- `_snd_pcm_hw_param_set()` and `snd_interval_refine_set()` are local helpers for setting ALSA hardware parameter masks/intervals.
- `playback_default_hw_params()` configures the opened playback substream for default interleaved S16_LE, 2 channels, 48000 Hz, issues DROP/HW_PARAMS/PREPARE ioctls, and stores the actual selected parameters.
- `u_audio_playback()` writes a USB audio buffer to the playback substream using `snd_pcm_kernel_write()`, preparing again after XRUN/SUSPENDED states.
- `u_audio_get_playback_channels()` and `u_audio_get_playback_rate()` expose configured playback parameters.
- `gaudio_open_snd_dev()` opens control, playback, and capture device files from `f_uac1_legacy_opts`; it obtains PCM substreams from file private data and initializes playback.
- `gaudio_setup()` opens the ALSA files; `gaudio_cleanup()` closes them.

Control flow:
- The legacy function owns a `struct gaudio` and calls `gaudio_setup()` during bind/activation. That opens the configured control file first, then playback, then optionally capture.
- USB OUT audio payloads are later forwarded by the UAC1 legacy function to `u_audio_playback()`, which handles XRUN recovery and writes frames into the kernel ALSA substream.
- Cleanup closes any opened files.

State and persistence:
- `struct gaudio_snd_dev` stores file pointers, substream pointers, access/format/channels/rate, and parent card pointer.
- The default file paths are declared in the header and can be overridden through `f_uac1_legacy_opts`.
- No samples are persisted; state exists only while the gadget function is bound/open.

Dependencies and integration:
- Depends on kernel file operations (`filp_open`, `filp_close`), ALSA PCM internals/ioctls, and `u_uac1_legacy.h`.
- Integrates with older UAC1 function code that manages USB descriptors/endpoints and calls these helpers for audio payloads.

Risks:
- Uses fixed default playback hardware params regardless of host-selected format unless higher layers coordinate separately.
- `u_audio_playback()` retries indefinitely on short/error writes by jumping to `try_again`; persistent errors can spin.
- Failure after opening control but before opening playback does not close the already opened control file in `gaudio_open_snd_dev()`; caller cleanup is needed.
- Capture open failures are logged but not fatal, leaving capture fields null.
- Direct use of ALSA internal helpers and kernel file paths is fragile compared with the modern virtual-card model.

Test signals:
- Configure valid and invalid playback/control/capture paths and verify setup failure/cleanup behavior.
- Stream UAC1 playback to an ALSA PCM and induce XRUN/SUSPEND to test recovery.
- Confirm reported playback channels/rate match actual `HW_PARAMS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1_legacy.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1_legacy.h

Purpose: declares the legacy UAC1 ALSA-file-backed audio helper API and option state.

Important APIs and types:
- Default paths are `FILE_PCM_PLAYBACK`, `FILE_PCM_CAPTURE`, and `FILE_CONTROL`.
- Legacy constants define OUT endpoint max packet size, request count, and audio buffer size.
- `struct gaudio_snd_dev` stores parent `gaudio`, opened file, PCM substream, access, format, channels, and rate.
- `struct gaudio` embeds `usb_function`, gadget pointer, and control/playback/capture ALSA device wrappers.
- `struct f_uac1_legacy_opts` embeds `usb_function_instance`, request/audio buffer sizing, configurable file paths, bound flag, ownership flags for path strings, `lock`, and `refcnt`.
- Declares `gaudio_setup()`, `gaudio_cleanup()`, `u_audio_playback()`, and playback channel/rate getters.

Control flow and integration:
- Legacy UAC1 function configures file paths/request sizing, calls `gaudio_setup()`, forwards payloads to `u_audio_playback()`, and calls cleanup on unbind.
- Path ownership flags tell configfs cleanup whether to free custom strings.

State and persistence:
- File path strings and request sizing persist in the configfs function instance.
- ALSA file/substream state persists while `gaudio_setup()` is active.

Dependencies:
- Linux device/error/USB composite APIs and ALSA core/PCM parameter headers.

Risks:
- Hard-coded defaults target card 0 device 0 and may be wrong on most systems.
- Kernel file access to ALSA devices couples gadget behavior to local sound-card availability and permissions.
- Ownership flags for path strings must be accurate.

Test signals:
- Override all three file paths and verify ownership cleanup.
- Test missing capture path is tolerated as implemented while missing control/playback fails setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1_legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac2.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac2.h

Purpose: declares defaults and configfs option state for the USB Audio Class 2 gadget function that uses `u_audio`.

Important APIs and types:
- Defaults define playback/capture channel masks, sample rates, sample sizes, high-speed bInterval defaults, capture sync mode, feature-unit mute/volume defaults, request counts, interrupt request count, and terminal types.
- `struct f_uac2_opts` embeds `usb_function_instance`, playback/capture audio parameters, capture sync and high-speed intervals, feature-unit settings, request count, feedback max drift, bound flag, configurable string names, playback/capture terminal types, `lock`, and `refcnt`.

Control flow and integration:
- The UAC2 function uses these options to build UAC2 descriptors, calculate endpoint bandwidth and feedback capabilities, and fill `uac_params` for `g_audio_setup()`.
- `fb_max` affects allowed faster-side pitch and endpoint bandwidth.

State and persistence:
- Per-instance configfs state in memory. Rate arrays are bounded by `UAC_MAX_RATES` and must be zero-terminated.
- String name buffers persist in the options object and map to USB string descriptors.

Dependencies:
- USB composite, `uac_common.h`, and `u_audio` implementation.

Risks:
- UAC2 async/sync endpoint behavior depends on `c_sync`, feedback endpoint descriptors, and `fb_max`; inconsistent options can cause host drift or bandwidth issues.
- Terminal type fields are `s16` but defaults are positive USB terminal constants; validation should reject invalid negative or out-of-range values.
- bInterval defaults of 0 must be interpreted carefully by descriptor code.

Test signals:
- Enumerate UAC2 at full/high/super-capable controllers, test playback/capture rates, feedback, terminal names/types, and feature-unit controls.
- Validate endpoint max packet calculations for high sample rates/channel counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uvc.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uvc.h

Purpose: declares configfs/legacy option state for the USB Video Class gadget function.

Important APIs and types:
- `fi_to_f_uvc_opts()` converts a function instance to `f_uvc_opts`.
- `struct f_uvc_opts` embeds `usb_function_instance`, streaming interval/maxpacket/maxburst, interface numbers, function name, last unit ID, interrupt endpoint enable flag, descriptor pointer arrays for control/streaming at full/high/super speed, default camera/processing/output terminal descriptors, configfs-owned control descriptor arrays, extension unit list, dynamically allocated streaming descriptor arrays, string descriptor indexes, `lock`, `refcnt`, and legacy-only `header`.

Control flow and integration:
- Configfs builds UVC control and streaming descriptor trees into the arrays in this options object.
- Legacy gadgets may override descriptor pointer arrays and use `header`.
- Bind consumes descriptors, interface numbers, endpoint parameters, and strings to instantiate `struct uvc_device` in `uvc.h`.

State and persistence:
- Descriptor pointers and allocated arrays persist while the function instance exists.
- `last_unit_id` coordinates descriptor unit IDs as configfs extension units are added.
- `refcnt` blocks mutation while functions are instantiated.

Dependencies:
- USB composite, USB video descriptor definitions, mutexes, and UVC implementation/configfs descriptor code.

Risks:
- Descriptor arrays are pointer-heavy and partially dynamic; cleanup must free only owned arrays and keep legacy overrides intact.
- Interface numbers and string indexes must stay consistent with composite allocation.
- `streaming_maxpacket`/`maxburst` must be valid for selected speeds and endpoint capabilities.

Test signals:
- Build UVC configfs trees with multiple formats/frames and extension units, bind/unbind, and verify descriptor arrays and host enumeration.
- Stream video at configured endpoint sizes and test interrupt endpoint enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uac_common.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uac_common.h

Purpose: provides the shared UAC constant used by UAC1, UAC2, and `u_audio` configuration structures.

Important APIs and types:
- `UAC_MAX_RATES` is defined as 10, the maximum number of configurable sample rates in the fixed arrays used by UAC1/UAC2/audio options.

Control flow and integration:
- Headers `u_audio.h`, `u_uac1.h`, and `u_uac2.h` include this file to size capture/playback sample-rate arrays.
- Parser/store code in UAC function implementations must enforce this bound and zero-terminate arrays.

State and persistence:
- No runtime state. It is a compile-time contract.

Dependencies:
- None beyond include guards.

Risks:
- Increasing the constant changes struct layout and configfs ABI expectations inside the kernel build.
- Missing zero terminators in arrays of this size can cause readers to scan stale values until they hit an incidental zero.

Test signals:
- Configfs tests should write exactly 1, `UAC_MAX_RATES`, and too many rates, verifying validation and descriptor generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uac_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc.h -->
## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc.h

Purpose: declares internal runtime structures, constants, tracing helpers, and function entry points for the USB Video Class gadget driver.

Important APIs and types:
- Trace flags (`UVC_TRACE_*`) and `uvc_trace()` gate debug logging via `uvc_gadget_trace_param`; `uvcg_dbg/info/warn/err` log through the gadget device.
- Constants define request size/event limits, UVC request header length, interrupt/zero counters, and minimum streaming buffers.
- `struct uvc_request` wraps a USB request, request buffer, owning `uvc_video`, scatterlist table, UVC payload header, last video buffer, and list linkage.
- `struct uvc_video` owns the streaming endpoint, pump work/workqueues, kernel worker submission, queued counter, current frame parameters protected by `mutex`, request counts/sizes/lists, request lock, encoder callback, payload sizing, video queue, and frame ID.
- `enum uvc_state` tracks disconnected, connected, and streaming states.
- `struct uvc_device` combines `video_device`, `v4l2_device`, state, `usb_function`, `uvc_video`, release completion, function connection/unbound locking, descriptor pointers, control/streaming interface numbers, interrupt endpoint/control request/buffer state, and event setup state.
- `struct uvc_file_handle` embeds `v4l2_fh`, points to `uvc_video`, and marks whether a handle is the UVC application handle.
- Helpers convert from `usb_function` or file handles to UVC containers.
- Declares `uvc_function_setup_continue()`, `uvc_function_connect()`, and `uvc_function_disconnect()`.

Control flow and integration:
- Composite bind creates a `uvc_device` and fills descriptor pointers from `f_uvc_opts`.
- V4L2 userspace opens the video node, configures frame parameters, queues buffers, and handles UVC events.
- When the host completes class-specific setup negotiation, `uvc_function_setup_continue()` resumes EP0 control handling.
- USB connect/disconnect transitions use `uvc_function_connect()` / `uvc_function_disconnect()` to notify state and wake waiting userspace.
- Streaming uses `uvc_video` request lists: free requests are encoded from queued V4L2 buffers, moved to ready, submitted to the endpoint, and recycled on completion.

State and persistence:
- Runtime state persists while the UVC function is bound and the video device exists.
- Frame format/size/interval are mutable under `uvc_video.mutex`.
- Request lists and payload counters reset with stream enable/disable.
- `func_unbound` and `func_connected` coordinate teardown and userspace waiters.

Dependencies:
- Linux list/mutex/spinlock/wait APIs, USB composite, V4L2 device/file-handle APIs, videodev2, and `uvc_queue.h`.

Risks:
- Streaming request lists are split across free/ready/all lists with both workqueue and completion contexts; locking mistakes can lose requests.
- UVC setup event length/direction state must match EP0 control continuation or hosts can stall.
- V4L2 buffer availability and USB request availability must be balanced to avoid underruns or deadlocks.
- Descriptor pointers are owned by UVC option/configfs code; lifetime must outlive the bound function.

Test signals:
- Enumerate UVC gadget, open V4L2 node, negotiate probe/commit, stream frames, disconnect/reconnect, and run with dynamic format changes.
- Exercise request pool exhaustion, zero-length/short payload edge cases, and host setup cancellation.
- Use trace flags to confirm descriptor, control, streaming, suspend, and status paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc.h -->
