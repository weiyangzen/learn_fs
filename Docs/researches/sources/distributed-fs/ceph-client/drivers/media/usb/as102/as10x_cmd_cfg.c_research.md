# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd_cfg.c

## Purpose
Implements AS10x firmware context and eLNA configuration commands.

## Important APIs, types, and functions
`as10x_cmd_get_context()` sends `CONTROL_PROC_CONTEXT` with `GET_CONTEXT_DATA` and returns a 32-bit value. `as10x_cmd_set_context()` sends `SET_CONTEXT_DATA` and a 32-bit context value. `as10x_cmd_eLNA_change_mode()` sends `CONTROL_PROC_ELNA_CHANGE_MODE`. `as10x_context_rsp_parse()` handles the context-specific response layout, which differs from the common response union.

## Control flow and state
Each function builds the command header with a new `cmd_xid`, writes the specific request body, transfers through `ops->xfer_cmd`, and validates the response. Callers such as `as102_stream_ctrl()` use set-context to program `CONTEXT_LNA` before turning the receiver on.

## Dependencies and integration points
Depends on shared `as10x_cmd_t` buffers in the bus adapter and USB command transport. Integrated with frontend/stream control paths that configure eLNA behavior.

## Risks and test signals
Risks include using the common response parser for context commands, missing locks around shared buffers, and unvalidated context tags. Test signals include successful eLNA context programming, get-context round trips returning expected values, and no command failures when `elna_enable` is toggled.
