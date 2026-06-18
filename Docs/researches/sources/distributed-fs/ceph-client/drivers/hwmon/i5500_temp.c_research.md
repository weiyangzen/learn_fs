# sources/distributed-fs/ceph-client/drivers/hwmon/i5500_temp.c

## Purpose
`i5500_temp.c` exposes the thermal sensor in Intel 5500/5520/X58 chipsets as a single hwmon temperature channel with input, critical threshold, and fault status.

## Important APIs, Types, and Functions
`i5500_read()` is the hwmon read callback and decodes PCI config registers for `temp1_input`, `temp1_crit`, and `temp1_fault`. `i5500_ops`, `i5500_info`, and `i5500_chip_info` describe the hwmon interface. `i5500_temp_probe()` enables the PCI device, checks sensor availability, and registers the hwmon device. `i5500_temp_driver` binds PCI IDs for Intel 5500/5520/X58 thermal sensor devices.

## Control Flow
Probe enables the PCI function with `pcim_enable_device()`, reads `REG_TSTHRCATA`, and rejects the device if the unavailable bit is set. It then registers `intel5500`. Reads use `pci_read_config_word()` or `pci_read_config_byte()` from the PCI device stored as the parent of the hwmon device. Temperature input and critical threshold are derived from register fields as `millidegrees`; fault reports the alarm bit.

## State and Persistence
The driver has no private state and no cache. All values are read live from PCI config space. It does not write thresholds or alter chipset settings.

## Dependencies and Integration Points
It depends on PCI config access, managed PCI enablement, and hwmon callback registration. It is registered with `module_pci_driver()`.

## Risks
The implementation assumes the hwmon device parent is the PCI device and uses `to_pci_dev(dev->parent)`. A config read failure would leave local variables at zero because return codes are not checked. The sensor is rejected only by one availability bit; platform firmware quirks may still expose unusable readings.

## Test Signals
Test PCI ID binding, unavailable-bit probe rejection, config-space decode vectors for input/crit/fault, behavior under failed PCI config reads, and absence of writable attributes.
