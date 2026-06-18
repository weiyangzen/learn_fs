# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/strlen.c

Purpose: test and micro-benchmark harness for `test_strlen()` implementations over many offsets and NUL positions.

Important APIs/types/functions: `test_one()` compares libc `strlen()` with `test_strlen()` at every offset; `bench_test()` prints timing; `testcase()` creates randomized nonzero buffers and inserts NUL terminators.

Control flow: it first grows a string one byte at a time with nonzero random characters, validating after each write. It then performs randomized iterations where the final several bytes are set to zero in turn. Finally it runs timing loops for several string lengths.

State and persistence behavior: a single aligned heap buffer holds mutable test data. No external state is changed.

Dependencies and integration points: links either `string.c` or `strlen_32.S` as the `test_strlen` provider and uses kselftest harness.

Risks and test signals: mismatches are printed but `test_one()` does not abort or return failure on mismatch, so this file has weaker failure enforcement than `memcmp.c`. Build/runtime harness failure is otherwise the main signal.
