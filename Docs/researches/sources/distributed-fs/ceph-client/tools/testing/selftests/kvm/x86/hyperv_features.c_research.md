# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_features.c

Purpose: Exhaustively tests Hyper-V feature gating for synthetic MSRs and hypercalls. It checks that accesses succeed only when the relevant Hyper-V CPUID feature is exposed and fail with the expected guest exception or hypercall status when absent.

Important APIs/types/functions: `struct msr_data` and `struct hcall_data` describe target MSRs/hypercalls and expected access properties; `is_write_only_msr()`, `guest_msr()`, `guest_hcall()`, `vcpu_reset_hv_cpuid()`, `guest_test_msrs_access()`, and `guest_test_hcalls_access()` implement the matrix. The file uses many Hyper-V constants, `HV_X64_MSR_*`, `HVCALL_*`, VP assist/hypercall pages, and CPUID feature toggling.

Control flow: The host creates vCPUs with selected Hyper-V CPUID feature sets and syncs test descriptors into guest memory. Guest code attempts reads/writes of Hyper-V MSRs or hypercalls, records fault vectors/statuses, and asserts access matches the exposed feature bits. The host resets Hyper-V CPUID between cases to isolate features.

State and persistence behavior: Synthetic MSR state, hypercall page state, and guest CPUID state are vCPU-local. Test data is shared through guest memory. No external persistence exists.

Dependencies and integration points: Depends on KVM Hyper-V CPUID/MSR/hypercall emulation, exception injection, and the selftest Hyper-V helper layer. It overlaps with but is broader than positive functional tests such as `hyperv_extended_hypercalls.c`.

Risks and maintenance notes: The feature matrix must track TLFS and KVM feature definitions closely. Write-only MSR exceptions and unsupported hypercall statuses are easy to regress. Adding a Hyper-V feature should be reflected here to avoid silent coverage gaps.

Test signals: Passing means KVM enforces Hyper-V feature dependencies for MSRs and hypercalls, including negative paths. Failures point to overexposed features, missing access checks, or incorrect fault/status reporting.
