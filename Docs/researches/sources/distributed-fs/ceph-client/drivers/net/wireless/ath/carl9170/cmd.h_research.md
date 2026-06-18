# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/cmd.h

## Purpose
`cmd.h` declares carl9170 command helper APIs and defines macro-based batching helpers for synchronous and asynchronous register writes. It is the command access interface used by MAC/PHY/setup code to program firmware-controlled hardware registers.

## Important APIs, types, and macros
Declarations cover register read/write, echo, reboot, MAC reset, powersave, tally, beacon control, and command buffer allocation. Inline helpers include `carl9170_flush_cab()` and `carl9170_rx_filter()`. Synchronous batching uses `carl9170_regwrite_begin`, `carl9170_regwrite`, `carl9170_regwrite_finish`, and `carl9170_regwrite_result`. Async batching uses `carl9170_async_regwrite_begin`, `carl9170_async_regwrite`, `carl9170_async_regwrite_flush`, `carl9170_async_regwrite_finish`, and `carl9170_async_regwrite_result`.

## Control flow and integration
The batching macros open a scoped `do { ... } while (0)` block with hidden locals. They accumulate register/value pairs in `ar->cmd_buf` or an allocated async `struct carl9170_cmd`, flush when the payload reaches `PAYLOAD_MAX / 2` pairs, stop if `IS_ACCEPTING_CMD()` fails, and expose the final error through the result macro. Async flush transfers ownership to `__carl9170_exec_cmd()` and allocates a new buffer when needed.

## State and persistence behavior
Synchronous batching temporarily uses the per-device `ar->cmd_buf` union. Async batching temporarily owns heap command buffers. The persistent effect is the firmware/hardware register state changed by successful write commands. No standalone state is stored in this header.

## Dependencies
The header depends on `carl9170.h`, firmware command IDs and payload layouts, `PAYLOAD_MAX`, `CARL9170_MAX_CMD_PAYLOAD_LEN`, `IS_ACCEPTING_CMD()`, and command execution functions.

## Risks
Macro scope and hidden local names make misuse easy: callers must pair begin/finish/result correctly, cannot safely nest these macros, and must avoid control-flow surprises around labels. Async batching must avoid double-free after ownership transfer; synchronous batching assumes exclusive safe use of `ar->cmd_buf` in the current context. Failing `IS_ACCEPTING_CMD()` can silently skip remaining writes except for the returned error state.

## Test signals
Signals include register programming sequences longer than one payload, async and sync flush boundary tests, teardown-time command rejection, memory leak checks for async allocation/failure paths, and readback of configured MAC/PHY registers after batched writes.
