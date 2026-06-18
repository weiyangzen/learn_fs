# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_fused_io.c

## Purpose
`dc_fused_io.c` builds and executes fused write-poll-read I2C or AUX transactions through DMUB. The immediate use is HDCP atomic operations where the driver must write a register, poll for a condition, and then read data as one ordered firmware command sequence.

## Important APIs, Types, And Functions
`op_i2c_convert` converts a `mod_hdcp_atomic_op_i2c` into a `dmub_cmd_fused_request`, filling I2C location fields, DDC line, address, offset, length, and request buffer. `op_aux_convert` does the same for `mod_hdcp_atomic_op_aux`, marking the location as AUX and using AUX address/length fields.

`atomic_write_poll_read` prepares three `union dmub_rb_cmd` entries as `DMUB_CMD__FUSED_IO` requests with `multi_cmd_pending` set on the first two. It sets poll mask and poll timeout on the middle request, computes an overall timeout budget from a fixed 10 ms per request plus poll timeout and extra AUX transaction time, and calls `dm_helpers_execute_fused_io`. It returns success only if execution succeeds and the first request status is `FUSED_REQUEST_STATUS_SUCCESS`.

`dm_atomic_write_poll_read_i2c` and `dm_atomic_write_poll_read_aux` are the exported functions. They validate `link`, derive `ddc_line` from `link->ddc->ddc_pin->pin_data->en`, convert write/poll/read ops, execute the fused sequence, copy the response buffer into the read op, and return the result.

## Control Flow And State
The sequence is deterministic: validate link, convert three operations, set headers and timeout, execute through DMUB, copy read data, return success. State is transient in the stack-allocated command array and in DMUB firmware execution. No persistent driver state is updated here.

## Dependencies And Integration Points
It includes `dc_fused_io.h`, `dm_helpers.h`, and `gpio.h`, and relies on DMUB fused IO command definitions, HDCP atomic op structs from `mod_hdcp.h`, and link DDC/GPIO metadata. It integrates with HDCP authentication over DDC/I2C or DP AUX and with the DM helper execution path.

## Risks
Only `link` is checked before dereferencing `link->ddc`, `ddc_pin`, and `pin_data`, so malformed or partially initialized links can crash. Operation size is bounded by the DMUB request buffer, but `memcpy(read->data, commands[0].fused_io.request.buffer, read->size)` copies from command 0 rather than the read command slot; this is worth auditing because the read result would intuitively reside in `commands[2]`. `atomic_write_poll_read` checks only request 0 status, not poll/read statuses. AUX timeout scaling uses `length / 16`, which gives no extra timeout for 1-15 bytes and may under-budget small AUX reads.

## Test Signals
Unit tests with fake DMUB execution should verify command header fields, multi-command flags, request locations, timeout calculation, buffer copy source, oversized-op rejection, and failure propagation. Integration signals include HDCP 1.x/2.x authentication over native AUX and I2C-over-AUX, plus timeout/error injection in poll and read phases.
