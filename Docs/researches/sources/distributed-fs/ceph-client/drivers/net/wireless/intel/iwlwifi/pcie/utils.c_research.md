# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/utils.c

## Purpose
This file provides PCIe diagnostic support for iwlwifi, currently centered on `iwl_trans_pcie_dump_regs()`. It emits a one-time dump of PCI config space, selected device MMIO registers, device AER capability, parent bridge config space, and root-port AER capability after a transaction failure.

## Important APIs, Types, and Functions
- `iwl_trans_pcie_dump_regs(struct iwl_trans *trans, struct pci_dev *pdev)` is the exported utility function declared in `utils.h`.
- Local constants define dump sizes for iwlwifi PCI config, MMIO, parent config, and prefix length.
- It uses PCI helpers such as `pci_read_config_dword()`, `pci_find_ext_capability()`, `pcie_find_root_port()`, and `pci_name()`.
- It uses `iwl_read32()` for MMIO register reads and `print_hex_dump()`/`IWL_ERR()` for logging.

## Control Flow
The function returns immediately after the first dump due to a static `pcie_dbg_dumped_once` guard. It allocates a single atomic buffer large enough for all dump variants plus a prefix, dumps endpoint PCI config, dumps the first 64 bytes of iwlwifi MMIO, optionally dumps the endpoint AER capability, optionally moves to the parent bridge and dumps its config space, optionally finds the root port and dumps its AER capability, then marks the dump as emitted and frees the buffer. If a config read fails, it prints the partial buffer and reports the failing offset.

## State and Persistence Behavior
State is minimal: the static boolean suppresses repeated dumps globally. No hardware state is modified except for read side effects inherent to register access. The buffer is transient and allocated with `GFP_ATOMIC`, making it usable in error paths that may have limited sleeping context.

## Dependencies and Integration Points
It depends on PCI core APIs, iwlwifi register access, and logging. It is meant for PCIe transaction failure paths where the driver still has enough bus access to read endpoint/bridge diagnostics.

## Risks and Edge Cases
The one-time guard prevents log flooding but can hide later failures from different devices or later phases. Config read failures produce partial dumps. MMIO reads after a transaction failure may themselves be unreliable. The function assumes requested dump sizes remain <= 4 KiB and dword-aligned, enforced by `BUILD_BUG_ON`.

## Test Signals
Useful signals are build coverage, forced PCI transaction error paths, observed one-time register dumps, and clean behavior when the device lacks AER capability or parent/root-port references.
