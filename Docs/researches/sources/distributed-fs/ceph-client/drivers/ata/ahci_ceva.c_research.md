# sources/distributed-fs/ceph-client/drivers/ata/ahci_ceva.c

Purpose: CEVA/Xilinx AHCI platform driver programming vendor AXI/cache, OOB timing, PHY timing, Rx watermark, and speed policy registers from device tree.

Important APIs/types: `struct ceva_ahci_priv`, `ceva_ahci_read_id`, `ahci_ceva_setup`, `ceva_ahci_platform_enable_resources`, `ceva_ahci_probe`, `ceva_ahci_suspend`, `ceva_ahci_resume`, module param `rx_watermark`, and DT flag `ceva,broken-gen2`.

Control flow: probe gets resources/reset, enables regulators/clocks/resets/PHYs in a CEVA-specific sequence, parses required timing arrays for two ports, detects DMA coherency for CCI cache config, stores private data, runs register setup, and activates the host. Resume repeats resource enable/setup before host resume.

State/persistence: per-port PP2C/PP3C/PP4C/PP5C timing values, AXI cache policy, CCI flag, broken Gen2 flag, AHCI enable, SControl speed/IPM, and powered PHY/reset state. Read-ID clears IDENTIFY DEVSLP support because hardware lacks it.

Dependencies/integration: DT properties, optional reset control, generic PHY, `ahci_platform`, libata identify handling, and `AHCI_SHT`.

Risks/test signals: required DT properties can fail probe; casts of byte/halfword properties assume size/endian expectations; broken Gen2 forces Gen1. Test DT validation, negotiated speed, DEVSLP masking, coherent DMA, and resume.
