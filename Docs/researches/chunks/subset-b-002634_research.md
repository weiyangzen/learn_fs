# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 4823-7193

## Scope

This chunk covers a generated AMD GC 9.1 shader/register mask header range. It starts at the `GB_GPU_ID` field macros without the preceding register comment and ends in the middle of `VM_CONTEXT9_CNTL`, so merge-time reconciliation should join it with adjacent chunks for the complete file-level view. The range contains 2,186 `#define` macros, almost entirely paired `...__SHIFT` and `..._MASK` constants for 32-bit hardware register bitfields.

## Purpose

The header provides compile-time bitfield metadata for programming GC 9.1 registers in the AMDGPU driver. Consumers use these macros with the companion address/default headers to construct, decode, compare, or patch hardware register values without hard-coding bit positions. The covered registers describe graphics backend topology, tiling modes, color-buffer hardware controls, EA/RMI data path behavior, debug register ports, ATC L2 translation cache controls, VM L2 page table/fault state, and VM context controls.

This chunk does not implement executable logic or define C types. Its behavioral importance comes from being included by AMDGPU generation-specific code and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD`, where the mask and shift names become the ABI between driver source and GC 9.1 hardware register layout.

## Important API Surface

- `GB_GPU_ID`, `CC_RB_DAISY_CHAIN`, and `GB_ADDR_CONFIG_READ` expose GPU/backend identity and address configuration fields: pipe count, pipe interleave, compressed fragment count, bank interleave/count, shader engine count, multi-GPU tile size, render backends per shader engine, row size, lower-pipe count, and SE enable.
- `GB_TILE_MODE0` through `GB_TILE_MODE31` define repeated tiling descriptors with `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, `MICRO_TILE_MODE_NEW`, and `SAMPLE_SPLIT`. `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15` define macro tile bank width, bank height, aspect, and bank count.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, and `CB_DCC_CONFIG` cover color-buffer cache eviction, cache/tag sizing, FIFO depths, blend and fast-clear workaround bits, memory arbitration weights, and DCC overwrite-combiner behavior.
- `GC_USER_RB_REDUNDANCY` and `GC_USER_RB_BACKEND_DISABLE` expose user-visible render-backend redundancy and disable masks.
- The `gc_ea_gceadec2` block defines `GCEA_EDC_CNT`, `GCEA_EDC_CNT2`, DSM controls, TCC/XBR credit and burst controls, probe controls, error status, misc, SDP backdoor command/data/misc credits, and `GCEA_SDP_ENABLE`. These fields support error counting, data path arbitration/credit tuning, diagnostics, and service/data path enablement.
- The `gc_rmi_rmidec` block defines RMI control/status fields: general RMI mode and arbitration controls, subblock status registers, xbar configuration, UTC/XNACK and UTCL1 controls, TCIW formatter controls, scoreboard controls/status, xbar arbiter weights, clock control, UTCL1 fault/retry/PRT status, and spare control words.
- The `gc_dbgu_gfx_dbgudec` block defines debug port A/B/C/D address selectors and low/high data registers, allowing register-level debug access through port address/data pairs.
- The `gc_utcl2_atcl2dec` block defines ATC L2 translation cache controls, cache-data readout fields, busy/parity status, clock-gating, memory light-sleep, and CGTT clock control.
- The `gc_utcl2_vml2pfdec` block defines VM L2 controls, cache invalidation fields, cache sizing/update modes, busy/parity status, dummy-page fault address/control registers, protection fault control/status/address/default-address registers, context1 identity aperture registers, physical offset registers, group/real-time class fields, reserved CID bank selection, cache parity controls, and clock control.
- The `gc_utcl2_vml2vcdec` block defines `VM_CONTEXT0_CNTL` through the first half of `VM_CONTEXT9_CNTL`, with repeated fields for enabling a VM context, page table depth and block size, retry policy, and per-fault-class interrupt/default behavior.

## Control Flow

There is no direct control flow in this range. Runtime behavior is indirect:

1. AMDGPU code reads or initializes a 32-bit register value using SOC15/MMIO helpers or command-stream state setup.
2. It clears and inserts fields using generated names, usually through macros that combine `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
3. It writes the resulting value to the matching register offset from `gc_9_1_d.h` or a closely related generated address header.
4. Hardware consumes the programmed fields as persistent graphics, memory, translation, or fault-handling state until later state emission, reset, or context restore changes them.

Indexed register groups introduce implicit control flow in consumers. Tiling mode setup can iterate over `GB_TILE_MODE0..31` and `GB_MACROTILE_MODE0..15`; VM setup computes context register offsets from `VM_CONTEXT0_CNTL` to later contexts; RMI scoreboard and status fields are used by fault/invalidation paths that poll or inspect progress bits.

## State and Persistence

The macros are stateless build-time constants, but the registers they describe hold durable GPU state:

- `GB_ADDR_CONFIG_READ`, tile modes, and macrotile modes encode memory layout and backend topology used by surface addressing, render target setup, and compatibility decisions. Incorrect field extraction can produce wrong tiling, wrong pipe/bank interpretation, or surface corruption.
- `CB_HW_*` and `CB_DCC_CONFIG` tune color-buffer caches, DCC behavior, blend/resolve optimizations, fast-clear behavior, and memory arbitration. These values persist as graphics backend state and often appear in golden-register programming.
- `GCEA_*`, `RMI_*`, and `ATC_L2_*` state affects fabric credits, crossbar arbitration, request formatting, cache behavior, clock gating, parity reporting, and debug visibility. Misprogramming can manifest as hangs, bandwidth loss, dropped status, or noisy/hidden fault signals.
- `VM_L2_*` and `VM_CONTEXTn_CNTL` state controls GPU virtual-memory translation, TLB/cache invalidation, dummy-page handling, protection fault classification, interrupt/default responses, and per-context enablement. These registers persist across workloads until VM hub setup, context management, or reset changes them.
- Protection fault address/status registers are diagnostic state. Clear/update fields such as `CLEAR_PROTECTION_FAULT_STATUS_ADDR` and `ALLOW_SUBSEQUENT_PROTECTION_FAULT_STATUS_ADDR_UPDATES` affect whether later faults overwrite captured fault information.

## Dependencies and Integration Points

- Depends on AMD-generated GC 9.1 register specifications. The names and bit positions must stay synchronized with companion generated headers such as `gc_9_1_d.h`, default-value headers, and any ASIC-specific aliases used by SOC15 register helpers.
- Integrated through AMDGPU register programming under `drivers/gpu/drm/amd/amdgpu`. Repository usage shows GC 9.x paths reading/programming `GB_ADDR_CONFIG_READ`, using `GB_TILE_MODE0__*` field shifts in tiling helpers, setting `VM_CONTEXT0_CNTL` fields in gfxhub/mmhub setup, and decoding `GCEA_EDC_CNT`/`GCEA_EDC_CNT2` error counters via `SOC15_REG_FIELD`.
- Golden-register and IMU/RLC initialization tables use these register names and masks to enforce ASIC-specific defaults for backend, RMI, and VM behavior.
- Debug and telemetry paths use status and counter masks for EDC accounting, VM fault capture, UTCL1 fault/retry/PRT detection, parity status, and register dumps.
- User-visible graphics and compute APIs reach these fields indirectly through memory allocation layout, render-target/DCC setup, GPUVM/KFD VMID setup, page fault handling, reset recovery, and performance/power controls.

## Risks

- Bitfield drift is the main risk. If this generated header does not match the hardware spec or the companion address header, `REG_SET_FIELD`/`REG_GET_FIELD` will silently target the wrong bits.
- This chunk is not self-contained: it begins after the `GB_GPU_ID` register comment and ends before the final `VM_CONTEXT9_CNTL` masks. Automated documentation or validation should merge with adjacent chunks before making file-level claims.
- Repeated register families create copy/paste and index hazards. Using `GB_TILE_MODEn` or `GB_MACROTILE_MODEn` fields with the wrong slot can corrupt surface layout; using the wrong `VM_CONTEXTn_CNTL` slot can enable or alter the wrong VMID/context.
- Fault-control fields are high impact. Defaults for range, PDE0, dummy-page, valid, read, write, and execute faults decide whether faults interrupt, retry, use default handling, or continue; wrong settings can hide memory bugs or cause excessive GPU faults.
- Cache, arbitration, and credit fields in `CB_HW_*`, `GCEA_*`, `RMI_*`, `ATC_L2_*`, and `VM_L2_*` are performance- and hang-sensitive. Many are hardware tuning or workaround bits, so changing masks without matching firmware/hardware guidance can cause subtle regressions.
- Address split fields for dummy pages, protection fault addresses, default fault addresses, identity apertures, and physical offsets require correct low/high composition and alignment. Mask mistakes can redirect fault handling or identity mappings.

## Test Signals

- Build coverage: compile AMDGPU with this header included; duplicate macros, syntax mistakes, or missing field names fail quickly.
- Generation consistency: compare this range against the GC 9.1 register source used to generate `gc_9_1_sh_mask.h`, and verify one-to-one pairing with matching offsets in `gc_9_1_d.h`.
- Register programming smoke tests: boot a GC 9.1 ASIC, load AMDGPU, initialize gfxhub/mmhub/graphics, and watch for VM setup errors, golden-register warnings, GPU hangs, or reset loops.
- GPUVM and fault tests: exercise userptr/BO mapping, VM context enablement, invalid mappings, read/write/execute protection faults, dummy-page behavior, retry paths, and fault address capture.
- Graphics layout tests: run rendering workloads that cover tiled surfaces, DCC, fast clears, resolves, MRT/blend paths, and display/3D transitions; corruption often indicates wrong `GB_*` or `CB_*` field use.
- Diagnostics validation: compare register dumps and EDC/VM fault counters decoded with these masks against expected hardware state, especially `GCEA_EDC_CNT*`, `RMI_*STATUS*`, `ATC_L2_STATUS*`, `VM_L2_STATUS`, `VM_L2_PROTECTION_FAULT_STATUS`, and `VM_CONTEXTn_CNTL`.
