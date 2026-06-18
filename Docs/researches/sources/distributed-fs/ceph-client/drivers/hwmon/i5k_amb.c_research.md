# sources/distributed-fs/ceph-client/drivers/hwmon/i5k_amb.c

## Purpose
`i5k_amb.c` monitors AMB temperature sensors on Intel 5000-series FB-DIMM chipsets. It dynamically creates sysfs attributes for present AMB devices across memory branches, channels, and DIMM slots.

## Important APIs, Types, and Functions
`struct i5k_amb_data` stores chipset resources, AMB-present bitmasks, dynamically allocated attributes, and hwmon device pointer. `struct i5k_device_attribute` extends `sensor_device_attribute` with node/register metadata. Show helpers expose ambient temperature, status, alarm, and threshold fields. `i5k_channel_probe()` detects populated AMB channels through PCI config space. `i5k_amb_hwmon_init()` creates sysfs files and registers hwmon. `i5k_amb_probe()` identifies the chipset, maps resources, reads AMB presence, and initializes hwmon; `i5k_amb_remove()` tears it down.

## Control Flow
Module init registers a platform driver and platform device. Probe finds a supported Intel memory controller/chipset, maps AMB MMIO, probes channel presence via PCI devices, calculates which AMBs exist, and calls hwmon init. Hwmon init creates a `name` attribute, allocates per-sensor attributes for every present AMB and supported register, creates each sysfs file manually, then registers a legacy hwmon device. On failure or removal it walks the created attributes and removes them.

## State and Persistence
The driver stores discovered AMB presence and the list of created attributes in RAM. Readings and threshold/status values are read live from chipset/AMB registers. No writes are exposed in this source, so hardware thresholds are not changed.

## Dependencies and Integration Points
It uses PCI discovery/config access, platform driver/device plumbing, MMIO access, hwmon legacy registration, and manual sysfs file creation. It predates the modern `hwmon_chip_info` model.

## Risks
Manual sysfs creation has many partial-failure cleanup paths. Dynamic attribute naming/indexing must stay aligned with branch/channel/DIMM register layout. Legacy `hwmon_device_register()` is deprecated. Hardware presence probing is chipset-specific and depends on PCI IDs and config offsets. The report should watch for unchecked low-level read failures and assumptions around AMB bitmaps.

## Test Signals
Test supported and unsupported chipset probing, AMB presence bitmaps, generated attribute names/counts, partial sysfs creation cleanup, remove cleanup, MMIO decode for all exposed fields, and behavior when a channel probe PCI device is absent.
