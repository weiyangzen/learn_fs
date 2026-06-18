# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_pr_papr.c

Purpose: this file implements PAPR hypercall handling for PR KVM Book3S guests, especially HPT manipulation hcalls that operate on the guest/userspace hash page table.

Important APIs: `kvmppc_h_pr()` dispatches hcalls. `kvmppc_hcall_impl_pr()` reports implemented hcalls, and `kvmppc_pr_init_default_hcalls()` enables the historical default set. HPT helpers include `kvmppc_h_pr_enter()`, `remove()`, `bulk_remove()`, and `protect()`. Other handlers wrap logical CI load/store, `H_SET_MODE`, TCE calls when configured, XICS hcalls, `H_CEDE`, and `H_RTAS`.

Control flow: HPT hcalls compute the target PTEG address from SDR1, lock `kvm->arch.hpt_mutex`, copy HPTEs from userspace HPT memory, validate flags/AVPN/slot state, update or clear entries with `copy_to_user()`, and call the vCPU MMU `tlbie()` hook when mappings change. `kvmppc_h_pr()` first checks the enabled-hcall bitmap, then handles in-kernel operations or falls back to `EMULATE_FAIL` so userspace can process unsupported calls.

State and persistence: persistent state includes the userspace HPT contents, SDR1, enabled hcall bits, vCPU GPR return values, and guest-visible HPTE referenced/change bits returned by removal operations. The file does not own the HPT memory; it synchronizes access with `hpt_mutex`.

Dependencies and integration: it depends on user accessors, PAPR hcall constants, `compute_tlbie_rb()`, PR MMU callbacks, optional SPAPR TCE IOMMU helpers, XICS, and RTAS. It is invoked from syscall exit handling in `book3s_pr.c` for `sc 1` PAPR hypercalls.

Risks: user memory copies can fail and return `H_FUNCTION`. HPT locking must cover read-modify-write plus TLB invalidation. Bulk remove encodes per-request status in guest registers and must not mix incompatible flags. The default hcall enable list intentionally excludes `H_RTAS`; changing that affects userspace ABI.

Test signals: PAPR guests under PR KVM, H_ENTER exact and non-exact insertion, remove/protect/bulk-remove with AVPN and ANDCOND flags, user HPT fault injection, TCE enabled/disabled builds, XICS hcalls, RTAS token presence/absence, and `H_CEDE` halt/wakeup behavior.
