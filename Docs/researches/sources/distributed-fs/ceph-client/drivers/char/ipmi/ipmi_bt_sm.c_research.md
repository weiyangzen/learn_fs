# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_bt_sm.c

Purpose: host-side IPMI BT state machine used by `ipmi_si` to send one request at a time over a BT system interface.

Important APIs, types, and functions: `struct si_sm_data`, `enum bt_states`, `bt_init_data()`, `bt_start_transaction()`, `bt_get_result()`, `bt_event()`, `bt_detect()`, and exported `bt_smi_handlers`.

Control flow: transactions frame request bytes with BT length and sequence, then `bt_event()` advances through write start, write bytes, wait for BMC consume, wait for response attention, clear B2H, read bytes, and complete. It drains stale responses before new writes, reports SMS attention while idle, retries timeouts based on BT capabilities, can issue a soft reset during early failures, and enters `LONG_BUSY` if BMC remains busy.

State and persistence: state machine holds sequence number, write/read buffers, timeout, retry count, truncation flag, detected capabilities, and completion diversion state. No persistence beyond SI device lifetime.

Dependencies and integration: depends on `ipmi_si_sm.h` I/O callbacks, IPMI completion codes, module debug parameter, and upper SI scheduler calling `event()` with elapsed microseconds.

Risks and test signals: static debug helpers are not multi-open safe; timeout/retry behavior depends on detected capabilities and state timing. Tests should cover capability detection fallback, stale response draining, sequence mismatch, truncation, busy timeout, reset path, SMS_ATN, and all `si_sm_result` transitions.
