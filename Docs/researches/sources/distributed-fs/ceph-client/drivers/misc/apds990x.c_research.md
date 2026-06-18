# sources/distributed-fs/ceph-client/drivers/misc/apds990x.c

Purpose: implements an I2C driver for APDS990x combined ambient-light and proximity sensors, exposing calibration, thresholds, reporting mode, raw proximity, and power controls through sysfs.

Important APIs and functions: probe/remove are `apds990x_probe` and `apds990x_remove`; IRQ handling is `apds990x_irq`. Register helpers wrap command-bit SMBus byte/word accesses. Core algorithms include `apds990x_get_lux`, `apds990x_calc_again`, `apds990x_lux_to_threshold`, `apds990x_refresh_athres`, and `apds990x_refresh_pthres`. PM paths are system and runtime suspend/resume.

Control flow: probe requires platform data, loads optical factors or defaults, computes reverse threshold factors, initializes calibration/threshold/gain defaults, enables regulators, detects chip id/revision, configures integration/wait/persistence registers, starts ALS, creates sysfs files, and requests a threaded IRQ. The IRQ acknowledges ALS/proximity interrupts, reads clear/IR/proximity data, computes lux, adjusts gain, refreshes thresholds, wakes readers waiting for a fresh lux result, and notifies sysfs attributes. Sysfs stores adjust calibration, ALS rate, proximity enable count, reporting mode, thresholds, and runtime power state.

State and persistence: `struct apds990x_chip` caches platform data, regulators, wait queue, lux/proximity readings, gain state, calibration, thresholds, persistence, and chip identity. Hardware register configuration is rewritten after power-on/resume.

Dependencies and integration points: depends on I2C, threaded IRQs, regulators named `Vdd` and `Vled`, runtime PM, wait queues, and `linux/platform_data/apds990x.h`.

Risks: this snapshot contains duplicate/malformed-looking lines around `apds990x_force_a_refresh` and `apds990x_rate_store`, which are build risks if not source corruption. The driver requires platform data and has no OF/ACPI matching. Many register writes combine errors with bitwise OR or ignore return values. Sysfs proximity enable is a reference count without owner tracking.

Test signals: chip-id detection, IRQ-driven lux/proximity updates, sysfs polling/notify behavior, regulator and runtime PM cycles, gain adaptation under bright/dark conditions, threshold hysteresis, and fault injection for I2C and IRQ setup.
