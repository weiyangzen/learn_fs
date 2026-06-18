# sources/distributed-fs/ceph-client/drivers/ata/ahci_dwc.c

Purpose: Synopsys DesignWare AHCI driver that validates synthesized capabilities, initializes CCC/DevSlp timer, programs per-port DMA transaction sizes, and preserves them over PM.

Important APIs/types: `struct ahci_dwc_plat_data`, `struct ahci_dwc_host_priv`, `ahci_dwc_check_cap`, `ahci_dwc_init_timer`, `ahci_dwc_init_dmacr`, `ahci_dwc_init_host`, `ahci_dwc_reinit_host`, `ahci_dwc_clear_host`, `ahci_dwc_probe`, suspend/resume hooks.

Control flow: probe gets resources with resets, enables resources, optionally runs platform init, masks unsupported MPS/CPD/FBS bits from DWC parameter registers, updates the 1 ms timer from `aclk`, parses child-node `snps,tx-ts-max`/`snps,rx-ts-max`, saves DMACR, and activates. Resume restores timer and DMACR before host resume.

State/persistence: platform callbacks, platform device, saved timer value, saved DMACR per AHCI port, modified capability/port-cap bits, and resource state.

Dependencies/integration: OF match data, `ahci_platform`, clock lookup, child-node DT properties, bitfield helpers, and custom `.host_stop`.

Risks/test signals: capability masking changes exposed hardware features; invalid DT transaction sizes rely on hardware clamping; timer accuracy depends on `aclk`. Test warning logs, DT parsing, DMACR preservation, CCC/DevSlp, and suspend/resume.
