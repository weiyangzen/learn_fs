# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg_def.h

Purpose: this header is the low-level hardware register, bit-mask, interrupt, OOB/PHY, sequencer-CIO, sequencer-scratch, PCI/EXSI, and timer address contract for the aic94xx SAS/SATA driver. It is intentionally data-only: consumers such as `aic94xx_reg.h`, `aic94xx_seq.c`, `aic94xx_scb.c`, and the HWI path use these constants to issue memory-mapped register reads/writes without open-coded offsets.

Important APIs/types/functions: there are no functions or C types beyond macros. The important surfaces are register base/address macros such as `COMBIST`, `COMSTAT`, `CHIMINT`, `CMDCTXBASE`, `CARP2CTL`, `CSEQm_CIO_REG()`, `LmSEQ_PHY_REG()`, `LmARP2CTL()`, `LmPRMSTAT0()`, and `LmSCRATCH()`. Bit groups include reset/BIST bits, done-list availability and exception interrupt masks, overlay-DMA controls, ARP2 pause/halt flags, CSEQ/LSEQ interrupt masks, primitive status masks, OOB status/clear/enable bits, PHY tuning values, PCI config offsets, flash BAR access offsets, and scratch-memory aliases such as `CSEQ_Q_EXE_HEAD` and `LmSEQ_CONNECTION_STATE`.

Control flow and state: the file does not execute control flow, but it defines the state machine vocabulary used elsewhere. Sequencer setup writes CSEQ/LSEQ queue heads, tails, interrupt vectors, timeout constants, and `DDB 0` link maps through these scratch offsets. Event handling decodes done-list status with primitive/OOB masks. PHY control builds `CONTROL_PHY` SCBs from `FUNCTION_MASK_DEFAULT`, `SPEED_MASK`, `CURRENT_*`, and OOB constants. Firmware download uses overlay-DMA constants such as `OVLYDMACTL`, `STARTOVLYDMA`, `OVLYCSEQ`, and `OVLYDMADONE`.

Persistence behavior: none in the filesystem sense. The persistence is hardware-resident: register values, sequencer scratch RAM, SCB/DDB context memory, and flash-bar configuration survive only according to adapter reset/firmware behavior. Incorrect constants can corrupt hardware state across tasks until a chip reset.

Dependencies and integration points: depends on `REG_BASE_ADDR`, `REG_BASE_ADDR_CSEQCIO`, and `REG_BASE_ADDR_EXSI` from `aic94xx_reg.h`. It is coupled to the sequencer firmware ABI and to packed SCB/DDB layouts from `aic94xx_sas.h`; offsets written in `aic94xx_seq.c` must match the firmware's expected scratch layout.

Risks: high blast radius from any offset or mask change. Duplicate macro definitions exist for a few names, so refactors must avoid accidentally changing semantics. Endianness is implicit in the caller helpers, not this file. Several masks define hardware errata/workarounds and are hard to validate without real controllers.

Test signals: a successful kernel build catches syntax and missing macro users. Runtime signals are adapter probe, sequencer firmware download/verify, phy bring-up, link reset events, done-list interrupts, and task I/O on SAS/SATA targets. Hardware or emulation is required for meaningful regression confidence.
