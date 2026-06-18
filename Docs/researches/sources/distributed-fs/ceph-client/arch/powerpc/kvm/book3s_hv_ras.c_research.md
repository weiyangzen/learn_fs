# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_ras.c

## Purpose

`book3s_hv_ras.c` contains real-mode reliability, availability, and serviceability handlers for Book3S HV KVM. It handles guest machine checks and hypervisor maintenance interrupts, especially SLB/TLB recovery on POWER7-era systems and timebase/HMI coordination across split subcores. It also provides POWER9-specific HMI handling for the C P9 entry path.

## Important APIs, Types, And Functions

Important functions are `kvmppc_realmode_machine_check()`, `kvmppc_p9_realmode_hmi_handler()`, `kvmppc_subcore_enter_guest()`, `kvmppc_subcore_exit_guest()`, and `kvmppc_realmode_hmi_handler()`. Local helpers include `reload_slb()`, `kvmppc_realmode_mc_power7()`, `kvmppc_cur_subcore_size()`, `kvmppc_tb_resync_required()`, and `kvmppc_tb_resync_done()`. The file uses `struct machine_check_event`, PACA sibling subcore state, OPAL HMI/timebase hooks, and the vcore timebase offset fields.

## Control Flow

For machine checks, `kvmppc_realmode_machine_check()` either lets FWNMI guests handle recovery or calls `kvmppc_realmode_mc_power7()` to recover known SLB parity/multihit, DERAT multihit, and TLB multihit conditions. It then retrieves the machine-check event with `get_mce_event(MCE_EVENT_RELEASE)`, marks it recovered when appropriate, and stores it in `vcpu->arch.mce_evt` for virtual-mode completion.

`kvmppc_p9_realmode_hmi_handler()` is used by the P9 C entry path. It first unapplies any guest timebase offset so OPAL/debug handling observes host-relative time. It counts the HMI, lets `hmi_handle_debugtrig()` consume debug-trigger HMIs, calls `ppc_md.hmi_exception_early()` when available, and reapplies the guest timebase offset before returning.

The older `kvmppc_realmode_hmi_handler()` coordinates HMI handling across subcores. The primary thread sets a shared resync-required bit, clears its subcore guest state, waits for all sibling subcores to leave guest context, calls OPAL's early HMI handler, has one elected thread perform `opal_resync_timebase()`, and makes all others wait until resync is complete. It clears `tb_offset_applied` so the guest exit path does not subtract an already-resynchronized guest offset.

## State And Persistence Behavior

Persistent outputs are the stored machine check event in `vcpu->arch.mce_evt`, PACA `hmi_irqs`, sibling subcore `in_guest[]` and `flags`, and vcore `tb_offset_applied`. `kvmppc_subcore_enter_guest()` and `_exit_guest()` update shared subcore state that the HMI handler uses to decide when it is safe to resynchronize a whole core. SLB reload uses a pinned guest SLB shadow buffer when present, but only after bounds checks against `pinned_end`.

## Dependencies And Integration Points

This file is called from both `book3s_hv_p9_entry.c` and `book3s_hv_rmhandlers.S` for machine check and HMI exits. It integrates with OPAL (`opal_resync_timebase()`), platform HMI callbacks (`ppc_md.hmi_exception_early`), machine-check event retrieval, PACA sibling subcore state, and KVM's vcore timebase-offset machinery.

## Risks

Timebase resynchronization is the main risk: resync is core-wide, so doing it while a sibling subcore is still in guest context can corrupt guest time. Conversely, failing to clear `tb_offset_applied` can double-subtract offsets. Machine-check recovery must only report recoverable conditions when all remaining status bits are understood. Real-mode execution limits available services, so event queuing is deferred through vcpu state rather than normal host queues.

## Test Signals

Signals include injected machine checks for SLB/TLB multihit and unrecoverable cases, FWNMI guest behavior, HMI debug-trigger handling, OPAL HMI callbacks, split-core/subcore guest runs with concurrent HMI, timebase offset guests, and verifying that `vcpu->arch.mce_evt` reaches virtual-mode handling with the expected disposition.
