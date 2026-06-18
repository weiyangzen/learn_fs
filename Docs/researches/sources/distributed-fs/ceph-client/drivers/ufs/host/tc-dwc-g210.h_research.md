# sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210.h

## Purpose
Declares the shared Synopsys G210 PHY configuration entry points used by PCI and platform glue.

## Important APIs and types
Forward declares `struct ufs_hba` and exposes `tc_dwc_g210_config_40_bit(struct ufs_hba *hba)` and `tc_dwc_g210_config_20_bit(struct ufs_hba *hba)`.

## Control flow and state
There is no runtime behavior or persistent state in this header. It defines the compile-time contract between transport glue and the shared configuration implementation.

## Dependencies and integration points
Included by `tc-dwc-g210.c`, `tc-dwc-g210-pci.c`, and `tc-dwc-g210-pltfrm.c`. It intentionally avoids including full UFSHCD headers by forward declaration, keeping the interface small.

## Risks and test signals
Risks are ABI-level within the module build: changing prototypes without updating all users breaks compilation or exported symbol use. Test signals are clean builds for both PCI and platform G210 options and successful modpost resolution of exported functions.
