# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h lines 7203-8262

## Scope And Purpose

This chunk is the final 1,060-line segment of AMD's generated VCN 5.3.0 shift/mask header. It contains C preprocessor constants only: hardware register fields are exposed as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. It defines no functions, structs, variables, allocations, locking, or executable control flow.

The file sits under a `ceph-client` source mirror, but this content is AMDGPU media-engine register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU VCN/JPEG/UMSCH code that combines these masks with addresses from `vcn_5_3_0_offset.h` and uses SOC15/SOC24 register helpers to read, write, or compose MMIO values.

The chunk starts in the middle of `JPEG_MEMCHECK_SYS_INT_ACK2`, after its first few field definitions in the previous chunk. It ends at the `#endif` closing the header guard, so there is no following VCN 5.3.0 shift/mask content in this file.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: raw bit mask for a field in a 32-bit hardware register.

Major register groups in this chunk:

- JPEG interrupt and arbitration tail: the remainder of `JPEG_MEMCHECK_SYS_INT_ACK2`, `JPEG_MASTINT_EN`, `JPEG_IH_CTRL`, and `JRBBM_ARB_CTRL`. These cover memory-check error acknowledgements for JPEG read/write clients, master interrupt overrun reset and interrupt-overrun mask fields, interrupt-handler routing fields such as VMID/user-data/ring-id, and JRBBM drop controls for SRBM, EJRBC, and DJRBC0 paths.
- `uvd_uvd_jpeg_common_sclk_dec`: `JPEG_CGC_GATE`, `JPEG_CGC_CTRL`, `JPEG_CGC_STATUS`, common/decoder/encoder CGC memory controls, and `JPEG_PERF_BANK_*` registers. These describe JPEG decoder/encoder/JMCIF/JRBBM clock gates, dynamic clock-gating mode, gate/off delays, active-clock status, memory light-sleep/deep-sleep/shutdown enables, and four performance-counter event/count banks.
- `uvd_vcn_umsch_dec`: UMSCH scheduler and MES front-end registers including `VCN_UMSCH_MES_CNTL`, `UMSCH_CTL`, AGDB write pointers, four mailbox/response pairs, UTCL1 control, busy flags, ring-buffer base/size/read/write pointers, master interrupt control, IH control, system interrupt enable/status/ack/source, IH context ID, force/drop/UTCL2 response controls, and `UMSCH_MES_RESET_CTRL`.
- `uvd_vcn_cprs64dec`: a large MES core/control/debug register block. It covers program counter and interrupt routine start addresses, trap vector halves, `VCN_MES_CNTL` core control bits, pipe priorities, interrupt masks and pending status, scratch index/data, instruction pointer, RISC-V-like machine CSRs (`MSTATUS`, `MEPC`, `MCAUSE`, `MBADADDR`, `MIP`, cycle/time/instret, ISA/vendor/arch/imp/hart IDs), icache/dcache operations, general-purpose registers, indexed data memory access, local instruction/data/scratch apertures, perf-count selection, interrupt data words 16 through 31, and 16 data-cache aperture base/mask/control triplets.
- `uvd_vcn_hypdec`: hypervisor-visible MES instruction/data base and bounds registers. These define low/high halves, VMID, execute-disable, cache-policy, and bound fields for instruction and data memory mappings, with both `IC/DC` and `MI/MD` naming aliases.
- `uvd_slmi_adpdec`: S/LMI adapter registers for MMSCH non-cacheable windows. These include eight 64-bit BAR low/high pairs, packed VMID fields for NC0 through NC7, MMSCH coherency/VM/privilege/swap/read/write/drop controls, MMSCH LMI status/error fields, active PF/VF identity, and UMSCH LMI clean-status bits.

## Control Flow And Runtime Behavior

There is no control flow in this header. Runtime use is indirect:

1. ASIC-specific AMDGPU code includes `vcn_5_3_0_offset.h` for register addresses and this header for field masks/shifts.
2. Helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_UMSCH`, `SOC15_WAIT_ON_RREG`, and SOC24 JPEG DPG helpers compose, preserve, poll, or update the actual register values.
3. JPEG initialization and power-management paths use the JPEG CGC masks to enable/disable media clock gating and DPG SRAM programming.
4. UMSCH setup programs MES reset, cache invalidation, pipe reset/active/halt state, instruction/data bases, local masks, interrupt routine addresses, and force/GPUVM policy before starting the media scheduler firmware.

Concrete consumers in this tree include `amdgpu/jpeg_v5_3_0.c`, where `JPEG_CGC_CTRL__*` and `JPEG_CGC_GATE__*` fields drive JPEG clock gating and DPG mode, and `amdgpu/umsch_mm_v4_0.c`, where `UMSCH_MES_RESET_CTRL`, `VCN_MES_CNTL`, `VCN_MES_IC_BASE_CNTL`, `VCN_MES_PRGRM_CNTR_START*`, local aperture, instruction/data base, bound, and `UVD_UMSCH_FORCE` fields are programmed for the UMSCH micro-engine.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe stateful hardware registers whose values persist in JPEG, UMSCH, MES, hypervisor, and LMI blocks until reset, power-gating, firmware reinitialization, suspend/resume restore, or another register write changes them.

State represented by this chunk includes JPEG memory-check acknowledgement bits, interrupt routing metadata, clock-gating enable/mode/status, memory low-power controls, JPEG performance counter configuration and counts, UMSCH ring-buffer pointers and mailboxes, system interrupt latch/ack/source fields, scheduler busy state, MES firmware entry points, cache invalidation/prime/bypass state, pipe reset/active/halt/step controls, debug and machine CSR snapshots, local and data-cache aperture mappings, hypervisor instruction/data bounds, MMSCH non-cacheable BARs and VMIDs, read/write drop controls, and LMI clean/error status.

Access semantics are not encoded in macro names. Some fields are persistent configuration, some are hardware-updated status, some are interrupt acknowledgements, some are command/self-clearing operations, and some are firmware/debug scratch state. Consumers must preserve reserved bits and follow the owning block's sequencing rules, especially around cache invalidation, interrupt acknowledgement, firmware address programming, VMID/aperture setup, and LMI drop/error status.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_offset.h`, which supplies matching addresses such as `regJPEG_CGC_GATE`, `regVCN_UMSCH_MES_CNTL`, `regVCN_MES_PRGRM_CNTR_START`, `regVCN_MES_PRGRM_CNTR_START_HI`, `regVCN_MES_IC_BASE_LO`, and `regUVD_LMI_MMSCH_CTRL`.

The primary integration points are:

- JPEG 5.3.0 bring-up, suspend/resume, power-gating, dynamic-power-gating, and clock-gating code.
- UMSCH media scheduler firmware loading and start-up code, including UMSCH-specific write helpers and firmware GPU-address programming.
- VCN interrupt handling, where IH control, master interrupt enable, system interrupt status/source/ack, and interrupt-data registers route events into AMDGPU interrupt rings.
- Firmware and debug tooling that reads MES status, machine CSRs, busy flags, scratch registers, perf counters, and pending interrupts during bring-up or failure diagnosis.
- Virtualization and memory-management paths that depend on VMID, GPUVM force, hypervisor base/bounds, MMSCH NC BARs, PF/VF active ID, and LMI clean/drop/error fields.

The generated names are the compile-time contract. Missing or renamed symbols generally fail to build, but incorrect numeric masks or shifts can compile cleanly and cause incorrect MMIO programming at runtime.

## Risks And Edge Cases

- The chunk begins mid-register. The first field definitions for `JPEG_MEMCHECK_SYS_INT_ACK2` are in the previous chunk, so final per-file reconciliation must merge the boundary before making complete claims about that register.
- JPEG clock-gating masks are used directly in `jpeg_v5_3_0.c`. Bad `JPEG_CGC_GATE` or `JPEG_CGC_CTRL` masks can leave JPEG clocks enabled, gate clocks while active, break DPG-mode SRAM programming, or cause resume-only media failures.
- Interrupt fields are sequencing-sensitive. Incorrect master/IH/sys-int/ack/source masks can lose events, route them to the wrong VMID/ring/user-data, fail to clear latched interrupts, or hide memory-check failures.
- UMSCH ring-buffer pointer, mailbox, and AGDB write-pointer fields are full-width or alignment-sensitive. Wrong shifts or masks can desynchronize firmware/driver queues and produce scheduler hangs.
- MES firmware entry-point and aperture fields encode shifted or partial address values. Off-by-shift errors in `*_BASE_LO`, `*_PRGRM_CNTR_START*`, local masks, or hypervisor bounds can start firmware at the wrong address or map code/data incorrectly.
- Cache-control and reset fields such as `VCN_MES_CNTL`, `VCN_MES_IC_OP_CNTL`, `VCN_MES_DC_OP_CNTL`, and `UMSCH_MES_RESET_CTRL` may be self-clearing or require polling. Treating them as ordinary sticky bits risks stale cache contents or incomplete reset sequencing.
- Many debug/status registers are hardware-owned. Writing full register values to MES CSR/status/counter/pending-interrupt fields or LMI status fields could clear diagnostics or perturb firmware state.
- Repetitive aperture definitions (`VCN_MES_DC_APERTURE0` through `15`) and MMSCH NC BAR/VMID definitions are copy-error prone; a single incorrect index can affect only one VMID/window and appear only under specific virtualization or firmware workloads.
- The generated file includes both `DEPRECATED` and misspelled `DEPRACATED` field names in `VCN_MES_DC_OP_CNTL`; consumers must use the generated spelling that matches the header rather than normalizing names locally.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with VCN 5.3.0, JPEG 5.3.0, and UMSCH support enabled so include users and `REG_SET_FIELD`/`REG_GET_FIELD` expansions catch missing symbols.
- Mechanically compare this header with the authoritative VCN 5.3.0 register database and the companion `vcn_5_3_0_offset.h` address header.
- Diff against nearby VCN 5.x and 4.x generated headers where layout parity is expected, while accounting for VCN 5.3.0-specific address shifts and JPEG0-only decode fields.
- Exercise JPEG decode/encode paths across suspend/resume, DPG mode, clock-gating enable/disable, power-gating transitions, and interrupt delivery; watch for media timeouts, stuck busy bits, and unexpected memory-check acknowledgements.
- Exercise UMSCH firmware load/start, ring submission, mailbox responses, interrupt routing, reset/recovery, and GPUVM/VMID paths; watch for scheduler firmware hangs, invalid instruction/data fetches, stale cache behavior, and missed system interrupts.
- For virtualization-sensitive systems, validate PF/VF active function reporting, MMSCH NC window VMIDs, hypervisor instruction/data bounds, LMI clean bits, and MMSCH unsupported-length/address-alignment error reporting.
- Use hardware register dumps or tracepoints around firmware setup to confirm programmed base/bound/mask values match the expected shifted address encodings and that reserved bits remain preserved.

## Cross-Chunk Notes

The previous chunk is required for the beginning of `JPEG_MEMCHECK_SYS_INT_ACK2` and other JPEG common register definitions immediately before line 7203. This chunk closes `vcn_5_3_0_sh_mask.h`, so final reconciliation should combine all chunks for the source file before presenting a complete generated-header inventory.
