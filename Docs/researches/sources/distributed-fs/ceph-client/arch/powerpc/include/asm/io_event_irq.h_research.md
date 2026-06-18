# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io_event_irq.h

Purpose: Defines pSeries I/O event interrupt payload format and notifier entry point for platform event-log I/O notifications.

Important APIs, types, and functions: Defines event type, subtype, and scope constants; `PSERIES_IOEI_RPC_MAX_LEN`; `struct pseries_io_event`; and global `pseries_ioei_notifier_list`.

Control flow: Firmware/platform code decodes an I/O event section, populates `struct pseries_io_event`, then notifies registered listeners through the atomic notifier chain.

State and persistence: Event structs are transient. The notifier list is runtime kernel state.

Dependencies and integration points: Depends on Linux notifier APIs and pSeries platform event logging. It integrates PCI/PHB, service processor, node online/offline, and device rebalance notifications.

Risks: RPC data length must not exceed the fixed 216-byte buffer. Atomic notifier callbacks must be safe in the context used by the event IRQ path.

Test signals: Inject event types/subtypes, maximum RPC length, multiple notifier registrations, callback failure ordering, and node/PHB rebalance notifications.
