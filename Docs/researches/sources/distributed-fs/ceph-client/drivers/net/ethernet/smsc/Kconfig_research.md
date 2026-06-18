# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/Kconfig

## Purpose
This Kconfig file declares the SMSC/Western Digital Ethernet vendor menu and the selectable driver options in this directory: `SMC91X`, `EPIC100`, `SMSC911X`, `SMSC911X_ARCH_HOOKS`, and `SMSC9420`.

## Important APIs, Types, and Data
- `NET_VENDOR_SMSC` is a boolean vendor gate, defaulting to `y`, with broad architecture and bus dependencies.
- `SMC91X` is a tristate for SMC 91C9x/91C1xxx devices, selecting `CRC32` and `MII`, depending on suitable embedded/platform architectures and `!OF || GPIOLIB`.
- `EPIC100` is a PCI tristate for SMC EtherPower II 9432 / SMC83c17x hardware, selecting `CRC32` and `MII`.
- `SMSC911X` is a HAS_IOMEM embedded Ethernet driver option selecting `CRC32`, `MII`, and `PHYLIB`.
- `SMSC911X_ARCH_HOOKS` is a dependent internal-style boolean for architecture hooks.
- `SMSC9420` is a PCI tristate selecting `CRC32`, `PHYLIB`, and `SMSC_PHY`.

## Control Flow
Kconfig flow is menu gating only. If `NET_VENDOR_SMSC` is disabled, the nested driver choices are hidden. Enabled driver symbols feed the adjacent Makefile to include the corresponding objects or subdrivers in the build.

## State and Persistence
The file contributes persistent kernel configuration state in `.config`. It has no runtime state. Its selections may indirectly enable library code and PHY support in the built kernel.

## Dependencies and Integration Points
The options integrate the SMSC drivers into the kernel networking vendor hierarchy and Kbuild. Help text points users to relevant networking and module documentation. The `SMSC911X_ARCH_HOOKS` option creates an architecture-to-driver extension point.

## Risks and Edge Cases
- Architecture and bus dependencies control option visibility; missing `PCI`, `HAS_IOMEM`, `GPIOLIB`, or architecture symbols can hide drivers even when source exists.
- `select` pulls in dependencies without prompting, which can change build contents.
- `SMC91X` has an OF/GPIOLIB dependency because DT-based reset/power GPIO handling is compiled in when Open Firmware matching is used.

## Test Signals
Run targeted `oldconfig`/`allmodconfig` checks for supported and unsupported architectures, verify each symbol builds as module and built-in where allowed, and confirm Makefile object inclusion matches the selected symbols.
