# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-linkage.h

Purpose: Header declaring linkage-test symbols shared between nolibc test sources.

Important APIs/types/functions: include guard `_NOLIBC_TEST_LINKAGE_H`; declares `void *linkage_test_errno_addr(void);` and `extern int linkage_test_constructor_test_value;`.

Control flow: none; declarations are consumed by test code and implemented in `nolibc-test-linkage.c`.

State and persistence: exposes one external process-global integer owned by the C file.

Dependencies and integration: used by nolibc/libc test binaries to test errno linkage and constructor execution.

Risks: minimal. Any signature mismatch with the C implementation would be caught at compile/link time.

Test signals: successful compilation and downstream checks using the declared symbols.
