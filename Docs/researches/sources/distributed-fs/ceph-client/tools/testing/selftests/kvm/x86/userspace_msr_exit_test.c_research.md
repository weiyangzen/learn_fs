<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/userspace_msr_exit_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/userspace_msr_exit_test.c

## Purpose
This test validates userspace MSR exits and MSR filtering. It covers allow-list filtering, default-deny filtering, unknown MSR exits, filter permission-bitmap updates, forced-emulation-prefix paths, and ioctl flag validation.

## Important APIs, Types, and Functions
Key data structures are `struct kvm_msr_filter` instances `filter_allow`, `filter_deny`, `filter_fs`, `filter_gs`, and `no_filter_deny`. Important functions include `test_rdmsr()`, `test_wrmsr()`, `test_em_rdmsr()`, `test_em_wrmsr()`, `guest_code_filter_allow()`, `guest_code_filter_deny()`, `guest_code_permission_bitmap()`, `process_rdmsr()`, `process_wrmsr()`, `handle_rdmsr()`, `handle_wrmsr()`, `run_user_space_msr_flag_test()`, and `run_msr_filter_flag_test()`. It uses `KVM_CAP_X86_USER_SPACE_MSR`, `KVM_CAP_X86_MSR_FILTER`, `KVM_EXIT_X86_RDMSR`, `KVM_EXIT_X86_WRMSR`, and MSR exit reason flags.

## Control Flow, State, and Persistence
The allow-filter test traps known, semi-known, and fabricated MSRs, lets userspace return data or errors, and verifies guest #GP handling for rejected accesses; it repeats through forced emulator paths when enabled. The deny-filter test defaults to trapping, allows specific ranges through bitmaps, disables filtering mid-test through a ucall, and counts userspace reads/writes. The permission-bitmap test alternates FS/GS base traps and verifies KVM updates interception. Flag tests iterate all bits in enable-cap and filter flags expecting success only for valid masks. State is per-VM MSR filter configuration, user-maintained fake MSR data, guest exception counters, and run-page MSR exit fields.

## Dependencies and Integration Points
It integrates with KVM MSR filtering, userspace MSR exit reasons (`FILTER`, `UNKNOWN`, `INVAL`), in-kernel MSR emulation, forced emulation prefix support, GP handler RIP fixups, and the one-vCPU harness.

## Risks and Test Signals
Risks include wrong exit reason, stale permission bitmap after filter changes, accepting invalid flag bits, failing to inject #GP from `run->msr.error`, or mishandling fabricated MSRs. Signals are expected exit sequence, exact read/write counters, guest assertions on returned values, and ioctl `EINVAL` for invalid flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/userspace_msr_exit_test.c -->
