# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_buslock_test.c

Purpose: Tests `KVM_CAP_X86_BUS_LOCK_EXIT` by deliberately generating split-cacheline atomic operations in L1 and optional L2 and verifying KVM exits to userspace on each bus lock.

Important APIs/types/functions: A cacheline-aligned `buffer` and misaligned `atomic_t *val` create bus locks; `guest_generate_buslocks()` performs `NR_BUS_LOCKS_PER_LEVEL` atomic increments; `l1_svm_code()`, `l1_vmx_code()`, and `l2_guest_code()` extend coverage to nested guests; `main()` enables `KVM_BUS_LOCK_DETECTION_EXIT`.

Control flow: The host enables bus-lock exits before adding the vCPU, allocates nested data if SVM or VMX is available, and runs until `UCALL_DONE`. Non-ucall exits must be `KVM_EXIT_X86_BUS_LOCK`. For each bus-lock exit, the host syncs `val` from guest memory and verifies the counter has advanced according to Intel trap-like or AMD fault-like semantics.

State and persistence behavior: `val` is guest global memory shared back to the host for verification. Nested control pages persist for the VM lifetime only.

Dependencies and integration points: Depends on KVM bus-lock detection, host CPU vendor semantics, Linux atomic helpers, and nested VMX/SVM setup.

Risks and maintenance notes: Bus-lock exit timing differs by vendor, and the test explicitly accounts for that. Hardware or kernel changes in bus-lock detection policy can alter expected exit counts.

Test signals: Passing means KVM exits for every generated bus lock in L1 and L2 without skipping or double-executing the instruction. Failures indicate detection, nested propagation, or vendor semantic regressions.
