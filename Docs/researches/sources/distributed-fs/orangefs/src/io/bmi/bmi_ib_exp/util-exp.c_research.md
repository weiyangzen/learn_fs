# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/util-exp.c

## Purpose
Provides small utility routines shared by the experimental BMI InfiniBand implementation: logging wrappers, checked allocation, quicklist head removal, state-name formatting, buffer-list copying, and full-length TCP read/write helpers.

## Important APIs, Types, And Functions
Logging functions are `error`, `error_errno`, `error_xerrno`, `warning`, `warning_errno`, and `warning_xerrno`. Other helpers are `bmi_ib_malloc`, `qlist_del_head`, `qlist_try_del_head`, `sq_state_name`, `rq_state_name`, `msg_type_name`, `memcpy_to_buflist`, `memcpy_from_buflist`, `read_full`, and `write_full`. Defining `__util_exp_c` before including `ib-exp.h` materializes the state/message name tables consumed by `name_lookup`.

## Control Flow
Logging wrappers format into fixed local buffers and write to the OrangeFS gossip error stream. `error()` additionally emits a backtrace but does not exit. `bmi_ib_malloc` rejects zero-byte requests and logs allocation failure. The quicklist helpers remove the first list entry, either strictly or with an empty-list NULL return. The copy helpers walk `ib_buflist_t` scatter/gather arrays to copy eager payloads into or out of contiguous eager buffers. `read_full` and `write_full` loop until EOF/error or the requested byte count is transferred for TCP handshake records.

## State And Persistence
No persistent state is owned here beyond the static name arrays compiled from `ib-exp.h`. The routines operate on caller-provided lists, buflists, file descriptors, and buffers.

## Dependencies And Integration Points
This file depends on standard C/POSIX headers, OrangeFS gossip logging via `ib-exp.h`, and `pvfs2-internal.h` formatting helpers. It supports all generic and provider-specific files, particularly TCP connection exchange and debug logging of state-machine transitions.

## Risks And Test Signals
The logging routines use `vsprintf` into 2048-byte buffers, so long formatted messages can overflow. `error()` and related functions have `exit(1)` commented out, which changes many caller assumptions from fatal to log-and-continue. `read_full` and `write_full` do not retry `EINTR`, so signal interruption can fail handshakes. State-name lookup only matches exact enum values, not combined receive bitmasks. Test signals include compiler format warnings, long-message handling, interrupted TCP read/write simulations, buflist copy bounds checks, and debug output for combined receive states.
