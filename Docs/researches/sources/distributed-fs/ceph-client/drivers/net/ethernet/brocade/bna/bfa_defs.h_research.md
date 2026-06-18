# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs.h

Purpose: shared public definition header for BFA adapter, IOC, manufacturing, PCI, mode, and flash data structures used by the BNA/QLogic BR-series driver stack.

Important APIs/types/functions: defines size constants such as `BFA_VERSION_LEN`, adapter string lengths, and IOC string lengths. Key types include `struct bfa_adapter_attr`, `struct bfa_ioc_driver_attr`, `struct bfa_ioc_pci_attr`, `enum bfa_ioc_state`, `struct bfa_fw_ioc_stats`, `struct bfa_ioc_drv_stats`, `struct bfa_ioc_stats`, `enum bfa_ioc_type`, `struct bfa_ioc_attr`, `struct bfa_mfg_block`, `enum bfa_mode`, `struct bfa_flash_part_attr`, and `struct bfa_flash_attr`. It also defines adapter capability bits, PCI device/subsystem IDs, ASIC ID helpers, and flash partition constants.

Control flow: no executable flow. Runtime code fills these structures when firmware returns IOC attributes, manufacturing data, and flash partition tables. `bfa_ioc.c` uses the IOC state enum for state reporting and uses flash partition structures in flash query responses.

State and persistence behavior: structures describe both runtime status (`bfa_ioc_attr`, stats) and persistent manufacturing/flash data (`bfa_mfg_block`, VPD embedded via `bfa_defs_mfg_comm.h`, flash partition attributes). The manufacturing block is explicitly packed and documents big-endian numerical fields.

Dependencies and integration points: includes `cna.h`, `bfa_defs_status.h`, and `bfa_defs_mfg_comm.h`. Integrates with firmware message structures, adapter attribute reporting, ethtool/debugfs, flash management, and PCI probe logic.

Risks: structure layout and field widths are part of firmware/userspace-facing contracts; padding or endian mistakes can corrupt displayed adapter attributes or flash partition parsing. Capability and mode enums must stay synchronized with firmware definitions. Manufacturing fields are persistent identity data, so any writer must enforce checksums and bounds.

Test signals: compare `bfa_nw_ioc_get_attr` output against known adapter data, verify card type and capability decoding for CT/CT2 devices, and validate flash query conversion with realistic partition tables.
