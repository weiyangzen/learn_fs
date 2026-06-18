# sources/distributed-fs/ceph-client/drivers/mfd/intel_quark_i2c_gpio.c

Purpose: PCI MFD splitter for Intel Quark I2C and GPIO controllers that share one PCI function. It creates DesignWare I2C and GPIO DW APB child devices with board-specific software-node properties.

Important APIs/types/functions: `intel_quark_mfd_probe()`, `intel_quark_i2c_setup()`, `intel_quark_gpio_setup()`, fixed I2C clock registration helpers, DMI table for Galileo/GalileoGen2/SIMATIC IOT2000, and two `mfd_cell` entries.

Control flow: probe enables PCI, allocates state, registers a 33 MHz fixed I2C clock lookup, enables bus mastering, allocates one IRQ vector, fills BAR/IRQ resources for I2C and GPIO cells, registers GPIO software-node group, and adds MFD devices. Remove reverses MFD devices, nodes, IRQ vectors, and clock.

State and persistence: only per-device clock lookup and software-node registration are retained. Static resource arrays are patched at probe time for the active PCI device.

Dependencies and integration: depends on PCI ID 0x0934, clk/clkdev, DMI, software-node APIs, `i2c_designware`, `gpio-dwapb`, and ACPI `_ADR` child matching.

Risks: static resource/cell mutation assumes one active device instance. GPIO node group must be unregistered on all failure paths. DMI selection controls I2C speed and must match board wiring.

Test signals: PCI bind/unbind, fixed clock lookup by `i2c_designware.0`, GPIO software-node children, board-specific I2C frequency on Galileo variants, shared IRQ handling, and error-path cleanup.
