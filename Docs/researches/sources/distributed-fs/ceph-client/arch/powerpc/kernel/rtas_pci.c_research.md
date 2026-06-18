# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_pci.c

Purpose: RTAS-backed PCI configuration-space operations and PHB setup for PowerPC platforms that access PCI config space through firmware calls.

Important APIs/types/functions: static RTAS token variables `read_pci_config`, `write_pci_config`, `ibm_read_pci_config`, `ibm_write_pci_config`; `config_access_valid()`, `rtas_pci_dn_read_config()`, `rtas_pci_read_config()`, `rtas_pci_dn_write_config()`, `rtas_pci_write_config()`, `rtas_pci_ops`, `is_python()`, `python_countermeasures()`, `init_pci_config_tokens()`, `get_phb_buid()`, `phb_set_bus_ranges()`, and `rtas_setup_phb()`.

Control flow: platform setup calls `init_pci_config_tokens()` to cache standard and IBM RTAS config tokens. `rtas_setup_phb()` applies the Python host bridge workaround if the PHB model matches, parses `bus-range`, assigns `rtas_pci_ops`, and records BUID from the PHB resource if IBM config tokens exist. Config reads/writes validate the `pci_dn`, range, optional extended config-space flag, and EEH blocked state; then they build `rtas_config_addr()` and call either IBM BUID-aware or standard RTAS config methods. Read paths default to all ones and integrate with EEH error detection.

State and persistence: persistent state is limited to cached tokens and PHB fields (`ops`, `buid`, bus range). The Python workaround mutates bridge MMIO state by clearing `PRG_CL_RESET_VALID`.

Dependencies and integration points: integrates with the PCI core through `struct pci_ops`, Open Firmware PCI node metadata, EEH state, `pci_dn`, `pci_controller`, and RTAS token/call APIs. Python workaround depends on OF address translation and big-endian MMIO accessors.

Risks: invalid bus-range or BUID detection can break all config cycles under a PHB. EEH blocked checks must prevent config access during recovery. Python register mapping clears a hardware bit based on model-string heuristics and assumes the register window size. Extended config access is allowed only when firmware/device node advertises it.

Test signals: boot on CHRP/pSeries PCI systems, enumerate devices behind BUID and non-BUID PHBs, read/write standard and extended config offsets, simulate EEH-blocked devices, and verify Python workaround logging on matching hardware.
