# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-mpfs-iomux0.c

## Purpose
This driver controls the PolarFire SoC IOMUX0 register that selects whether fixed peripheral interfaces are connected to MSSIO pins or FPGA fabric. It presents each peripheral as a pin/function with two groups: `<name>_mssio` and `<name>_fabric`.

## Important APIs, Types, and Functions
- `MPFS_IOMUX0_REG` is the syscon register offset (`0x200`) containing one selection bit per peripheral.
- `struct mpfs_iomux0_pinctrl` stores pinctrl device, device pointer, syscon regmap, and descriptor.
- `struct mpfs_iomux0_pin_group` stores group name, one-pin list, mask, and setting.
- `struct mpfs_iomux0_function` maps a function to its two groups.
- `MPFS_IOMUX0_GROUP()` generates MSSIO/fabric group pairs.
- Pinctrl ops expose group count/name/pins, generic DT map conversion, and debug display.
- Pinmux ops expose function enumeration and `mpfs_iomux0_pinmux_set_mux()`, which writes the group mask/setting with `regmap_assign_bits()`.
- `mpfs_iomux0_probe()` gets the parent syscon regmap, fills the descriptor, and registers pinctrl.

## Control Flow
Probe obtains the parent node's regmap and registers a pinctrl device. Device-tree pinctrl states map to one of the generated groups. On mux selection, the selected group directly writes its bit in `MPFS_IOMUX0_REG`: zero selects MSSIO and one selects fabric for that peripheral. Debug display reads the same bit for a pin.

## State and Persistence
Runtime software state is the small `mpfs_iomux0_pinctrl` allocation. Selection state persists in the syscon register. There is no suspend/resume save/restore and no software cache.

## Dependencies and Integration Points
The driver depends on syscon/regmap, platform devices, OF matching, generic pinctrl/pinmux helpers, and pinconf DT map helpers. It binds to `microchip,mpfs-pinctrl-iomux0` and expects its parent DT node to provide a syscon regmap.

## Risks
`mpfs_iomux0_probe()` calls `dev_err_probe()` when `device_node_to_regmap()` fails but does not return the error, leaving an `ERR_PTR` regmap available for later registration and operations. That can turn a probe-time resource failure into later invalid regmap use. The function-to-group relation assumes every function has exactly two groups. All selection writes are bit-level and lack locking beyond regmap internals.

## Test Signals
Build with `CONFIG_PINCTRL_POLARFIRE_SOC`, boot with `microchip,mpfs-pinctrl-iomux0`, verify probe fails cleanly when the parent syscon is absent, and use pinctrl states to switch SPI/I2C/CAN/QSPI/UART/MDIO interfaces between MSSIO and fabric while reading back the IOMUX0 register or debugfs.
