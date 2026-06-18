# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio_context.c

## Purpose
`mmio_context.c` saves, restores, and switches engine-related MMIO context when ownership moves between host and vGPU workloads. It also restores context-inhibited state through command-stream LRI packets and handles MOCS and TLB-invalidate state.

## Important APIs, Types, And Functions
Public functions are `intel_gvt_switch_mmio`, `intel_gvt_init_engine_mmio_context`, `is_inhibit_context`, and `intel_vgpu_restore_inhibit_context`. Private data includes `engine_mmio`, Gen8/Gen9 lists, Gen9 render MOCS tables, MOCS offset lists, and TLB invalidate offsets.

## Control Flow
Initialization selects Gen8/Gen9 lists, assigns TLB/MOCS offsets, counts in-context MMIOs, and marks those registers as save/restore-in-context. `intel_gvt_switch_mmio` forcewakes all domains, saves previous owner registers, restores next owner registers, switches MOCS, skips Gen9 in-context registers unless restore is inhibited, handles pending TLB invalidation, and releases forcewake. Inhibit restore emits MI commands to disable arbitration, load tracked context MMIOs and render MOCS/L3CC, then re-enable arbitration.

## State And Persistence
Per-vGPU values live in `vgpu->mmio.vreg`; host baselines are cached in `engine_mmio.value` and `gen9_render_mocs`; pending TLB bits live in `vgpu->submission.tlb_handle_pending`; active lists live in `gvt->engine_mmio_list`.

## Dependencies And Integration Points
It integrates i915 engine/context/request/ring APIs, uncore forcewake, GVT submission shadow contexts, MMIO metadata marking, scheduler ownership changes, and tracepoints.

## Risks
Incorrect save/restore can leak state between host and vGPUs. Forcewake coverage, Gen9 inhibit detection, MOCS handling, and TLB invalidation waits are sensitive. Timeouts can affect guest translation correctness.

## Test Signals
Stable workload switching, no register leakage, correct inhibit-context execution, MOCS preservation, TLB bits cleared after invalidation, no forcewake warnings, and expected trace old/new values.
