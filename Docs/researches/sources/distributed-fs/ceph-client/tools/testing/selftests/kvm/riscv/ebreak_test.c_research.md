<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/ebreak_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/ebreak_test.c

## Purpose
`riscv/ebreak_test.c` verifies RISC-V KVM guest-debug handling for software breakpoints. It checks that `ebreak` exits to userspace while guest debug is enabled and is handled inside the guest after debug controls are disabled.

## Important APIs, Types, and Functions
Key elements are `guest_code()`, `guest_breakpoint_handler()`, and `main()`. The test labels two non-compressed `ebreak` instructions as `sw_bp_1` and `sw_bp_2`, stores the handled breakpoint address in `sw_bp_addr`, and uses `struct kvm_guest_debug`.

## Control Flow
Host setup requires `KVM_CAP_SET_GUEST_DEBUG`, creates one vCPU, initializes vector tables, installs an exception handler for `EXC_BREAKPOINT`, enables guest debug, and runs until `KVM_EXIT_DEBUG`. It verifies the PC equals `sw_bp_1`, advances PC by 4 to skip it, disables debug controls, and resumes. The second `ebreak` is then handled by the guest exception handler, which records EPC and advances it by 4. Guest code asserts that the handled address is `sw_bp_2` and reports done.

## State and Persistence
State is limited to guest global `sw_bp_addr`, host guest-debug control state, and the vCPU PC. No state persists after VM cleanup.

## Dependencies and Integration Points
The file depends on RISC-V KVM register access, vector table setup, exception installation, `ucall_common.h`, and the guest debug capability. It integrates with KVM's `KVM_SET_GUEST_DEBUG` and `KVM_EXIT_DEBUG` ABI.

## Risks and Test Signals
Risks include compressed instruction encoding changing breakpoint length, not advancing PC correctly, debug controls leaking after disable, and exception handler registration failure. Test signals are `KVM_EXIT_DEBUG` at `sw_bp_1`, final guest assertion that `sw_bp_2` was handled internally, and `UCALL_DONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/ebreak_test.c -->
