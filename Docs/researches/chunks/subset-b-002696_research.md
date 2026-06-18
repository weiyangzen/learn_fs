# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 27088-29458

## Scope

This chunk is a generated AMD GC 9.4.3 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are exposed as `__SHIFT` and `__MASK` macros for composing or decoding 32-bit register values. There are no functions, structs, enums, includes, branches, allocations, locks, callbacks, or file/network persistence behavior in this range.

The selected lines start in the middle of `RLC_SRM_RLCV_COMMAND`, carrying only the final `START_OFFSET`, reserved, and `DEST_MEMORY` masks from that register. The chunk then covers a broad RLC block for SRM command/status, indexed SRM control windows, SMU command arguments, GPM/SPM UTCL1 controls and error capture, semaphores, interrupts, prewalker controls, UTCL2/R2I/LB/DS controls, GPU clock counters, RLC CPG invalidation, UE/CE error status, DSM irritator and error-injection controls, and the RLC SMU clock request bit. It then crosses the `addressBlock: xcd0_gc_pwrdec` marker into CGTS power/clock-gating controls, including global CGTS state-machine/readback/TCC-disable registers, per-CU subblock controls for CUs 0-15, and the beginning of the per-CU TCPI control sequence through the first three fields of `CGTS_CU9_TCPI_CTRL_REG`.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 9.4.3 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_9_4_3_sh_mask.h` supplies bit layouts for GC 9.4.3 registers. Driver code pairs these field definitions with register addresses from the matching offset header and, where generated, reset/default values from the matching default header. Consumers typically use AMDGPU helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, or equivalent generated-register helpers, to pack field values before MMIO, indexed register, or command-stream access.

This slice focuses on two related but distinct hardware surfaces:

- RLC service, microcontroller, memory-management, interrupt, error-reporting, and diagnostic controls. The RLC block defines command/status fields for SRM/RLCV operations, indexed address/data windows, busy and abort status, command/argument mailboxes to SMU, scheduler byte fields, UTCL1 translation retry/drop/invalidate/snoop controls, translated request error VMID/address capture, semaphore client IDs, EOF/spare interrupt bits and counters, prewalker trigger/address/size fields, UTCL2 cache and invalidation controls, LB threshold data registers, clock counters, CPG status invalidation, CE/UE error status, DSM memory irritator controls, and RLC-SMU clock request validity.
- CGTS power-decode and clock-gating state. The `xcd0_gc_pwrdec` block defines global CGTS state-machine delays, MGCG enable/mode/override bits, readback mux selection, TCC disable masks, per-compute-unit SP/LDS/SQ/TA/SQC/TD/TCPF controls, and TCPI controls. The repeated per-CU fields provide local clock/power gating thresholds and override paths for shader and texture/cache-related subblocks.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register address macros are expected in the companion GC 9.4.3 offset header.
- Callers use these constants with AMDGPU register packing/extraction helpers, direct MMIO helpers, indexed register helpers, firmware mailbox setup, diagnostics, or power-management programming sequences.

Important register families in this slice include:

- `RLC_SRM_*`: RLC service/resource-management command status, indexed control address/data windows 0-7, busy status, and GPM abort.
- `RLC_CSIB_*`, `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_*`, `RLC_SMU_CLK_REQ`, and `RLC_CP_SCHEDULERS`: RLC-to-firmware/control-plane data paths, scheduler bytes, SMU command arguments, clock request validity, and command buffer or instruction-buffer address/length style fields.
- `RLC_GPM_GENERAL_*`, `RLC_GPM_UTCL1_CNTL_*`, `RLC_SPM_UTCL1_CNTL`, `RLC_PREWALKER_UTCL1_*`, `RLC_UTCL1_STATUS*`, and `RLC_UTCL2_CNTL`: scratch/general registers and memory-translation/cache-control fields for GPM, SPM, and prewalker traffic.
- `RLC_*_UTCL1_*ERROR_*`, `RLC_UE_ERR_STATUS_*`, and `RLC_CE_ERR_STATUS_*`: error-capture fields for translated request failures and corrected/uncorrected RLC memory errors, including valid flags, address fragments, VMID, memory ID, error info, counters, parity/ECC/poison indicators, and reserved bits.
- `RLC_SEMAPHORE_*`, `RLC_CP_EOF_INT*`, `RLC_SPARE_INT*`, and `RLC_RLCV_SPARE_INT*`: small client-ID, interrupt, and interrupt-count fields used by RLC/CP/RLCV synchronization and notification paths.
- `RLC_DSM_TRIG`, `RLC_DSM_CNTL*`, and `RLC_DSM_CNTL2*`: diagnostic stress/error-injection controls for RLCG/RLCV instruction RAM, scratch RAM, TCTAG RAM, SPM scratch RAM, SRM data/address RAM, and per-SE SPM scratch RAM.
- `CGTS_SM_CTRL_REG`, `CGTS_RD_CTRL_REG`, `CGTS_RD_REG`, `CGTS_TCC_DISABLE`, and `CGTS_USER_TCC_DISABLE`: global CGTS state-machine, readback, and TCC-disable controls.
- `CGTS_CU<n>_SP0_CTRL_REG`, `CGTS_CU<n>_LDS_SQ_CTRL_REG`, `CGTS_CU<n>_TA_SQC_CTRL_REG`, `CGTS_CU<n>_SP1_CTRL_REG`, and `CGTS_CU<n>_TD_TCP_CTRL_REG` for CUs 0-15: repeated subblock control fields with base 7-bit values plus override, busy override, light-sleep override, and SIMD-busy override bits.
- `CGTS_CU<n>_TCPI_CTRL_REG`: per-CU TCPI controls begin at the end of the chunk, complete for CUs 0-8 and partial for CU9.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 9.4.3 register metadata for the active ASIC.
2. Choose an address macro from the matching offset header.
3. Build a register value from firmware state, power-management policy, error handling, debugfs/diagnostic input, or a read-modify-write of current hardware state.
4. Pack or extract fields using the `__SHIFT`/`__MASK` pairs, usually through common AMDGPU register helpers.
5. Issue MMIO/indexed writes or reads, send RLC/SMU mailbox commands, poll status bits, service interrupts/errors, or program CGTS clock-gating state.

The RLC-side runtime sequences are generally command/status or diagnostic flows: write command/argument registers, poll FIFO/busy/ready/status fields, capture errors, trigger prewalker or DSM behavior, and update interrupt or semaphore state. The CGTS-side runtime sequences are power-management flows: configure global CGTS behavior, select readback muxes, disable or mask TCCs, and apply per-CU subblock override or gating policy. This header does not define required waits, side effects, reset ordering, privilege rules, pulse-versus-level semantics, or whether a field is read-only/write-only; those constraints must come from the hardware spec and the AMDGPU code that uses the macros.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware fields whose values live in GPU registers, firmware-visible mailboxes, diagnostic latches, or command/state storage until overwritten, reset, restored after GPU reset, or reinitialized during suspend/resume and power transitions.

Several fields in this chunk represent persistent control state:

- RLC UTCL1/UTCL2 controls can change retry timing, drop behavior, invalidation, fragment limit mode, and snooping behavior for RLC-originated translation traffic. Stale or incorrectly restored values can affect later RLC memory operations beyond the code path that programmed them.
- `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_*`, and `RLC_SMU_CLK_REQ` are mailbox-style fields. Their correctness depends on firmware protocol ordering and ownership, not just field packing.
- Semaphores, interrupts, and EOF counters are synchronization-visible state. Misinterpreting level, pulse, clear-on-read, or write-one-to-clear semantics can lose events or leave stale notifications.
- Error-status registers capture hardware fault state. Valid flags, address-valid flags, counters, VMID, memory ID, and high/low address fragments must be read consistently before software clears or overwrites the source state.
- DSM controls are diagnostic and error-injection state. Leaving irritator or injection bits enabled outside controlled test paths can intentionally corrupt internal RLC memories or produce artificial error reports.
- CGTS state-machine and per-CU control registers persist as power/clock-gating policy. Override and busy-override fields can hold hardware units on, force light-sleep behavior, or defeat normal automatic gating until explicitly changed.

The header does not encode reset defaults, reserved-bit preservation requirements, access width, or safe read-modify-write rules. Callers should preserve reserved bits unless writing a documented full-register value and should use unsigned 32-bit arithmetic because many masks occupy high bits or full 32-bit data fields.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.4.3 register set staying internally consistent:

- The companion `gc_9_4_3_offset.h` provides the register addresses corresponding to these field masks.
- A matching `gc_9_4_3_default.h`, where present for the same families, provides reset/default values.
- AMDGPU register helpers provide field packing/extraction plus MMIO, indexed-register, mailbox, and power-management access paths.
- Firmware protocols with RLC and SMU determine legal command/argument values, readiness polling, and clock-request semantics.
- GPU memory-management, VM fault handling, interrupt handling, reset/recovery, suspend/resume, RAS, diagnostics, debugfs, and power-gating code rely on these bit layouts matching the hardware database.

Integration points include RLC SRM/RLCV command submission, indexed SRM register access, RLC-to-SMU communication, UTCL1/UTCL2 translation tuning, prewalker memory priming, RLC error capture and reporting, CP EOF and spare interrupt handling, RLC semaphores, GPU clock counter reads, CPG invalidation, RLC diagnostic stress/error injection, TCC disable policy, CGTS readback/debug selection, and per-CU clock-gating override programming for SP, LDS, SQ, TA, SQC, TD, TCPF, and TCPI blocks.

The `addressBlock: xcd0_gc_pwrdec` marker is a meaningful boundary: macros after it describe CGTS power-decode registers rather than the preceding RLC service/control register block. The final per-file merge should preserve that boundary.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Wrong shifts or masks compile cleanly but can program unrelated hardware bits, causing RLC hangs, lost firmware commands, false or missed errors, broken interrupt signaling, bad power behavior, or device reset failures.
- The chunk starts mid-register: only the last three masks of `RLC_SRM_RLCV_COMMAND` are present here. The preceding chunk is required to understand the full command layout.
- The chunk ends mid-register: `CGTS_CU9_TCPI_CTRL_REG` includes only `TCPI`, `TCPI_OVERRIDE`, and `TCPI_BUSY_OVERRIDE` shifts here. The following chunk is required for its remaining shifts and masks plus later TCPI instances.
- Repeated CGTS per-CU layouts invite generator or copy/paste errors. A mismatch on one CU or one subblock may present as a topology-specific performance or power regression rather than a broad failure.
- RLC mailbox, semaphore, interrupt, and status registers may have side-effect semantics not visible in the mask header. Treating them as ordinary read/write state can lose events, clear latches unexpectedly, or race firmware.
- Address fields in prewalker and CSIB registers are split into low/high fragments and may use hardware-specific alignment units. Raw byte-address assumptions can produce plausible but wrong register values.
- UTCL1/UTCL2 retry, drop, invalidation, force-snoop, and cache-control fields affect memory-translation behavior. Incorrect values can cause timeouts, translation faults, stale translations, or poor performance under VM pressure.
- Error-status low/high pairs must be correlated carefully. Reading only one half, ignoring valid flags, or clearing in the wrong order can produce misleading RAS reports.
- DSM irritator and error-injection controls are intentionally hazardous diagnostic knobs. They should be isolated to test/debug paths with explicit cleanup.
- CGTS override and TCC-disable fields can silently alter power, clock, cache, and compute-unit behavior. Full-register writes that do not preserve reserved or ASIC-specific bits can cause subtle instability or power regressions.

## Test Signals

Useful validation is mostly build coverage, generated-data consistency checks, and hardware/runtime coverage:

- Kernel build coverage for AMDGPU files including `gc_9_4_3_sh_mask.h`, especially RLC, GC power management, RAS, reset/recovery, suspend/resume, diagnostics, and debugfs paths.
- Mechanical comparison against AMD's authoritative GC 9.4.3 register database for every `__SHIFT`/`__MASK` pair in this line range.
- Cross-checks that every complete register family in this chunk has matching address macros in `gc_9_4_3_offset.h` and expected defaults in generated default headers where those defaults exist.
- Static sanity checks that masks align with shifts, full-width data registers use `0xFFFFFFFFL`, high-bit masks are handled as unsigned values, split low/high address fields are complete across chunks, and repeated per-CU CGTS patterns remain consistent.
- Runtime RLC tests that exercise SRM/RLCV command/status paths, SMU command/argument handshakes, scheduler fields, semaphore/interrupt handling, EOF counters, GPU clock counter capture, CPG invalidation, and reset/recovery reinitialization.
- VM and fault-path tests that cover UTCL1/UTCL2 controls, prewalker trigger/address/size programming, translated request error capture, CE/UE error reporting, poison/ECC/parity indicators, and RAS logging.
- Diagnostic tests that enable and disable DSM irritator/error-injection fields in a controlled environment and verify cleanup restores normal behavior.
- Power-management tests that cover CGTS global mode programming, readback muxes, TCC disable masks, per-CU SP/LDS/SQ/TA/SQC/TD/TCPF/TCPI overrides, compute workloads across all CUs, idle transitions, clock gating, suspend/resume, and GPU reset.
- Runtime warning signals include RLC busy or FIFO status stuck, SMU command timeouts, missing or repeated EOF/spare interrupts, malformed RAS addresses or counters, VM faults after prewalker/UTCL changes, artificial errors outside diagnostic mode, unexpected TCC disablement, per-CU performance asymmetry, higher idle power, failed clock-gating transitions, and regressions isolated to one CU index.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002696`. It covers lines 27088-29458 of `gc_9_4_3_sh_mask.h`. The final per-file document should merge it with the preceding chunk for the complete `RLC_SRM_RLCV_COMMAND` field list and with the following chunk for the rest of `CGTS_CU9_TCPI_CTRL_REG` and subsequent CGTS TCPI controls.
