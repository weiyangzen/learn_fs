# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/Kconfig

## Purpose
Adds the Google Ethernet vendor menu and the `GVE` driver configuration option for Google Virtual NIC support.

## APIs and Build Semantics
`NET_VENDOR_GOOGLE` is a boolean vendor gate defaulting to `y`. Under that gate, `GVE` is a tristate option labelled "Google Virtual NIC (gVNIC) support". It depends on MSI-X-capable PCI and either x86 or little-endian CPU support, plus optional PTP clock support via `PTP_1588_CLOCK_OPTIONAL`, and selects `PAGE_POOL`.

## Control Flow and Integration
Kconfig controls whether the `google/Makefile` descends into the `gve/` directory and whether the gve object is built-in or a module. The help text states the module name is `gve`.

## State and Persistence
No runtime state is stored here. It persists build-time feature selection and dependency constraints.

## Dependencies and Risks
The dependency on `PCI_MSI` is required by the driver's MSI-X model; `PAGE_POOL` is required by receive buffer management; PTP optional support aligns with conditional `gve_ptp.o`. Risks are misconfigured builds on unsupported endian/architecture targets or accidentally hiding the driver when `NET_VENDOR_GOOGLE=n`. Test signals include `allyesconfig`, `allmodconfig`, `GVE=m`, `GVE=y`, and builds with and without `CONFIG_PTP_1588_CLOCK`.
