# sources/distributed-fs/ceph-client/include/linux/mfd/da9150/core.h

Purpose: This is the DA9150 MFD core interface. It defines paging constants, logical IRQ numbers, platform data, the parent `struct da9150`, and exported register and query-interface accessors used by DA9150 charger, fuel gauge, GPADC, and other child drivers.

Important APIs, types, and functions: `DA9150_REG_PAGE_SHIFT` and `DA9150_REG_PAGE_MASK` encode 16-bit register page addressing. `DA9150_NUM_IRQ_REGS` and IRQ numbers from `DA9150_IRQ_VBUS` through `DA9150_IRQ_WKUP` define the regmap IRQ namespace. `struct da9150_fg_pdata` carries fuel-gauge update and warning thresholds; `struct da9150_pdata` carries IRQ base and fuel-gauge platform data; `struct da9150` holds `dev`, `regmap`, the fuel-gauge query-interface I2C client, IRQ chip data, and IRQ bases. Exported helpers include `da9150_read_qif`, `da9150_write_qif`, `da9150_reg_read`, `da9150_reg_write`, `da9150_set_bits`, `da9150_bulk_read`, and `da9150_bulk_write`.

Control flow, state, and persistence: The core probes the I2C PMIC, initializes regmap and regmap-irq, and child drivers call these helpers rather than open-coding page selection. The query interface is a separate I2C endpoint used for fuel-gauge operations. Persistent state is in PMIC registers and firmware/fuel-gauge memory, while the in-kernel `struct da9150` tracks only live handles and IRQ metadata.

Dependencies and integration points: The header depends on device, I2C, interrupt, and regmap infrastructure. It integrates with `da9150/registers.h` for register addresses and bitfields, with MFD cell registration for children, and with the Linux IRQ and power-supply/charger stacks through child drivers.

Risks and test signals: Risks include incorrect page calculations, confusing standard register access with the query interface, and mismatched IRQ numbering relative to the regmap IRQ chip. Test signals include child-driver probe against a mocked regmap, IRQ mapping coverage for all 21 logical IRQs, bulk read/write boundary tests across page changes, and fuel-gauge query-interface transaction tests.
