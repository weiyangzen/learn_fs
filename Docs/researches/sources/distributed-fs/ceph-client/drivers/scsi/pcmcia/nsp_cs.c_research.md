# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_cs.c

Purpose: full 16-bit PCMCIA WorkBit NinjaSCSI-3/NinjaSCSI-32Bi SCSI host driver. It handles PCMCIA configuration, SCSI host registration, queueing, arbitration/selection, phase-driven interrupt handling, PIO/MMIO FIFO transfers, SDTR negotiation, reset, suspend, and resume.

Important APIs/functions: `nsp_queuecommand()` initializes command-private SG cursors and starts selection through `nsphw_start_selection()`. `nsphw_init()`, `nsp_setup_fifo()`, `nsp_nexus()`, `nsp_pio_read()`, `nsp_pio_write()`, `nsp_fifo_count()`, `nsp_analyze_sdtr()`, and `nspintr()` implement hardware sequencing. PCMCIA lifecycle uses `nsp_cs_probe()`, `nsp_cs_config()`, `nsp_cs_release()`, `nsp_cs_detach()`, suspend, and resume. Module parameters are `nsp_burst_mode` and `free_ports`.

Control flow/state: the driver accepts one active command via `CurrentSC`. The ISR advances selection timeout, reselection, command, data, status, message-in/out, bus reset, bus free, and completion. `nsp_hw_data` stores base/MMIO addresses, FIFO count, transfer mode, timers, per-target SDTR state, message buffer, lock, and PCMCIA glue. Per-command `struct scsi_pointer` stores phase, status/message, SG pointer, residual, and direction.

Dependencies/integration: PCMCIA, SCSI midlayer, `nsp_cs.h`, `nsp_io.h`, direct `nsp_message.c`, and optional `nsp_debug.c`.

Risks/test signals: risks include polling in interrupt context, single-command state, old pointer/MMIO assumptions, alignment-sensitive burst modes, and quirks for skipped data phases. Test probe/scan, IO8/IO32/MEM32 transfer, SDTR display, timeout, reselection, bus reset, suspend/resume, and removal.
