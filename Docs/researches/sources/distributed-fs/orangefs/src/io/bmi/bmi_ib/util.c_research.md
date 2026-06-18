# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/util.c

## Purpose
`util.c` provides shared support routines for the BMI InfiniBand implementation: logging wrappers, allocation checks, quicklist helpers, debug name lookups, buflist copy helpers, and full-length socket read/write loops used during TCP bootstrap handshakes.

## Important APIs, Types, and Functions
Logging helpers are `error`, `error_errno`, `error_xerrno`, `warning`, `warning_errno`, and `warning_xerrno`. Allocation and list helpers are `bmi_ib_malloc`, `qlist_del_head`, and `qlist_try_del_head`. Debug lookup helpers are `sq_state_name`, `rq_state_name`, and `msg_type_name`, backed by arrays materialized from `ib.h` when `__util_c` is defined. Data movement helpers are `memcpy_to_buflist` and `memcpy_from_buflist`. Socket helpers are `read_full` and `write_full`.

## Control Flow
The logging functions format messages into a fixed stack buffer and send them to the gossip logging system; `error` also emits a backtrace but does not exit. `bmi_ib_malloc` rejects zero-byte allocations and logs allocation failures. The qlist helpers remove the first list item, either logging on empty (`qlist_del_head`) or returning null (`qlist_try_del_head`).

`memcpy_to_buflist` copies a bounded contiguous source into a receive buflist, stopping when the requested length has been copied. `memcpy_from_buflist` flattens all send buflist entries into a contiguous destination. `read_full` and `write_full` loop until the requested byte count is consumed, an error occurs, or read returns EOF.

## State and Persistence Behavior
The file maintains no persistent state of its own. It reads static name arrays emitted through `ib.h` and operates on caller-owned buffers, lists, and file descriptors.

## Dependencies and Integration Points
`ib.c`, `openib.c`, `vapi.c`, and `mem.c` all rely on these helpers. The socket full-read/full-write routines are part of the TCP exchange protocol used by both provider backends to trade QP connection data. The debug name functions are used throughout queue state logging.

## Risks and Edge Cases
The logging functions use `vsprintf` into 2048-byte buffers, so long formatted messages can overflow. `error()` no longer exits, which makes it important that callers return or otherwise recover after invariant failures. `read_full` and `write_full` do not retry on `EINTR` internally; callers must handle negative returns if interruption matters. `write_full` stores `num` in an `int total`, which can truncate very large sizes, though current handshake writes are small.

## Test Signals
Unit tests can validate state/message name mapping, list removal on empty and non-empty lists, buflist copy behavior with partial final buffers, and full read/write behavior over pipes or socketpairs including EOF and interrupted system calls. Static analysis should flag unbounded formatting.
