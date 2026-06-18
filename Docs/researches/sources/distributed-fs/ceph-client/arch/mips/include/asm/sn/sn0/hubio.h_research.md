<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubio.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubio.h

Purpose: Defines SN0 hub I/O interface register offsets, BTE registers, widget/LLP control/status formats, I/O translation/error/CRB registers, PRB formats, and BTE control/status fields.

Important APIs/types/functions: Friendly aliases `IIO_WIDGET*`, raw offsets `IIO_WID`, `IIO_ILCSR`, `IIO_PRTE`, `IIO_ICRB_*`, BTE aliases and offsets; union formats `hubii_wid_t`, `hubii_wcr_t`, `hubii_wstat_t`, `hubii_ilcsr_t`, `icrba_t`, `icrbb_t`, `icrbc_t`, `icrbd_t`, `iprte_a_t`, `iprb_t`, `icrbp_a_t`, `hubii_idsr_t`; error/command constants `IIO_ICRB_ECODE_*`, `IIO_ICCR_CMD_*`, `IECLR_*`, `IBLS_*`, `IBCT_*`, widget constants.

Control flow: I/O setup and error handlers read widget/LLP state, program protection/access registers, configure PIO read table entries, inspect/deallocate CRBs, control BTE transfers, clear IO errors, and manage per-widget PRBs. The file warns that CRB writes require I/O quiescence.

State and persistence: Hardware state includes hub widget identity, LLP link state, scratch registers, ITTE/PRTE mappings, CRB/PRB queues, BTE length/source/destination/control/interrupt registers, interrupt destination, and error-clear latches.

Dependencies and integration points: Consumed by SN I/O setup, Xtalk/PCI bridge code, BTE DMA support, and IO error recovery. Relies on SN address accessors from includers.

Risks: CRB manipulation is explicitly dangerous if DMA/PIO is active. Several legacy duplicate field/macro names and typo-like aliases exist, so compiler coverage per config matters. Wrong BTE or PRB programming can corrupt memory or wedge I/O.

Test signals: SN I/O link bring-up, Xtalk/PCI probing, BTE transfer tests, IO error injection/recovery, and CRB dump tooling are useful signals.

Source read size: 972 lines, 31329 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubio.h -->
