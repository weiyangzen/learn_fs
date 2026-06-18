# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-linkage.c

Purpose: Nolibc linkage helper that exposes the address of `errno` and verifies constructor execution via a global bitmask.

Important APIs/functions: includes `nolibc-test-linkage.h` and `<errno.h>`. `linkage_test_errno_addr()` returns `&errno`, allowing tests to compare errno storage linkage. Global `linkage_test_constructor_test_value` starts at 0. Two `__attribute__((constructor))` functions set bit 0 and bit 1.

Control flow: constructors run before `main()` of the final test binary, mutating the global. The exported function is called by other test code to inspect errno address behavior.

State and persistence: one process-global integer bitmask; no persistent files.

Dependencies and integration: compiled into nolibc/libc test binaries with the companion header. Behavior differs meaningfully under nolibc vs libc and helps catch startup/linkage regressions.

Risks: constructor support can vary by architecture/link mode, especially with `-nostdlib -static`; that is exactly what the test aims to detect. The file itself does not assert; consumers must check the global/function.

Test signals: successful link plus downstream checks that both constructor bits are set and errno address semantics are correct.
