
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/tm.S

## Purpose
Implements low-level save and restore of PowerPC transactional memory state for KVM, including checkpointed GPRs, FP/VMX/VSX state, TM SPRs, CR, LR, CTR, XER, AMR, TAR, PPR, and DSCR. It is active only under `CONFIG_PPC_TRANSACTIONAL_MEM`.

## Important APIs, Types, And Functions
Core symbols are `__kvmppc_save_tm`, `_kvmppc_save_tm_pr`, `__kvmppc_restore_tm`, and `_kvmppc_restore_tm_pr`. PR wrappers export `_kvmppc_save_tm_pr` and `_kvmppc_restore_tm_pr`. It uses offsets such as `VCPU_GPRS_TM`, `VCPU_TEXASR`, `VCPU_TFHAR`, `VCPU_TFIAR`, `VCPU_FPRS_TM`, and `VCPU_VRS_TM`, plus helpers `store_fp_state`, `store_vr_state`, `load_fp_state`, and `load_vr_state`.

## Control Flow
Save enables TM/FP/VEC/VSX in MSR, checks the guest TS bits, and if transactional state is active, uses `treclaim` to expose checkpointed state. It preserves host scratch, CR, DSCR, optional nonvolatile GPRs, captures GPRs and TM SPRs into the vCPU, saves FP/vector state, restores host CR/DSCR/nonvolatile state, and optionally restores MSR bits. Restore writes TFHAR/TFIAR/TEXASR, verifies active TS, forces TEXASR failure summary, loads checkpointed FP/vector and scalar state, clears RI around volatile register replacement, executes `trechkpt`, restores host state, and restores MSR bits when requested.

## State And Persistence
Persistent guest TM state is stored in the vCPU arch save area. Temporary host state is kept on the stack, PACA scratch, and HSTATE scratch registers. PR wrappers preserve TAR around calls for C callers.

## Dependencies And Integration Points
Depends on PowerPC transactional memory instructions, PACA/HSTATE conventions, asm offsets generated from C structs, CPU feature sections for P9 TM HV assist, and FP/vector save helpers. Called by HV and PR KVM paths that need to context-switch transactional state.

## Risks
This is highly sensitive assembly: RI is cleared while stack/PACA state is transient, and any offset or calling-convention drift can corrupt host or guest state. TEXASR is adjusted to avoid host program checks on restore. Feature-specific behavior around P9 TM assist must match hardware. Incorrect nonvolatile preservation can break C callers.

## Test Signals
Signals include TM-enabled guest workloads, suspend/resume of active transactions across KVM exits, migration/register tests for TM SPRs, and stress on PR/HV wrappers. Build coverage should include TM disabled, TM enabled, and P9 TM assist configurations.
