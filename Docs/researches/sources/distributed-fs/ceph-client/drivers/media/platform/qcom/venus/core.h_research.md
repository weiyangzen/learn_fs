# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/core.h

## Purpose
`core.h` defines the shared Venus driver data model: platform resource descriptors, V4L2/HFI format descriptors, per-core runtime state, per-instance session state, controls, buffers, and helper macros used throughout the core, encoder, decoder, PM, firmware, and HFI layers.

## Important Types And APIs
- Platform descriptors: `struct freq_tbl`, `struct reg_val`, `struct bw_tbl`, `enum vpu_version`, `struct firmware_version`, `struct venus_resources`.
- Format model: `enum venus_fmt`, `struct venus_format`.
- Core state: `struct venus_core`, with MMIO base pointers, IRQ, clocks, interconnects, PM domains, resets, V4L2 devices, firmware metadata, locks, instance list/count, HFI state, capabilities, debugfs root, firmware version, dynamic OF changeset, and hardware mode flag.
- Controls: `struct vdec_controls` and `struct venc_controls` capture V4L2 control values for decoder and encoder sessions.
- Buffer/session state: `struct venus_buffer`, `struct clock_data`, decoder/encoder state enums, `struct venus_ts_metadata`, `enum venus_inst_modes`, and `struct venus_inst`.
- Inline helpers/macros: HFI version checks (`IS_V1`, `IS_V3`, `IS_V4`, `IS_V6`), VPU version checks, `is_lite()`, `ctrl_to_inst()`, `to_inst()`, `to_hfi_priv()`, `venus_caps_by_codec()`, firmware revision comparisons.
- Declares exported `venus_close_common()`.

## Control Flow And Integration
This header drives how the rest of the driver shares state. `core.c` initializes `venus_core`; decoder/encoder open paths allocate and initialize `venus_inst`; `helpers.c` manipulates lists and buffer metadata; `hfi.c` uses `state`, completions, errors, and instance lists; firmware and PM code use core resource fields. The version macros select code paths across HFI packet formats, buffer requirements, power sequencing, and register layouts.

## State And Persistence
`venus_core` is the driver-wide state object for a physical VPU. `venus_inst` is per-file/session state and persists from open through close. It includes V4L2 queue state, stream-on flags, format sizes, DPB/output buffer types, firmware minimum counts, timestamps, payload cache, codec state, completion/error fields, HFI callbacks, core acquisition, bit depth, picture structure, drain flags, low-power flags, and DPB ID allocator.

## Dependencies
Includes V4L2, vb2, list/bitops, debugfs, HFI platform/helper headers, and HFI interface definitions. Struct members require PM helper definitions in implementation files.

## Risks And Edge Cases
- Many fields are shared across IRQ, workqueue, ioctl, and runtime PM contexts; lock discipline around `core->lock`, `inst->lock`, `ctx_q_lock`, and waitqueues is critical.
- Bitfields and flags such as `core_acquired`, `session_error`, `next_buf_last`, and `drain_active` encode lifecycle assumptions that must remain synchronized with HFI callbacks.
- Static limits such as clock/reset array sizes and `VIDEO_MAX_FRAME`-sized timestamp/payload arrays constrain supported hardware/session layouts.
- Firmware version comparisons only compare exact major/minor with rev thresholds, not arbitrary semantic ordering.

## Test Signals
Build coverage across all translation units validates shared type compatibility. Runtime signals include correct per-instance state transitions, no stale list entries on close, correct capability lookup by codec/domain, and stable behavior under concurrent decoder/encoder sessions and system-error recovery.
