# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_mb.h

## Purpose
`csio_mb.h` declares the mailbox module interface and data structures. It defines mailbox sizing/timing, device mastership/ownership/state enums, firmware parameter macros, mailbox/request manager structures, stats, command-builder APIs, response parsers, interrupt controls, issue/completion/timeout/cancel functions, and FCoE-specific mailbox helpers.

## Important APIs, Types, and Constants
- Constants: `CSIO_MB_MAX_REGS`, `CSIO_MAX_MB_SIZE`, `CSIO_MB_POLL_FREQ`, `CSIO_MB_DEFAULT_TMO`, `CSIO_STATS_OFFSET`, and `CSIO_NUM_STATS_PER_MB`.
- `struct fw_fcoe_port_cmd_params` carries port stats read parameters.
- `CSIO_DUMP_MB()` logs mailbox register contents for debugging.
- Enums `csio_dev_master`, `csio_mb_owner`, and `csio_dev_state` model firmware HELLO ownership and state.
- `FW_PARAM_DEV()` and `FW_PARAM_PFVF()` construct firmware parameter mnemonics.
- `CSIO_INIT_MBP()` zeroes and initializes a `struct csio_mb` command with timeout, private pointer, callback, list head, and size.
- `struct csio_mb` stores the firmware-format 64-byte mailbox payload, timeout, completion object, callback, owner private pointer, and list linkage.
- `struct csio_mbm` stores async mailbox number, interrupt index, timer, hardware pointer, request/callback queues, current command, queue count, and stats.
- The declarations cover generic firmware commands, queue allocation/free, FCoE link/VNP/FCF/stats commands, module init/exit, interrupt enable/disable, issue/completion/event/ISR/timeout/cancel.

## Control Flow and State
The header defines the command lifecycle contract: callers initialize a mailbox payload with a helper, then submit it via `csio_mb_issue()`. If `mb_cbfn` is null, completion is synchronous/polled; otherwise completion is interrupt-driven and later delivered through `csio_mb_completions()`. `struct csio_mbm` is embedded in `struct csio_hw`, making mailbox state per hardware function.

## Dependencies and Integration Points
It includes firmware API headers `t4fw_api.h` and `t4fw_api_stor.h`, plus `csio_defs.h`. It forward-declares queue parameter structures from the work-request layer and depends on `struct csio_hw`, `struct csio_lnode`, and `struct fw_fcoe_port_stats` users in implementation files.

## Risks and Edge Cases
- `CSIO_INIT_MBP()` sets `mb_size = sizeof(*cmdp)`; commands that expect full 64-byte transfers must override `mb_size`, as stats reads do.
- `CSIO_DUMP_MB()` performs eight 64-bit MMIO reads and should remain debug-gated.
- The mailbox payload is a raw `__be64[8]`; every command builder must handle endian conversion correctly.
- Async callback ownership of `struct csio_mb` memory is external; callbacks and timeout/cancel paths must agree on who frees or reuses the object.

## Test Signals
Compile tests should ensure all command helper declarations match implementations. Runtime tests should validate synchronous and asynchronous mailbox behavior, correct timeout values, callback invocation, stats counter increments, queue response parsing, FCoE command formatting, and absence of pending `req_q`/`cbfn_q` entries at module exit.
