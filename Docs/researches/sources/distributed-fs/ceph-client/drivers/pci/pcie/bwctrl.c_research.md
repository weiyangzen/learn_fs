<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/bwctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/bwctrl.c

## Purpose
`bwctrl.c` implements the PCIe bandwidth notification/control service. It observes Link Bandwidth Management/Autonomous Bandwidth interrupts, updates cached bus link speed, tracks degraded link events, and exposes a controlled helper for changing a downstream port target speed, also used by PCIe thermal cooling support.

## Important APIs, Types, and Functions
The central state type is `struct pcie_bwctrl_data`, containing a speed-change mutex and optional thermal cooling device. Public functionality includes `pcie_set_target_speed()` and `pcie_reset_lbms()`. Service callbacks are `pcie_bwnotif_probe()`, `pcie_bwnotif_remove()`, `pcie_bwnotif_suspend()`, `pcie_bwnotif_resume()`, and `pcie_bwctrl_init()`.

## Control Flow and State
Probe rejects ports with disabled notifications or no subordinate bus, allocates service data, stores it in `port->link_bwctrl` under `pcie_bwctrl_setspeed_rwsem`, requests the shared service IRQ, enables LBMIE/LABIE, clears LBMS/LABS, updates cached link speed, and registers a cooling device if possible. IRQ handling reads LNKSTA, acknowledges LBMS/LABS, records `PCI_LINK_LBMS_SEEN`, and calls `pcie_update_link_speed()`. Speed changes select the highest speed supported by both port and first downstream device at or below the request, write Target Link Speed, retrain, and return `-EAGAIN` if a non-empty bus did not reach the requested speed.

## Dependencies and Integration Points
Bandwidth control depends on PCIe port bus services, `pcie_retrain_link()`, `pci_bus_sem`, PCIe link capability fields, private `pci_dev` fields, and `drivers/thermal/pcie_cooling.c`. `portdrv.c` creates this service when a Root/Downstream Port supports bandwidth notifications and multiple speeds.

## Risks and Test Signals
Risks include selecting speed from only the first child on a bus, races between removal and speed changes, missed LBMS events if status clear/read ordering changes, and thermal cooling registration failures. Tests should cover IRQ delivery, hot-remove during target-speed changes, quirks that call `pcie_set_target_speed()` before service probe, empty downstream bus behavior, and speed downgrade/restore through PCIe cooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/bwctrl.c -->
