# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h lines 4920-7410

## Scope

This chunk is a generated AMDGPU GC 9.4.2 register-offset header segment. It contains C preprocessor constants only: each `reg*` macro names a GC MMIO register word offset and each matching `*_BASE_IDX` selects the SOC15 base-index slot. The final `gccacind` lines use the `ix*` naming convention for GC CAC indirect-register indexes. The matching bitfield definitions are in `gc_9_4_2_sh_mask.h`.

The source path is under the local `ceph-client` mirror, but this file is AMDGPU hardware metadata for Aldebaran/GC 9.4.2 graphics and compute blocks, not Ceph filesystem code.

## Purpose

The purpose of this slice is to provide stable symbolic offsets for low-level GC register programming, debug, RAS, compute queue setup, virtual memory, and cache/translation controls on GC 9.4.2 hardware. Driver code includes this header through `amdgpu/gfx_v9_4_2.c` and `amdgpu/amdgpu_amdkfd_aldebaran.c`, then passes these symbols to helpers such as `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `SOC15_REG_GOLDEN_VALUE`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_RLC`.

Because these constants feed table-driven register access, offset or base-index drift can compile cleanly while programming the wrong hardware register. In this chunk that is especially relevant for shader dispatch state, TCP watchpoint stride assumptions, EDC/RAS counter tables, SQ indirect access, UTCL2/VM controls, and SR-IOV PF/VF aperture registers.

## Address Blocks and Register Families

The range begins in the `gc_rlcpdec` block, whose address-block comment appears just before the chunk. These `regRLC_*` registers cover RLC interrupt/status, load balancing, microcode/GPM thread controls, clock counters, dynamic and static power-gating state, CU masks, SERDES read/write windows, SPM/GPM logging, SRM command/status and indexed control/data registers, UTCL1/prewalker controls, semaphores, CP EOF interrupts, DSM controls, and RLC EDC counters. `gfx_v9_4_2.c` directly uses `regRLC_EDC_CNT` and `regRLC_EDC_CNT2` in RAS poison/EDC tables.

`gc_rmi_rmidec` maps the render/memory-interface block: general control/status, subblock status, XBAR configuration and arbitration, UTC/UTCL1 controls, TCIW formatter controls, scoreboard control/status, clock control, and spare registers.

`gc_shdec` is the largest shader-programming window in this chunk. It defines pixel, vertex, geometry, export, hull/local, common, and compute shader state: `SPI_SHADER_PGM_*`, `SPI_SHADER_USER_DATA_*`, `COMPUTE_DISPATCH_*`, `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_NUM_THREAD_*`, `COMPUTE_PGM_*`, `COMPUTE_RESOURCE_LIMITS`, static thread-management masks for SE0..SE7, relaunch/restart registers, checksum, and `COMPUTE_USER_DATA_0..15`. `gfx_v9_4_2.c` uses several `COMPUTE_*` offsets when assembling the Aldebaran register-init IB for GPR/LDS initialization.

`gc_shsdec` contributes shader/SPI shared state: SPI debug and graphics controls, DSM and EDC counters, PS CU enable, wave-lifetime limit/status registers, load-balance counters, GDS/SX buffer sizing, active-wave counters, and trap-screen registers for debug state.

`gc_spipdec` maps SPI arbitration, work-control percentages for GFX/HP3D/CS0..CS7, graphics debug trap registers, compute queue reset, and per-CU resource reserve registers. `amdgpu_amdkfd_aldebaran.c` and `gfx_v9_4_2.c` build `SPI_GDBG_PER_VMID_CNTL` values with the paired mask header, and `gfx_v9_4_2.c` writes `SPI_GDBG_TRAP_DATA0/1`.

`gc_sqdec` covers shader-queue and SQC controls. It includes `SQ_CONFIG`, `SQC_CONFIG`, LDS and register credits, random wave priority, debug/status/cmd/timestamp registers, indirect access through `SQ_IND_INDEX` and `SQ_IND_DATA`, instruction-format decode aliases, load-balance counters, EDC/parity counters, thread-trace word aliases, buffer/image/sampler resource words, flat scratch, M0/GPR index metadata, and SQC ICACHE/DCACHE UTCL1 controls. `gfx_v9_4_2.c` reads and writes `SQ_CONFIG1`, accesses `SQ_IND_INDEX/DATA`, and uses many SQ/SQC EDC offsets in RAS tables.

`gc_tcdec`, `gc_tcpdec`, and `gc_tpdec` cover texture/cache and texture pipeline registers. `gc_tcdec` includes TCP invalidation/status/channel steering/address config, L1/L2 cache policy registers, TCI/TCC/TCA/TCX controls, soft reset, writeback/invalidate, DSM, and EDC counters. `gfx_v9_4_2.c` applies per-die golden settings to `TCP_CHAN_STEER_0..5`, uses `TCP_EDC_CNT_NEW`, `TCC_EDC_CNT`, `TCC_EDC_CNT2`, `TCA_EDC_CNT`, `TCX_EDC_CNT`, and `TCX_EDC_CNT2` in RAS tables. `gc_tcpdec` defines four TCP watchpoint high/low/control triplets plus GATCL1/UTCL1 controls; `amdgpu_amdkfd_aldebaran.c` depends on `regTCP_WATCH1_ADDR_H - regTCP_WATCH0_ADDR_H` as the watchpoint stride. `gc_tpdec` exposes TD status, scratch, DSM, and EDC registers; `gfx_v9_4_2.c` uses `TD_EDC_CNT`.

The UTCL2 and VM blocks map GPU address translation. `gc_utcl2_atcl2dec` and its performance-counter subblocks define ATC L2 control/cache data/status, DSM index/control registers for 2M/32K/4K caches, performance counter configuration, and high/low result registers. `gc_utcl2_l2tlbdec` and its counter blocks expose L2 TLB status, GPUVA/VMID translation-assist request/response, and performance counters. `gfx_v9_4_2.c` lists the ATC L2 DSM index/control offsets in its UTC RAS block descriptors.

`gc_utcl2_vml2pfdec`, `gc_utcl2_vml2pldec`, `gc_utcl2_vml2prdec`, and `gc_utcl2_vml2vcdec` define VM L2 controls, status, dummy-page fault handling, protection-fault status/default address, invalidate request/ack/status, context TLB control, walker controls/status, MMU control, per-context `VM_CONTEXT0..15_*` controls, page-table start/end/base registers, protection-fault default addresses, per-context performance counters, and VMID/PASID mapping. These offsets integrate with the broader `gmc_v9_0.c` VM setup and KFD VMID/PASID programming paths for GC 9.4.2.

`gc_utcl2_vmsharedhvdec`, `gc_utcl2_vmsharedpfdec`, and `gc_utcl2_vmsharedvcdec` map shared VM aperture state. The hypervisor block includes per-VF framebuffer size offsets, MARC base/relocation/length windows, per-VF PCIe ATS controls, active function ID, and XGMI GPUIOV enable. The PF and VC shared blocks provide framebuffer offsets/location, default system aperture addresses, steering, virtual reset request, memory power, cacheable DRAM and local HBM windows, XGMI LFB controls, host mapping, AGP windows, and L1 TLB control.

The chunk ends at the beginning of `gccacind`, an indirect GC current/activity counter register block. The visible `ixGC_CAC_*` macros cover CAC control, override select/value, and early weight registers for BCI, CB, CP, DB, GDS, IA, LDS, PA, and PC. Other CAC indirect registers continue after this chunk.

## Important APIs, Types, and Functions

This header defines no functions, structs, enums, or runtime storage. Its exported API is the generated macro namespace:

- `reg<REGISTER>` is the word offset consumed by SOC15 GC register helpers.
- `reg<REGISTER>_BASE_IDX` selects the hardware base slot. Most blocks in this chunk use base index `0`; the opening RLC block uses base index `1`; the generated VM hypervisor block also uses base index `1`.
- `ix<REGISTER>` is an indirect-register index, not a direct MMIO offset. In this range that applies to the visible `GC_CAC` registers.
- Address-block comments such as `gc_shdec`, `gc_sqdec`, and `gc_utcl2_vml2vcdec` document the generator's hardware grouping and base address.

The paired `gc_9_4_2_sh_mask.h` file supplies field shifts and masks. Consumers combine the offset macros here with mask helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`.

## Control Flow

There is no executable control flow in this file. Runtime sequencing is implemented by consumers:

1. GC 9.4.2 device setup includes the offset and mask headers.
2. Initialization code programs golden registers, including TCP channel steering and TCI controls.
3. Compute/GPR/LDS initialization code builds indirect buffers containing `COMPUTE_*` register writes.
4. KFD debug paths build SPI debug/trap register values, program TCP watchpoint address/control registers, and use inherited GFX v9 queue, VMID, and wave-control helpers.
5. RAS code uses RLC, SPI, SQC, SQ, TCP, TCC, TCA, TCX, and TD EDC counters to query and clear error counts.
6. GMC/KFD VM paths program VM context, PASID/VMID, protection fault, invalidate, and shared aperture registers through the same generated offsets.

The header does not encode ordering, locking, reset behavior, or access type. Consumers still need to hold the correct SRBM/GRBM selection locks, choose the right VMID/context, and follow hardware-defined write, poll, invalidate, clear, and indirect-access sequences.

## State and Persistence Behavior

The macros are compile-time constants and hold no software state. The described hardware registers are volatile GPU state with several persistence categories:

- RLC, SPI, SQ, TCP, TCC, TCA, TCX, TD, UTCL2, and VM registers retain programmed hardware state until reset, power transition, firmware action, or another driver write changes them.
- Shader and compute registers represent per-dispatch or per-queue execution state. Bad offsets can break program address, resource limits, static CU masks, relaunch/restart, or user-data programming until the queue/context is rebuilt.
- VM context and aperture registers define GPU address translation and fault behavior. Incorrect values can persist as invalid page-table ranges, wrong PASID/VMID ownership, broken XNACK/ATS behavior, or bad PF/VF aperture setup.
- EDC, status, performance-counter, protection-fault, thread-trace, and trap registers are diagnostic latches or counters. Some are sticky or clear-on-write according to hardware rules not visible in the offset header.
- CAC `ix*` entries are indirect-indexed hardware state; using them as direct MMIO addresses would be incorrect.

## Dependencies and Integration Points

This chunk depends on the generated AMDGPU register ecosystem: `gc_9_4_2_sh_mask.h` for field layout, SOC15 register-offset tables, GC IP discovery identifying `IP_VERSION(9, 4, 2)`, and the GFX/KFD/GMC code that selects Aldebaran-specific paths.

Direct include users in this tree are `amdgpu/gfx_v9_4_2.c` and `amdgpu/amdgpu_amdkfd_aldebaran.c`. Broader integration includes:

- `gfx_v9_4_2.c` golden-register programming, SQ setup, debug trap setup, GC CAC indirect writes, EDC/RAS counter metadata, UTC RAS block descriptors, and SQ timeout/indirect access.
- `amdgpu_amdkfd_aldebaran.c` KFD debug trap setup and TCP address-watch programming.
- Shared GFX v9 KFD helpers for shader memory settings, VMID/PASID mapping, HQD loading/dumping/destroy, wave control, trap handler programming, and queue reset.
- `gmc_v9_0.c` and related GMC/VM code for VM context, protection fault, invalidation, aperture, XGMI, ATS, and SR-IOV handling on GC 9.4.2-class devices.
- Firmware-mediated paths for RLC, MEC/MES-style queue handling, power management, and SR-IOV/GPUIOV ownership.

## Risks and Edge Cases

- Generated-header drift is the main risk. A wrong offset or base index can silently target another GC register while preserving a valid C symbol.
- This chunk starts in the middle of `gc_rlcpdec` and ends in the early `gccacind` block, so the final per-file report must merge neighboring chunks for complete block coverage.
- Direct `reg*` offsets and indirect `ix*` indexes have different access paths. Mixing them can corrupt CAC programming.
- TCP watchpoint code assumes contiguous register spacing derived from `regTCP_WATCH1_ADDR_H - regTCP_WATCH0_ADDR_H`; register reordering would break watch slots even if individual macro names remain present.
- `*_BASE_IDX` values are part of the ABI with `adev->reg_offset`. Copying an offset with the wrong base index can hit a different aperture or fail on multi-die/SR-IOV hardware.
- VM and shared aperture registers are high impact. Wrong context, PF/VF, MARC, ATS, XGMI, AGP, HBM, or system-aperture offsets can cause faults, memory isolation failures, or device reset loops.
- EDC/RAS counters require correct instance counts, clear semantics, and block mapping. A wrong register can under-report poison events or clear unrelated diagnostic state.
- Debug/trap, SQ indirect, and thread-trace aliases include many same-address decode views. Consumers must know whether a register is a command, status, data, alias, or formatted trace word before reading or writing.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU with GC 9.4.2/Aldebaran and KFD enabled so generated symbols are checked in `gfx_v9_4_2.c`, `amdgpu_amdkfd_aldebaran.c`, shared GFX v9 KFD helpers, and GMC v9 code.
- Mechanically compare this line range against the authoritative generated GC 9.4.2 register database and the paired `gc_9_4_2_sh_mask.h`.
- Boot or emulate on Aldebaran-class hardware and verify golden TCP channel-steering values, SQ init, GPR/LDS init IB submission, debug trap configuration, and TCP address watchpoints.
- Exercise compute queue creation, dispatch, preemption/reset, VMID/PASID mapping, shader memory setup, and wave-control/debug workflows through KFD.
- Run VM stress with page faults, XNACK/ATS paths, SR-IOV PF/VF aperture setup, XGMI peer mappings, invalidate requests, and protection-fault reporting.
- Run RAS/EDC diagnostics for RLC, SPI, SQC, SQ, TCP, TCC, TCA, TCX, and TD counters; verify counts, clear behavior, and block labels match hardware.
- Inspect register dumps before and after reset, suspend/resume, queue teardown, VM context teardown, and RAS counter clearing to catch persistent bad state or wrong-address writes.
