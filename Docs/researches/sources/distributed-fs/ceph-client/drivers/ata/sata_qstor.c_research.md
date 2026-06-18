# sources/distributed-fs/ceph-client/drivers/ata/sata_qstor.c

## Purpose
Implements the libata low-level driver for Pacific Digital QStor four-port SATA controllers. It drives a packet DMA engine for ATA DMA commands, uses MMIO/SFF register mode for other commands and reset/EH, handles the controller's status FIFO interrupt format, initializes global/channel FIFO and PHY state, and chooses 32- or 64-bit DMA masks based on the host bus.

## Important APIs, Types, And Functions
- `qs_port_info`, `qs_ata_pci_tbl`, and `qs_ata_ops` define a four-port SATA, PIO-polling, UDMA6 libata controller.
- `struct qs_port_priv` stores one coherent packet/PRD buffer, its DMA address, and whether the port is in MMIO or packet mode.
- Command path functions are `qs_qc_prep`, `qs_fill_sg`, `qs_packet_start`, and `qs_qc_issue`.
- Mode/reset/EH functions include `qs_enter_reg_mode`, `qs_reset_channel_logic`, `qs_freeze`, `qs_thaw`, `qs_prereset`, `qs_error_handler`, and SCR accessors.
- Interrupt and completion helpers include `qs_intr`, `qs_intr_pkt`, `qs_intr_mmio`, and `qs_do_or_die`.
- Probe/setup helpers include `qs_ata_setup_port`, `qs_port_start`, `qs_host_init`, `qs_set_dma_masks`, `qs_host_stop`, and `qs_ata_init_one`.

## Control Flow
Probe allocates a four-port host, enables PCI, maps BAR4, selects a DMA mask from the QStor physical-interface register, assigns per-port MMIO taskfile and SCR addresses at 0x4000-byte channel strides, performs global/channel reset and FIFO/CPB setup through `qs_host_init`, enables PCI bus mastering, and activates the host with `qs_intr`.

Before command prep, `qs_qc_prep` forces register mode. Non-DMA commands are left to libata SFF. DMA commands fill a 64-byte command packet: a host control block with flags, byte count, PRD count, and PRD DMA address; a device control block with PIO/DMA and LBA48 flags; and a register FIS from `ata_tf_to_fis`. Issue switches DMA commands to packet mode, clears channel errors, flushes memory writes, writes the run-packet command FIFO, and otherwise uses `ata_sff_qc_issue`.

Interrupt handling first drains packet completions from the host status FIFO, decoding valid entries for device status, host status, and port number. Successful or device-error packet statuses switch the port back to register mode and complete or abort/freeze through `qs_do_or_die`. Then MMIO-mode interrupts scan all ports, tolerate known spurious interrupts when no command is active by reading status, and route real active commands through `ata_sff_port_intr`.

## State And Persistence
Per-port state is the coherent packet/PRD allocation, the packet DMA address programmed into channel CPB base registers, and the `qs_state_mmio`/`qs_state_pkt` mode flag. Persistent hardware state includes global interrupt enable, global reset, PHY enable, per-channel register-vs-packet mode, channel/device reset bits, FIFO thresholds, CPB separation factor, command FIFO, status FIFO, SCR registers, and bus-width information. Host stop disables interrupts and asserts global reset.

## Dependencies And Integration Points
The driver depends on PCI managed resource mapping, DMA mask APIs, libata SFF helpers and EH, SCSI host templates, ATA FIS construction, and QStor/PDC PCI IDs. It integrates with libata through custom `qc_prep`/`qc_issue`, SCR callbacks, prereset/error-handler hooks that force register mode, and an IRQ handler that combines packet FIFO and normal SFF interrupt processing.

## Risks And Edge Cases
ATAPI DMA is explicitly unsupported and `qs_qc_issue` treats `ATAPI_PROT_DMA` as a bug. Packet mode/MMIO mode transitions are fragile and can generate spurious interrupts that the driver deliberately acknowledges. `qs_fill_sg` writes 64-bit addresses and lengths but advances by 16 bytes per PRD, so packet layout and `QS_MAX_PRD` sizing must match hardware. Host status FIFO decoding depends on valid/empty bits; mishandling can drop completions or spin. The DMA mask must match the bridge-visible bus width even though packet fields are always 64-bit.

## Test Signals
Useful tests include four-port probe with BAR4 MMIO descriptors, 32-bit and 64-bit DMA-mask selection, host/channel reset and FIFO setup, DMA packet issue/completion with status FIFO host status 0 and 3, device-error abort versus host-error freeze, MMIO fallback for PIO/no-data commands, spurious no-active-command interrupts, SCR read/write bounds, prereset forcing register mode, and host stop disabling interrupts plus global reset.
