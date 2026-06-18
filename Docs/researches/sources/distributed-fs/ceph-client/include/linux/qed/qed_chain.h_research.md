# sources/distributed-fs/ceph-client/include/linux/qed/qed_chain.h

Purpose: implements QED's generic DMA ring/chain abstraction used for producer/consumer queues, including single-page, next-pointer linked-page, and PBL-backed modes with 16-bit or 32-bit producer/consumer counters.

Important APIs/types/functions: `enum qed_chain_mode`, `qed_chain_use_mode`, and `qed_chain_cnt_type` define layout and counter semantics. `struct qed_chain` stores fast-path element pointers, PBL address table, counter union, capacity, page/element sizing, mode, slow-path allocation metadata, and optional external PBL state. `struct qed_chain_init_params` describes allocation input. Macros calculate elements per page, unusable next-pointer slots, usable elements, and page count. Inline APIs include producer/consumer index getters, used/left calculations, `qed_chain_advance_page`, `qed_chain_return_produced`, `qed_chain_produce`, `qed_chain_get_capacity`, `qed_chain_recycle_consumed`, `qed_chain_consume`, `qed_chain_reset`, `qed_chain_get_last_elem`, `qed_chain_set_prod`, and `qed_chain_pbl_zero_mem`.

Control flow: queue allocation fills a `qed_chain` with pages and optional PBL metadata. Producers call `qed_chain_produce()` to get the next writable element and later ring a doorbell; consumers call `qed_chain_consume()` for firmware-produced elements. In consume-mode chains, reset pre-produces empty elements by recycling consumed entries. When an index reaches the last usable slot on a page, `qed_chain_advance_page()` wraps via linked `qed_chain_next`, resets to the single page base, or advances through the PBL address table.

State and persistence: chain state is in-memory driver state plus DMA pages visible to firmware. Producer/consumer indices and page indices persist for the queue lifetime and are mutated on every enqueue/dequeue. PBL tables and chain pages must remain DMA-mapped until queue teardown.

Dependencies and integration points: depends on Linux types/list/sizes/slab, byteorder, and `common_hsi.h` `regpair`. Allocation/free are exposed through `qed_common_ops.chain_alloc` and `chain_free` in `qed_if.h`; chains back Ethernet BDs/CQEs, storage queues, LL2 queues, SPQ-style single chains, and RDMA rings.

Risks: off-by-one errors around unusable next-pointer slots, non-power-of-two element counts, page wrapping, 16-bit counter overflow, and `qed_chain_set_prod()` page-index rewind can corrupt queue state. Callers must check `qed_chain_get_elem_left()` before producing; the helpers do not enforce capacity. PBL mode assumes address table validity and stable DMA mappings.

Test signals: unit-test page-count/usable-element macros, produce/consume across page boundaries for all modes, U16/U32 wraparound, reset behavior for all intended-use modes, `qed_chain_set_prod()` rewind/advance in PBL mode, and zeroing PBL memory. Hardware tests should stress RX/TX rings with small page counts and maximum BD occupancy.
