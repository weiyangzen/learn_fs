# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-sata.c

Purpose: Provides Broadcom SATA PHY initialization for STB 16/28/40 nm, iProc NS2/NSP/Stingray, and DSL 28 nm variants, with optional spread-spectrum clocking, receive equalization, and TX amplitude tuning.

Important APIs and types: `struct brcm_sata_phy` owns common MMIO bases, version, and up to two `brcm_sata_port` entries. Each port stores `ssc_en`, `rxaeq_mode`, `rxaeq_val`, and `tx_amplitude_val` from child DT properties. Register helpers select PCB banks and account for 28 nm versus 40 nm per-port spacing.

Control flow: probe requires child port nodes, maps the `phy` resource and optionally `phy-ctrl` for NS2, selects version from compatible, creates one PHY per child `reg`, reads port tuning properties, and registers a simple provider. Init dispatches by version: STB variants set SSC/TX frequency and RX AEQ, 16 nm applies detailed CDR/PPM/TX amplitude settings, NS2/NSP/SR/DSL program OOB/PLL registers and poll PLL lock. Calibrate is supported only on STB 28/40 nm and enables RX frequency monitor correction.

State and persistence: Per-port DT tuning persists in memory. Hardware state is banked PHY register programming and optional NS2 PHY-control reset pulses.

Dependencies and integration: It depends on generic PHY, platform resources named `phy` and sometimes `phy-ctrl`, OF child nodes, and compatible-specific variant selection. AHCI/SATA controllers consume child PHYs.

Risks and test signals: Many values are characterized magic constants; PLL lock timeout is the main hard failure. Manual RX AEQ validates only the value range. Test each compatible, both port ids, duplicate/invalid child regs, SSC on/off, manual/auto/off RX AEQ, TX amplitude values 400/500/600/800/default, PLL timeout paths, and calibrate support returning `-EOPNOTSUPP` on unsupported variants.
