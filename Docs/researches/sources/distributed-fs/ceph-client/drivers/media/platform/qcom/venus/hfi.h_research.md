# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi.h

## Purpose
`hfi.h` defines the high-level HFI interface shared between Venus core/helpers and the lower-level transport. It declares session/domain constants, buffer/frame descriptors, callback structures, core/session state values, operation tables, and wrapper APIs.

## Important Types And Constants
- Session domains: `VIDC_SESSION_TYPE_VPE`, `VIDC_SESSION_TYPE_ENC`, `VIDC_SESSION_TYPE_DEC`.
- Resource IDs: `VIDC_RESOURCE_NONE`, `OCMEM`, `VMEM`.
- Data descriptors: `struct hfi_buffer_desc`, `struct hfi_frame_data`, and `union hfi_get_property`.
- Events and event payload: `EVT_SYS_EVENT_CHANGE`, watchdog/system/session errors, `struct hfi_event_data`.
- Core/session states: `CORE_UNINIT`, `CORE_INIT`, `INST_UNINIT`, `INST_INIT`, `INST_LOAD_RESOURCES`, `INST_START`, `INST_STOP`, `INST_RELEASE_RESOURCES`.
- Callback/ops tables: `struct hfi_core_ops`, `struct hfi_inst_ops`, and `struct hfi_ops`.
- Public HFI wrapper declarations corresponding to `hfi.c`.

## Control Flow And Integration
`struct hfi_ops` is filled by the lower transport and used by `hfi.c` to send commands. `struct hfi_inst_ops` is supplied by decoder/encoder sessions so HFI message processing can report buffer completion, events, and flush completion. `hfi_frame_data` carries vb2 buffer metadata into ETB/FTB commands.

## State And Persistence
The header defines state numbers and data structures but stores no state. Runtime state lives in `venus_core` and `venus_inst`.

## Dependencies
Includes interrupt declarations and `hfi_helper.h` for HFI constants and property structs.

## Risks
- State constants begin at mixed numeric ranges (`CORE_*` and `INST_*`), so callers must compare only within the proper domain.
- `device_addr` fields are `u32`; hardware and DMA masks must keep addresses within representable ranges.
- Callback pointers are required for normal session operation; missing `buf_done` or `event_notify` would crash on firmware events.

## Test Signals
Compile coverage across core, helpers, transport, and decoder/encoder validates ABI shape. Runtime tests should confirm callback delivery for buffer done, event notify, and flush done across encoder and decoder sessions.
