# sources/distributed-fs/ceph-client/tools/testing/radix-tree/idr-test.c

## Purpose
`idr-test.c` exercises the IDR and IDA APIs in the user-space radix-tree harness, including cyclic allocation, NULL entries, preload/no-wait behavior, 32-bit ID boundaries, iteration alignment, RCU lookup races, memory-allocation failure paths, and threaded IDA stress.

## Important APIs, Types, And Functions
Major IDR functions include `idr_alloc_test()`, `idr_alloc2_test()`, `idr_replace_test()`, `idr_null_test()`, `idr_nowait_test()`, `idr_get_next_test()`, `idr_u32_test()`, `idr_align_test()`, `idr_find_test()`, and `idr_checks()`. IDA functions include `ida_check_nomem()`, `ida_check_conv_user()`, `ida_check_random()`, `ida_alloc_free_test()`, `user_ida_checks()`, `ida_thread_tests()`, and `ida_tests()`. The file includes `../../../lib/test_ida.c` after defining module stubs.

## Control Flow
`idr_checks()` runs a broad deterministic sequence: fill/remove/destroy cycles, boundary allocations near `INT_MAX`, cyclic wraparound, base-offset tests, NULL replacement, preload tests, u32 handle tests, alignment iteration, and RCU find-race tests. IDA tests simulate no-memory paths with `GFP_NOWAIT`, conversion between exceptional entries and bitmaps, random allocate/free loops, and multithreaded random/leak tests. A weak `main()` runs this file standalone when not linked into the full harness.

## State And Persistence
Most state is local IDR/IDA instances. `DEFINE_IDR(find_idr)` is global for the concurrent find test. Threads register with the user-space RCU harness and clean up after time-bounded loops. No durable state is persisted.

## Dependencies And Integration Points
The file depends on Linux IDR/IDA APIs, XArray value encoding, local `struct item` helpers, pthreads, RCU user-space shims, and the kernel `test_ida.c` source. It is called from `main.c` as part of full radix-tree testing and can run as `idr-test`.

## Risks
Several tests are time-bound and randomized, so failures can be seed or scheduling sensitive. The `idr_u32_test()` path intentionally exercises IDs above `INT_MAX`, where `idr_get_next()` cannot represent them and warnings are expected. The included `test_ida.c` means upstream changes in that file directly affect this test.

## Test Signals
Signals are assertion/BUG_ON absence, no leftover allocations after RCU barriers, and successful thread joins. Printed warnings around large u32 IDs are expected and bracketed by messages.
