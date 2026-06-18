# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h lines 7095-9511

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 9.3.0 register mask header. It starts in the middle of the `MMEA1_DSM_CNTL` family and ends inside the `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32` register, after the high logical-page-number shift definition but before that field's mask in the next chunk. The covered range includes:

- `MMEA1` diagnostic/safety/error-injection fields, clock-gating controls, EDC mode, error status, and memory-arbitration miscellaneous fields.
- `mmhub_pctldec` power-controller fields for deep sleep, page-gating ignore control, DAGB deep-sleep state, RENG RAM access/execution, and register-save ranges for `PCTL0`, `PCTL1`, and `PCTL2`.
- `mmhub_l1tlb_vml1dec` L1 TLB status registers for TLB instances 0 through 7.
- `mmhub_l1tlb_vml1pldec` and `mmhub_l1tlb_vml1prdec` L1 TLB performance-counter configuration, result control, and counter data windows.
- `mmhub_utcl2_atcl2dec` ATC L2 control, cache-data, status, clock-gating, and memory light-sleep fields.
- `mmhub_utcl2_vml2pfdec` VM L2 cache, page-fault/default-address, protection-fault, identity-aperture, bank-selection, parity, clock-gating, and real-time-class fields.
- `mmhub_utcl2_vml2vcdec` VM context controls for contexts 0 through 15, context-disable bits, invalidate-engine semaphore/request/ack/address-range registers for engines 0 through 17, and the beginning of VM context page-table base/start address registers.

The file is a generated hardware bitfield map. This chunk defines preprocessor constants only: there are no C functions, structs, variables, allocations, or executable branches here.

## Purpose

This header section provides the bit-level ABI used by AMDGPU MMHUB code when composing or decoding 32-bit MMIO register values for MMHUB 9.3.0. Each field follows the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask used to isolate or insert the field.

The sibling `mmhub_9_3_0_offset.h` file supplies register addresses such as `mmPCTL_MISC`, `mmVM_L2_CNTL`, and `mmVM_CONTEXT0_CNTL`; this file supplies the field layouts for those register addresses. Driver code normally consumes these definitions through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### MMEA1 DSM, EDC, Error, and Arbitration Fields

The opening lines continue from the prior chunk's `MMEA1_DSM_CNTL` register. The visible fields cover DSM irritator data and single-write enables for DRAM read/write command memories, DRAM write data memory, read/write return tag memories, and GMI read/write command/data memories. `MMEA1_DSM_CNTLA` repeats the same pattern for page-memory and IO command/data paths, while `MMEA1_DSM_CNTL2` and `MMEA1_DSM_CNTL2A` define error-injection enables, inject-delay selection bits, and a shared `INJECT_DELAY` field for command/data/page memories.

`MMEA1_CGTT_CLK_CTRL` controls local clock-gating timing and overrides through `ON_DELAY`, `OFF_HYSTERESIS`, soft-stall override bits for write/read/return paths, `LS_OVERRIDE`, and soft override bits for write/read/return/register domains.

`MMEA1_EDC_MODE` exposes EDC behavior flags including fed-out counting, FUE gating, DED mode, FED propagation, and bypass. `MMEA1_ERR_STATUS` reports SDP read/write response status, read-response data status, data parity error, busy-on-error, FUE flag, and a `CLEAR_ERROR_STATUS` command bit. `MMEA1_MISC2` covers CSGROUP swap controls, DRAM/GMI burst limits, and IO read/write priority enable.

### MMHUB Power Controller and Register Save/Restore

The `mmhub_pctldec` block starts with `PCTL_MISC`, which controls deep-sleep allowance, RSMU/DAGB idle thresholds, whether STCTRL ignores protection faults, EA0/EA1 SDP acknowledgements, and page-gating FSM command status.

`PCTL_MMHUB_DEEPSLEEP`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_DAGB` define dense per-domain `DS0` through `DS16` bitmaps. The deep-sleep register also includes a top-bit `SETCLEAR` selector, while the ignore register adds an `ALLIPS` bit. These masks encode which MMHUB subdomains may enter deep sleep, which domains are overridden, which domains page gating should ignore, and which deep-sleep domains interact with DAGB.

`PCTL0_RENG_*`, `PCTL1_RENG_*`, and `PCTL2_RENG_*` expose three RENG control windows. Each instance has a RAM index, full 32-bit RAM data, execution control bits for power-up execution, immediate execution, immediate-mode selection, start/end pointers, and execution-on-register-update. `PCTL0` uses wider 11-bit RENG pointers than `PCTL1` and `PCTL2`, which use 10-bit pointers. The matching `PCTL*_MISC` registers lock critical registers, set tile idle thresholds, enable RENG memory light sleep, force PGFSM command completion, and, for `PCTL1`/`PCTL2`, control deep-sleep disconnect from SDP.

The `PCTL*_STCTRL_REGISTER_SAVE_RANGE0..4` registers encode base/limit pairs for state-controller register-save ranges. `PCTL*_STCTRL_REGISTER_SAVE_EXCL_SET` and `PCTL*_STCTRL_REGISTER_SAVE_EXCL_SET1` encode excluded register IDs. These fields describe hardware state-save coverage used around power transitions, not software persistence in this header.

### L1 TLB Status and Performance Counters

The `MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS` registers expose identical `BUSY` and `FOUND_PARITY_ERRORS` bits for eight L1 TLB instances.

The L1 performance-counter block defines `MC_VM_MX_L1_PERFCOUNTER0_CFG` through `MC_VM_MX_L1_PERFCOUNTER3_CFG`. Each counter has `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR` fields. `MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL` selects which counter is read and defines start/stop triggers, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`.

The result-read block provides `MC_VM_MX_L1_PERFCOUNTER_LO` for the low 32 counter bits and `MC_VM_MX_L1_PERFCOUNTER_HI` for the high counter bits plus a compare value. These macros support profiling and debug paths that need MMHUB L1 TLB event counts.

### ATC L2 Control, Cache Data, Status, and Clock Gating

The `ATC_L2_*` registers describe the address-translation cache L2 path. `ATC_L2_CNTL` controls translation read/write request counts, whether request counts depend on address modifiers, cache-invalidate mode, and default-page output to system memory. `ATC_L2_CNTL2` selects banks, cache update mode, write-driven LRU updates, tag-index low-bit swap, VMID mode, and wildcard reference values.

`ATC_L2_CACHE_DATA0..2` expose cache-entry validity, cached attributes, virtual page address high/low portions, and physical page address. `ATC_L2_CNTL3` controls invalidation-request delay, ATS request credits, and component-clock request hysteresis.

`ATC_L2_STATUS` and `ATC_L2_STATUS2` report busy state and parity error information, including IFIFO nonfatal and fatal parity details. `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL` define clock-gating and memory light-sleep controls for this cache block.

### VM L2 Cache and Page-Fault Handling

The `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, and `VM_L2_CNTL4` definitions control MMHUB's VM L2 cache behavior, L1/L2 invalidation, cache banking, update modes, hit/miss handling, PDE/PTE request behavior, IFIFO active-transaction limits, and clock-gating/light-sleep override behavior. These are core bring-up and reset registers for MMHUB address translation.

`VM_L2_STATUS` exposes cache/TLB busy and invalidation state. `VM_DUMMY_PAGE_FAULT_CNTL` plus `VM_DUMMY_PAGE_FAULT_ADDR_LO32/HI32` describe dummy-page fault behavior and the captured logical page address.

`VM_L2_PROTECTION_FAULT_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL2`, `VM_L2_PROTECTION_FAULT_MM_CNTL3`, and `VM_L2_PROTECTION_FAULT_MM_CNTL4` define how range, PDE0, PDE1, valid, read, write, execute, NACK, dummy-page, and retry faults are interrupted, retried, redirected to defaults, or filtered by client ID. `VM_L2_PROTECTION_FAULT_STATUS` reports `MORE_FAULTS`, walker error, permission fault class, mapping error, client ID, read/write direction, atomic access, VMID, VF bit, and VFID. The matching address/default-address registers hold logical fault addresses and default physical page addresses.

The identity-aperture fields, `VM_L2_CONTEXT1_IDENTITY_APERTURE_LOW_ADDR_*`, `VM_L2_CONTEXT1_IDENTITY_APERTURE_HIGH_ADDR_*`, and `VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`, encode logical aperture bounds and the physical offset for identity-mapped context 1 traffic.

`VM_L2_MM_GROUP_RT_CLASSES` is a 32-bit bitmap of real-time class assignment for MM client groups. `VM_L2_BANK_SELECT_RESERVED_CID` and `VM_L2_BANK_SELECT_RESERVED_CID2` reserve read/write client IDs for special bank-selection and invalidation behavior. `VM_L2_CACHE_PARITY_CNTL` controls parity checking and forced parity mismatch injection for 4K PTE, bigK PTE, and PDE caches, including bank/number/associativity selection.

### VM Contexts and Invalidation Engines

`VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` are repeated context-control registers. Each context has fields for enabling the context, page-table depth, page-table block size, retry behavior for permission/invalid/other faults, and interrupt/default-response enables for range, dummy-page, PDE0, valid, read, write, and execute protection faults. The repeated layout lets AMDGPU program context 0 and then program contexts 1 through 15 using register-distance arithmetic.

`VM_CONTEXTS_DISABLE` provides per-context disable bits for contexts 0 through 15. The invalidate-engine block defines `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`, `REQ`, `ACK`, and address-range low/high registers. Each engine has a semaphore field, a request register with per-VMID invalidation request bits and flush/control modifiers, an ack register with a 16-bit ack bitmap, and optional address-range registers. The low address-range register carries an `S_BIT` plus low logical-page-address bits; the high register carries the remaining high address bits.

The chunk then starts the VM context page-table address block. `VM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` through `VM_CONTEXT15_PAGE_TABLE_BASE_ADDR_LO32/HI32` hold page-directory-entry low/high words for all 16 contexts. The final visible complete register is `VM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32`; the chunk ends after `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4__SHIFT`, so the corresponding mask and subsequent context start/end address registers belong to the next chunk.

## Control Flow and State Behavior

This header has no runtime control flow. It affects behavior at compile time by defining how driver code constructs register writes and interprets register reads.

The state represented by this chunk lives in MMHUB hardware. Durable or latched state includes MMHUB power-controller deep-sleep selections, RENG RAM contents and execution pointers, state-controller save ranges, L1 TLB busy/parity status, performance-counter configuration and values, ATC L2 cache controls and cache-data windows, VM L2 cache configuration, protection-fault policy and captured fault status/address registers, identity-aperture bounds, VM context enable/page-table/fault policy registers, invalidation-engine requests and acks, and page-table base/start addresses.

Several fields are command-like rather than simple persistent configuration. Examples include `MMEA1_ERR_STATUS__CLEAR_ERROR_STATUS`, performance-counter `CLEAR`/`CLEAR_ALL`, RENG `RENG_EXECUTE_NOW`, VM L2 invalidation controls, fault-status capture/clear flows, and VM invalidate-engine request bits. Consumers must follow the ordering, polling, and timeout rules in MMHUB driver code and the hardware specification; the masks alone do not encode sequencing.

## Dependencies and Integration Points

The chunk depends on the generated AMD register-header convention:

- `mmhub_9_3_0_offset.h` supplies MMHUB 9.3.0 register addresses and base indices.
- AMDGPU register helpers consume the `__SHIFT` and `_MASK` definitions to build and read register values without hard-coded bit positions.
- Cross-generation MMHUB code often shares register names, but the exact layouts are generation-specific and must be paired with the matching offset/mask header.

Observed integration points in this source tree include `drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, which programs MMHUB L1 TLB controls, VM L2 controls, protection-fault policy, context controls, invalidation-engine offsets, and fault-status registers using the same `REG_SET_FIELD`/`SOC15_REG_OFFSET` patterns represented by these masks. That file also records MMHUB RAS CE/UE register entries for `MMEA1`, tying the `MMEA1` status/control space to error reporting.

The VM context and invalidation macros also integrate with common AMDGPU VM/GMC state. `struct amdgpu_vmhub` stores distances such as context register spacing, invalidate request spacing, and invalidate address-range spacing; those distances are derived from adjacent generated register offsets and are used to program repeated context and invalidate-engine registers.

Performance-counter masks are integration points for profiling and diagnostics. Power-controller and clock-gating masks integrate with power-management, suspend/resume, reset, and golden-register programming. Protection-fault masks integrate with VM fault interrupt handling, retry-fault behavior, default-page policy, and SR-IOV diagnostics through the VF/VFID status fields.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated MMHUB fields, causing GPUVM faults, hangs during TLB/cache invalidation, missed interrupts, incorrect page-table configuration, bad power-state transitions, or misleading fault diagnostics.
- Many register families are mechanically repeated. `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` and invalidate engines 0 through 17 look regular, but consumers still depend on exact register spacing and field widths.
- Power-controller bits can affect hardware state save/restore and deep-sleep entry. Incorrect `PCTL_*` deep-sleep, RENG, or save-range programming can break suspend/resume, power gating, or register restoration.
- Error-injection and parity-forcing fields must remain restricted to diagnostics. Enabling MMEA1 DSM injection or VM L2 parity mismatch fields in normal paths can create artificial faults or poison error accounting.
- VM protection-fault policy fields determine whether faults interrupt, retry, or fall back to default pages. Incorrect policy can hide real memory faults, create interrupt storms, or make retryable faults unrecoverable.
- Invalidation-engine request/ack fields require sequencing. Issuing requests with wrong VMID bits, address ranges, or engine spacing can leave stale translations or make the driver wait on the wrong ack bit.
- The chunk begins and ends mid-family. The merge lane must combine it with adjacent chunks for the full `MMEA1_DSM_CNTL` and `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32` definitions.

## Test and Validation Signals

Useful validation is mostly build, bring-up, and hardware-integration coverage:

- Build AMDGPU/MMHUB code that includes `mmhub/mmhub_9_3_0_sh_mask.h`; this catches missing or renamed macros.
- MMHUB/GMC initialization tests should verify L1 TLB enablement, VM L2 cache setup, bank selection, partition count, fault defaults, and context 0/context 1 programming.
- GPUVM tests should exercise VM context enablement, page-table depth/block-size fields, page-table base/start address programming, context disable bits, and retry-fault policy.
- TLB invalidation tests should issue full and address-range invalidations across supported engines and confirm matching ack bits and stale-translation removal.
- Page-fault tests should validate range, valid, read, write, execute, dummy-page, PDE, retry, NACK, and VF/VFID fault status reporting.
- Suspend/resume and power-gating tests should cover `PCTL_*` deep-sleep, RENG execution, state-controller register-save ranges, ATC/VM L2 clock-gating, and memory light-sleep fields.
- RAS and diagnostic tests should cover MMEA1 CE/UE reporting, EDC mode/status, parity status, parity injection controls, and status clear behavior.
- Performance-counter tests should configure L1 TLB performance events, enable/clear counters, read low/high counter data, and validate stop-on-saturate behavior.

## Unresolved Cross-Chunk References

This chunk starts after the `MMEA1_DSM_CNTL` register has already begun, so its earliest visible macros are the tail of that family. It ends after the `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4__SHIFT` definition and before the associated mask. The final per-file research document should stitch this report with adjacent chunks to describe those register families completely.
