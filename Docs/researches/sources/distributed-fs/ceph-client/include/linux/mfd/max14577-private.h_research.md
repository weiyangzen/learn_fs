# Research: sources/distributed-fs/ceph-client/include/linux/mfd/max14577-private.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max14577-private.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max14577-private.h

**Purpose:** Defines the internal MFD register, IRQ, and regmap helper contract for Maxim MAX14577 and MAX77836 MUIC/charger/PMIC/fuel-gauge devices.

**Important APIs and types:** Declares I2C addresses for PMIC, MUIC, and fuel gauge; `enum maxim_device_type`; MUIC/charger/PMIC/fuel-gauge register enums; charger-type enums encoding MAX14577 and MAX77836 differences; interrupt masks; field masks for MUIC control/status, charger controls, LDOs, and PMIC top-system interrupts; charger voltage/current limits; `enum max14577_irq`; `struct max14577`; and inline regmap helpers for read, bulk read/write, write, and update.

**Control flow:** The parent MFD creates one or more I2C clients/regmaps based on device type. MUIC, charger, regulator, and fuel-gauge child drivers select register enums and masks for their sub-block and use the inline regmap wrappers.

**State and persistence:** Runtime state is the parent `struct max14577`, including MUIC/charger and PMIC regmaps, IRQ chip data, device type, and IRQ number. Hardware state persists in PMIC/MUIC/fuel-gauge registers.

**Dependencies and integration:** Depends on I2C and regmap. Integrates with MUIC/extcon, charger/power-supply, regulator, and IRQ children.

**Risks:** MAX14577 and MAX77836 share fields but differ in charger type meanings and current limits; wrong `dev_type` changes behavior. A source typo appears in the CDET mask area: `MAX77836_CDETCTRL1_CDLY_SHIFT` is defined, while `MAX77836_CDETCTRL1_CDDLY_MASK` references `MAX77836_CDETCTRL1_CDDLY_SHIFT`, which would fail if compiled through that macro. Inline `max14577_read_reg()` writes `*dest` even when `regmap_read()` fails, using the last local `val`.

**Test signals:** Compile tests that exercise every mask macro, device-type-specific charger limit tests, regmap error-path tests for read helper behavior, IRQ mapping tests for MUIC/charger/top-system sources, and probe tests for MAX14577-only vs MAX77836 multi-client paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max14577-private.h -->
