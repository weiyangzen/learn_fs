<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip_core.c

Purpose: Main PCI/netdevice driver for Digital 21x4x Tulip and many compatible Ethernet chips. It owns module parameters, PCI ID matching, probe/remove, open/close, ring allocation, TX, multicast filtering, media startup, WOL, and power management.

Important APIs and functions: `tulip_tbl[]` maps chip IDs to names, I/O sizes, valid interrupts, flags, media timers, and work callbacks. `tulip_init_one()` performs PCI enablement, resource mapping, DMA ring allocation, EEPROM/MAC reading, media option setup, EEPROM parsing, MII probing, netdev registration, and initial transceiver setup. `tulip_open()`, `tulip_up()`, `tulip_close()`, and `tulip_down()` manage IRQs, NAPI, timers, RX/TX rings, interrupts, and power state. `tulip_start_xmit()` queues TX descriptors. `tulip_tx_timeout()` and `tulip_tx_timeout_complete()` recover from stuck TX. `set_rx_mode()` builds hash/perfect setup frames or programs hash registers. Ettool and private MII ioctls expose WOL and PHY state.

Control flow: Module init copies parameters into interrupt globals and registers `tulip_driver`. Probe builds `struct tulip_private`, reads hardware identity, applies chip quirks, and registers a netdev. Open initializes rings, requests IRQ, calls `tulip_up()`, then starts the queue. Runtime TX/RX completion is handled in `interrupt.c`; this file supplies TX enqueue and teardown. Timers/media work adapt link settings. Suspend tears down active devices and configures wake events; resume restores IRQ and restarts hardware.

State and persistence: Runtime state lives in `tulip_private`, netdev stats, descriptor rings, skb mappings, EEPROM cache, module arrays `options[]`, `full_duplex[]`, `mtu[]`, and WOL options. Hardware state spans CSR0/CSR3/CSR4/CSR5/CSR6/CSR7 and chip-specific CSRs. No source-controlled persistence.

Dependencies and integration: Uses Linux PCI managed resources, DMA APIs, netdevice, ethtool, MII, CRC, NAPI optionally, and submodules declared in `tulip.h`. Integrates with `eeprom.c`, `media.c`, `timer.c`, `pnic*.c`, `21142.c`, and `interrupt.c`.

Risks: Large hardware matrix with many vendor quirks. EEPROM absence and multiport MAC derivation can generate fake addresses. TX setup frames share the TX ring with packets. DMA mapping/unmapping, queue stopping, and descriptor ownership ordering are critical. WOL support is COMET-specific. PM paths free IRQs and depend on netif state correctness.

Test signals: PCI probe for each ID class, EEPROM-present and missing cases, forced media/module options, MII ioctl reads/writes, TX timeout recovery, multicast perfect/hash modes, NAPI and non-NAPI builds, suspend/resume with and without WOL, and remove while interface is down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip_core.c -->
