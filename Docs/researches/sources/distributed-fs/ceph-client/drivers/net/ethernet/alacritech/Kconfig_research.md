# sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/Kconfig

## Purpose
This Kconfig file defines the Alacritech Ethernet vendor menu and the `SLICOSS` driver option for Alacritech SLIC-based Gigabit adapters.

## Important configuration
- `NET_VENDOR_ALACRITECH` is a boolean vendor gate, defaulting to `y`, that controls visibility of Alacritech device options.
- `SLICOSS` is a tristate driver option depending on `PCI` and selecting `CRC32`. Its help text documents Mojave and Oasis copper/fiber cards and the `slicoss` module name.

## Control flow and integration
Kconfig selection controls whether `drivers/net/ethernet/alacritech/Makefile` builds `slicoss.o`. Selecting `SLICOSS=m` builds a loadable module; selecting `y` builds it into the kernel.

## State and persistence behavior
There is no runtime state in this file. It persists only the build-time configuration decisions.

## Dependencies and integration points
The file integrates into the kernel networking driver Kconfig tree. It exposes the SLIC driver only under the vendor gate and pulls in CRC32 for multicast hash filtering in the driver.

## Risks and edge cases
Because the vendor gate defaults to enabled, distribution configs will usually show the SLIC option. Missing `PCI` prevents the driver from being selectable. CRC32 is selected rather than depended on, so it is automatically available when the driver is enabled.

## Test signals
Validate `CONFIG_NET_VENDOR_ALACRITECH=n` hides `SLICOSS`, `CONFIG_SLICOSS=m` produces `slicoss.ko`, and built-in/module builds include CRC32 support.
