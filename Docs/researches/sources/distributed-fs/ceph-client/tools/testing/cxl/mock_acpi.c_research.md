# sources/distributed-fs/ceph-client/tools/testing/cxl/mock_acpi.c

Purpose: overrides CXL host-bridge discovery for mocked ACPI/platform devices.

Important APIs, types, and functions: defines `to_cxl_host_bridge(struct device *host, struct device *dev)`. It uses `get_cxl_mock_ops()`, `put_cxl_mock_ops()`, `ops->is_mock_bridge()`, `ACPI_COMPANION()`, `dev_is_platform()`, `to_acpi_device()`, `acpi_pci_find_root()`, and ACPI HID comparison to `"ACPI0016"`.

Control flow: obtains registered mock ops under SRCU. If a mock ops provider exists and marks the device as a mock bridge, the function returns the device's ACPI companion. Platform devices that are not mock bridges are ignored. For real ACPI devices, it checks that the device has a PCI root and HID `ACPI0016`, logs a debug message, and returns it. The mock ops reference is released before return.

State and persistence: no local persistent state; it consults the global mock-ops registry.

Dependencies and integration points: compiled into the mocked `cxl_acpi` module and works with `test/mock.c` operations supplied by `test/cxl.c`. It intercepts host bridge discovery in the production ACPI CXL driver path.

Risks: assumes mock bridge devices have a valid ACPI companion. If `dev_is_platform()` filters new legitimate cases, discovery can fail. Mock ops must remain registered while discovery runs; SRCU protects this.

Test signals: mock host bridges should be discovered as CXL host bridges during `cxl_test` topology enumeration. Real ACPI `ACPI0016` devices should still fall back to normal logic.
