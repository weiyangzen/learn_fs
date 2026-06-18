# sources/distributed-fs/ceph-client/drivers/thermal/pcie_cooling.c

Purpose: PCIe cooling-device helper that throttles a PCIe port by lowering target link speed. It exposes thermal cooling states as inverse PCIe speed levels.

Important APIs/functions: `pcie_cooling_get_max_level()` returns the number of throttling steps from 2.5 GT/s up to the subordinate bus maximum. `pcie_cooling_get_cur_level()` maps current bus speed to cooling state, where state 0 means maximum speed. `pcie_cooling_set_cur_level()` converts a requested cooling state back to `enum pci_bus_speed` and calls `pcie_set_target_speed(port, speed, true)`. `pcie_cooling_device_register()` creates a named cooling device with `kasprintf()` and `thermal_cooling_device_register()`. `pcie_cooling_device_unregister()` unregisters it.

Control flow: users of the helper pass a PCIe port with a subordinate bus. Thermal governors operate on cooling states; the helper maps those states to PCIe bandwidth-control requests. Static assertions verify that enum speed values are contiguous for arithmetic.

State/persistence: no private state beyond `cdev->devdata` pointing to the PCI device; target speed persists through PCIe bandwidth-control machinery. Dependencies: PCI core, `pci-bwctrl`, thermal cooling-device framework.

Risks: assumes `port->subordinate` is valid and bus speed enum values remain contiguous; cooling-state semantics are inverse of performance, which can cause mistakes in callers; registration is non-devm and caller must unregister. Test signals include state/speed mapping for every supported speed, set-target errors, subordinate absence protection by callers, and unregister on caller teardown.
