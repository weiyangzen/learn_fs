# sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx.h

## Purpose
Shared public header for the SC16IS7xx serial implementation and its I2C/SPI transport modules. It defines the transport-neutral device type contract, maximum UART channel count, and exported symbols needed by bus-specific probe/remove code.

## Important APIs, Types, And Functions
`SC16IS7XX_MAX_PORTS` is fixed at two. `struct sc16is7xx_devtype` carries the variant name plus `nr_gpio` and `nr_uart`. The header declares the exported `sc16is7xx_regcfg`, `sc16is7xx_dt_ids`, variant descriptors, `sc16is7xx_regmap_name()`, `sc16is7xx_regmap_port_mask()`, `sc16is7xx_probe()`, and `sc16is7xx_remove()`.

## Control Flow
Bus drivers include this header, match a device to one of the exported devtypes, create one regmap per UART channel, and pass the resulting array and IRQ to `sc16is7xx_probe()`. Removal calls `sc16is7xx_remove()` with the same device object.

## State And Persistence
The header owns no runtime storage. It defines the ABI between the core module and transport modules, so layout and symbol changes affect module loading and namespace imports.

## Dependencies And Integration Points
Includes `mod_devicetable.h`, `regmap.h`, and `types.h`; forward declares `struct device`. Symbols are exported from the core module under the `SERIAL_NXP_SC16IS7XX` namespace and imported by SPI/I2C wrappers.

## Risks
The regmap array contract relies on callers allocating entries up to `devtype->nr_uart` and respecting `SC16IS7XX_MAX_PORTS`. Changing devtype contents or symbol names can break both bus modules.

## Test Signals
Build both SPI and I2C modules, verify namespace import/export resolution, probe one- and two-port variants, and confirm invalid or missing match data returns probe errors.
