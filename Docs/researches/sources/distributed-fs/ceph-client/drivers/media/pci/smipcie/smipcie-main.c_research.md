<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/smipcie-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/smipcie-main.c

Purpose: main SMI PCIe DVBSky driver. It probes PCI cards, maps MMIO, initializes hardware, bit-banged I2C, TS DMA ports, DVB frontend/demux/net plumbing, IR support, interrupts, and supported board tables.

Important APIs, types, and functions: `smi_probe()` and `smi_remove()` own lifecycle. `smi_hw_init()` configures muxes, DTV registers, interrupts, and demod reset. `smi_i2c_init()` creates two bit-banged I2C adapters. `smi_port_init()` allocates coherent TS DMA buffers and work items. `smi_dma_xfer()` feeds completed DMA buffers into DVB demux and restarts DMA. `smi_fe_init()` attaches demod/tuner combinations. `smi_dvb_init()` registers DVB core objects. `smi_start_feed()` and `smi_stop_feed()` drive DMA by feed count.

Control flow: probe enables PCI, maps BAR0, sets 32-bit DMA, initializes hardware/I2C, attaches enabled TS ports from board config, initializes IR, optionally enables MSI, requests IRQ, then starts IR. IRQ dispatch fans out to port DMA handlers and IR. DMA IRQ queues bottom-half work that validates transfer length, swfilters packets, restarts channels, and re-enables interrupts.

State and persistence: state is in `smi_dev`, two `smi_port`s, two I2C adapters, coherent DMA buffers, frontend/tuner I2C clients, DVB objects, and IR state. EEPROM is read for proposed MAC addresses; no writes are performed.

Dependencies and integration points: PCI, DMA, I2C algo-bit, DVB core/demux/net, m88ds3103, ts2020, m88rs6000t, si2168, si2157, RC core, and board-specific PCI IDs.

Risks: feed `users` is not protected by a mutex in start/stop paths. Probe error unwind is detailed but cross-port/IR/MSI ordering must stay balanced. `i2c_client_has_driver()` is called on clients returned by `i2c_new_client_device()` without an explicit `IS_ERR()` check in helper. DMA completion accepts mismatched lengths after debug logging.

Test signals: card detection for all PCI IDs, I2C bus scan/attach, frontend lock on each port, feed start/stop cycles, DMA packet continuity, MAC assignment from EEPROM, IR operation, MSI and shared IRQ operation, and clean remove after active feeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/smipcie-main.c -->
