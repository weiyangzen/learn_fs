# sources/distributed-fs/ceph-client/drivers/ata/ahci.h

Purpose: shared AHCI header for register offsets, bit definitions, DMA/FIS layout sizes, private structures, host flags, SCSI template wiring, and prototypes used by PCI and platform AHCI drivers.

Important APIs/types: `AHCI_MAX_*` constants, `HOST_*` and `PORT_*` registers, EM masks, `AHCI_HFLAG_*`, `AHCI_FLAG_COMMON`, `struct ahci_cmd_hdr`, `struct ahci_sg`, `struct ahci_em_priv`, `struct ahci_port_priv`, `struct ahci_host_priv`, `AHCI_SHT()`, `ahci_ignore_port`, `ahci_port_base`, and `ahci_nr_ports`.

Control flow role: no runtime flow; defines the ABI used by libahci and edge drivers. Edge drivers fill `ahci_host_priv` with MMIO/resources/flags/callbacks before calling shared AHCI activation.

State/persistence: `ahci_host_priv` caches caps, port maps, EM config, remapped NVMe count, clocks, resets, regulators, PHYs, IRQ hooks, and engine callbacks. `ahci_port_priv` stores command slots/tables/FIS DMA memory, FBS state, interrupt mask, NCQ observations, and LED activity state.

Dependencies/integration: includes PCI, clock, libata, PHY, regulator, and bit helpers; declares shared helpers such as `ahci_save_initial_config`, `ahci_reset_controller`, `ahci_do_softreset`, `ahci_do_hardreset`, `ahci_qc_issue`, `ahci_host_activate`, and `ahci_handle_port_intr`.

Risks/test signals: register mask or structure changes affect every AHCI driver. Validate by build coverage, probe, DMA command completion, FBS/PMP, EM LED behavior, and suspend/resume resource handling.
