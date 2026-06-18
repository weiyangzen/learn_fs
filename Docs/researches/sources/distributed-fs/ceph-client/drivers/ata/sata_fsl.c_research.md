# sources/distributed-fs/ceph-client/drivers/ata/sata_fsl.c

## Purpose
`sata_fsl.c` drives Freescale/PQ 3.0 Gbps SATA controllers. It implements a one-port-per-controller queued command engine with command headers/descriptors, NCQ, PMP, asynchronous notification, sysfs interrupt coalescing and RX watermark controls, and controller-specific hard/soft reset flows.

## Important APIs, Types, and Functions
Important structures are `struct cmdhdr_tbl_entry`, `struct command_desc`, `struct prde`, `struct sata_fsl_port_priv`, and `struct sata_fsl_host_priv`. Main functions include `fsl_sata_set_irq_coalescing()`, sysfs show/store methods, `sata_fsl_setup_cmd_hdr_entry()`, `sata_fsl_fill_sg()`, `sata_fsl_qc_prep()`, `sata_fsl_qc_issue()`, `sata_fsl_qc_fill_rtf()`, `sata_fsl_scr_read/write()`, `sata_fsl_freeze/thaw()`, `sata_fsl_port_start/stop()`, `sata_fsl_hardreset()`, `sata_fsl_softreset()`, `sata_fsl_error_intr()`, `sata_fsl_host_intr()`, `sata_fsl_interrupt()`, `sata_fsl_init_controller()`, and `sata_fsl_probe()`.

## Control Flow, State, and Persistence
Probe maps controller registers, derives SSR/CSR bases, configures RX watermark for non-MPC8315 variants, allocates host private data, obtains IRQ and data-snoop mode, initializes the controller offline with interrupts masked, activates libata, and creates `intr_coalescing` and `rx_watermark` sysfs files. Port start allocates coherent command-slot and command-descriptor memory, writes CHBA, and brings the controller online with PHY reset. `qc_prep` converts taskfiles to CFIS, copies ATAPI CDBs, builds PRDTs including one indirect extension segment when direct entries overflow, and writes command headers. `qc_issue` writes PMP target and queues the tag in `CQ`. Completion reads `CC`, clears completed bits, and calls `ata_qc_complete_multiple()`; error paths classify fatal, PHYRDY, SNotification, and per-device errors before freezing or aborting links.

## Dependencies and Integration Points
The driver depends on OF platform resources, libata PMP/NCQ infrastructure, coherent DMA memory, sysfs device attributes, controller-specific HCR/SSR/CSR registers, `sata_pmp_error_handler()`, and ATA reset helpers. It exposes module parameters for interrupt coalescing defaults and persists user-tuned coalescing/watermark values in hardware registers until reconfigured.

## Risks and Test Signals
Risks include command-tag reuse if `CQ` state and libata tags diverge, PRD indirect-chain mistakes, sysfs cleanup gaps after partial probe failure, PMP error attribution, hardreset timing assumptions, and data-length mismatch errata masking real ATAPI errors. Tests should cover NCQ queue depth 16, PMP attach/detach and per-link errors, ATAPI commands including length mismatch workaround, sysfs read/write validation, interrupt coalescing thresholds, hardreset/softreset with and without signature update, suspend/resume CHBA restoration, SG lists crossing direct-entry limits, and fatal/PHYRDY/SNotification interrupts.
