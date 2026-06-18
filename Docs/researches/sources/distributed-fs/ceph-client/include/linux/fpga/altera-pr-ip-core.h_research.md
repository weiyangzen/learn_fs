# sources/distributed-fs/ceph-client/include/linux/fpga/altera-pr-ip-core.h

## Purpose
This small header exposes registration for the Altera/Intel Partial Reconfiguration IP core driver.

## APIs, types, and control flow
`alt_pr_register(struct device *dev, void __iomem *reg_base)` registers an FPGA manager or related partial-reconfiguration provider backed by memory-mapped IP registers. The caller supplies the owning device and an already mapped register base.

## State and dependencies
All state is implementation-owned after registration, likely tied to the device and register base. The header depends on `linux/io.h` for `__iomem` annotations and device declarations through included kernel headers.

## Integration, risks, and tests
Platform drivers for Altera partial reconfiguration use this as a helper to bind the IP core into the FPGA framework. Risks include passing an unmapped or wrongly sized register window, registering before clock/reset readiness, and failing to unregister through devm or remove paths if the implementation requires it. Tests should cover probe failure cleanup, MMIO access error paths, partial bitstream load through the resulting manager, and static analysis for `__iomem` misuse.
