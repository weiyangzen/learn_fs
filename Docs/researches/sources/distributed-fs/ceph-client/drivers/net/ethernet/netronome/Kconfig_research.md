# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/Kconfig

## Purpose
This Kconfig file defines the Netronome Ethernet driver menu and feature switches for the NFP4000/NFP6000 driver family. It controls whether the `nfp` driver is built and whether optional firmware/application integrations such as TC flower offload, ABM NIC support, IPsec offload, and debugfs/debug checks are compiled.

## Important options
`NET_VENDOR_NETRONOME` gates all Netronome questions and defaults to `y`. `NFP` is a tristate driver option that depends on `PCI_MSI`, compatible VXLAN/TLS settings, and selects `NET_DEVLINK`, `CRC32`, and `DIMLIB`. `NFP_APP_FLOWER` depends on `NFP` and `NET_SWITCHDEV` and defaults to `y`. `NFP_APP_ABM_NIC` also depends on `NFP` and `NET_SWITCHDEV`, defaults to `y`, and builds ABM support into `nfp.ko`. `NFP_NET_IPSEC` depends on `NFP` and `XFRM_OFFLOAD`. `NFP_DEBUG` depends on `NFP`.

## Control flow
Kconfig evaluation first exposes the vendor gate. When enabled, it exposes the base NFP driver and feature booleans. These booleans are then consumed by makefiles and C preprocessor conditionals to include optional object files and code paths.

## State and persistence
The only persistent state is kernel configuration. The selected symbols determine build artifacts and runtime feature availability but do not store runtime driver state.

## Dependencies and integration points
This file integrates with kernel configuration, the Netronome makefiles, devlink support, switchdev/TC offload infrastructure, TLS device offload, XFRM offload, VXLAN support, and debugfs/debug infrastructure.

## Risks and edge cases
Default-y optional features increase build coverage and binary size when dependencies are present. Dependency expressions like `VXLAN || VXLAN=n` and `TLS && TLS_DEVICE || TLS_DEVICE=n` enforce compatibility with built-in/module combinations; changing them can create unresolved symbol or unusable feature combinations. ABM and flower support require matching firmware even when the code is compiled.

## Test signals
Validation is primarily configuration matrix coverage: `NFP=m/y`, optional app booleans on/off, dependency-disabled combinations, allmodconfig/allnoconfig style builds, and runtime checks that devlink, flower, ABM, IPsec, and debug features appear only when configured and supported by firmware.
