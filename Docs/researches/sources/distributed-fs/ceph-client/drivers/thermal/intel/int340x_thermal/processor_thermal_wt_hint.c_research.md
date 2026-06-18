# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_wt_hint.c

## Purpose

`processor_thermal_wt_hint.c` exposes firmware-predicted workload type hints and notification controls through a `workload_hint` sysfs group.

## Important APIs, Types, and Functions

Attributes are `workload_type_index`, `workload_hint_enable`, `workload_slow_hint_enable`, and `notification_delay_ms`. Exports include `proc_thermal_check_wt_intr()`, `proc_thermal_wt_intr_callback()`, `proc_thermal_wt_hint_add()`, and `proc_thermal_wt_hint_remove()`. `workload_hint_enable()` programs mailbox interrupt config for fast or slow prediction bits.

## Control Flow

Add creates the sysfs group and marks it created. Users enable prediction through mailbox config with a programmable time window. Reads of workload index require at least one hint mode enabled, then extract bits 47:40 from the shared status register. IRQ top-half checks active bit 2; threaded callback sends `sysfs_notify()` for `workload_hint/workload_type_index`. Remove disables the fast hint if enabled and removes the group.

## State and Persistence Behavior

Static globals track enable states, notification delay encoding, notification delay in milliseconds, and group creation. Hardware prediction status and interrupt config live in MMIO/mailbox registers.

## Dependencies and Integration Points

It depends on mailbox helpers, PCI drvdata, newer Processor Thermal PCI IRQ handling, and common `SOC_WT_RES_INT_STATUS_OFFSET`. Attribute visibility hides slow hints on selected platforms.

## Risks and Test Signals

Risks include global enable/delay state, remove disabling only the fast hint path, concurrent IRQ/status reads around sysfs changes, and rounding delay values to powers of two. Test signals include sysfs enable/disable, slow-hint visibility by PCI ID, notification delay encoding bounds, workload status extraction, interrupt notification, and cleanup after enabled hints.
