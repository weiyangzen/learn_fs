# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/debug-exceptions.c

Purpose: this arm64 KVM selftest validates guest debug exception behavior and userspace single-step debug control, covering software breakpoints, hardware breakpoints, watchpoints, single step, OS lock effects, context-linked breakpoints/watchpoints, and KVM_EXIT_DEBUG sequencing.

Important APIs and functions: debug-register writer macros generate `write_dbgbcr()`, `write_dbgbvr()`, `write_dbgwcr()`, and `write_dbgwvr()`. Guest helpers include `reset_debug_state()`, `enable_os_lock()`, `enable_monitor_debug_exceptions()`, `install_wp()`, `install_hw_bp()`, `install_wp_ctx()`, `install_hw_bp_ctx()`, `install_ss()`, `guest_code()`, and `guest_code_ss()`. Exception handlers record PCs/FAR and advance as needed. Host functions include `test_guest_debug_exceptions()`, `test_single_step_from_userspace()`, and `test_guest_debug_exceptions_all()`.

Control flow: `main()` reads `ID_AA64DFR0_EL1`, requires debug architecture >= v8, parses single-step iteration count, runs the guest exception suite across all supported breakpoint/watchpoint/context breakpoint combinations, then runs userspace-driven single-step tests. The userspace single-step loop enables `KVM_GUESTDBG_SINGLESTEP` after a bare ucall and checks sequential PC values until `iter_ss_end`.

State and persistence: guest globals record observed PCs/data addresses and single-step indices. Host `struct kvm_guest_debug` toggles debug control. No persistent state is stored.

Dependencies and integration points: depends on arm64 debug sysregs, KVM guest debug UAPI, descriptor-table exception handlers, ID register feature fields, and libkvm ucall handling.

Risks: guest ucall internals can use exclusive access instructions, so the single-step test uses a bare `GUEST_UCALL_NONE()` to avoid forward-progress issues. Hardware debug resource counts vary; the test dynamically iterates but requires at least two breakpoints. OS lock behavior is nuanced and architecture-dependent.

Test signals: assertions compare captured PCs/FAR against labeled assembly symbols, verify OS lock blocks only expected debug sources, and check userspace `KVM_EXIT_DEBUG` PC progression. Unexpected ucall or debug exit is a failure.
