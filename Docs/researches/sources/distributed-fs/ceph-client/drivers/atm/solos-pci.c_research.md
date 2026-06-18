<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/solos-pci.c -->
# sources/distributed-fs/ceph-client/drivers/atm/solos-pci.c

## Purpose

This is the Traverse/Xrio Solos PCI ADSL2+ multiport ATM driver. It maps FPGA config/data RAM, registers one ATM device per port, moves ATM AAL5 PDUs and firmware command packets between Linux and the FPGA using MMIO or DMA, exposes modem parameters and GPIOs through sysfs, and optionally performs FPGA/firmware flash upgrades from named firmware blobs.

## Important APIs, types, and functions

Core protocol types are `struct pkt_hdr`, `struct solos_skb_cb`, `struct solos_card`, and `struct solos_param`. PCI entry points are `solos_pci_init()`, `fpga_probe()`, `fpga_remove()`, and `fpga_driver`. ATM operations are `popen()`, `pclose()`, `psend()`, and `fpga_ops`. Data path functions are `fpga_queue()`, `fpga_tx()`, `solos_irq()`, `solos_bh()`, `find_vcc()`, and `process_status()/process_command()`. Sysfs paths are `solos_param_show/store()`, `console_show/store()`, GPIO/hardware attributes, and the macro-included `solos-attrlist.c`. Firmware upgrade is handled by `flash_upgrade()`.

## Control flow

Probe allocates `solos_card`, enables PCI, sets a 32-bit DMA mask, requests BARs, maps config and data RAM, optionally resets the FPGA, reads FPGA version/port count/flash type, chooses MMIO or DMA transport, initializes locks/waitqueues/tasklet, requests IRQ, enables FPGA IRQs, optionally runs flash upgrades, then registers ATM devices. TX queues are per port: `psend()` prepends a packet header and calls `fpga_queue()`, which sets `tx_mask` and may immediately call `fpga_tx()`. `fpga_tx()` checks FPGA flags, dequeues eligible packets, copies to TX buffers or maps DMA, starts transmission, and completes old skbs. IRQs clear the FPGA IRQ register and schedule `solos_bh()` once ATM devices exist. The tasklet drains TX, receives packets, dispatches data to VCCs, status to link-state updates, and command replies to waiting sysfs callers or console queues.

## State and persistence behavior

Runtime state includes mapped FPGA registers, port count, version, flash type, per-port ATM devices, sk_buff queues, in-flight DMA skbs, bounce buffers, waitqueues, tasklet, tx masks, CLI queues, and pending parameter requests keyed by PID/port. Firmware/FPGA upgrade mode writes device flash and is the only durable behavior; normal sysfs parameter writes may also alter firmware-managed modem configuration. Remove disables IRQs, resets/releases FPGA mode, deregisters ATM devices, unmaps DMA, drains queues, unmaps BARs, and frees memory.

## Dependencies and integration points

The driver depends on PCI, ATM core, sk_buff APIs, DMA mapping, sysfs, firmware loader, waitqueues, tasklets, spinlocks, and global ATM VCC hash/list locking. It declares required firmware names and integrates with `/sys/class/atm`, PCI driver binding, and device firmware command protocols.

## Risks

Concurrency risk is high: TX queue, CLI queue, parameter queue, tasklet, IRQ, sysfs, and VCC close paths share skbs and VCC pointers. `pclose()` uses `tasklet_unlock_wait()` to avoid use-after-free after VCC close. DMA alignment requires bounce buffers. Firmware upgrade loops copy blocks to MMIO and wait on `fw_wq`; bad firmware size/block handling or timeouts can brick devices. `find_vcc()` depends on global ATM internals. The code uses fixed four-element arrays while `nr_ports` is read from hardware, so unexpected port counts would be dangerous. `print_buffer()` uses fixed stack strings and verbose debug paths that deserve care under malformed packet lengths.

## Test signals

Build `CONFIG_ATM_SOLOS`, bind supported PCI IDs, verify BAR mapping/version/port detection, ATM device registration, VCC open/close/send/receive, sysfs parameter read/write timeouts and responses, console queue limits, MMIO and DMA FPGA versions, IRQ/tasklet RX/TX paths, firmware upgrade with safe test images, hot remove, and lockdep/KASAN/KCSAN under concurrent sysfs and traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/solos-pci.c -->
