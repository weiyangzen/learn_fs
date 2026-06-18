# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_kcs_sm.c

Purpose: host-side IPMI KCS state machine used by `ipmi_si` for Keyboard Controller Style system interfaces.

Important APIs, types, and functions: `struct si_sm_data`, `enum kcs_states`, `init_kcs_data()`, `start_kcs_transaction()`, `get_kcs_result()`, `kcs_event()`, `kcs_detect()`, and exported `kcs_smi_handlers`.

Control flow: a transaction starts in `KCS_START_OP`, verifies idle state, sends `KCS_WRITE_START`, writes all bytes with `KCS_WRITE_END` before the final byte, then reads bytes while hardware is in read state until idle completes. `kcs_event()` gates all states on input-buffer-free, separately waits for output-buffer-full during reads, detects attention while idle, and runs a multi-stage abort/error recovery path before retrying or marking `KCS_HOSED`.

State and persistence: state machine holds write/read buffers, positions, original write count for retries, truncation flag, error retry count, IBF/OBF timeouts, and `ERROR0` jiffies deadline. No persistence outside SI lifetime.

Dependencies and integration: `ipmi_si_sm.h` I/O callbacks, IPMI completion codes, jiffies timing, module debug parameter, and upper SI poll/interrupt scheduler.

Risks and test signals: hardware deviations are common, so error recovery and final idle-without-OBF behavior are critical. Tests should cover invalid request lengths, ATN in idle, normal write/read sequence, OBF/IBF timeout, abort recovery retry, hosed reset, truncation, bogus status 0xff detection, and scheduler return values.
