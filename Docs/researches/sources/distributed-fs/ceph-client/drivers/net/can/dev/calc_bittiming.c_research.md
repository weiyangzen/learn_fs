# sources/distributed-fs/ceph-client/drivers/net/can/dev/calc_bittiming.c

Purpose: calculates CAN nominal, FD data, and XL data timing parameters from requested bitrate/sample-point constraints.

Important APIs and functions: `can_calc_bittiming()` searches valid TSEG/BRP combinations, chooses the lowest bitrate and sample-point error under `CAN_CALC_MAX_ERROR`, sets prop/phase segments, TQ, SJW, BRP, sample point, and actual bitrate. `can_calc_tdco()` derives automatic transmitter delay compensation offset when data BRP is 1 or 2. `can_calc_pwm()` derives CAN XL PWM short/long symbol settings that divide the XL data bit time.

Control flow and state: the main loop iterates doubled TSEG values to account for rounding, clamps sample-point splits with `can_update_sample_point()`, and emits extack diagnostics for bitrate error. The function mutates the caller-provided timing structures and may set TDC control-mode flags. Dependencies include controller timing constants, `struct can_priv` clock, CAN XL/PWM helpers, and `can_sjw_check()`. Risks are edge-case arithmetic around high bitrates, sample-point preference changes, TDC enablement assumptions, and integer division rounding. Test signals include requested versus realized bitrate/sample point, extack error percentages above 5%, TDC auto activation, and PWM divisibility validation for CAN XL TMS.
