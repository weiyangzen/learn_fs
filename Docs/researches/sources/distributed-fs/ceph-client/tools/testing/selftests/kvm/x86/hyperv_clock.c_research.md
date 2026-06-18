# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_clock.c

Purpose: Tests Hyper-V clocksource emulation, including time reference count MSR, TSC frequency MSR, and the Hyper-V TSC reference page. It verifies that guest-observed Hyper-V time advances consistently with `RDTSC`.

Important APIs/types/functions: `struct ms_hyperv_tsc_page` mirrors the TSC reference page layout; `mul_u64_u64_shr64()` computes scaled TSC values; `check_tsc_msr_rdtsc()` compares `HV_X64_MSR_TIME_REF_COUNT` against TSC; `get_tscpage_ts()` and `check_tsc_msr_tsc_page()` validate the reference page; `guest_main()` and `host_check_tsc_msr_rdtsc()` coordinate guest and host checks.

Control flow: The host enables Hyper-V CPUID/MSRs, allocates a TSC page, and runs guest checks. The guest sets Hyper-V guest OS ID and hypercall/time configuration, reads TSC frequency and time reference values around a delay, and checks the TSC page sequence/scale/offset data. Host-side checks also validate MSR monotonicity where relevant.

State and persistence behavior: State includes Hyper-V synthetic MSRs and the shared TSC reference page. The TSC page fields are KVM-maintained guest memory and valid only while the VM is alive.

Dependencies and integration points: Depends on KVM Hyper-V CPUID support, `hyperv.h` helpers, synthetic MSR emulation, stable TSC frequency reporting, and guest memory mapping for the TSC page.

Risks and maintenance notes: Timing tolerance is necessary because host scheduling and VM exits add noise. The scale calculation duplicates Hyper-V reference-page math, so layout or semantics changes need careful updates.

Test signals: Passing means Hyper-V time reference count, frequency, and TSC page all produce coherent advancing time. Failures identify Hyper-V clock MSR or reference-page regressions.
