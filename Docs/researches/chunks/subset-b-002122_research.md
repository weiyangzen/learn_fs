# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 9970-12458

## Purpose

This chunk is generated AMD DCN 3.6.0 register field metadata. It contains no executable C code; it publishes preprocessor constants that describe field bit positions and masks inside DCN hardware registers. The matching `dcn_3_6_0_offset.h` header supplies MMIO offsets and base indices, while this shift/mask header supplies the layout used by AMDGPU display code to pack and decode register fields without overwriting adjacent bits.

The assigned range begins at `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_HIGH_ADDR` after the immediately preceding low-address aperture register, then covers the rest of HUBP/HUBPREQ/HUBPRET/cursor/perfmon definitions for pipe 1, all equivalent definitions for pipe 2, and most equivalent definitions for pipe 3. It ends inside `HUBPRET3_HUBPRET_INTERRUPT`, before that register's remaining status/int-status shifts and masks. Adjacent chunks are required for complete file-level treatment of split registers at both boundaries.

Although this source is under a local `ceph-client` mirror path, the file is AMDGPU display-driver hardware metadata and is not related to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or direct includes in this chunk. The effective API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Instance prefixes such as `HUBP2_`, `HUBPREQ3_`, `HUBPRET1_`, `CURSOR0_2_`, and `DC_PERFMON9_` identify repeated display pipe instances and per-pipe subblocks.

The range contains 2,120 macro lines covering 337 distinct register tokens. Major families are:

- `HUBPREQ1_*`, continuing from a previous chunk: VM system aperture high address, L1 TLB control, display logic generator timing parameters, prefetch settings, vblank/flip/nominal PTE and metadata timing parameters, per-line delivery, cursor request scheduling, reference-to-pixel frequency conversion, DRQ limit, request-side memory power control/status, UCLK p-state force, and status registers.
- `HUBPRET1_*`: return-side control, DET buffer plane-1 base, 3-to-2 packing disable, component crossbar source selection, return-side memory power control/status, read-line programming, read-line interrupt control/status, current read-line value, and read-line window status.
- `CURSOR0_1_*`: cursor enable/mode/request/magnify/pitch/TMZ/chunk/perfmon fields, cursor surface address and high bits, size, position, hot spot, stereo, destination offset, cursor memory power state, and DMDATA address/control/QoS/status/software access fields.
- `DC_PERFMON8_*`: per-HUBP performance counter control, counter selection, counter state, perfmon enable/clear/interrupt control, threshold/current values, and high/low counter readback.
- `HUBP2_*`: pipe 2 request and surface-front-end fields for surface format, swizzle, tiling, primary/secondary luma/chroma viewports, request size, HUBP enable/blank/status/underflow paths, clock control/status, VMPG/MALL/sub-VP configuration, debug doorbell/debug, DCFCLK/DPPCLK measurement windows, and MALL status.
- `HUBPREQ2_*`: complete pipe 2 surface pitch, VMID, primary/secondary luma/chroma surface and metadata addresses, surface control/TMZ/DCC state, flip control and flip interrupt, surface in-use and earliest-in-use readbacks, expansion mode, TTU/QoS controls, DMDATA VM control, VM aperture, L1 TLB, DLG timing, prefetch, vblank/flip/nominal timing, delivery timing, cursor settings, memory power, UCLK p-state force, and status fields.
- `HUBPRET2_*`, `CURSOR0_2_*`, and `DC_PERFMON9_*`: pipe 2 equivalents of the return path, cursor, DMDATA, and perfmon register layouts.
- `HUBP3_*` and `HUBPREQ3_*`: pipe 3 equivalents of HUBP/HUBPREQ surface, request, VM, DLG, TTU, memory power, p-state, and status fields.
- `HUBPRET3_*`: pipe 3 return-side control, memory power, read-line control, and the first part of read-line/vblank interrupt fields. `HUBPRET3_HUBPRET_INTERRUPT` is split at the end boundary.

## Control Flow

This header has no runtime control flow. Runtime behavior is macro-driven:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and this shift/mask header.
2. Register-table macros such as `SRI_ARR`, `HUBP_REG_LIST_DCN30_RI`, `HUBP_MASK_SH_LIST_DCN35`, and IRQ `IRQ_REG_ENTRY` paste block, instance, register, and field tokens into names defined here.
3. DCN 3.6 resource setup populates per-block register, shift, and mask tables. In this tree, `dcn36_resource.c` initializes four HUBP register instances with `HUBP_REG_LIST_DCN30_RI(id)` and uses `HUBP_MASK_SH_LIST_DCN35(__SHIFT/_MASK)` for HUBP masks and shifts.
4. Operational code then uses helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_GET_7`, `REG_READ`, and `REG_WAIT`. Those helpers combine offsets, shifts, and masks from the generated tables to write MMIO registers or extract field values.

The macros do not encode programming order. Modeset, flip, cursor, VM, deadline, memory-power, and read-line code still owns sequencing: program VM/system aperture before enabling translations, program deadline/TTU values from DML output, update surface addresses and flip controls around vupdate/vblank rules, wait for read-line/vblank status where required, and preserve status/clear semantics for interrupt-like fields.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- HUBP/HUBPREQ surface fields hold per-plane format, tiling, swizzle, viewport, address, metadata, TMZ, DCC, pitch, VMID, flip, and in-use state for luma and chroma surfaces.
- VM and aperture fields hold display-side translation behavior: system aperture high/low bounds, L1 TLB enable, system access mode, unmapped access behavior, and advanced-driver-model enable.
- DLG, TTU, vblank, flip, nominal, and per-line-delivery fields hold computed memory-fetch deadlines and request-delivery timing from Display Mode Library calculations.
- Cursor and DMDATA fields hold cursor image address, geometry, hot spot, stereo behavior, cursor request mode, cursor memory-power state, and display metadata DMA/software access status.
- HUBPREQ/HUBPRET memory power fields hold force/disable controls and status for DPTE, MPTE, metadata, PDE, DMROB, and PIXCDC memories.
- UCLK p-state force fields can disallow data or cursor memory clock p-state changes for timing-sensitive scenarios.
- HUBPRET crossbar and read-line fields hold return-path component mapping and read-line window/interrupt/readback state.
- PERFMON8/9 fields hold per-pipe performance counter selection, enable, clear, state, thresholds, current values, interrupt status/ack, and high/low counter data.
- Status registers expose transient hardware state such as blanking, HUBP enable, underflow, MPTE row ready, chunk request position, self-refresh, p-state allowance, QoS urgency, recovery/flush, flip active, clock states, MALL hit/miss, and VM/DMDATA faults or late/underflow conditions.

Persistence is hardware-defined. Configuration bits generally remain until modeset reprogramming, power-gating reset, suspend/resume, or ASIC reset. Status, interrupt, clear, pending, counter, and readback fields may be read-only, sticky, self-clearing, or write-one-to-clear. This generated header only describes bit layout; it does not document access type or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 3.6.0 register database and with local consumers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`, the matching register-offset/base-index header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, which includes this header, builds DCN 3.6 resource register tables, and uses the HUBP shift/mask lists for the fields in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, which includes this header and uses `FD_MASK`/`FD_SHIFT` expansions through DMUB DCN35 field lists to initialize firmware-accessible register metadata for DCN 3.6.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c`, which includes this header and expands `HUBPREQn_DCSURF_SURFACE_FLIP_INTERRUPT` fields for pflip interrupt enable/ack programming.
- Shared HUBP code under `display/dc/hubp/`, especially `dcn10_hubp.c`, `dcn30_hubp.c`, and `dcn32_hubp.c`, which uses the generated tables for VM L1 TLB programming, deadline/DMDATA timing, cursor and surface state readback, HUBPREQ/HUBPRET memory-power readback, read-line waits, and UCLK p-state force updates.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h`, whose reusable `HUBP_REG_LIST_*_RI` macros enumerate most register names covered here and are reused by DCN 3.6 resource setup.
- DML and HWSS/resource paths that calculate deadline, prefetch, MALL/SubVP, p-state, and memory-fetch values later written into these registers.

The integration contract is token spelling plus numeric correctness. Missing or renamed macros usually fail at compile time through token-pasted register tables. Incorrect numeric masks or shifts can compile cleanly and then program the wrong hardware bits at runtime.

## Risks And Edge Cases

- The chunk boundary is artificial. It begins with `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_HIGH_ADDR`; the preceding low-address aperture and earlier pipe 1 HUBP/HUBPREQ fields are in the previous chunk. It ends after only the early `HUBPRET3_HUBPRET_INTERRUPT` shift definitions; the remaining shifts and all masks for that register continue in the next chunk.
- These are untyped integer constants. A one-bit shift or mask error can corrupt adjacent hardware fields without compiler diagnostics.
- Repeated instance layouts are easy to update inconsistently. A pipe 2 or pipe 3-only mismatch can leave single-pipe testing clean while multi-display, ODM, or pipe-reassignment scenarios fail.
- Surface address, metadata address, VMID, aperture, L1 TLB, TMZ, and DCC fields are security- and correctness-sensitive. Bad values can cause VM faults, protected-content mishandling, stale metadata fetches, corruption, black screens, or GPU hangs.
- DLG/TTU/vblank/flip/nominal delivery masks are timing-critical. Incorrect field widths can produce underflow, missed prefetch, late flips, failed SubVP/MALL behavior, unstable p-state transitions, or visible corruption only at high bandwidth.
- Memory power and p-state force fields interact with clock/power management. Wrong masks can leave memories forced on, power-gated when needed, or disallow UCLK transitions unnecessarily.
- Read-line and interrupt fields are side-effect-sensitive. Misprogramming clear/status/mask bits can hide vblank/read-line events, trigger spurious interrupts, or break waits such as `HUBPRET_READ_LINE_STATUS.PIPE_READ_VBLANK`.
- Perfmon fields are diagnostic but can still be stateful. Wrong enable/clear/ack/threshold fields produce misleading performance data or stale interrupts.

## Test Signals

Useful validation combines generated-header checks with hardware/display behavior:

- Build AMDGPU/DC with DCN 3.6 enabled. Token-pasted resource, DMUB, HUBP, and IRQ tables should catch missing or misspelled macro names.
- Mechanically verify every `__SHIFT` in the range has the expected `_MASK`, masks align with shifts and expected bit widths, and split boundary registers are reconciled with neighboring chunks before reporting mismatches.
- Diff the range against AMD's authoritative DCN 3.6 register database or adjacent generated DCN headers when compatibility is expected.
- Exercise multi-pipe modesets across pipe instances 1, 2, and 3: enable/disable, hotplug, suspend/resume, resolution/refresh changes, plane movement between pipes, and repeated atomic commits.
- Exercise surface formats and memory layouts that rely on HUBP/HUBPREQ fields: RGB, YUV 4:2:0, chroma viewports, DCC on/off, TMZ surfaces, metadata address changes, primary/secondary flips, and VMID changes.
- Exercise cursor and DMDATA paths: cursor enable/disable, size/position/hot spot changes, stereo cursor, cursor p-state force, DMDATA programming, and VM fault/late/underflow status readback.
- Exercise DML-sensitive timing paths: high-bandwidth modes, SubVP/MALL, DRR/vblank stretch, p-state changes, flip stress, and underflow detection while monitoring DC traces and kernel logs.
- Check debugfs or register-state capture for `hubp3_read_reg_state`-style readbacks of HUBPREQ/HUBPRET, memory-power, UCLK p-state, aperture, deadline, and read-line registers.
- Validate pflip, vblank/read-line, and related interrupt behavior for no missed acks, no interrupt storms, and no stuck status/clear bits.

## Cross-Chunk Notes

Previous chunks are needed for the beginning of pipe 1 HUBP/HUBPREQ definitions, including `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_LOW_ADDR`. The next chunk continues `HUBPRET3_HUBPRET_INTERRUPT` with the remaining status/int-status shifts and all masks, then proceeds into `HUBPRET3_HUBPRET_READ_LINE_VALUE`, read-line status, and pipe 3 cursor definitions.
