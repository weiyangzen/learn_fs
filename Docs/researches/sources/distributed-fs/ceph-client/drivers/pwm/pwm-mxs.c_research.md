<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mxs.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-mxs.c

Purpose: drives Freescale MXS PWM hardware with per-channel active/period registers and a small clock divider table.

Important APIs/types/functions: `struct mxs_pwm_chip` stores MMIO base and clock. `mxs_pwm_apply()` computes period count, duty count, divider selection from `cdiv_shift[]`, active/inactive polarity bits, and enable control. Probe reads the `fsl,pwm-number` property and registers that many channels.

Control flow: probe maps registers, gets/enables the clock, determines channel count, and registers the PWM chip. Apply rejects periods that cannot fit the divider/count encoding, writes active count and period/polarity/divider fields, then sets or clears the channel enable bit through SET/CLR aliases.

State and persistence: hardware registers hold all state; the driver keeps no channel cache. Clock is enabled for the lifetime of the device after probe. No get-state or PM callbacks are present.

Dependencies and integration: depends on OF/platform, clk, MMIO set/clear aliases, device property `fsl,pwm-number`, and PWM core.

Risks and test signals: channel count comes from firmware data, so bad DT can expose nonexistent channels. Test divider selection boundaries, normal/inverse polarity bits, enable set/clear aliases, requested period beyond 16-bit range, and clock disable cleanup on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mxs.c -->
