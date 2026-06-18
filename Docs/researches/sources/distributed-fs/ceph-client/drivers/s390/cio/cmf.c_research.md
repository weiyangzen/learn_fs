# sources/distributed-fs/ceph-client/drivers/s390/cio/cmf.c

## Purpose
This file implements the s390 Channel Measurement Facility for CCW devices. It allocates channel measurement blocks, enables/disables subchannel measurement, exposes per-device measurement sysfs attributes, reads accumulated timing/count data, and reactivates measurement after recovery or hibernation.

## Important APIs, Types, and Functions
Important types are `enum cmb_index`, `enum cmb_format`, `struct cmb_operations`, `struct cmb_data`, `struct cmb_area`, basic `struct cmb`, and extended `struct cmbe`. Public functions are `enable_cmf()`, `disable_cmf()`, `cmf_read()`, `cmf_readall()`, `cmf_reenable()`, `cmf_reactivate()`, `retry_set_schib()`, and `cmf_retry_copy_block()`. Module parameters select `format` and basic `maxchannels`. `cmbops_basic` and `cmbops_extended` abstract allocation, setup, read, read-all, reset, and sysfs attributes.

## Control Flow
`init_cmf()` autodetects basic versus extended measurement using CSS characteristics unless overridden. Enabling a device locks the device, allocates a measurement block, resets it, creates the `cmf` sysfs group, and calls the format-specific `set()` to update the subchannel SCHIB measurement mode. Basic mode allocates one global contiguous CMB array and uses indices; extended mode allocates per-device cache-aligned CMBEs and programs a block address. Reads either sample individual live fields or copy a stable block after waiting for in-progress I/O to quiesce through temporary `DEV_STATE_CMFCHANGE` or `DEV_STATE_CMFUPDATE` state-machine states.

## State and Persistence
State is volatile. Per-device `cdev->private->cmb` points to `struct cmb_data`, with hardware and last-copied blocks plus timestamps. Global `cmb_area` tracks all measured devices and the basic global CMB array; `cmbe_cache` owns extended blocks. Hardware accumulates counts/times until reset/disable. There is no disk persistence.

## Dependencies and Integration Points
It depends on CCW device private state and locks, CIO subchannel configuration, `cio_commit_config()`, TOD clock conversion, sysfs, module parameters, CSS characteristic detection, and the s390 `schm` instruction. `device.c` exposes `cmb_enable`, disables CMF on remove/shutdown, and calls retry helpers from the CCW state machine.

## Risks and Test Signals
Risk areas include global CMB array sizing, measurement block lifetime while hardware may update it, state-machine waits timing out or being interrupted, read atomicity during active I/O, basic versus extended format selection, sysfs cleanup on partial enable failure, and disabling after the device disappeared. Test signals include boot with `s390cmf` parameters, enabling/disabling `cmb_enable`, readout of all basic/extended attributes, active-I/O read waits, CMF reenable after disconnected recovery, hibernate resume reactivation, allocation exhaustion, and subchannel removal during measurement.
