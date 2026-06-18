# sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/set_pcie_cooling_state.sh

Purpose: top-level PCIe bandwidth-control test. It finds a thermal cooling device of type `PCIe_Port_Link_Speed`, maps it to the corresponding PCI device current-link-speed sysfs file, and delegates state transitions to `set_pcie_speed.sh`.

Important functions: `prerequisite()` enforces root, mounted sysfs, thermal cooling devices, and at least one PCIe link-speed cooling device. `find_pcie_port()` optionally filters by BDF and selects the port with the highest current speed delta. `find_sysfs_pci_dev()` derives `/sys/bus/pci/devices/<BDF>/current_link_speed`. `parse_arguments()` supports `-d <BDF>` and `-h`.

Control flow: parse args, run prerequisite checks, locate a cooling device, locate the PCI link-speed file, then execute `./set_pcie_speed.sh "$testport" "$sysfspcidev"` and return its status.

State and persistence: reads sysfs and delegates writes to the helper. It does not persist state itself.

Dependencies/integration: requires root, sysfs, thermal cooling device naming convention `PCIe_Port_Link_Speed[_BDF]`, readable PCI `current_link_speed`, and the helper installed in the current directory.

Risks: the script discovers sysfs mount via `mount -t sysfs | head -1`, which may be brittle with unusual mount output. Some path probes use unquoted globs/variables. The helper invocation assumes current working directory is the installed test directory.

Test signals: prerequisite failures print `skip all tests:` and exit 4. Helper pass/fail is propagated.
