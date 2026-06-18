<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/fsi/Kconfig

## Purpose
`drivers/fsi/Kconfig` defines the build-time configuration surface for the Linux FSI subsystem and its FSI masters/client drivers in this source tree.

## Important APIs, types, and functions
The top-level `menuconfig FSI` is a tristate depending on OF and selecting CRC4. Child symbols include `FSI_NEW_DEV_NODE`, `FSI_MASTER_GPIO`, `FSI_MASTER_HUB`, `FSI_MASTER_AST_CF`, `FSI_MASTER_ASPEED`, `FSI_MASTER_I2CR`, `FSI_SCOM`, `FSI_SBEFIFO`, `FSI_OCC`, and `I2CR_SCOM`.

## Control flow
Kconfig has no runtime control flow. Build selection controls whether the core, masters, and clients are compiled. `FSI_OCC` depends on `FSI_SBEFIFO`; `I2CR_SCOM` depends on `FSI_MASTER_I2CR`; GPIO and Aspeed ColdFire masters declare GPIO-related dependencies.

## State and persistence behavior
The file controls kernel configuration state only. `FSI_NEW_DEV_NODE` changes runtime device-node naming conventions by selecting `/dev/fsi/...` paths and shifted numbering, but the option itself is build-time state.

## Dependencies and integration points
It integrates with Kbuild via the sibling Makefile and with the broader kernel configuration system. Dependency choices reflect driver requirements: OF enumeration, CRC4 protocol support, GPIOLIB, GPIO_ASPEED, GENERIC_ALLOCATOR, HAS_IOMEM, I2C, and OF_ADDRESS.

## Risks and edge cases
Changing dependencies can produce drivers without required framework support or hide valid hardware. `FSI_NEW_DEV_NODE` affects userspace ABI expectations, so enabling it without updated udev/userspace can break legacy tooling.

## Test signals
Configuration matrix builds with core-only, each master, SBEFIFO/OCC, and I2CR combinations are the primary signals. Runtime checks should verify device-node paths under both legacy and new dev-node modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/Kconfig -->
