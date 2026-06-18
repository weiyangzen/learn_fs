<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sil24.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_sil24.c

## Purpose

This is the libata PCI driver for Silicon Image 3124/3132/3131/3531 SATA-II controllers. Unlike classic SFF controllers, it uses PRB/SGE command blocks, 64-bit command activation registers, NCQ, port multipliers, asynchronous notification, and controller-specific error classification.

## Important APIs, types, and functions

The file defines hardware command structures `struct sil24_prb`, `struct sil24_sge`, `struct sil24_ata_block`, `struct sil24_atapi_block`, `union sil24_cmd_block`, and `struct sil24_port_priv`. `sil24_ops` supplies queue defer, prep, issue, result taskfile fill, reset, PMP attach/detach, freeze/thaw, error handling, internal command cleanup, port start, SCR access, and PM resume callbacks. The central functions are `sil24_qc_defer()`, `sil24_qc_prep()`, `sil24_qc_issue()`, `sil24_error_intr()`, `sil24_host_intr()`, `sil24_interrupt()`, `sil24_init_port()`, `sil24_softreset()`, `sil24_hardreset()`, `sil24_port_start()`, `sil24_init_controller()`, and `sil24_init_one()`.

## Control flow

Probe maps host BAR0 and port BAR2, applies PCI-X completion-IRQ workaround detection, allocates one to four ports from encoded flags, sets a 64-bit DMA mask, optionally enables MSI, initializes ports, and activates the host. Each port start allocates a page-sized coherent command block array for 31 tags. Queue prep fills a PRB FIS and SGEs, with ATAPI CDB storage in a separate layout; issue writes the command block DMA address to the tag's activation register. Interrupts read global host status, dispatch per-port status, complete multiple tags from `PORT_SLOT_STAT`, or analyze attention/error status through command error lookup and libata EH actions.

## State and persistence behavior

Per-port private state tracks the coherent command block DMA base and whether a full port reset is needed. PMP attachment temporarily toggles port-multiplier enable and may disable NCQ for a Marvell 4140 quirk. The module parameter `msi` controls MSI use. All state is runtime-only and is rebuilt on probe/resume.

## Dependencies and integration points

The driver depends on PCI, DMA mapping, libata NCQ/PMP helpers, SCSI queue-depth plumbing, IRQ handling, and optional PM. It exposes NCQ queue-depth controls through the SCSI host template and integrates with SATA PMP error handling through `sata_pmp_error_handler()`.

## Risks

The command block layout must remain exactly page-sized and hardware-aligned. `sil24_qc_defer()` serializes ATAPI/result-taskfile commands to avoid an LRAM read corruption erratum. PMP mode has a DMA context-switch erratum when three or more links are active, forcing reset. Error decoding must map `PORT_CMD_ERR` precisely; unknown or protocol errors freeze/reset. The source duplicates the `SIL24_FLAG_PCIX_IRQ_WOC` enum line in the viewed file, which is another build-surface risk if not preprocessed away.

## Test signals

Build and boot on 3124/3132/3131 variants, run NCQ queue-depth stress, ATAPI packet commands, passthrough commands needing result taskfiles, PMP attach/detach with multiple disks, MSI and INTx modes, suspend/resume, and injected command errors. Expected signals include correct multi-tag completion, reset after injected protocol/PCI errors, no LRAM corruption under exclusive commands, and stable PMP notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sil24.c -->
