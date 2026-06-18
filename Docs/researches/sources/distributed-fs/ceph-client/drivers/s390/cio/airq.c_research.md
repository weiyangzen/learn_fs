# sources/distributed-fs/ceph-client/drivers/s390/cio/airq.c

Purpose: supports s390 adapter interrupts and interrupt-vector allocation for CIO users such as QDIO and other adapter-backed devices.

Important APIs/types/functions: exports `register_adapter_interrupt`, `unregister_adapter_interrupt`, `airq_iv_create`, `airq_iv_release`, `airq_iv_alloc`, `airq_iv_free`, and `airq_iv_scan`; initializes interrupt handling with `init_airq_interrupts` and DMA pool with `airq_init`.

Control flow: registration validates handler/ISC, allocates a local-summary indicator when missing, registers the ISC, and RCU-adds the descriptor to the ISC list. Thin interrupt handler gets `tpi_info`, traces it, walks the ISC hlist under RCU, and calls handlers whose summary indicator is nonzero. Interrupt vectors may be cacheline DMA, guest-provided, or CIO DMA allocated; optional availability, bitlock, pointer, and data side arrays are allocated based on flags.

State and persistence: maintains one RCU hlist per ISC, a spinlock for list mutation, a DMA pool for cacheline vectors, and per-vector allocation metadata. No persistent storage.

Dependencies and integration: uses s390 `THIN_INTERRUPT`, ISC registration, CIO DMA helpers, dummy irq chip, tracepoints, RCU hlist APIs, DMA pools, and inverted-bit operations.

Risks: unregister must synchronize RCU before freeing indicators; `airq_iv_create` error unwind must match allocation mode, especially guest vectors; `airq_iv_alloc/free/scan` use inverted bit semantics; handlers are called only when summary indicators are nonzero.

Test signals: register/unregister across ISCs, interrupt delivery to multiple descriptors, RCU lifetime under concurrent interrupts, vector allocation/free/scan with all flag combinations, and DMA-pool failure paths.
