# sources/distributed-fs/lustre-release/lnet/selftest/framework.c

## Purpose
Implements the LNet Selftest framework layer: remote session handling, framework SRPC service dispatch, stats/debug, batch control, test instance creation, client test loops, test service registration, and endian/body unpacking.

## Important APIs And Functions
Exports `LST_INVALID_SID`, `sfw_make_session()`, `sfw_create_rpc()`, `sfw_create_test_rpc()`, `sfw_post_rpc()`, `sfw_abort_rpc()`, `sfw_alloc_pages()`, `sfw_unpack_message()`, `sfw_startup()`, and `sfw_shutdown()`. Internal handlers include `sfw_remove_session()`, `sfw_get_stats()`, `sfw_debug_session()`, `sfw_add_test()`, `sfw_control_batch()`, `sfw_handle_server_rpc()`, and `sfw_bulk_ready()`.

## Control Flow
Startup registers BRW and ping test cases/services, then framework services for debug, stats, make/remove session, batch, and test. Framework RPC handling removes the session timer, validates features, dispatches by service id, writes reply feature bits, restores the timer, and clears the active RPC. Test add validates request geometry and service ids; client-side test add waits for bulk destinations and creates one test unit per destination/concurrency. Batch run schedules client test units on CPT-affine workqueues; completions reschedule loops or mark units, instances, and batches complete.

## State And Persistence
Volatile framework state lives in `sfw_data`: active session, zombie sessions/RPCs, test registry, active server RPC, and shutdown flag. Sessions have timers, refs, counters, batches, and error counts. Test instances own free/active RPC lists.

## Dependencies And Integration Points
Depends on SRPC transport, selftest timers, module-created workqueues, ping/BRW test modules, LNet counters/NID helpers, and packed request/reply structs from `rpc.h`.

## Risks
Timer expiry races can drop framework RPCs with `-EAGAIN`. Zombie cleanup depends on active batch counters. Feature compatibility with old peers is subtle. Buffer reservation recovery relies on lazy portals. Body unpacking must stay synchronized with wire structs.

## Test Signals
Exercise session timeout, force session replacement, stats counters, ping/BRW add paths, forced/non-forced stop, feature mismatch, endian-swapped messages, and clean shutdown without zombie state.
