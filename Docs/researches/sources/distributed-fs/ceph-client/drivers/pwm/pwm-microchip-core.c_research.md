<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-microchip-core.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-microchip-core.c

Purpose: implements the Microchip FPGA corePWM block, with a shared prescale/period and per-channel positive/negative edge registers for up to sixteen PWM outputs.

Important APIs/types/functions: `struct mchp_core_pwm_chip` stores MMIO base, clock, mutex, channel count, and shared period parameters. `mchp_core_pwm_calc_period()`, `mchp_core_pwm_calc_duty()`, `mchp_core_pwm_apply_duty()`, `mchp_core_pwm_apply_locked()`, `mchp_core_pwm_get_state()`, and `mchp_core_pwm_wait_for_sync_update()` handle rounding and hardware programming.

Control flow: probe maps registers, gets the clock, reads or configures channel count from OF match data, initializes the mutex, and registers the PWM chip. Apply locks the shared state, computes feasible shared prescale/period steps, rejects period changes that conflict with active users, writes shared registers and per-channel edge registers, requests synchronous update, waits for sync completion, and toggles channel enable. Get-state decodes shared period and channel edges.

State and persistence: shared period/prescale are hardware-global and mirrored in driver state for conflict checking. Per-channel duty/enable are in MMIO registers. No persistent state exists outside hardware; no explicit suspend/resume code is present.

Dependencies and integration: depends on platform/OF, clk, mutexes, MMIO, PWM core, and Microchip corePWM register semantics.

Risks and test signals: shared-period constraints and sync-update timeouts are main risks. Test multiple active channels, period conflict rejection, 0%/100% duty edge programming, sync timeout, channel-count match data, and get-state after hardware reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-microchip-core.c -->
