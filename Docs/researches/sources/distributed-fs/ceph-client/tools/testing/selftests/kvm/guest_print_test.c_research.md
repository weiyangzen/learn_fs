<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_print_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_print_test.c

Purpose: this test validates KVM selftest guest-side formatted output and assertion formatting through `GUEST_PRINTF()` and `__GUEST_ASSERT()`/`GUEST_ASSERT_FMT`-style ucalls for supported integer, character, string, and pointer formats.

Important APIs, types, and functions: `struct guest_vals` carries two arguments and an enum type to guest code. `TYPE_LIST` drives generation of expected printf/assert format strings and host helper functions for signed/unsigned 64-bit, hex, 32-bit, int, char, string, and pointer types. `guest_code()` emits a formatted printf then an assertion comparing `vals.a` and `vals.b`. `run_test()` handles `UCALL_PRINTF`, intentional `UCALL_ABORT`, and `UCALL_DONE`. `test_limits()` runs `guest_code_limits()` to ensure overlong printf buffers abort.

Control flow: `main()` creates one VM/vCPU and runs generated helpers with equal and unequal values for every format. Equal values produce printf then done; unequal values produce printf then an abort whose trailing assertion message is compared with the expected string. After freeing the main VM, `test_limits()` verifies that a string longer than `UCALL_BUFFER_LEN` triggers `UCALL_ABORT`.

State, persistence, and dependencies: state is the synced global `vals` and transient ucall buffers. Dependencies include selftest ucall common infrastructure, guest printf/assert macros, KVM run-page exit reason mapping, and format compatibility between guest and host snprintf.

Risks and edge cases: floats/doubles are deliberately unsupported. Assertion ucalls include extra metadata before the message, so the test compares the expected assertion as a suffix. Pointer and string values are cast through `u64`, which is suitable for the selftest ABI but should not be generalized beyond it.

Test signals: exact string equality for `UCALL_PRINTF`, suffix equality for `UCALL_ABORT`, `UCALL_DONE` after each case, and expected abort for overlong output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_print_test.c -->
