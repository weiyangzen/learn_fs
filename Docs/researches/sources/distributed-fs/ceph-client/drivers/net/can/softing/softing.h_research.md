# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing.h

Purpose: shared internal header for Softing DPRAM CAN driver objects. It defines per-bus and per-card state, exported internal functions, and the DPRAM layout/protocol constants used by firmware and runtime paths.

Important APIs/types/functions: `struct softing_priv` embeds `can_priv`, netdev/card pointers, TX echo ring counters, bittiming const, bus index, output mode, and chip ID. `struct softing` owns platform data, two netdev slots, spinlock, timestamp references, firmware lock/up state, IRQ bookkeeping, card-wide TX state, DPRAM mapping, and card identity. Function prototypes cover firmware loading, card power-on, IRQ enablement, bus start/stop, timestamp conversion, RX injection, and default output selection. DPRAM offsets define RX/TX FIFOs, function command mailboxes, reset/IRQ registers, time registers, and firmware command/receipt areas.

Control flow: no executable flow, but this header encodes the contract between `softing_main.c`, `softing_fw.c`, and platform providers. Runtime code uses the DPRAM offsets to queue TX/RX entries and send synchronous firmware functions.

State and persistence: all structs are volatile kernel/card runtime state. DPRAM fields are card-shared memory; host fields track firmware status, TX pending, timestamp overflow, and identity read from firmware. No disk persistence.

Dependencies/integration: depends on netdevice, SocketCAN, ktime, mutex/spinlock, atomic headers, and `softing_platform.h`. Consumers must hold the documented locks around firmware-up state and DPRAM access.

Risks: DPRAM offsets are ABI with firmware; errors cause silent card miscommunication. The card has up to two netdevs but one shared firmware state and TX FIFO, so per-bus operations are coupled. Ring constants determine echo skb capacity.

Test signals: compile both Softing objects; boot card and read identity; RX/TX FIFO offsets verified by traffic; state transitions tested on one and two bus configurations; timestamp conversion tested across overflow.
