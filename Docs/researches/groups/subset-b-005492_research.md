# subset-b-005492 Research

Grouped source research for USB gadget mass-storage, MIDI, MIDI 2.0, and CDC NCM function drivers under `sources/distributed-fs/ceph-client/drivers/usb/gadget/function`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_mass_storage.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_mass_storage.c

## Purpose

`f_mass_storage.c` implements the USB composite Mass Storage Function. It exposes one or more file-backed logical units to a USB host through Bulk-Only Transport and a SCSI command emulation layer, with configfs and legacy helper entry points for gadget compositions.

## Important APIs, Types, and Functions

The central runtime object is `struct fsg_common`, which owns gadget references, EP0 state, LUN array, pipeline buffers, exception state, SCSI command state, wait queues, the backing-file semaphore, and the main kernel thread. `struct fsg_dev` is the per-USB-function endpoint wrapper. Public helper exports include `fsg_common_set_sysfs()`, `fsg_common_set_num_buffers()`, `fsg_common_set_cdev()`, `fsg_common_create_lun()`, `fsg_common_create_luns()`, `fsg_common_set_inquiry_string()`, `fsg_common_free_buffers()`, `fsg_common_remove_lun()`, `fsg_common_remove_luns()`, and `fsg_config_from_params()`.

Control requests enter through `fsg_setup()` for Bulk-Only reset and Get Max LUN. USB data movement is handled by `start_transfer()`, `start_in_transfer()`, `start_out_transfer()`, `bulk_in_complete()`, and `bulk_out_complete()`. SCSI command handling is split across `received_cbw()`, `get_next_command()`, `do_scsi_command()`, `check_command()`, `finish_reply()`, and `send_status()`. The file-backed command implementations include `do_read()`, `do_write()`, `do_verify()`, `do_synchronize_cache()`, `do_inquiry()`, `do_request_sense()`, capacity and CD-ROM helpers, mode sense/select, start-stop, prevent-allow, and format-capacity handling.

## Control Flow

`fsg_alloc_inst()` creates configfs instance state, allocates buffer heads, and creates a default removable `lun.0`. `fsg_alloc()` creates a `usb_function`. `fsg_bind()` verifies at least one LUN, attaches strings, starts the `file-storage` kernel thread if needed, allocates interface and endpoints, and assigns FS/HS/SS descriptors. `fsg_set_alt()` and `fsg_disable()` do not directly reconfigure endpoints; they raise configuration-change exceptions for the main thread. `do_set_interface()` then disables old endpoints, frees requests, enables the selected endpoints, allocates per-buffer IN/OUT requests, and marks LUN unit attention as reset.

At runtime `fsg_main_thread()` loops through CBW receive, SCSI dispatch, data reply, and CSW status. It polls for signals and raised exceptions between each phase. CBW parsing validates signature, LUN, flags, CDB length, and transfer length. SCSI commands set expected direction and byte count, check the medium and CDB fields, perform file I/O under `filesem`, then update residue and sense data. Exceptions such as protocol reset, abort bulk-out, config change, and exit cancel pending USB requests, reset buffer state, optionally clear forced halts, and complete delayed EP0 status.

## State and Persistence Behavior

Persistent device-visible state is the host-visible SCSI medium backed by files or block devices opened by `storage_common` helpers. Driver state is in-memory: LUN flags, sense data, unit attention, prevent-removal flag, CBW/CSW fields, buffer-head state, and endpoint enablement. The backing file remains open while the main thread is alive, which intentionally keeps the underlying filesystem busy. `filesem` serializes backing file changes against command execution; `lock` protects exception state and thread pointer; wait queues coordinate USB completion with the main thread.

Configfs state controls `stall`, optional debug `num_buffers`, and per-LUN `file`, `ro`, `removable`, `cdrom`, `nofua`, `inquiry_string`, and `forced_eject`. Sysfs LUN attributes are available when `fsg_common_set_sysfs()` is used. No driver settings are persisted across module or gadget teardown.

## Dependencies and Integration Points

The implementation depends on the USB composite framework, gadget endpoint APIs, configfs, kernel threads/freezer, Linux file I/O (`kernel_read`, `kernel_write`, fsync/invalidate helpers), and `storage_common.h` for LUN definitions, descriptors, SCSI constants, and attribute helpers. It registers as `DECLARE_USB_FUNCTION_INIT(mass_storage, ...)`, so configfs gadgets instantiate it as the `mass_storage` function. Legacy composite gadgets can use the exported common helpers and `fsg_config_from_params()`.

## Risks and Test Signals

Risks include races around delayed EP0 status tags, endpoint halt/wedge recovery on controllers with limited stall support, keeping backing files open during shutdown, partial read/write rounding to block size, SCSI phase-error correctness, overflow in command block counts, malformed CBW handling, and configfs LUN mutation while bound. `fsg_common_set_num_buffers()` accepts the requested count and relies on callers/configfs policy; very small or large values should be tested under debug builds.

Strong test signals include enumeration at FS/HS/SS, Get Max LUN and Bulk Reset, invalid CBW wedge and reset recovery, read/write/verify/capacity/mode-sense command sequences from Linux, Windows, and macOS hosts, removable-media eject and forced-eject behavior, read-only/CD-ROM/nofua combinations, backing-file replacement while idle versus busy, suspend/freezer interaction, bind/unbind with live transfers, and failure injection in endpoint autoconfig, request allocation, and backing-file I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_mass_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_mass_storage.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_mass_storage.h

## Purpose

`f_mass_storage.h` declares the shared Mass Storage Function configuration contract used by `f_mass_storage.c` and legacy gadget users. It exposes module-parameter helpers, configfs option structures, LUN configuration structures, and the exported `fsg_common` management API.

## Important APIs, Types, and Functions

`struct fsg_module_parameters` holds module-style arrays for backing files, read-only flags, removable flags, CD-ROM flags, no-FUA flags, LUN count, and stall behavior. `FSG_MODULE_PARAMETERS()` and the internal parameter macros define the matching module parameters, adding `num_buffers` when `CONFIG_USB_GADGET_DEBUG_FILES` is enabled.

`struct fsg_lun_opts` and `struct fsg_opts` are configfs-facing state containers. `struct fsg_lun_config` is the per-LUN construction input, including filename, `ro`, `removable`, `cdrom`, `nofua`, and inquiry string. `struct fsg_config` is the whole-function legacy configuration, including LUN array, optional callbacks/private data, vendor/product names, stall behavior, and buffer count. Prototypes expose the common setup, LUN lifecycle, buffer lifecycle, composite-device binding, inquiry-string setup, and module-parameter conversion functions implemented in `f_mass_storage.c`.

## Control Flow

The header has no executable control flow beyond the inline `fsg_opts_from_func_inst()`. Its structures determine how allocation flows in the C file: configfs creates `fsg_opts`, each LUN directory maps to `fsg_lun_opts`, and legacy users fill `fsg_config` either directly or through `fsg_config_from_params()`.

## State and Persistence Behavior

The header defines runtime-only state layouts. `fsg_opts.refcnt` and `lock` protect configfs mutation while functions are active; `no_configfs` distinguishes legacy gadget users from configfs-created functions. Persistence is external to the header: backing file contents persist, but option structures and module parameters are in-memory kernel state.

## Dependencies and Integration Points

It depends on `<linux/usb/composite.h>` and `storage_common.h` for composite-function and LUN definitions. The exported declarations are the integration boundary for older composite gadgets and for `f_mass_storage.c` itself. Changes here affect configfs function instantiation, legacy mass-storage gadgets, and any module that consumes the exported GPL symbols.

## Risks and Test Signals

Risks are mostly contract drift: changing structure fields, flag types, or module-parameter macro behavior can break legacy callers or configfs attribute semantics. `fsg_config_from_params()` depends on `file_count` and `luns` interpretation described by this header. Test signals include compiling both configfs and legacy gadget users, module-parameter parsing for multiple LUNs, debug and non-debug builds, and ABI-like behavior of default removable LUN creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_mass_storage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_midi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_midi.c

## Purpose

`f_midi.c` implements a USB MIDI 1.0 class function for the composite gadget framework. It bridges USB MIDIStreaming bulk endpoints to ALSA rawmidi substreams, supporting configurable cable counts, request sizes, queue depth, ALSA card index/id, and interface string through configfs.

## Important APIs, Types, and Functions

`struct f_midi` owns the USB function, IN/OUT bulk endpoints, ALSA card/rawmidi objects, endpoint request FIFO, work item, port counts, queue sizing, transmit lock, active output bitmap, and an array of `struct gmidi_in_port` for ALSA-output-to-USB-IN state. `struct gmidi_in_port` tracks the rawmidi substream, cable number, active flag, MIDI parser state, and buffered status/data bytes.

Descriptor construction uses AudioControl and MIDIStreaming descriptors plus dynamically generated jack descriptors for up to `MAX_PORTS` cables. USB request handling is in `f_midi_complete()`, `f_midi_handle_out_data()`, and `f_midi_read_data()`. MIDI byte packetization is in `f_midi_transmit_byte()` and `f_midi_do_transmit()`, while `f_midi_transmit()` and `f_midi_in_work()` drive queued transmission. ALSA callbacks are `f_midi_in_open/close/trigger()` for rawmidi output to USB IN and `f_midi_out_open/close/trigger()` for USB OUT to rawmidi input.

## Control Flow

`f_midi_alloc_inst()` creates configfs defaults: `buflen=512`, `qlen=32`, one input and one output port. `f_midi_alloc()` copies options, allocates the flexible `f_midi` instance, initializes cable numbers, allocates a FIFO of preallocated IN requests, and wires USB function callbacks. `f_midi_bind()` registers the ALSA card, assigns strings and two interfaces, autoconfigures bulk endpoints, builds jack and endpoint descriptors according to configured port counts, and copies FS/HS/SS descriptor sets.

When the host selects the MIDIStreaming alternate setting, `f_midi_set_alt()` enables endpoints, preallocates IN requests into `in_req_fifo`, allocates and queues OUT requests, and leaves completions to recycle requests. USB OUT completions decode four-byte USB MIDI event packets and deliver MIDI bytes to active ALSA input substreams. ALSA output triggers queue high-priority work that drains rawmidi bytes through the MIDI state machine into USB MIDI event packets and queues IN requests. Disable tears down endpoints, frees queued IN requests, and drops pending ALSA output.

## State and Persistence Behavior

Runtime state is volatile. MIDI running status, SysEx assembly, active cable flags, rawmidi substream pointers, and queued USB requests live in `struct f_midi`. `transmit_lock` serializes use of the IN request FIFO and parser state. `free_ref` coordinates lifetime between the USB function and ALSA rawmidi private free path. Configfs options are locked by `f_midi_opts.lock` and become immutable after active references. No MIDI data or configuration is persisted by the driver.

## Dependencies and Integration Points

The driver depends on the USB composite framework, USB Audio/MIDI descriptor definitions, `linux/usb/func_utils.h` request helpers, ALSA core/rawmidi, `kfifo`, workqueues, and configfs. It registers as `DECLARE_USB_FUNCTION_INIT(midi, ...)`, exposing a `midi` function in configfs. User space sees an ALSA rawmidi card named `MIDI Gadget` and a USB MIDIStreaming interface on the host side.

## Risks and Test Signals

Risks include MIDI parser correctness for running status, SysEx termination, real-time interleaving, and malformed USB MIDI CIN values; request leaks or double-free during disable and disconnect; endpoint queue failure recovery that halts OUT; unbounded config choices for `buflen` and `qlen`; port-count edge cases at 0 or 16; and lifetime coupling between ALSA card closure and USB function free.

Strong test signals include ALSA rawmidi loopback across all configured cables, SysEx and real-time message streams, short packets and disconnect while transfers are pending, repeated set-alt/disable cycles, FS/HS/SS descriptor validation, configfs writes rejected while bound, port-count boundary tests, and host interoperability with Linux/macOS/Windows class drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_midi2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_midi2.c

## Purpose

`f_midi2.c` implements a USB MIDI 2.0 gadget function with mandatory MIDI 1.0 compatibility. It exposes ALSA UMP endpoints and function blocks, builds USB MIDI 2.0 group terminal block descriptors, supports UMP Stream discovery/control messages, and converts between MIDI 1.0 USB event packets and UMP when the host selects altsetting 0.

## Important APIs, Types, and Functions

`struct f_midi2` is the per-function device state, containing the USB function, ALSA card, MIDI 1.0 compatibility endpoints, UMP conversion state, cable/group mappings, operation mode, queue lock, card configuration, UMP endpoint array, and string tables. `struct f_midi2_ep` represents one UMP endpoint with ALSA `snd_ump_endpoint`, configured endpoint info, function blocks, USB IN/OUT resources, and group-to-cable mapping. `struct f_midi2_usb_ep` and `struct f_midi2_req_ctx` manage request pools with a bitmap of free requests. `struct f_midi2_block` mirrors UMP function blocks and USB group terminal blocks.

UMP-native processing uses `process_ump()`, `process_ump_stream_msg()`, `reply_ump_stream_*()`, `f_midi2_ep_out_complete()`, `process_ump_transmit()`, and `f_midi2_ep_in_complete()`. MIDI 1.0 compatibility uses `process_midi1_byte()`, pending-byte helpers, `process_midi1_transmit()`, `f_midi2_midi1_ep_in_complete()`, and `f_midi2_midi1_ep_out_complete()`. Descriptor and endpoint setup is handled by `assign_block_descriptors()`, `f_midi2_setup()`, `f_midi2_create_card()`, `f_midi2_create_usb_configs()`, `fill_midi2_class_desc()`, `f_midi2_bind()`, `f_midi2_set_alt()`, and `f_midi2_get_alt()`.

## Control Flow

`f_midi2_alloc_inst()` creates a default configfs tree with `ep.0/block.0`, static blocks, request count 32, request buffer size 512, UMP processing enabled, protocol 2 with caps 1 and 2, and one MIDI1 group. Configfs can add endpoint groups and block groups before binding. `f_midi2_alloc()` verifies contiguous endpoints and blocks, validates protocol/group ranges, copies configfs state, assigns one-based GTB IDs, creates string definitions, and fills MIDI1 cable mappings. Allocation fails if no MIDI1-compatible group exists.

`f_midi2_bind()` creates the ALSA UMP card, attaches strings, assigns an AudioControl interface plus one MIDIStreaming interface with altsetting 0 for MIDI1 and altsetting 1 for MIDI2, initializes compatibility and native endpoints, builds speed-specific descriptors, and registers class-specific GTB descriptor handling through `setup()`. `set_alt()` switches operation mode, stops endpoints for the old mode, starts endpoints and queues OUT requests for the new mode, and `get_alt()` reports altsetting 1 only in MIDI2 mode. UMP stream discovery requests can return endpoint info, device info, endpoint name, product ID, stream config, function block info, and block names; stream config requests switch the ALSA UMP protocol.

## State and Persistence Behavior

State is in-memory and mode-dependent. Request pools are protected by `queue_lock` and tracked by per-endpoint `free_reqs` bitmaps. `operation_mode` is also exposed as a volatile ALSA rawmidi control. UMP protocol can change at runtime through stream config messages and is mirrored into ALSA via `snd_ump_switch_protocol()`. Configfs options are immutable once `refcnt` is nonzero. No data is persisted beyond ALSA/USB runtime objects.

## Dependencies and Integration Points

The driver depends on USB composite/gadget APIs, USB Audio and MIDI 2.0 descriptor definitions, `func_utils` request helpers, ALSA card/control APIs, ALSA UMP core, UMP conversion helpers, configfs, and `u_midi2.h` configuration types. It registers as `DECLARE_USB_FUNCTION_INIT(midi2, ...)`. Host integration is through a USB Audio MIDIStreaming interface with alternate settings and class-specific group terminal block descriptors; local user space integrates through ALSA UMP endpoints plus attached legacy rawmidi devices.

## Risks and Test Signals

Risks include static descriptor templates serialized by a global mutex, request bitmap races during mode switches and completions, missed request return on queue failures, MIDI1 pending-buffer truncation when conversion output exceeds the 32-byte temporary buffer, correctness of cable/group mapping for directional blocks, validating class-specific GTB descriptor length against EP0 request size, and UMP Stream protocol switches while traffic is active. The code assumes a contiguous configfs endpoint/block prefix; sparse configfs groups are treated as absent after the first gap.

Strong test signals include descriptor inspection for FS/HS/SS, GET_DESCRIPTOR for group terminal blocks with short and full lengths, switching between altsetting 0 and 1 under traffic, UMP discovery and stream config exchanges, ALSA UMP transmit/receive in MIDI1 and MIDI2 protocols, MIDI1 compatibility conversion for SysEx/running-status/real-time streams, multiple endpoint and block configurations, directional input/output-only blocks, configfs validation failures, and disconnect/unbind while requests are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_midi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_ncm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_ncm.c

## Purpose

`f_ncm.c` implements the USB CDC Network Control Model gadget function. It presents a USB NCM Ethernet link, integrates with the `u_ether` network gadget core, wraps outgoing Ethernet frames into NCM Transfer Blocks, unwraps incoming NTBs into SKBs, and handles CDC NCM class control requests and notifications.

## Important APIs, Types, and Functions

`struct f_ncm` embeds `struct gether` and adds control/data interface IDs, host MAC string, notify endpoint/request state, NDP parser mode, CRC mode, notification lock/count, netdev pointer, multi-frame TX aggregation SKBs, datagram count, and an hrtimer. `struct ndp_parser_opts` abstracts NDP16 versus NDP32 field widths, signatures, header sizes, alignment, and field positions. Configfs state is `struct f_ncm_opts` from `u_ncm.h`, with Ethernet address/qmult/ifname helpers and local `max_segment_size`.

Key functions include `ncm_reset_values()`, `ncm_setup()` for CDC requests, `ncm_set_alt()`/`ncm_get_alt()`/`ncm_disable()` for interface activation, `ncm_notify()` and `ncm_notify_complete()` for network connection and speed notifications, `ncm_wrap_ntb()` and `package_for_tx()` for TX aggregation, `ncm_unwrap_ntb()` for RX validation and SKB extraction, `ncm_tx_timeout()` for delayed TX flush, and `ncm_bind()`/`ncm_unbind()`/`ncm_alloc()` for function lifecycle.

## Control Flow

`ncm_alloc_inst()` creates a default Ethernet netdev and configfs/OS descriptor state. `ncm_alloc()` allocates a function, exports the host MAC address string, resets NCM defaults to NDP16/no-CRC/default filters, and wires `gether` wrap/unwrap callbacks. `ncm_bind()` registers or attaches the Ethernet netdev, assigns string/interface IDs, autoconfigures bulk and interrupt endpoints, allocates the notification request, copies endpoint addresses across speeds, assigns descriptors, sets `open`/`close` callbacks, and initializes the TX hrtimer.

The control interface altsetting initializes the notification endpoint. The data interface altsetting 0 disconnects the network path; altsetting 1 configures bulk endpoints, enables ZLP policy, resets filters, calls `gether_connect()`, stores the netdev, and queues notifications. CDC requests set packet filters, get/set NTB input size, get NTB parameters, get/set NDP16/NDP32 format, and get/set CRC mode. `ncm_wrap_ntb()` aggregates outgoing frames until size, datagram-count, or timeout limits force `package_for_tx()`. `ncm_unwrap_ntb()` validates NTH/NDP signatures, lengths, indexes, optional CRCs, max segment size, and chained NTBs before queuing Ethernet SKBs to `u_ether`.

## State and Persistence Behavior

Runtime state includes selected NDP format, CRC mode, CDC packet filter, fixed NTB input/output lengths, open/closed notification state, active netdev, and partially built TX NTB SKBs. `ncm->lock` serializes notification state with open/close and completion. The hrtimer persists only until pending TX aggregation is flushed or unbound. Configfs values for addresses, qmult, interface name, and max segment size live in `f_ncm_opts` and are not persistent across teardown. The Ethernet netdev is shared across binds through the function instance and detached when bind count drops to zero.

## Dependencies and Integration Points

The driver depends on USB composite/gadget APIs, CDC/NCM descriptor definitions, Linux networking/SKB helpers, CRC32, `u_ether` and `u_ether_configfs`, `u_ncm.h`, configfs, OS descriptors, and hrtimers. It registers as `DECLARE_USB_FUNCTION_INIT(ncm, ...)`. It integrates with host CDC NCM class drivers, Linux network stack through `gether`, and Microsoft OS descriptors when the composite device enables OS strings.

## Risks and Test Signals

Risks include NTB parser boundary mistakes, CRC mode interoperability, NDP16/NDP32 switching while traffic is active, hrtimer flush invoking `ndo_start_xmit(NULL)` as a known layering compromise, notification request lifetime during disconnect/unbind, static global descriptor mutation across instances, max segment size validation and MTU interaction, and filter writes lacking full cross-CPU serialization with TX paths. The TX error path must free both aggregate SKBs and the current input SKB without leaving stale pointers.

Strong test signals include FS/HS/SS enumeration, control requests for NTB parameters/input size/format/CRC mode, invalid control-request stalls, altsetting 0/1 transitions, netdev open/close notifications, traffic with and without CRC, NDP16 and NDP32 RX/TX, chained NTBs and Windows one-byte ZLP avoidance padding, small-frame aggregation and timer flush, max_segment_size boundary tests, OS descriptor presence, bind-count attach/detach behavior, and disconnect/unbind with notification and TX timer pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_ncm.c -->
