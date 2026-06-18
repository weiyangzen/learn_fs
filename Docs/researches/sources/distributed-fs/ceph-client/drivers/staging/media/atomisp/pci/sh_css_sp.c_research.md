# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_sp.c

## Purpose
Implements host-side construction, serialization, and control of AtomISP SP pipeline state. It translates `ia_css_pipeline` stages, frames, firmware binaries, metadata, queues, and event/command state into SP-visible DDR/DMEM structures and starts or controls the SP.

## Important APIs, Types, and Functions
Global stage state is held in `sh_css_sp_group`, `sh_css_sp_stage`, `sh_css_isp_stage`, private `sh_css_sp_output`, `per_frame_data`, and `sp_running`. Key entry points include `sh_css_sp_init_pipeline()`, `store_sp_stage_data()`, `store_sp_group_data()`, `sh_css_sp_start_binary_copy()`, `sh_css_sp_start_isp()`, `sh_css_write_host2sp_command()`, host2sp frame/metadata update functions, IRQ-mask functions, IF/input-circuit configuration, DMA debug-mask helpers, and `sh_css_sp_reset_global_vars()`. Important helpers include `sh_css_copy_frame_to_spframe()`, `set_input_frame_buffer()`, `set_output_frame_buffer()`, `sh_css_sp_init_stage()`, `sp_init_stage()`, and `configure_isp_from_args()`.

## Control Flow
Pipeline setup starts in `sh_css_sp_init_pipeline()`: it derives the SP thread id, clears the per-thread pipeline, counts stages, initializes group input configuration, records metadata and queue ids, then walks each stage. SP-only copy stages route to raw/isys copy setup; ISP/firmware stages route through `sp_init_stage()` and `sh_css_sp_init_stage()`, which copy binary/blob metadata, frame descriptors, queue-backed buffers, parameter DDR maps, crop offsets, ISP kernel configs, and state initialization. Each stage is stored to DDR, then the group address is stored in per-frame data. Runtime control writes host2sp commands and frame addresses into SP DMEM and starts the SP controller after cache invalidation.

## State and Persistence Behavior
The file relies on mutable global staging structs that are reused while building stages, with fields such as `program_input_circuit` explicitly preserved across clears and reset after storing. Per-frame state stores the current SP group address. Host2sp communication is persistent SP DMEM state for commands, offline frames, MIPI frames, metadata, raw-frame counts, and event masks. `sp_running` gates cache invalidation and SP start behavior.

## Dependencies and Integration Points
Depends on many AtomISP internals: HMM/MMU, binary metadata, queues, ISP parameter copy/configure functions, frame conversion, event public ABI, SP control, input formatter, GDC, DMA ids, and debug graph dumping. It is the bridge between high-level CSS pipeline objects and firmware symbols exposed by `sh_css_sp_fw`.

## Risks
Global staging structs are not inherently reentrant and are sensitive to pipe/thread ordering. Many address writes use firmware symbol offsets and `offsetof()` divided by `sizeof(int)`, so layout drift can break SP communication. Several paths assert on unsupported frame formats but still return errors that callers may not propagate. Firmware generation, ISP2400/ISP2401 differences, metadata queues, and continuous capture all introduce subtle branch-specific behavior.

## Test Signals
Good coverage includes raw copy, isys copy, binary copy, multi-stage ISP pipelines, metadata-enabled streams, continuous capture, memory-input streams, parameter sampling, SP start/stop, host2sp command readiness, MIPI/offline frame updates, IRQ masks, DMA debug masks, and reset/reinitialize cycles without stale frame descriptors.
