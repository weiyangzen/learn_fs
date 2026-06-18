# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_regs.h

Purpose: This header provides the low-level MMIO helper contract for Ionic interrupt-control registers and queue doorbells. It defines the interrupt register layout, legal mask/credit bit encodings, coalescing maximums, doorbell bit packing macros, and inline write/read helpers used by queue and NAPI code.

Important APIs/types: `struct ionic_intr` maps one interrupt-control register block with `coal_init`, `mask`, `credits`, `mask_assert`, and current `coal`. `enum ionic_intr_mask_vals` defines mask and unmask values. `enum ionic_intr_credits_bits` defines the credit count mask, signed count mask, unmask bit, reset-coalesce bit, and combined rearm value. Inline functions are `ionic_intr_coal_init()`, `ionic_intr_mask()`, `ionic_intr_credits()`, `ionic_intr_clean()`, `ionic_intr_mask_assert()`, and `ionic_dbell_ring()`. Doorbell macros `IONIC_DBELL_QID()` and `IONIC_DBELL_RING()` compose queue ID and ring selector fields, with `IONIC_DBELL_INDEX_MASK` reserved for producer index bits supplied by callers.

Control flow: These helpers are small MMIO operations. Queue setup initializes coalescing and masks interrupts. Queue enable cleans credits, enables NAPI, installs affinity hints, and unmasks with `ionic_intr_mask()`. NAPI completion returns processed credits plus unmask/reset flags with `ionic_intr_credits()`. Queue disable masks interrupts and synchronizes IRQs. Doorbell ring writes a 64-bit value to the queue-type slot in a mapped doorbell page.

State and persistence behavior: Interrupt mask, coalescing, and credit state live in device MMIO registers and persist until explicitly changed or device reset. `ionic_intr_clean()` preserves the signed outstanding credit count while resetting coalescing. `ionic_intr_credits()` guards against credit values larger than the hardware count field and falls back to the current signed count before writing flags.

Dependencies: The header depends on Linux `io.h` accessors and the device BAR mappings established by bus/device code. It is consumed by `ionic_lif.c`, queue code, adminq service, and datapath NAPI handlers.

Integration points: Interrupt helpers integrate with MSI-X allocation, NAPI poll completion, DIM coalescing updates, queue enable/disable, and firmware queue initialization through interrupt indices. Doorbell helpers integrate with queue producer updates for admin, notify, Tx, Rx, and RDMA-style queues via the mapped per-LIF doorbell page.

Risks: Incorrect credit accounting can leave interrupts masked, over-credit hardware, or produce interrupt storms. Coalescing values are device units, so callers must convert from microseconds correctly. Doorbell writes rely on qtype indexing into the mapped page; wrong qtype or QID composition can ring the wrong queue. MMIO ordering assumptions are delegated to `iowrite32()`/`writeq()` and caller-side queue posting barriers.

Test signals: Validate interrupt mask/unmask on queue enable/disable, NAPI credit return under heavy Tx/Rx, coalescing changes through ethtool/DIM, interrupt affinity movement, adminq doorbell workaround behavior, and queue progress after firmware reset. Hardware counters or dynamic debug should show no stuck queues, lost interrupts, or excessive interrupt rates.
