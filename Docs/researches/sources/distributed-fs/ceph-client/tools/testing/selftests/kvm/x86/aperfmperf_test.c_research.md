# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/aperfmperf_test.c

Purpose: Tests `KVM_X86_DISABLE_EXITS_APERFMPERF`, i.e. KVM's ability to stop intercepting guest reads of `MSR_IA32_APERF` and `MSR_IA32_MPERF` so the guest observes host counter values. It also verifies the default negative behavior: without the capability, guest `RDMSR` of APERF/MPERF injects `#GP`.

Important APIs/types/functions: Host helpers `open_dev_msr()` and `read_dev_msr()` read `/dev/cpu/<cpu>/msr`; guest helpers `guest_read_aperf_mperf()`, `guest_no_aperfmperf()`, `l1_svm_code()`, `l1_vmx_code()`, and `l2_guest_code()` exercise L1 and optional L2 reads. The test uses `KVM_CAP_X86_DISABLE_EXITS`, `KVM_X86_DISABLE_EXITS_APERFMPERF`, `vcpu_alloc_svm()`, `vcpu_alloc_vmx()`, VMX MSR bitmaps, and SVM/VMX nested helpers.

Control flow: `main()` first creates a normal one-vCPU VM and proves APERF/MPERF reads fault. It then pins the host thread, opens the matching host MSR device, creates a VM before adding vCPUs so `KVM_ENABLE_CAP` is legal, enables APERF/MPERF exit disablement, and runs guest code. The guest repeatedly syncs APERF/MPERF values to userspace, then launches nested L2 when SVM or VMX is available. The host brackets each guest value with host MSR reads and asserts `host_before < guest_value < host_after` for both counters.

State and persistence behavior: No persistent storage is used. State consists of the host CPU pinning, the open MSR file descriptor, APERF/MPERF monotonic counter snapshots, and optional nested control pages. Nested setup persists only for the lifetime of the VM.

Dependencies and integration points: Depends on readable `/dev/cpu/*/msr`, x86 APERF/MPERF support, KVM disable-exit capability reporting, selftest ucall plumbing, and nested VMX/SVM helpers. It reaches into host CPU MSRs, so permissions and CPU migration are critical integration points.

Risks and maintenance notes: The strict monotonic bracketing can be sensitive to scheduling, counter behavior, permissions, or systems where APERF/MPERF are unavailable or virtualized differently. The test intentionally requires nonstandard VM construction order because `KVM_ENABLE_CAP` must occur before vCPU creation. Nested VMX relies on explicitly enabling MSR bitmaps because Intel normally requires MSR exiting.

Test signals: Passing means APERF/MPERF are hidden by default, the disable-exits capability exposes live host counter reads to L1 and L2, and nested MSR interception configuration does not break the passthrough behavior. Failures identify capability gating, MSR permission, counter monotonicity, or nested MSR-bitmap regressions.
