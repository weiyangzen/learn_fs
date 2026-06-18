# sources/distributed-fs/ceph-client/drivers/ptp/ptp_dte.c Research

## Purpose
`ptp_dte.c` is a Broadcom Digital Timing Engine PTP clock driver. It maps a 44-bit NCO timer, exposes get/set/adjust/frequency operations, and preserves basic register state across suspend.

## Important APIs, Types, And Functions
`struct ptp_dte` stores MMIO base, PTP clock, clock caps, device, overflow tracking, spinlock, and saved registers. Helpers include `dte_write_nco()`, `dte_read_nco()`, `dte_write_nco_delta()`, `dte_read_nco_with_ovf()`, and PTP ops `ptp_dte_adjfine()`, `ptp_dte_adjtime()`, `ptp_dte_gettime()`, `ptp_dte_settime()`, and `ptp_dte_enable()`.

## Control Flow
Probe allocates state, maps the platform resource, initializes lock, copies static caps, registers with the PTP core, and stores driver data. Settime disables the increment register, writes the NCO registers, resets wrap tracking, then reenables default increment. Gettime reads the hardware NCO, detects wrap by comparing overflow bits, extends it with `ts_wrap_cnt`, and returns a timespec. Adjtime applies a signed delta while accounting for wrap/underflow. Adjfine converts scaled ppm to ppb, bounds it by `max_adj`, and writes an adjusted increment value. Suspend saves four registers and disables the NCO; resume restores them with special formatting for the overflow register.

## State And Persistence
Hardware stores low/time/overflow/increment registers. Software extends the 44-bit hardware clock using `ts_wrap_cnt` and `ts_ovf_last`, so long gaps without reads can lose wrap information. Suspend state is in `reg_val`.

## Dependencies And Integration Points
The driver depends on platform-device probing, OF compatible `brcm,ptp-dte`, MMIO accessors, PM sleep hooks, and PTP core registration.

## Risks
The 44-bit timer wraps in about 4.9 hours; wrap extension only updates on reads or adjustments. `ptp_dte_enable()` returns unsupported for all event requests. Negative adjustments around zero clamp if no wrap count exists. Frequency math assumes 125 MHz and the documented 3.29 register format.

## Test Signals
Validation should cover probe/remove, set/get monotonicity, wrap detection through simulated overflow, adjtime across wrap and underflow, adjfine max range, suspend/resume register restoration, and unsupported PEROUT/EXTTS/PPS ioctls.
