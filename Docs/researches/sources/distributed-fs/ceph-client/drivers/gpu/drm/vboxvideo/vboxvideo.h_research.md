# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo.h

## Purpose

`vboxvideo.h` is the main VirtualBox graphics protocol header. It documents VRAM layout and defines VBVA ring buffers, guest-to-host command ids, host-to-guest events, configuration indices, screen/mode/cursor/capability structures, mode hints, and input mapping payloads.

## Important APIs, Types, and Functions

- VRAM and adapter constants: `VBOX_VIDEO_MAX_SCREENS`, `VBVA_ADAPTER_INFORMATION_SIZE`, `VBVA_MIN_BUFFER_SIZE`, and interpret/disable command values.
- VBVA ring structures: `vbva_cmd_hdr`, `vbva_host_flags`, `vbva_record`, and `vbva_buffer`.
- Command ids: `VBVA_QUERY_CONF32`, `VBVA_INFO_VIEW`, `VBVA_FLUSH`, `VBVA_INFO_SCREEN`, `VBVA_ENABLE`, `VBVA_MOUSE_POINTER_SHAPE`, `VBVA_INFO_CAPS`, `VBVA_QUERY_MODE_HINTS`, `VBVA_REPORT_INPUT_MAPPING`, and cursor position commands.
- Config indices: monitor count, host heap size, mode hint reporting, guest cursor reporting, cursor capabilities, screen flags, and max record size.
- Payload structures: `vbva_conf32`, `vbva_infoview`, `vbva_infoscreen`, `vbva_enable_ex`, `vbva_mouse_pointer_shape`, `vbva_caps`, `vbva_query_mode_hints`, `vbva_modehint`, and `vbva_report_input_mapping`.

## Control Flow

Implementation files allocate HGSMI buffers containing these structures and submit them on the VBVA channel. The host interprets command ids and modifies result fields, mode hints, or shared ring-buffer offsets according to this ABI.

## State and Persistence Behavior

The header defines both transient command payloads and persistent shared VRAM structures. `vbva_buffer` maintains ring offsets and record queues shared between guest and host; mode hints and host flags persist across hotplug updates; capability and display info commands update host-side state.

## Dependencies and Integration Points

Used across all VirtualBox driver files, especially `vbva_base.c`, `modesetting.c`, `hgsmi_base.c`, `vbox_irq.c`, and `vbox_mode.c`. It is the bridge between DRM/KMS state and the VirtualBox host protocol.

## Risks and Edge Cases

- Packed structure layouts and numeric command values are ABI and must remain stable.
- Ring buffer fields are shared-memory concurrency points with one side updating `free_offset` and the other `data_offset`.
- Large record support depends on partial-record semantics and `VBVA_RING_BUFFER_THRESHOLD`.
- The protocol contains historical misspellings/quirks such as `partial_write_tresh`; renaming fields would break compatibility.

## Test Signals

Compile-time size/offset assertions, host interoperability tests for every command structure used by the driver, ring buffer wrap/partial-record tests, mode hint parsing, cursor shape upload, and multi-monitor display-info updates.
