# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_main.c

Purpose: generic platform driver and runtime data path for Softing DPRAM CAN cards. It boots firmware, creates up to two CAN netdevs, handles TX/RX FIFOs, threaded interrupts, sysfs attributes, and platform-device lifecycle.

Important APIs/types/functions: `softing_netdev_start_xmit()` queues CAN frames into the DPRAM TX FIFO. `softing_handle_1()` processes one RX FIFO or status/lost-message event. `softing_irq_v1()`/`softing_irq_v2()` acknowledge hardware IRQ status; `softing_irq_thread()` drains DPRAM and wakes queues. `softing_enable_irq()` requests/frees threaded IRQs. `softing_card_boot()` validates DPRAM, loads firmware, starts app, and powers on chips. `softing_netdev_create()` configures per-bus CAN devices. Platform callbacks `softing_pdev_probe()` and `softing_pdev_remove()` own mapping, boot, sysfs, and registration.

Control flow: platform probe validates platform data, allocates card state, maps DPRAM, records IRQ, boots the card, creates platform sysfs attributes, allocates/registers netdevs for discovered chip IDs, and publishes readiness. Netdev open calls `open_candev()` then `softing_startstop(up=1)`; stop calls card-wide startstop down. TX encodes command flags, bus ID, CAN ID/DLC/data into FIFO slot, advances hardware write pointer, stores echo skb, and may stop all queues if card FIFO is full. IRQ top halves clear generation-specific IRQ flags and wake the thread; thread drains RX/status entries, updates stats/error states, completes TX echoes, and wakes eligible queues.

State and persistence: card state includes firmware up/down, DPRAM mapping, IRQ request state, card-wide and per-bus TX pending rings, timestamp references, identity, sysfs-visible output/chip fields, and netdev stats. Sysfs `output` is mutable only while netdev is down and persists until device removal.

Dependencies/integration: platform bus, firmware helpers in `softing_fw.c`, SocketCAN, DPRAM I/O barriers, threaded IRQs, sysfs, ethtool timestamp info, and platform data from PCMCIA or other bridge drivers.

Risks: TX/RX FIFO pointer arithmetic and shared card spinlock are critical. RX lost-message reporting is broadcast to active buses because the card does not identify the bus. Error state handling manually updates `priv->can.state` and invokes `can_bus_off()`. Probe creates `ARRAY_SIZE(card->net)` netdevs, so platform `nbus` validation and discovered chip IDs must be coherent. Failure paths must avoid double unregister/free after partially registered netdevs.

Test signals: probe with valid platform data and firmware; DPRAM memory self-test failure; RX normal, RTR, EFF, and error status frames; TX ACK echo completion; FIFO full queue stopping/waking; sysfs output write while up/down; generation 1 and 2 IRQ paths; remove with active netdevs.
