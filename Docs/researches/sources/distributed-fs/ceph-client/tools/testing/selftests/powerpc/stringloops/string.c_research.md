# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/string.c

Purpose: simple C reference-style `test_strlen()` implementation copied from Linux `lib/string.c` for the `strlen` selftest target.

Important APIs/types/functions: defines `size_t test_strlen(const char *s)`.

Control flow: increments a pointer until the first NUL byte and returns the distance from the original pointer.

State and persistence behavior: stateless and read-only over caller memory.

Dependencies and integration points: linked into the default `strlen` target when not testing the 32-bit assembly implementation.

Risks and test signals: this simple implementation is effectively the baseline, so the surrounding `strlen.c` benchmark mostly validates harness behavior for this target.
