# sources/distributed-fs/ceph-client/drivers/pci/pcie/tlp.c

## Purpose
This file centralizes PCIe Transaction Layer Packet (TLP) log length calculation, config-space reads, and printk formatting for AER and DPC error reporting. It handles both conventional four-DWORD TLP header logs with optional end-to-end prefixes and newer Flit-mode logs whose length is encoded in capability registers.

## Important APIs, types, and functions
`aer_tlp_log_len()` calculates an AER header/prefix length from the AER Capabilities and Control register and `dev->eetlp_prefix_max`. `dpc_tlp_log_len()` is compiled under `CONFIG_PCIE_DPC` and derives DPC RP PIO log length from `dev->dpc_rp_log_size`, excluding the implementation-specific log register. `pcie_read_tlp_log()` reads DWORDs from header and prefix config offsets into `struct pcie_tlp_log`. `pcie_print_tlp_log()` formats the captured DWORDs for kernel logs.

## Control flow
A caller determines the log size, calls `pcie_read_tlp_log()` with the config offsets for the header and optional prefix areas, then passes the filled `struct pcie_tlp_log` to `pcie_print_tlp_log()`. The reader clamps the requested length to the destination array size, clears the log, reads the standard header first, and then switches to the second offset for prefix DWORDs. It records `header_len` as the full Flit length or four DWORDs for non-Flit mode.

## State and persistence
The file does not retain state. It consumes per-device capability state initialized elsewhere, notably `eetlp_prefix_max` and DPC log size, and writes only into caller-provided `struct pcie_tlp_log`. Output is transient kernel logging.

## Dependencies and integration points
The code depends on PCI config accessors, AER/DPC register definitions, `FIELD_GET()`, `ARRAY_SIZE()`, and the PCI core's `struct pcie_tlp_log` layout. It is used by PCIe AER and DPC paths when reporting captured request/completion headers after errors. It also depends indirectly on `probe.c` configuring E-E Prefix support so prefix length calculation reflects the path capability.

## Risks
For non-Flit mode, `pcie_read_tlp_log()` hard-codes `header_len` to four DWORDs even if the exact packet header length could be shorter; this is acknowledged in the comment and means formatting is conservative rather than parsed. `pcie_print_tlp_log()` only prints non-Flit prefixes until it reaches a zero prefix DWORD, so a valid zero-valued prefix would terminate printing. Length calculations depend on correct capability values; oversized values are clamped silently to the local buffer.

## Test signals
Exercise AER logs with no prefixes, with E-E prefixes, and with Flit-mode `PCI_ERR_CAP_TLP_LOG_FLIT`. DPC builds should validate the implementation-specific register subtraction. Fault injection should show expected DWORD order and offsets in logs, and config-read failure tests should verify `pcibios_err_to_errno()` propagation without partial stale log content.
