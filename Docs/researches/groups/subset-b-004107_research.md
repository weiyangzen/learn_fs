# subset-b-004107 Research

Grouped research for the requested media I2C, media-controller, MMC/SDIO, and PCI build files. Each source section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vd56g3.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/vd56g3.c

Purpose: V4L2 subdevice driver for ST VD56G3 monochrome and VD66GY Bayer global-shutter CSI-2 sensors. It powers the sensor, validates the device-tree CSI-2 endpoint, configures clocks, image format, crop/binning, exposure/AE, test pattern, GPIO strobe LED mode, and starts/stops streaming.

Important APIs/types/functions: `struct vd56g3` owns regulators, reset GPIO, xclk, CCI regmap, CSI lane/output-interface settings, GPIO role masks, and V4L2 controls. The key entry points are `vd56g3_probe()`, `vd56g3_remove()`, runtime PM callbacks `vd56g3_power_on()`/`vd56g3_power_off()`, pad ops `vd56g3_enum_mbus_code()`, `vd56g3_set_pad_fmt()`, `vd56g3_get_selection()`, `vd56g3_get_frame_desc()`, and stream ops `vd56g3_enable_streams()`/`vd56g3_disable_streams()`. Control handling centers on `vd56g3_s_ctrl()`, `vd56g3_g_volatile_ctrl()`, `vd56g3_update_controls()`, `vd56g3_update_expo_cluster()`, and `vd56g3_read_expo_cluster()`.

Control flow: probe allocates state, initializes the I2C subdev, parses the fwnode endpoint, gets regulators/clock/reset, creates a 16-bit CCI regmap, powers the sensor, enables runtime PM autosuspend, detects model/cut/optical variant, initializes media entity and controls, finalizes subdev state, then async-registers the subdevice. Streaming resumes runtime PM, writes clock and PLL parameters, programs RAW8/RAW10 format and CSI-2 datatype, configures binning and ROI/crop registers, applies GPIO defaults and all controls, sends the standby start command, then polls command acknowledgement and the streaming FSM state. Stop caches applied exposure/gain values for AE cold-start, sends stop, waits for standby, unlocks controls, and autosuspends.

State/persistence: state is volatile kernel driver state plus sensor register programming. Runtime PM keeps the chip powered only while needed. Exposure/gain controls are refreshed from applied hardware registers on stop or volatile control read so the next auto-exposure cold-start can reuse current values. There is no durable persistence.

Dependencies/integration: depends on V4L2 subdev, async registration, media entity pads, V4L2 fwnode parsing, MIPI CSI-2 descriptors, runtime PM, regulator/clock/GPIO frameworks, CCI regmap helpers, and device-tree compatibles `st,vd56g3`/`st,vd66gy`.

Risks/test signals: endpoint validation is strict: only one or two data lanes, clock lane zero, and one exact link frequency. PLL math and line/vblank/exposure range changes can misprogram timing. Streaming error paths must release runtime PM references. Tests should cover both mono/Bayer DT compatibles, invalid optical variant mismatch, supported mode selection, RAW8/RAW10 code selection with H/V flips, vblank-driven exposure range changes, LED GPIO property validation, stream start failure unwinds, and stop-time exposure caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vd56g3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vgxy61.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/vgxy61.c

Purpose: V4L2 subdevice driver for the ST VG5661/VG5761 global-shutter sensor family. It detects the sensor variant, uploads and verifies a firmware patch, configures CSI-2 lane mapping, clocks, ROI/binning, HDR modes, exposure/gain, strobe GPIOs, test patterns, and stream control.

Important APIs/types/functions: `struct vgxy61_dev` stores I2C/regmap resources, media pad/subdev, regulators, reset GPIO, clock, model dimensions/modes, CSI output control, timing, HDR/exposure/gain/strobe state, and a lock-protected control handler. Important functions include `vgxy61_probe()`, `vgxy61_power_on()`, `vgxy61_detect()`, `vgxy61_patch()`, `vgxy61_configure()`, `vgxy61_tx_from_ep()`, `vgxy61_set_fmt()`, `vgxy61_s_stream()`, `vgxy61_stream_enable()`, `vgxy61_stream_disable()`, and the control update helpers for HDR, vblank, exposure, analog/digital gain, pattern generator, and strobe mode.

Control flow: probe builds the regmap, parses the CSI-2 endpoint, checks xclk range, reads optional strobe polarity, initializes the subdev/media entity, obtains reset/regulators, powers on the sensor, detects model/cut/NVM state, patches firmware, configures PLL/output registers, selects per-model mode tables, initializes controls, enables runtime PM, and registers the async subdev. Stream enable checks line bandwidth against MIPI capacity, resumes PM, writes format/datatype/readout/ROI, applies cached settings, sends the start request, waits for request clear and streaming FSM, then locks H/V flip controls. Stream disable requests stop, waits for standby, unlocks flips, and drops PM.

State/persistence: driver state is cached in memory so controls can be set while not streaming and later applied in `vgxy61_apply_settings()`. The firmware patch is uploaded at power-on and verified by the sensor patch revision register; it is not persistent across power loss. Requests, mode state, exposure bounds, and `streaming` are runtime-only.

Dependencies/integration: uses CCI regmap, V4L2 controls/events/subdev pad ops, media entity link validation, V4L2 fwnode endpoint parsing, runtime PM, regulators, clocks, GPIO, MIPI CSI-2 constants, and compatible `st,st-vgxy61`.

Risks/test signals: HDR exposure formulas clamp to hardware rules and can produce warnings if ranges invert. The patch writer honors I2C adapter max-write quirks but still depends on chunked writes succeeding. Lane remapping assumes valid physical lane indexes. Tests should cover VG5661 and VG5761 mode tables, invalid cut1 rejection, patch version mismatch, xclk range limits, one/two/four-lane endpoint parsing, bandwidth rejection, HDR/vblank/exposure range updates, control changes while streaming vs idle, and PM cleanup after failed stream start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vgxy61.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/video-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/video-i2c.c

Purpose: generic V4L2 video-node driver for simple I2C thermal image sensors, currently Panasonic AMG88xx Grid-Eye and Melexis MLX90640. It exposes fixed-size frame capture through videobuf2, runtime power management, AMG88xx hwmon thermistor readings, and MLX90640 EEPROM through nvmem.

Important APIs/types/functions: `struct video_i2c_chip` describes per-chip format, frame size, intervals, buffer size, bpp, regmap config, setup/xfer/power/hwmon/nvmem hooks. `struct video_i2c_data` owns V4L2 device/video_device, vb2 queue, active buffer list, capture kthread, locks, sequence, regmap, and selected frame interval. Main paths are `video_i2c_probe()`, `video_i2c_remove()`, vb2 ops `queue_setup()`, `buffer_prepare()`, `buffer_queue()`, `start_streaming()`, `stop_streaming()`, capture thread `video_i2c_thread_vid_cap()`, and ioctl ops for format/input/frame interval.

Control flow: probe allocates state, selects chip data from I2C/OF match, initializes regmap and V4L2 device, configures a vmalloc-backed capture queue, powers the chip if needed, enables runtime PM autosuspend, optionally registers hwmon/nvmem, then registers the video node. Streaming resumes PM, applies chip frame-rate setup, starts a freezable kthread, and returns queued buffers as each I2C bulk read completes. Stop kills the thread, autosuspends, and returns all pending buffers with error state.

State/persistence: frame interval, sequence number, queued buffers, and thread pointer are in-memory only. MLX90640 nvmem exposes device EEPROM contents but the driver itself does not persist settings. Runtime PM powers AMG88xx sleep/normal mode and leaves MLX90640 without chip-specific power hooks.

Dependencies/integration: integrates I2C regmap, V4L2 video_device/ioctls, vb2-vmalloc, runtime PM, kthreads/freezer, hwmon, nvmem, and OF/I2C match tables.

Risks/test signals: the capture thread drops the newest queued list entry, so queue ordering expectations should be checked. I2C read failures produce errored buffers. `s_parm` changes frame interval without an explicit streaming busy check. Tests should cover minimum two-buffer queue setup, read/mmap/userptr/dmabuf capture, frame interval clamping for both chips, AMG88xx power-on reset delays and thermistor sign handling, MLX90640 EEPROM reads, kthread stop race cleanup, and runtime PM reference balance on start failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/video-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vp27smpx.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/vp27smpx.c

Purpose: legacy V4L2 I2C subdevice driver for the VP27SMPX audio processor/multiplexer. It tracks whether the parent is using radio or TV mode and programs audio mode bytes for mono, stereo, and bilingual modes.

Important APIs/types/functions: `struct vp27smpx_state` holds the subdev, `radio` flag, and cached `audmode`. `vp27smpx_set_audmode()` writes the three-byte mode command. Subdev ops are `vp27smpx_s_radio()`, `vp27smpx_s_std()`, `vp27smpx_s_tuner()`, `vp27smpx_g_tuner()`, and `vp27smpx_log_status()`. Probe checks `I2C_FUNC_SMBUS_BYTE_DATA`, allocates state, initializes the subdev, defaults to stereo, and writes the initial mode.

Control flow: setting radio marks the device as radio and suppresses TV tuner audio programming. Setting a video standard clears radio mode. `s_tuner` applies the requested audio mode only when not in radio mode. `g_tuner` returns stereo/LANG1/LANG2 capabilities and the cached mode for TV use.

State/persistence: only cached in-memory `radio` and `audmode` exist. The chip register state is volatile and initialized at probe.

Dependencies/integration: depends on Linux I2C, V4L2 subdev tuner/video/core ops, and a parent bridge that routes tuner calls to this subdevice.

Risks/test signals: `i2c_master_send()` errors are logged but not propagated from tuner operations. Radio mode hides state changes. Tests should cover mode byte mapping for all V4L2 tuner modes, radio vs TV transitions, initial stereo write, adapter functionality rejection, and remove-time subdev unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vp27smpx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vpx3220.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/vpx3220.c

Purpose: V4L2 I2C subdevice driver for VPX3220A/VPX3216B/VPX3214C analog video decoders. It initializes register and fast-processor tables, controls video standard, input routing, streaming output enable, signal/standard detection, and brightness/contrast/saturation/hue controls.

Important APIs/types/functions: `struct vpx3220` caches a 255-byte register shadow, control handler, current norm/input/enable. Low-level helpers are `vpx3220_write()`, `vpx3220_read()`, `vpx3220_fp_status()`, `vpx3220_fp_write()`, `vpx3220_fp_read()`, and block writers. Video ops include `vpx3220_init()`, `vpx3220_s_std()`, `vpx3220_s_routing()`, `vpx3220_s_stream()`, `vpx3220_querystd()`, and `vpx3220_g_input_status()`. Controls are implemented by `vpx3220_s_ctrl()`.

Control flow: probe validates SMBus byte/word support, creates controls, reads version/product registers for logging, writes common and FP initialization tables, and defaults to PAL. Standard changes save the current input-selection FP register, write NTSC/PAL/SECAM timing table, update `norm`, then restore/latch input selection. Status reads FP status register `0x0f3` to decide no-signal and constrain the reported standard mask.

State/persistence: V4L2 control values and `norm` are in-memory; register writes are volatile. The `reg[]` shadow is updated by byte writes but not by all FP writes.

Dependencies/integration: uses I2C SMBus byte/word transactions, V4L2 controls and subdev video/core ops, legacy analog TV standard constants, and parent bridge routing/streaming calls.

Risks/test signals: FP accesses return `-1` rather than standard errno in several paths; some write-block return values are ignored during init. Input/state fields are not fully updated by routing/stream functions. Tests should cover chip ID logging for all supported product IDs, FP busy timeout, standard table writes, invalid standard/input rejection, signal-status standard inference, control register mapping, and removal cleanup of the ctrl handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vpx3220.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/wm8739.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/wm8739.c

Purpose: V4L2 I2C subdevice driver for the WM8739 audio ADC. It configures reset, power, digital audio interface format, sample rate, activation, and clustered volume/mute/balance controls.

Important APIs/types/functions: `struct wm8739_state` contains the subdev, control handler, audio control cluster, and cached `clock_freq`. `wm8739_write()` performs 9-bit register-value writes over SMBus byte data with retries. `wm8739_s_ctrl()` maps V4L2 audio volume/mute/balance to left/right ADC volume registers. `wm8739_s_clock_freq()` programs 32/44.1/48 kHz sampling control. Probe initializes controls and writes the base register sequence.

Control flow: probe checks adapter functionality, allocates state, initializes subdev and controls, clusters volume/mute/balance, resets the codec, powers ADC/oscillator, configures 24-bit left-justified master mode, selects 48 kHz, activates, then applies controls. Control updates compute per-channel gain from volume scaled by balance, optionally set mute bit, and write R0/R1. Sample-rate changes deactivate R9, update R8 for recognized rates, and reactivate.

State/persistence: only `clock_freq` and V4L2 control state are cached in memory. Hardware register state is volatile and reinitialized at probe.

Dependencies/integration: depends on I2C SMBus byte-data support, V4L2 subdev core/audio ops, V4L2 controls, and parent bridge code that calls audio sample-rate ops.

Risks/test signals: unsupported sample rates leave the previous R8 setting but still reactivate and cache the requested frequency. I2C write failures return `-1`, and most initialization writes are not aborted. Tests should cover audio control scaling, mute bit behavior, balance extremes, all three supported sample rates, unsupported rate behavior, retry exhaustion, and remove-time ctrl cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/wm8739.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/wm8775.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/wm8775.c

Purpose: V4L2 I2C subdevice driver for the WM8775 audio ADC/mux. It initializes the codec, routes up to four input bits to the ADC, controls mute/volume/balance/loudness, and supports a Nova-S-specific initialization path through platform data.

Important APIs/types/functions: `struct wm8775_state` stores subdev, control handler, audio controls, and cached input bitmask. `wm8775_write()` writes register/value pairs over SMBus with retries. `wm8775_set_audio()` computes left/right ADC gain and safely mutes/unmutes around changes. Subdev callbacks are `wm8775_s_routing()`, `wm8775_s_ctrl()`, `wm8775_s_frequency()`, and `wm8775_log_status()`.

Control flow: probe checks platform data for `is_nova_s`, validates SMBus support, creates controls, resets and configures interface/power/ALC/noise gate/input registers, then either applies generic gain/ALC defaults or Nova-S-specific ALC and audio routing. Routing validates a 0..15 input mask, updates cached input, and only programs hardware when volume is nonzero and not muted. Loudness toggles ALC enable in R17.

State/persistence: control values and input mask are in-memory. Codec registers are volatile and reinitialized at probe; no persistent settings are stored.

Dependencies/integration: depends on I2C SMBus byte-data support, V4L2 subdev audio/tuner/core ops, V4L2 controls, and optional `struct wm8775_platform_data` from board drivers.

Risks/test signals: route changes can be skipped while muted or volume zero, relying on later control changes to apply. Initialization ignores individual write failures. Tests should cover all 16 input masks, mute/quiet gain update sequencing, volume/balance scaling, loudness/ALC bit changes, Nova-S and generic init paths, frequency-triggered audio refresh, and invalid input rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/wm8775.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/mc/Kconfig

Purpose: Kconfig fragment for media-controller-specific options. It currently defines `MEDIA_CONTROLLER_DVB`, an experimental boolean that enables Media Controller API support for DVB.

Important APIs/types/functions: no runtime APIs. The important symbol is `MEDIA_CONTROLLER_DVB`, which depends on `MEDIA_CONTROLLER && DVB_CORE` and is presented as "Enable Media controller for DVB (EXPERIMENTAL)".

Control flow: during kernel configuration, this file contributes one selectable option under the media-controller area. If enabled, downstream DVB code can conditionally compile media-controller integration.

State/persistence: state is the generated kernel configuration symbol in `.config`; no runtime persistence.

Dependencies/integration: sourced by the broader media Kconfig tree. It ties the media-controller core to DVB core availability.

Risks/test signals: since the help text marks DVB media-controller support experimental, build coverage should include both enabled and disabled combinations with `MEDIA_CONTROLLER` and `DVB_CORE`. Defconfig and randconfig coverage can catch unmet dependency or stale symbol use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/mc/Makefile

Purpose: builds the media-controller core object `mc.o` from device, devnode, entity, and request components, with optional USB media-device allocator support.

Important APIs/types/functions: `mc-objs` includes `mc-device.o`, `mc-devnode.o`, `mc-entity.o`, and `mc-request.o`; `mc-dev-allocator.o` is added when `CONFIG_USB` is non-empty. `obj-$(CONFIG_MEDIA_SUPPORT) += mc.o` links the aggregate into the media support build.

Control flow: Kbuild composes a single `mc.o` module/built-in object based on configuration. USB-specific allocator APIs are compiled only when USB is configured.

State/persistence: no runtime state; build output reflects configuration.

Dependencies/integration: integrates with Kbuild and the media subsystem. Exported symbols from the object are used by V4L2, DVB, USB, PCI, and media graph drivers.

Risks/test signals: the `ifneq ($(CONFIG_USB),)` check includes the allocator for either built-in or module USB configurations. Build tests should cover `MEDIA_SUPPORT=y/m`, `CONFIG_USB=n/y/m`, and users of `media_device_usb_allocate()` to ensure symbol availability matches callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-dev-allocator.c -->
# sources/distributed-fs/ceph-client/drivers/media/mc/mc-dev-allocator.c

Purpose: shared USB media-device allocator that gives multiple USB interface drivers for the same `usb_device` a single refcounted `struct media_device` instance.

Important APIs/types/functions: `struct media_device_instance` embeds `struct media_device`, owner module, list node, and `kref`. Public exports are `media_device_usb_allocate()` and `media_device_delete()`. Internal `__media_device_get()` searches or creates instances under `media_device_lock`; `media_device_instance_release()` unregisters, cleans up, removes from the global list, and frees.

Control flow: allocation locks the global list, finds an existing instance by `udev->dev` or creates one, takes a kref, manages owner module references when the requester differs, initializes the media device for USB if not already initialized, then returns it. Delete drops the module reference if needed and decrements the kref; last put unregisters and frees.

State/persistence: global in-memory list and krefs persist while drivers hold references. There is no durable persistence.

Dependencies/integration: depends on USB core, media-device helpers, module refcounting, and callers that pair `media_device_usb_allocate()` with `media_device_delete()`.

Risks/test signals: module reference acquisition failure is logged but the media device is still returned, which can surprise lifetime assumptions. Tests should cover multiple interfaces sharing one USB media device, owner mismatch refcounting, last-delete cleanup, allocation failure, initialization-on-first-use, and hot-unplug races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-dev-allocator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-device.c -->
# sources/distributed-fs/ceph-client/drivers/media/mc/mc-device.c

Purpose: implements the media-controller device object, userspace ioctls for graph/topology/link/request allocation, entity registration/unregistration, sysfs/debugfs hooks, and PCI/USB initialization helpers.

Important APIs/types/functions: userspace ioctl handlers include `media_device_get_info()`, `media_device_enum_entities()`, `media_device_enum_links()`, `media_device_setup_link()`, `media_device_get_topology()`, and `media_device_request_alloc()`. Registration exports include `media_device_init()`, `media_device_cleanup()`, `__media_device_register()`, `media_device_unregister()`, `media_device_register_entity()`, `media_device_unregister_entity()`, entity notify registration, `media_device_pci_init()`, and `__media_device_usb_init()`.

Control flow: device registration allocates a `media_devnode`, installs media-device file ops, registers `/dev/mediaX`, creates the model sysfs attribute, and optionally debugfs request counters. Ioctls copy arguments into a stack or heap buffer, optionally take `graph_mutex`, execute the handler, and copy results back. Entity registration assigns an internal ID, creates graph objects for entity and pads, calls notifiers, and resizes the PM graph walk. Unregistration clears the devnode registered bit, removes all entities, notifiers, interfaces, debugfs/sysfs, and unregisters the devnode.

State/persistence: `struct media_device` contains runtime graph lists, topology version, mutexes, IDA, request counters, bus/model/serial strings, and devnode pointer. Topology state is kernel memory only; userspace can observe it through ioctls.

Dependencies/integration: depends on `mc-devnode`, `mc-entity`, `mc-request`, Linux media uAPI structs, compat ioctl handling, debugfs, PCI/USB core helpers, and driver-provided `media_device_ops`.

Risks/test signals: topology enumeration must handle changing counts and userspace buffer sizes with `-ENOSPC`. Link setup depends on graph locking and entity callbacks. Request allocation is available only when request ops exist. Tests should cover all media ioctls, compat enum-links path, static topology version behavior, dynamic entity registration/unregistration, sysfs model read, debugfs counters, PCI/USB bus info formatting, and error unwinds after devnode registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-devnode.c -->
# sources/distributed-fs/ceph-client/drivers/media/mc/mc-devnode.c

Purpose: generic `/dev/mediaX` character-device registration layer for media devices, including dynamic major allocation, minor bitmap management, open/unregister race protection, file-operation dispatch, and media bus registration.

Important APIs/types/functions: exported functions are `media_devnode_register()`, `media_devnode_unregister_prepare()`, and `media_devnode_unregister()`. Internal file ops wrap `read`, `write`, `poll`, `ioctl`, compat ioctl, `open`, and `release` by checking registration state and dispatching to `devnode->fops`.

Control flow: subsystem init allocates a character-device range and registers the media bus. Register finds a free minor under `media_devnode_lock`, initializes `struct device` and `cdev`, sets the registered flag, and calls `cdev_device_add()`. Open takes the same lock, verifies the registered bit, gets a device ref, and then calls driver open. Unregister prepare clears the registered bit to stop new opens, and unregister removes the cdev/device, clears minor allocation, and drops the final device ref.

State/persistence: global `media_dev_t`, `media_devnode_nums` bitmap, `media_devnode_lock`, and `media_debugfs_root` live for the module lifetime. Individual devnodes are refcounted by the device core.

Dependencies/integration: used by `mc-device.c` and depends on Linux cdev/device/bus APIs, media devnode/device headers, compat ioctl support, and debugfs cleanup.

Risks/test signals: race safety depends on clearing the registered flag before cdev deletion and pairing get/put device refs around open/release. Tests should cover minor exhaustion, open while unregistering, missing fops returning `-EINVAL`/`-ENOTTY`, poll after unregister returning error/hup, cdev add failure cleanup, and module init/exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-devnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-entity.c -->
# sources/distributed-fs/ceph-client/drivers/media/mc/mc-entity.c

Purpose: core media graph implementation: graph object IDs/lists, entity pad initialization, graph walking, pipeline population/validation/start/stop, pad and interface link creation/removal, remote-pad helpers, and interface/ancillary link management.

Important APIs/types/functions: exports include `media_entity_pads_init()`, `media_graph_walk_init/start/next/cleanup()`, `__media_pipeline_start()`, `media_pipeline_start()`, `__media_pipeline_stop()`, `media_pipeline_stop()`, `media_pipeline_alloc_start()`, pipeline iterators, `media_create_pad_link()`, `media_create_pad_links()`, `media_entity_remove_links()`, `__media_entity_setup_link()`, `media_entity_setup_link()`, `media_entity_find_link()`, remote-pad helpers, `media_get_pad_index()`, `media_entity_get_fwnode_pad()`, `media_devnode_create/remove()`, `media_create_intf_link()`, interface link removers, and `media_create_ancillary_link()`.

Control flow: graph object creation assigns typed IDs and appends to media-device lists, bumping topology version. Simple graph walk follows enabled data links depth-first with an entity bitmap. Pipeline start builds a pad-level pipeline by traversing internal pad dependencies and enabled graph links, validates pad exclusivity, link validation callbacks, and must-connect pads, then marks each pad with the active pipeline and increments start count. Link setup rejects immutable/non-data flag changes, blocks non-dynamic changes while endpoints stream, calls media-device pre/post notifiers and entity link_setup callbacks, and mirrors flags to backlinks.

State/persistence: all graph objects, link lists, pad pipeline pointers, topology version, and pipeline pad lists are in-memory. Pipeline objects can be caller-owned or allocated by `media_pipeline_alloc_start()` and freed on final stop.

Dependencies/integration: depends on media-device graph lists/mutexes, media entity operations, fwnode endpoint parsing, bitmap helpers, and drivers that create pads/links and implement `link_validate`, `link_setup`, `has_pad_interdep`, or `get_fwnode_pad`.

Risks/test signals: graph correctness depends on balanced link/backlink allocation and removal. Pipeline traversal has bounded stack growth and validates busy pads; mistakes can create stale `pad->pipe` pointers. Tests should cover pad flag validation, enabled/disabled link traversal, internal route callbacks, must-connect enforcement, link validation failure rollback, dynamic vs non-dynamic link changes while streaming, n:n pad link creation, unique remote-pad error cases, and topology version increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-entity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-request.c -->
# sources/distributed-fs/ceph-client/drivers/media/mc/mc-request.c

Purpose: media request API implementation. It allocates request file descriptors, queues requests through driver validation/queue ops, supports poll/reinit/close, manages request object binding/completion/unbinding, and tracks request/request-object counters.

Important APIs/types/functions: exported functions include `media_request_put()`, `media_request_get_by_fd()`, `media_request_alloc()`, `media_request_object_find()`, `media_request_object_put()`, `media_request_object_init()`, `media_request_object_bind()`, `media_request_object_unbind()`, `media_request_object_complete()`, and `media_request_manual_complete()`. Internal ioctl paths are `media_request_ioctl_queue()` and `media_request_ioctl_reinit()`.

Control flow: allocation creates a request through optional driver `req_alloc`, initializes state/list/lock/waitqueue/kref, creates an anonymous inode fd, stores the request in file private data, and publishes the fd. Queue serializes with `mdev->req_queue_mutex`, transitions IDLE to VALIDATING, calls `req_validate`, then sets QUEUED before invoking non-failing `req_queue`. Completion happens when bound objects complete/unbind and `num_incomplete_objects` reaches zero, unless manual completion is active. Reinit is allowed only from IDLE or COMPLETE with no active access count, then cleans and returns to IDLE.

State/persistence: requests and objects are in-memory and fd/kref lifetime-managed. State transitions are protected by a spinlock; queue/cancel/update serialization uses `req_queue_mutex`. No durable persistence exists.

Dependencies/integration: depends on media-device request ops, anon inode/file descriptor helpers, spinlocks, waitqueues, krefs, and request-aware users such as V4L2 controls/buffers.

Risks/test signals: object binding assumes request state is UPDATING or QUEUED; invalid state transitions are WARN paths. Completion drops the queue reference via `media_request_put()`, so refcount balance is critical. Tests should cover queue validation failure, queue success with immediate object completion, poll returning `EPOLLPRI`/`EPOLLERR`, reinit busy cases, fd lookup with wrong mdev/fops, object find/get/put lifecycle, manual completion, and cleanup while objects remain bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mc/mc-request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/mmc/Kconfig

Purpose: top-level Kconfig include point for media drivers on MMC/SDIO buses.

Important APIs/types/functions: no runtime APIs. The file sources `drivers/media/mmc/siano/Kconfig`, thereby exposing Siano SDIO DVB adapter configuration under the media tree.

Control flow: during configuration, this file delegates all current MMC media options to the `siano` subdirectory.

State/persistence: generated kernel configuration only; no runtime state.

Dependencies/integration: integrated by the broader media Kconfig hierarchy and coupled to the Siano SDIO driver subtree.

Risks/test signals: minimal file, but stale include paths would hide all MMC media options. Kconfig tests should confirm `SMS_SDIO_DRV` remains visible when DVB/MMC prerequisites are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/mmc/Makefile

Purpose: top-level Kbuild file for MMC/SDIO media drivers.

Important APIs/types/functions: `obj-y += siano/` always descends into the Siano subdirectory; subdirectory Kbuild decides whether concrete objects are built.

Control flow: Kbuild visits `drivers/media/mmc/siano` whenever this directory is part of the build.

State/persistence: build-only state; no runtime behavior.

Dependencies/integration: integrates with Kbuild and the Siano media SDIO driver Makefile.

Risks/test signals: unconditional descent is safe if the subdir gates objects correctly. Build tests should cover `SMS_SDIO_DRV=n/m/y` to ensure no unwanted object is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/siano/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/mmc/siano/Kconfig

Purpose: Kconfig options for Siano SMS1xxx Mobile Digital TV devices connected through SDIO.

Important APIs/types/functions: defines `SMS_SDIO_DRV`, a tristate "Siano SMS1xxx based MDTV via SDIO interface". It depends on `DVB_CORE`, `HAS_DMA`, `MMC`, and the conditional RC core expression; it selects `MEDIA_COMMON_OPTIONS` and `SMS_SIANO_MDTV`.

Control flow: when selected, the SDIO transport driver and shared Siano common stack are built so SDIO boards can register with the Siano core.

State/persistence: kernel configuration symbol only.

Dependencies/integration: integrates the MMC/SDIO bus with DVB core, DMA-capable systems, optional RC support, and common Siano media code.

Risks/test signals: dependency combinations with `RC_CORE` are easy to regress. Kconfig tests should cover built-in/module configurations for DVB, MMC, RC, and common Siano options, and verify that selecting SDIO pulls required common code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/siano/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/siano/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/mmc/siano/Makefile

Purpose: Kbuild file for the Siano SDIO transport driver.

Important APIs/types/functions: `obj-$(CONFIG_SMS_SDIO_DRV) += smssdio.o` builds the transport. `ccflags-y += -I $(srctree)/drivers/media/common/siano` gives access to shared Siano headers.

Control flow: when `SMS_SDIO_DRV` is enabled as built-in or module, `smssdio.o` is compiled with the common Siano include path.

State/persistence: build-only state.

Dependencies/integration: depends on shared common Siano source/header layout and the Kconfig-selected `SMS_SIANO_MDTV` common implementation.

Risks/test signals: include path drift breaks compilation. Build tests should cover module and built-in SDIO driver builds and ensure common Siano headers remain reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/siano/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/siano/smssdio.c -->
# sources/distributed-fs/ceph-client/drivers/media/mmc/siano/smssdio.c

Purpose: SDIO transport driver for Siano SMS1xxx MDTV devices. It registers SDIO IDs, sends host requests to the device, receives interrupt-driven responses/data blocks, and connects the SDIO function to the shared Siano core.

Important APIs/types/functions: `struct smssdio_device` holds the `sdio_func`, Siano `coredev`, and partial split-message buffer. SDIO callbacks are `smssdio_probe()`, `smssdio_remove()`, and interrupt handler `smssdio_interrupt()`. Siano core callback `smssdio_sendrequest()` transmits buffers. The ID table maps Siano vendor/device IDs to board IDs.

Control flow: probe allocates transport state, fills `smsdevice_params_t`, rejects Stellar as unsupported, registers the common Siano device, sets board ID, claims the SDIO host, enables the function, sets 128-byte block size, claims IRQ, stores drvdata, releases host, and starts the core device. Interrupts acknowledge by reading `SMSSDIO_INT`, allocate or reuse a split buffer, read the first 128-byte block, determine remaining aligned length from the SMS header, read the rest either in one transfer or block-by-block fallback, endian-fix the message, and pass it to `smscore_onresponse()`. Remove unregisters the core, releases IRQ, disables function, and frees transport state.

State/persistence: runtime state is the SDIO function, common core device, and optional `split_cb`. Device buffers are transient and owned by the Siano core once delivered. No durable persistence.

Dependencies/integration: depends on Linux MMC/SDIO core, shared Siano `smscoreapi`, card database, endian helpers, firmware infrastructure through the core, and DMA-capable buffer allocation via core registration.

Risks/test signals: interrupt error path after failing the initial block read leaks `cb` because it returns without `smscore_putbuffer()`. Remove notes a racy split buffer cleanup. Pointer arithmetic is done on `void *`, relying on compiler extension. Tests should cover all matched board IDs, unsupported Stellar, enable/blocksize/IRQ/start unwind paths, split-message two-interrupt handling, fallback block reads after `-EINVAL`, endian conversion, send chunking by block size, and unplug during pending split message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/mmc/siano/smssdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/Kconfig

Purpose: top-level Kconfig menu for PCI/PCIe media adapters. It gates camera, analog TV, hybrid, digital TV, Intel, and sample skeleton PCI media drivers behind `PCI` and `MEDIA_PCI_SUPPORT`.

Important APIs/types/functions: defines `MEDIA_PCI_SUPPORT` menuconfig and `VIDEO_PCI_SKELETON`. It sources many subdriver Kconfig files based on feature groups such as `MEDIA_CAMERA_SUPPORT`, `MEDIA_ANALOG_TV_SUPPORT`, and `MEDIA_DIGITAL_TV_SUPPORT`.

Control flow: configuration enters this file only under `if PCI`. If `MEDIA_PCI_SUPPORT` is enabled, it conditionally exposes driver families by media capability class. The skeleton driver requires `SAMPLES`, `MEDIA_TEST_SUPPORT`, `PCI`, and `VIDEO_DEV`, and selects vb2 DMA-contig support.

State/persistence: kernel configuration symbols only.

Dependencies/integration: integrates PCI media drivers into the global media Kconfig tree and ties each family to media feature-class symbols.

Risks/test signals: misplaced source includes can hide whole driver families. Kconfig tests should cover camera-only, analog-only, digital-only, and mixed support, plus skeleton sample dependencies, with `PCI=n` ensuring the menu is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/Makefile

Purpose: Kbuild dispatcher for PCI media drivers. It descends into digital-TV and common PCI subdirectories and conditionally builds analog/capture driver directories by config symbol.

Important APIs/types/functions: unconditional `obj-y` descends into `ttpci`, `b2c2`, `pluto2`, `dm1105`, `pt1`, `pt3`, `mantis`, `ngene`, `ddbridge`, `saa7146`, `smipcie`, `netup_unidvb`, and `intel`. Conditional object lines include `VIDEO_BT848`, `VIDEO_COBALT`, `VIDEO_CX18`, `VIDEO_CX23885`, `VIDEO_CX25821`, `VIDEO_CX88`, `VIDEO_DT3155`, `VIDEO_IVTV`, `VIDEO_MGB4`, `VIDEO_SAA7134`, `VIDEO_SAA7164`, `VIDEO_SOLO6X10`, `VIDEO_TW5864`, `VIDEO_TW686X`, `VIDEO_TW68`, and `VIDEO_ZORAN`.

Control flow: Kbuild always visits some subdirectories so their internal Makefiles can gate objects, while other directories are only entered when their config symbol is enabled.

State/persistence: build-only state.

Dependencies/integration: integrates with Kbuild and all PCI media subdriver directories. The comments request alphabetic ordering, though the unconditional list is not purely alphabetical.

Risks/test signals: unconditional descent relies on subdirectories being present and self-gated. Build tests should cover allmodconfig, allyesconfig, randconfig, and selected individual driver configs to catch missing subdir Kconfig/Makefile synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/Kconfig

Purpose: Kconfig options for Technisat/B2C2 FlexCop PCI DVB/ATSC cards.

Important APIs/types/functions: `DVB_B2C2_FLEXCOP_PCI` is a tristate depending on `DVB_CORE && I2C`. `DVB_B2C2_FLEXCOP_PCI_DEBUG` depends on the PCI driver and selects shared `DVB_B2C2_FLEXCOP_DEBUG`.

Control flow: enabling the main symbol builds PCI transport support for Air/Sky/CableStar2 cards. Enabling debug exposes the shared FlexCop debug module option across the FlexCop drivers.

State/persistence: kernel configuration only.

Dependencies/integration: integrates PCI transport with DVB core, I2C, and common FlexCop support under `drivers/media/common/b2c2`.

Risks/test signals: debug selection affects common code as well as PCI. Kconfig/build tests should cover driver disabled, module, built-in, and debug enabled combinations, including I2C/DVB dependency absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/Makefile

Purpose: Kbuild file for the B2C2 FlexCop PCI driver object.

Important APIs/types/functions: when `CONFIG_DVB_B2C2_FLEXCOP_PCI` is set, `b2c2-flexcop-pci-objs` includes `flexcop-dma.o`; it always includes `flexcop-pci.o` before `obj-$(CONFIG_DVB_B2C2_FLEXCOP_PCI) += b2c2-flexcop-pci.o`. `ccflags-y` adds the common FlexCop include path.

Control flow: Kbuild composes one module/built-in object from PCI glue plus DMA support under the driver config. The common include path lets PCI code include shared FlexCop headers.

State/persistence: build-only state.

Dependencies/integration: depends on common B2C2 FlexCop headers and the config symbol from the local Kconfig. Runtime integration is with the common FlexCop core and PCI bus driver files outside this work item.

Risks/test signals: the conditional addition of DMA object should match all configurations where PCI object is linked. Build tests should cover module and built-in builds, header include path validity, and no-object build when the config is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/Makefile -->
