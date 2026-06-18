# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000_pcie.h

Purpose: Declares the PCIe-to-CPP constructor for NFP6000-family PCI devices.

Important APIs/types/functions: `nfp_cpp_from_nfp6000_pcie(struct pci_dev *pdev, const struct nfp_dev_info *dev_info)` returns a `struct nfp_cpp *` or `ERR_PTR()`.

Control flow/state: The header has no runtime state. It lets the PCI probe layer pass chip-specific `nfp_dev_info` into the PCIe backend implemented in `nfp6000_pcie.c`.

Dependencies/integration: Includes `nfp_cpp.h` and relies on visible `struct pci_dev` and `struct nfp_dev_info` declarations from users including this header. It connects PCI device discovery to the generic CPP subsystem.

Risks: Signature drift with `nfp6000_pcie.c` or missing forward declarations in include users will break the driver build.

Test signals: Compile coverage of the NFP PCI probe path and successful link of the constructor symbol.
