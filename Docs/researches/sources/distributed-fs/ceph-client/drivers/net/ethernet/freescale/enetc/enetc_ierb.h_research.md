# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ierb.h

## Purpose
Declares the optional ENETC IERB registration hook used by the rev1 PF driver to program LS1028A IERB resources before normal PF setup.

## Important APIs, Types, and Functions
The sole API is `enetc_ierb_register_pf(struct platform_device *pdev, struct pci_dev *pf_pdev)`. When `CONFIG_FSL_ENETC_IERB` is enabled it is an external symbol; otherwise it is an inline stub returning `-EOPNOTSUPP`.

## Control Flow
Runtime control flow is compile-time selected. Enabled builds call into `enetc_ierb.c`; disabled builds let callers receive an unsupported error without adding conditional compilation at call sites.

## State and Persistence
The header owns no state. It represents a build-time dependency edge between PF probing and platform IERB programming.

## Dependencies and Integration Points
Includes PCI and platform-device declarations. Used by `enetc_pf.c` during PF probe and by `enetc_ierb.c` for the implementation signature.

## Risks
The main risk is callers treating `-EOPNOTSUPP` as fatal on configurations where the platform driver is intentionally absent. Prototype drift would break module builds or stubs.

## Test Signals
Build with `CONFIG_FSL_ENETC_IERB=y/m` and disabled. PF probe should defer only when an enabled IERB node exists but is not yet ready; disabled builds should compile and warn/continue from the PF path.
