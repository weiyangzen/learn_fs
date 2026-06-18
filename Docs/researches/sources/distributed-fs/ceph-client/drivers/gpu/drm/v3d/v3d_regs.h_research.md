<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_regs.h

Purpose: Defines V3D register offsets, bitfields, and field helper macros for hub, GCA, bridge reset, TFU, MMU, core control, interrupts, command-list engine, performance counters, GMP, CSD, error status, and SMS registers.

Important APIs/types/functions: `V3D_MASK`, `V3D_SET_FIELD`, `V3D_SET_FIELD_VER`, and `V3D_GET_FIELD` compose/extract fields with WARN checks. Register constants are generation-aware where layouts differ, for example TFU offsets, CSD fields, performance counter mux widths, GMP offsets, and SMS state.

Control flow: All V3D implementation files use these constants through `V3D_READ/WRITE` macros from `v3d_drv.h` to program hardware, decode identities/faults, reset blocks, manage caches, submit work, and read perf counters.

State and persistence: No state; it encodes hardware ABI.

Dependencies and integration points: Depends on Linux bit operations and is central to V3D BO/MMU/IRQ/GEM/debugfs/perfmon/submit code.

Risks and test signals: Incorrect constants cause hardware faults. A notable risk is that register definitions are broad and generation-gated by callers, so misuse can compile cleanly. Test signals include register dump sanity on each supported generation, get-param values, MMU fault decoding, perf counter programming, CSD submits, and reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_regs.h -->
