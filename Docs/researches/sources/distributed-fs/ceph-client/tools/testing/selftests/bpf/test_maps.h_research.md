# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_maps.h

## Research

This small header shares retry helper declarations for map tests. It defines `retry_for_error_fn`, a predicate callback type used to decide whether a failed map operation should be retried, and declares `map_update_retriable()`.

The implementation in `test_maps.c` retries `bpf_map_update_elem()` with exponential backoff while the callback says the current `errno` is transient. This supports concurrent and `BPF_F_NO_PREALLOC` stress tests, where `EAGAIN`, `EBUSY`, `ENOMEM`, or `E2BIG` can be recoverable under contention or allocation pressure.

The header has no state, persistence, or control flow. It integrates with additional generated map tests under `map_tests/` that need the same retry behavior without duplicating the implementation. Dependencies are standard C types and the including test source providing the implementation.

Risks are signature drift between declaration and implementation or misuse with callbacks that retry permanent failures indefinitely if attempts are too high. Test signals are successful compilation of included map tests and stable parallel map update behavior under contention.
