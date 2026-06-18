# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device_pci.c

## Purpose

`processor_thermal_device_pci.c` is the PCI frontend for newer Processor Thermal Devices. It maps processor thermal MMIO, registers a package thermal zone, handles threshold/workload/power-floor interrupts, and enables optional feature modules based on PCI ID driver data.

## Important APIs, Types, and Functions

`struct proc_thermal_pci` tracks PCI device, core private data, MMIO thermal zone, delayed threshold work, stored threshold, and whether legacy ACPI setup failed. MMIO helper tables describe package temp, TjMax, threshold, interrupt enable, and status registers. `proc_thermal_irq_handler()` classifies MSI/shared interrupts and schedules work or wakes the threaded handler. `sys_get_curr_temp()` and `sys_set_trip_temp()` implement the `TCPU_PCI` zone.

## Control Flow

Probe enables PCI, maps feature MMIO, attempts legacy ACPI `proc_thermal_add()` but continues without it, registers one writable passive trip for package threshold, selects MSI when supported or requested, requests IRQs, then enables the zone. Threshold interrupts disable MMIO interrupt enable, delay notification for rate control, update the zone, and re-enable interrupt. Threaded IRQ callbacks notify workload and power-floor sysfs listeners and clear SoC status bits.

## State and Persistence Behavior

Runtime state includes `stored_thres`, delayed work, static MSI IRQ map, and static `msi_irq`. Hardware threshold and interrupt-enable registers persist across runtime until remove or suspend/resume rewrites them. Probe stores `proc_thermal_device` as PCI drvdata.

## Dependencies and Integration Points

It integrates PCI, thermal core, optional MSI/MSI-X, processor thermal core/MMIO features, workload hint/request, power-floor, and INT340x. PCI ID driver data encodes the feature mix for ADL, LNLM, MTLP, ARL, RPL, PTL, WCL, and NVL variants.

## Risks and Test Signals

Risks include global MSI state with multiple devices, resume restoring `stored_thres / 1000` instead of the TjMax-relative register value used by set_trip, continuing after legacy ACPI failure, IRQ status races, and feature cleanup paths. Test signals include shared IRQ and MSI modes, threshold set/clear/resume, workload/power-floor interrupts, feature-mask matrix probes, and delayed-work cancellation on remove/offline.
