# subset-b-005871 grouped research

Grouped research for Linux mailbox, MDIO/MEI, early-memory, NUMA/memcg, MemoryStick, and PM80x headers under the ceph-client source tree. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-vcp-mailbox.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-vcp-mailbox.h

## Purpose
This header defines the client-visible payload contract for the MediaTek VCP mailbox controller. It is a compact IPC descriptor used between VCP IPC code and the mailbox driver, pairing a shared buffer with mailbox signal metadata.

## Important APIs, types, and functions
`MTK_VCP_MBOX_SLOT_MAX_SIZE` fixes the maximum mailbox slot payload at `0x100` bytes. `struct mtk_ipi_info` carries `msg`, `len`, logical `id`, hardware signal `index`, shared-memory `slot_ofs`, and latched `irq_status`. There are no functions; consumers pass the structure to mailbox send/receive paths.

## Control flow
Client code fills the descriptor with a message buffer, length, identifier, slot offset, and signal index before handing it to the mailbox controller. RX-side code can use `irq_status` to communicate captured interrupt bits back to higher IPC layers.

## State and persistence
The header owns no persistent state. All fields are per-message or per-channel runtime metadata, and `msg` points at externally owned shared memory.

## Dependencies and integration points
It depends on Linux integer types being visible to includers and integrates with the `mtk-vcp-mailbox` driver and VCP IPC users that know the shared-buffer layout.

## Risks and test signals
The key risks are length overruns beyond `MTK_VCP_MBOX_SLOT_MAX_SIZE`, stale or invalid shared-buffer pointers, mismatched `slot_ofs`, and confusion between logical `id` and hardware `index`. Test by sending boundary-size messages, validating RX interrupt status propagation, and exercising multiple signal indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-vcp-mailbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/riscv-rpmi-message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/riscv-rpmi-message.h

## Purpose
This header defines the Linux mailbox message ABI for RISC-V RPMI service groups. It includes wire headers, service/message identifiers, error translation, helper initializers, and a send helper that bridges RPMI messages to the generic mailbox framework.

## Important APIs, types, and functions
Wire-level structures are `struct rpmi_message_header`, `struct rpmi_message`, and `struct rpmi_notification_event`. `enum rpmi_error_codes` maps RPMI negative status values, while `rpmi_to_linux_error()` converts them to Linux errno values. Service identifiers cover system MSI and clock service groups. The Linux mailbox wrapper is `struct rpmi_mbox_message`, whose union represents attribute operations, request/response service data, or notification events. Initializers include `rpmi_mbox_init_get_attribute`, `rpmi_mbox_init_set_attribute`, `rpmi_mbox_init_send_with_response`, and `rpmi_mbox_init_send_without_response`; `rpmi_mbox_send_message()` sends through `mbox_send_message()` and reports completion with `mbox_client_txdone()`.

## Control flow
Callers initialize a `rpmi_mbox_message` for one of the supported message types, pass it to `rpmi_mbox_send_message()`, and then inspect `msg->error` plus response fields. The send helper treats a negative mailbox submission as transport failure; otherwise it uses the controller/client-populated `msg->error` as the transaction result and explicitly completes the mailbox TX state machine.

## State and persistence
State is transient and message-local. Request and response pointers remain caller-owned; `out_response_len` and `error` are expected to be filled during mailbox handling. No persistent state is stored in this header.

## Dependencies and integration points
The header depends on errno constants, mailbox client APIs, endian-sized Linux types, and `upper_16_bits`/`lower_16_bits`. It integrates RPMI clock and system-MSI service clients with generic mailbox channels.

## Risks and test signals
Risks include endian mistakes in wire headers, stale request/response buffers, service IDs exceeding firmware support, response truncation when `max_response_len` is too small, and callers forgetting that completion is signaled explicitly. Test attribute get/set, no-response sends, response-length reporting, notification decoding, all RPMI-to-Linux errno mappings, and transport failures from `mbox_send_message()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/riscv-rpmi-message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/zynqmp-ipi-message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/zynqmp-ipi-message.h

## Purpose
This header defines the variable-length message container used by Xilinx ZynqMP IPI mailbox clients.

## Important APIs, types, and functions
`struct zynqmp_ipi_message` contains a payload `len` and flexible `data[]`. The comment documents a fixed maximum payload size of 32 bytes, but the limit is enforced by callers or the controller rather than by the type itself.

## Control flow
Clients allocate or embed a buffer large enough for the header plus payload, fill `len` and `data`, and submit it with `mbox_send_message()`. The mailbox controller interprets the byte payload according to ZynqMP IPI protocol rules.

## State and persistence
The message is transient. No global state or persistence is defined.

## Dependencies and integration points
It relies on `size_t` and `u8` from common Linux headers already included by users. It integrates ZynqMP firmware/IPI clients with the generic mailbox framework.

## Risks and test signals
Main risks are payloads longer than the 32-byte hardware contract, allocation sizes that do not match `len`, and protocol consumers assuming NUL-terminated data. Test zero-length, exact 32-byte, and over-limit messages and verify the controller rejects or truncates safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/zynqmp-ipi-message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox_client.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox_client.h

## Purpose
This is the public client-side interface to the Linux mailbox framework. It lets device drivers request mailbox channels, send messages, receive callbacks, flush blocking transfers, and release channels.

## Important APIs, types, and functions
`struct mbox_client` identifies the client device and TX policy: `tx_block`, `tx_tout`, `knows_txdone`, and optional `rx_callback`, `tx_prepare`, and `tx_done` callbacks. Public APIs include `mbox_bind_client`, `mbox_request_channel_byname`, `mbox_request_channel`, `mbox_send_message`, `mbox_flush`, `mbox_client_txdone`, `mbox_client_peek_data`, `mbox_chan_tx_slots_available`, and `mbox_free_channel`.

## Control flow
A driver fills `struct mbox_client`, requests a channel by name or index, submits messages, and optionally receives RX/TX callbacks in atomic context. If the client knows when TX is done, it calls `mbox_client_txdone()` to advance the framework state. Blocking clients can use `tx_block`/`tx_tout` and `mbox_flush()`.

## State and persistence
Client state is owned by the driver. The framework stores the client pointer in the channel while the channel is bound. There is no persistent storage; channel ownership ends with `mbox_free_channel()`.

## Dependencies and integration points
It depends on Linux device and OF support and is paired with `mailbox_controller.h`. Integration points are firmware/DT channel lookup, controller-specific transport drivers, and subsystem clients such as firmware, remoteproc, RPMI, and vendor IPC.

## Risks and test signals
Callbacks can be atomic, so sleeping operations in `rx_callback`, `tx_prepare`, or `tx_done` are risky. Clients must match TX completion mode with controller capabilities and avoid freeing message memory before completion. Test named/indexed channel lookup, blocking timeout, ACK-driven completion, RX callback delivery, and channel release during idle and queued states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox_controller.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox_controller.h

## Purpose
This header defines the provider/controller side of the Linux mailbox framework: controller registration, channel operations, TX-done detection modes, per-channel queues, and atomic notification entry points.

## Important APIs, types, and functions
`struct mbox_chan_ops` supplies controller callbacks for `send_data`, `flush`, `startup`, `shutdown`, `last_tx_done`, and `peek_data`. `struct mbox_controller` describes the controller device, channel array, TX-done policy, firmware/OF translators, and polling timer state. `struct mbox_chan` holds runtime channel state including owner client, completion, active request, circular queue of `MBOX_TX_QUEUE_LEN` messages, lock, and controller-private data. Public provider APIs are `mbox_controller_register`, `mbox_controller_unregister`, `devm_mbox_controller_register`, `mbox_chan_received_data`, and `mbox_chan_txdone`.

## Control flow
Controller drivers register an initialized `mbox_controller` with channel storage and ops. Client requests call `startup`; sends enqueue or invoke `send_data`; completion is signaled by IRQ, polling via `last_tx_done`, or client ACK via `mbox_client_txdone()`. RX paths call `mbox_chan_received_data()` from atomic context, and channel release calls `shutdown`.

## State and persistence
Runtime state lives in `mbox_controller` and `mbox_chan`: queue indices, message count, active request pointer, locks, completions, and polling timer. There is no on-disk persistence. `MBOX_NO_MSG` distinguishes no active request from a legitimate NULL message.

## Dependencies and integration points
It integrates Linux devices, firmware node and OF lookup, hrtimer polling, completions, spinlocks, and list registration. It is the counterpart to `mailbox_client.h` and is used by SoC mailbox controller drivers.

## Risks and test signals
Risks include sleeping from atomic `send_data`, queue overflow, incorrect TX-done mode combinations, stale callbacks after `shutdown`, translator mismatch, and active request lifetime bugs. Test IRQ, polling, and ACK completion modes; queue saturation; concurrent send/free; RX while shutting down; and firmware channel translation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox_controller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/maple.h -->
# sources/distributed-fs/ceph-client/include/linux/maple.h

## Purpose
This header defines the Sega Dreamcast Maple bus device/driver interface and command constants. It is unrelated to the kernel maple tree data structure.

## Important APIs, types, and functions
`enum maple_code` lists Maple command and response codes; `enum maple_file_errors` defines VMU/file error bits. `struct maple_buffer`, `struct mapleq`, `struct maple_devinfo`, `struct maple_device`, and `struct maple_driver` describe queued packets, device identity, driver binding, callbacks, and wait/busy state. Public APIs include `maple_getcond_callback`, `maple_driver_register`, `maple_driver_unregister`, `maple_add_packet`, and `maple_clear_dev`.

## Control flow
Maple device drivers register a `maple_driver` keyed by function bits. They can queue command packets with `maple_add_packet()` or schedule condition polling through `maple_getcond_callback()`. Completion routes through the device callback or file-error handler.

## State and persistence
State is runtime-only in each `struct maple_device`: current queue item, function mask, product strings, busy atomic, wait queue, polling interval, and embedded device-model object. Hardware state persists only on attached Maple peripherals.

## Dependencies and integration points
It includes platform-specific `<mach/maple.h>`, Linux device-model types, lists, wait queues, and atomics. It integrates with Dreamcast Maple bus core and device drivers for controllers, VMUs, and related peripherals.

## Risks and test signals
Risks include incorrect function matching, fixed-size product string truncation, queue lifetime bugs, unload while busy, and file-error handling for storage devices. Test driver bind/unbind, condition polling intervals, command retries, no-response handling, and file error callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/maple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/maple_tree.h -->
# sources/distributed-fs/ceph-client/include/linux/maple_tree.h

## Purpose
This header defines the Linux Maple Tree API and internal layout: an RCU-aware adaptive range tree used for efficient index-to-pointer and range storage, including allocation-range gap tracking.

## Important APIs, types, and functions
Important node structures include `struct maple_range_64`, `struct maple_arange_64`, `struct maple_node`, `struct maple_copy`, and `struct maple_metadata`. Public tree state is `struct maple_tree`; advanced iteration/write state is `struct ma_state` plus `struct ma_wr_state`. Initialization macros include `MTREE_INIT`, `MTREE_INIT_EXT`, `DEFINE_MTREE`, `MA_STATE`, `MA_WR_STATE`, and `MA_TOPIARY`. Public operations include `mtree_load`, `mtree_insert`, `mtree_insert_range`, `mtree_alloc_range`, `mtree_alloc_cyclic`, `mtree_alloc_rrange`, `mtree_store_range`, `mtree_store`, `mtree_erase`, `mtree_dup`, `mtree_destroy`, `mas_walk`, `mas_store`, `mas_erase`, `mas_store_gfp`, `mas_store_prealloc`, `mas_find`, `mas_find_range`, reverse/find-next helpers, `mas_empty_area`, and `mt_find`/`mt_prev`/`mt_next` iterators.

## Control flow
Simple users initialize a tree, lock if required, and call `mtree_*` helpers for lookup, insertion, range store, allocation, or erase. Advanced users create an `ma_state`, walk or search the tree, optionally preallocate nodes, store or erase, and reset/pause the state when locks are dropped. RCU readers rely on encoded node pointers, immutable node type after insertion, and removed-node parent self-pointers to detect stale slots. Allocation-range trees track largest gaps to accelerate empty-area search.

## State and persistence
The persistent in-memory state is `ma_flags`, encoded height, optional RCU mode, lock mode, and `ma_root`. Nodes are 256-byte aligned and encode root/node type/slot information in low pointer bits. `ma_state` carries transient traversal position, range bounds, cached node, allocation staging, depth, offset, and store classification.

## Dependencies and integration points
It depends on kernel, RCU, spinlock, lockdep, slab sheaf allocation, and debug infrastructure. Integration points include memory-management VMA storage and any subsystem needing sparse ranges with RCU-friendly lookup.

## Risks and test signals
Risks are pointer-tag encoding errors, invalid storage of reserved low-bit patterns, stale `ma_state` reuse after unlocking, RCU mode transitions with external locks, gap metadata corruption, height overflow, and allocation preflight bugs. Test dense and sparse ranges, storing entries at index zero with all low-bit patterns, splitting/rebalancing, reverse searches, empty-area allocation, cyclic allocation wrapping, debug validation, RCU readers during mutation, and external-lock configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/maple_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/marvell_phy.h -->
# sources/distributed-fs/ceph-client/include/linux/marvell_phy.h

## Purpose
This header centralizes Marvell Ethernet PHY and embedded switch-family IDs plus per-device flag bits used by PHY drivers.

## Important APIs, types, and functions
It defines `MARVELL_PHY_ID_MASK`, many `MARVELL_PHY_ID_*` constants for 88E/88X/88Q PHY families, `MARVELL_PHY_FAMILY_ID(id)`, and `dev_flags` bits such as `MARVELL_PHY_M1145_FLAGS_RESISTANCE`, `MARVELL_PHY_M1118_DNS323_LEDS`, and `MARVELL_PHY_LED0_LINK_LED1_ACTIVE`.

## Control flow
There are no functions. PHY drivers and MDIO matching tables use the constants to match IDs and select quirks or LED/resistance configuration paths.

## State and persistence
No state is stored here. `dev_flags` values become runtime state inside `struct phy_device` consumers.

## Dependencies and integration points
It integrates with phylib drivers, MDIO device ID matching, and Marvell DSA switch families that expose embedded PHY IDs through trapped reads.

## Risks and test signals
Risks include mask collisions across closely related PHYs, switch-family IDs masquerading as PHY model IDs, and incompatible `dev_flags` combinations. Test all declared IDs against expected driver entries, quirk selection, and family extraction for embedded PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/marvell_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/math.h -->
# sources/distributed-fs/ceph-client/include/linux/math.h

## Purpose
This header provides common integer math helpers for kernel code: rounding, division with rounding, fractional structures, overflow-avoiding multiply/divide, absolute values, reciprocal scaling, and integer powers/square roots.

## Important APIs, types, and functions
Macros include `round_up`, `round_down`, `DIV_ROUND_UP_POW2`, `DIV_ROUND_UP`, `DIV_ROUND_DOWN_ULL`, `DIV_ROUND_UP_ULL`, `roundup`, `rounddown`, `DIV_ROUND_CLOSEST`, `DIV_ROUND_CLOSEST_ULL`, `mult_frac`, `sector_div`, `abs`, and `abs_diff`. It declares fixed-size fraction structs such as `struct u32_fract`, defines `reciprocal_scale()`, and declares `int_pow`, `int_sqrt`, and `int_sqrt64`.

## Control flow
Most helpers are compile-time macros or inline arithmetic. `round_up/down` assume power-of-two alignment; `roundup/down` handle arbitrary multiples. `mult_frac()` splits quotient and remainder to reduce overflow in `x * n / d`; `reciprocal_scale()` maps a 32-bit value into a right-open interval using a 64-bit product.

## State and persistence
There is no state. All helpers operate on arguments.

## Dependencies and integration points
It depends on Linux types, architecture `do_div`, and UAPI kernel math macros. It is broadly included by drivers, filesystems, block code, and memory management.

## Risks and test signals
Risks include divide-by-zero, overflow in rounded additions, using power-of-two helpers with non-power-of-two divisors, side-effecting macro arguments, and `abs()` on signed minimum values. Test boundary values, 32-bit builds, unsigned and signed types, sector-sized divisions, and compiler type checking in `abs_diff()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/math.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/math64.h -->
# sources/distributed-fs/ceph-client/include/linux/math64.h

## Purpose
This header provides portable 64-bit division and multiply/divide helpers that work efficiently on both 32-bit and 64-bit kernels.

## Important APIs, types, and functions
It defines `div64_long`, `div64_ul`, `div_u64_rem`, `div_s64_rem`, `div64_u64_rem`, `div64_u64`, `div64_s64`, `div_u64`, `div_s64`, `iter_div_u64_rem`, `mul_u32_u32`, `add_u64_u32`, `mul_u64_u32_shr`, `mul_u64_u64_shr`, `mul_s64_u64_shr`, `mul_u64_u32_div`, `mul_u64_add_u64_div_u64`, `mul_u64_u64_div_u64`, rounded divide macros, and `roundup_u64`.

## Control flow
On 64-bit builds most division helpers compile to native operators. On 32-bit builds, missing architecture primitives are external declarations or use `do_div()`. Multiplication helpers use `unsigned __int128` when supported, otherwise split operands into 32-bit halves and recombine shifted products.

## State and persistence
There is no persistent state. Remainder pointers are caller-provided output state.

## Dependencies and integration points
It depends on Linux types, `math.h`, architecture `div64`, and VDSO math definitions. It is a low-level utility for timekeeping, drivers, block, networking, and memory code that cannot assume native 64-bit division.

## Risks and test signals
Risks include zero divisors, overflow behavior in generic multiply-add-divide, sign handling in `mul_s64_u64_shr`, shifts at or above word size, and mismatched 32-bit/64-bit code generation. Test signed negative dividends, high 64-bit values, shift boundaries 0/63/64+, divisor overflow cases, and cross-architecture builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/math64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mbcache.h -->
# sources/distributed-fs/ceph-client/include/linux/mbcache.h

## Purpose
This header defines the metadata block cache interface used by filesystems to cache keyed reusable entries with refcounted hash/list membership.

## Important APIs, types, and functions
`struct mb_cache_entry` contains list and hash nodes, `e_refcnt`, `e_key`, flags `MBE_REFERENCED_B` and `MBE_REUSABLE_B`, and user `e_value`. APIs include `mb_cache_create`, `mb_cache_destroy`, `mb_cache_entry_create`, `mb_cache_entry_put`, `mb_cache_entry_delete_or_get`, `mb_cache_entry_get`, `mb_cache_entry_find_first`, `mb_cache_entry_find_next`, `mb_cache_entry_touch`, `mb_cache_entry_wait_unused`, and internal free helper `__mb_cache_entry_free`.

## Control flow
Filesystems create a cache with a bucket count, insert keyed values, look up entries by key/value, iterate matching entries, touch entries for replacement policy, and put references when done. `mb_cache_entry_put()` decrements the refcount, wakes waiters for low counts, and frees when the count reaches zero.

## State and persistence
State is in-memory only: hash membership, cache list ordering, flags, refcounts, keys, and values. Entries are guaranteed hashed while refcounted.

## Dependencies and integration points
It uses hash helpers, bit-locked hlist nodes, lists, atomics, and filesystem types. Ext-family filesystems are typical consumers.

## Risks and test signals
Risks include refcount underflow, delete races with active references, waiting for unused entries while new users acquire references, and reusable flag policy mistakes. Test create/destroy, duplicate key/value handling, concurrent get/delete/put, low-refcount wakeups, and iteration with removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mbcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mbus.h -->
# sources/distributed-fs/ceph-client/include/linux/mbus.h

## Purpose
This header exposes Marvell MBUS DRAM and address-window helpers used by Orion/MVEBU SoC drivers.

## Important APIs, types, and functions
`struct mbus_dram_target_info` describes DRAM target ID and up to four chip-select windows with CS index, MBUS attribute, base, and size. Constants define PCI IO/MEM/WA region flags, no-remap sentinel, and maximum window-name size. APIs include `mv_mbus_dram_info`, `mv_mbus_dram_info_nooverlap`, `mvebu_mbus_get_io_win_info`, `mvebu_mbus_get_pcie_mem_aperture`, `mvebu_mbus_get_pcie_io_aperture`, `mvebu_mbus_get_dram_win_info`, add/delete window helpers, `mvebu_mbus_init`, and `mvebu_mbus_dt_init`, with stubs when unsupported.

## Control flow
Platform code initializes MBUS windows from SoC/DT data. Device drivers query DRAM or IO window attributes and add/remap decode windows for peripherals. On non-Orion or non-MVEBU builds, stubs return NULL or `-EINVAL`.

## State and persistence
The header defines query/update APIs for hardware decode-window state held by the MBUS driver and registers. It stores no state itself.

## Dependencies and integration points
It depends on errno, resources, physical addresses, and architecture Kconfig symbols. It integrates with PCIe, DMA engines, memory controllers, and Marvell platform boot code.

## Risks and test signals
Risks include overlapping windows, stale remap assumptions, ARM32 versus ARM64 stub behavior, and wrong target/attribute pairs causing DMA faults. Test DRAM window discovery, no-overlap variant, PCIe aperture reporting, add/delete/remap windows, and non-MBUS build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mc146818rtc.h -->
# sources/distributed-fs/ceph-client/include/linux/mc146818rtc.h

## Purpose
This header defines register offsets, bit masks, platform data, and helper APIs for MC146818-compatible RTC/CMOS chips.

## Important APIs, types, and functions
It declares global `rtc_lock`, `struct cmos_rtc_board_info`, RTC register indices, alarm don't-care bits, control/status register masks, I/O extent defaults, and functions `mc146818_does_rtc_work`, `mc146818_get_time`, `mc146818_set_time`, and `mc146818_avoid_UIP`.

## Control flow
RTC drivers use the register constants with architecture access macros from `<asm/mc146818rtc.h>`, serialize CMOS access with `rtc_lock`, check update-in-progress timing, and read or set `struct rtc_time`. Board info can supply wake hooks and extended alarm/century register locations.

## State and persistence
State lives in CMOS/RTC hardware and persists across runtime and often across power states via battery. The header exposes register meanings but owns no state.

## Dependencies and integration points
It depends on architecture I/O, RTC core types, BCD helpers, delay, PM trace, and platform-specific register access. It integrates with `rtc-cmos` and x86/PC-style CMOS consumers.

## Risks and test signals
Risks include reading during UIP, BCD/binary mode confusion, 12-hour conversion mistakes, register C side effects on read, century register quirks, and wake-alarm platform hooks. Test UIP avoidance, BCD and binary modes, alarm fields with don't-care bits, valid-RAM flag, suspend/resume wake alarms, and concurrent CMOS users under `rtc_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mc33xs2410.h -->
# sources/distributed-fs/ceph-client/include/linux/mc33xs2410.h

## Purpose
This header exports shared SPI register access helpers for the NXP MC33XS2410 multi-output switch/PWM support.

## Important APIs, types, and functions
It imports the `PWM_MC33XS2410` namespace and declares `mc33xs2410_read_reg_ctrl`, `mc33xs2410_read_reg_diag`, and `mc33xs2410_modify_reg`, each operating on a `struct spi_device`.

## Control flow
Consumers call the read helpers for control or diagnostic register spaces and `modify_reg()` for masked updates. The implementation lives in the corresponding driver namespace.

## State and persistence
State is in the MC33XS2410 device registers and SPI controller runtime; the header stores none.

## Dependencies and integration points
It depends on SPI core declarations and module namespace import. It integrates PWM and possibly high-side-switch child drivers with a shared register-access provider.

## Risks and test signals
Risks include register-space mixups, masked writes racing with other clients, namespace linkage failures, and SPI transfer errors. Test control and diagnostic reads, masked bit updates, multi-client access serialization, and module load ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mc33xs2410.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mc6821.h -->
# sources/distributed-fs/ceph-client/include/linux/mc6821.h

## Purpose
This header models the memory-mapped register layout and control bits for the Motorola MC6821 Peripheral Interface Adapter.

## Important APIs, types, and functions
`struct pia` lays out port A/B data or data-direction registers and control registers, separated by configurable `PIA_REG_PADWIDTH`. Convenience aliases `ppra`, `pddra`, `pprb`, and `pddrb` select union members. Control bits include `PIA_C1_ENABLE_IRQ`, `PIA_C1_LOW_TO_HIGH`, `PIA_DDR`, `PIA_IRQ2`, and `PIA_IRQ1`.

## Control flow
Drivers map hardware registers as `struct pia`, use control bit 2 to select data versus direction register views, configure IRQ edge/enable bits, and then read/write volatile port registers.

## State and persistence
Hardware port and control register state persists while the PIA is powered. The header only defines layout.

## Dependencies and integration points
It depends on legacy `u_char` types and optional platform-defined `PIA_REG_PADWIDTH`. It integrates with board drivers for MC6821-compatible hardware.

## Risks and test signals
Risks include wrong register padding, accidental data-register access while DDR is selected, volatile-only ordering assumptions, and IRQ polarity mistakes. Test port direction switching, register offsets for each board, IRQ edge configuration, and read/write side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mc6821.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mcb.h -->
# sources/distributed-fs/ceph-client/include/linux/mcb.h

## Purpose
This header defines the MEN Chameleon Bus core interfaces for FPGA-described MCB devices, buses, drivers, resources, and registration helpers.

## Important APIs, types, and functions
`struct mcb_bus` describes a carrier-backed bus and IRQ lookup callback. `struct mcb_device` holds device IDs, instance/group/variant/BAR/revision, IRQ and memory resources, bus pointer, and DMA device. `struct mcb_driver` provides ID table and probe/remove/shutdown callbacks. APIs include `mcb_register_driver`, `mcb_unregister_driver`, `module_mcb_driver`, bus/device allocation and registration helpers, memory request/release helpers, IRQ/resource queries, and bus reference helpers.

## Control flow
Carrier drivers allocate a bus, discover Chameleon table entries, allocate/register devices, and add them to the bus. Function drivers register an ID table and bind through probe. Drivers request memory or IRQ resources using MCB helpers and release them during remove.

## State and persistence
Runtime state is in device-model objects, resource descriptors, bus reference counts, and discovered FPGA metadata. Hardware FPGA configuration persists outside the header.

## Dependencies and integration points
It depends on Linux device model, module device tables, IRQ return types, and resources. It integrates FPGA carrier drivers with MCB function drivers.

## Risks and test signals
Risks include duplicate device registration, stale `is_added`, resource lifetime leaks, incorrect IRQ callback behavior, and carrier removal while devices are bound. Test bus allocation/release, device discovery, driver matching, resource request/release, IRQ lookup failures, and module unload ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdev.h -->
# sources/distributed-fs/ceph-client/include/linux/mdev.h

## Purpose
This header defines the mediated device (mdev) bus interfaces used by parent drivers to expose partitioned virtual devices and by mdev drivers to bind to those instances.

## Important APIs, types, and functions
`struct mdev_device` wraps a Linux device, UUID, type pointer, list node, and active flag. `struct mdev_type` describes a parent-provided type with sysfs and display names plus core-populated kobjects. `struct mdev_parent` ties a physical parent device, mdev driver, type set, unregister semaphore, and instance counter. `struct mdev_driver` declares `device_api`, optional `max_instances`, `probe`, `remove`, availability, and description callbacks. APIs include `mdev_register_parent`, `mdev_unregister_parent`, `mdev_register_driver`, `mdev_unregister_driver`, `to_mdev_device`, and `mdev_dev`.

## Control flow
Parent drivers register supported mdev types. Userspace creates mediated devices via sysfs, causing mdev device creation and driver probe. Unregistration synchronizes against creation/removal with `unreg_sem`; active instances are removed through driver callbacks.

## State and persistence
Runtime state includes UUIDs, active devices, type kobjects, available instance counts, and parent/type relationships. Persistent configuration is typically userspace-managed, not stored by the header.

## Dependencies and integration points
It depends on Linux device model, UUIDs, kobjects/ksets, lists, rw semaphores, atomics, and sysfs. It integrates with VFIO and parent drivers for GPUs, accelerators, and other partitionable devices.

## Risks and test signals
Risks include UUID collisions, available-instance accounting errors, parent unregistration races, stale kobjects, and mismatched `device_api`. Test create/remove under concurrency, unregister with active children, max-instance limits, type descriptions, and driver bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio-bitbang.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio-bitbang.h

## Purpose
This header defines the bit-banged MDIO bus abstraction for controllers that implement MDIO by toggling GPIO-like MDC/MDIO signals.

## Important APIs, types, and functions
`struct mdiobb_ops` provides `set_mdc`, `set_mdio_dir`, `set_mdio_data`, and `get_mdio_data` callbacks plus module owner. `struct mdiobb_ctrl` carries ops and optional Clause 22 opcode overrides. APIs include Clause 22 and Clause 45 read/write helpers, `alloc_mdio_bitbang`, and `free_mdio_bitbang`.

## Control flow
Controller drivers implement pin callbacks, allocate an unregistered `mii_bus` with `alloc_mdio_bitbang()`, then register it with phylib. MDIO transactions call the bitbang helpers, which sequence MDC edges, MDIO direction changes, opcodes, addresses, turnaround, and data bits.

## State and persistence
State is runtime-only in the controller callbacks, opcode overrides, and allocated `mii_bus`. PHY register state persists in hardware.

## Dependencies and integration points
It depends on phylib `struct mii_bus` and `struct phy_device` support. It integrates GPIO, platform, and legacy MAC drivers with generic MDIO/PHY infrastructure.

## Risks and test signals
Risks include timing violations, wrong turnaround direction, missing module pinning, Clause 45 address phase errors, and nonstandard Clause 22 opcodes. Test PHY ID reads, register writes, bus registration/unregistration, GPIO direction sequencing, and C22/C45 transactions under clock-rate variation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio-bitbang.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio-mux.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio-mux.h

## Purpose
This header exposes the MDIO mux framework used to present multiple child MDIO buses behind a selectable parent bus.

## Important APIs, types, and functions
`mdio_mux_init()` initializes a mux for a device node, switch callback, optional parent `mii_bus`, private data, and output handle. `mdio_mux_uninit()` tears the mux down. The switch callback receives current and desired child bus identifiers.

## Control flow
The mux driver calls `mdio_mux_init()`, which creates child buses from firmware data and routes transactions by invoking the switch callback before accessing the selected child. On removal, `mdio_mux_uninit()` unregisters and frees the mux-owned buses.

## State and persistence
Mux state is hidden behind `mux_handle`; the header stores none. Hardware selection state persists in the mux device until changed.

## Dependencies and integration points
It depends on Linux device, OF, phylib, and parent MDIO bus support. It integrates MDIO switches/multiplexers with PHY discovery and DSA-style nested MDIO topologies.

## Risks and test signals
Risks include incorrect child selection, nested bus locking deadlocks, parent-bus discovery failures, and uninit while child PHYs are active. Test each child bus, rapid switching, nested mux paths, failed switch callbacks, and remove after registered PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio-mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio.h

## Purpose
This header is the central Linux MDIO interface for generic MDIO devices, MDIO drivers, Clause 22/45 bus operations, and ethtool/linkmode translation helpers.

## Important APIs, types, and functions
It defines `enum mdio_mutex_lock_class`, `struct mdio_device`, `struct mdio_driver_common`, `struct mdio_driver`, and `struct mdio_if_info`. Device APIs include create/register/remove/reset, get/put, and driver register/unregister. Bus APIs include locked and unlocked Clause 22 helpers, Clause 45 helpers, modify/modify_changed variants, and `mdiodev_*` wrappers. Link helpers translate EEE, 10GBASE-T, BASE-T1, 10BASE-T1, and Clause 73 advertisement/status bits between MDIO registers and ethtool link modes.

## Control flow
MDIO bus providers register `mii_bus` instances; devices are created at addresses 0-31 and matched to `mdio_driver` instances. Callers use `mdiobus_*` functions when they need bus-level locking and `__mdiobus_*` under existing locks. Clause 45 helpers include device address selection. Ethtool helpers map raw MMD and AN register bits to userspace-visible link capabilities.

## State and persistence
`struct mdio_device` stores bus address, reset GPIO/control, delays, flags, and callbacks. PHY/MDIO register state persists in hardware; driver data persists through the device model until remove.

## Dependencies and integration points
It depends on UAPI MDIO constants, bitfield helpers, module device tables, netdevice and ethtool types, GPIO descriptors, reset controls, and phylib. It integrates MAC drivers, PHY drivers, PCS devices, and ethtool.

## Risks and test signals
Risks include using unlocked helpers without holding the bus lock, Clause 45 ID encoding mistakes, reset timing bugs, linkmode translation omissions, nested MDIO lock-class misuse, and read-modify-write races. Test C22/C45 reads and writes, nested and muxed buses, reset GPIO/control sequencing, EEE and BASE-T1 ethtool conversion, device removal, and modify_changed return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-i2c.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio/mdio-i2c.h

## Purpose
This header defines the MDIO-over-I2C bridge allocation API.

## Important APIs, types, and functions
`enum mdio_i2c_proto` identifies supported bridge protocols: none, Marvell Clause 22, Clause 45, and RollBall. `mdio_i2c_alloc()` creates an unregistered `mii_bus` backed by an I2C adapter and selected protocol.

## Control flow
A driver calls `mdio_i2c_alloc()` with parent device, I2C adapter, and protocol, then registers the returned MDIO bus with phylib. MDIO transactions are translated into I2C operations by the implementation.

## State and persistence
The header stores no state. Runtime bus state is in the allocated `mii_bus`; target PHY state persists in hardware.

## Dependencies and integration points
It integrates I2C adapters with MDIO/phylib consumers, especially SFP modules and PHYs behind protocol-specific I2C management bridges.

## Risks and test signals
Risks include selecting the wrong protocol, adapter lifetime bugs, unsupported Clause 45 access, and I2C transfer failures surfacing as MDIO errors. Test allocation failure, each protocol variant, bus register/unregister, PHY ID reads, and I2C error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-mscc-miim.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio/mdio-mscc-miim.h

## Purpose
This header exposes a setup helper for the Microsemi/Vitesse MIIM MDIO controller used in network switches.

## Important APIs, types, and functions
`mscc_miim_setup()` takes a parent device, output `mii_bus **`, bus name, MIIM regmap, status register offset, and an `ignore_read_errors` policy flag.

## Control flow
Switch or platform drivers call the helper to allocate/configure a `mii_bus` over a regmap-backed MIIM block, then use the returned bus for PHY discovery and MDIO transactions.

## State and persistence
State lives in the returned bus and MIIM hardware registers. The header stores none.

## Dependencies and integration points
It depends on device, phylib, and regmap APIs. It integrates regmap-backed switch management blocks with the MDIO subsystem.

## Risks and test signals
Risks include wrong status offset, suppressed real read errors when `ignore_read_errors` is set, regmap endianness/access-width mismatches, and bus lifetime leaks. Test setup failure, read/write transactions, status polling, ignored-read-error mode, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-mscc-miim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-regmap.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio/mdio-regmap.h

## Purpose
This header defines a devm-managed MDIO bus adapter for devices whose internal PHY or PCS registers are exposed through a regmap.

## Important APIs, types, and functions
`struct mdio_regmap_config` contains parent device, regmap, bus name, one valid address, and `autoscan` flag. `devm_mdio_regmap_register()` registers a managed `mii_bus` using that config.

## Control flow
A driver fills the config and calls the devm helper. MDIO operations are translated to regmap reads/writes, optionally scanning addresses depending on configuration. Device-managed cleanup unregisters the bus on driver detach.

## State and persistence
Runtime state is in the registered bus and regmap-backed hardware. The header stores none.

## Dependencies and integration points
It depends on phylib, device-managed resources, and regmap. It integrates internal PHY/PCS blocks inside MMIO devices with generic MDIO consumers.

## Risks and test signals
Risks include invalid address filtering, duplicate bus names, regmap access failures, autoscan discovering unintended devices, and devm cleanup ordering. Test valid and invalid addresses, autoscan enabled/disabled, read/write translation, and detach cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-regmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-xgene.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio/mdio-xgene.h

## Purpose
This header defines register offsets, bitfield helpers, platform data, and exported routines for the AppliedMicro X-Gene MDIO controller.

## Important APIs, types, and functions
It declares CSR offsets for MAC, diagnostics, MDIO, management, reset/clock, and MIIM registers; bitfield positions/lengths; command enums; `enum xgene_mdio_id`; and `struct xgene_mdio_pdata` holding clocks, device, MMIO bases, bus, ID, and MAC lock. Inline helpers `xgene_enet_set_field_value()` and `xgene_enet_get_field_value()` back `SET_VAL`, `SET_BIT`, `GET_VAL`, and `GET_BIT`. Exported functions include MAC read/write, RGMII read/write, and PHY registration.

## Control flow
The X-Gene driver uses the platform data to access the correct CSR block, composes bitfields for MDIO commands, waits on busy/done indicators, serializes MAC register access with `mac_lock`, and registers PHY devices on the `mii_bus`.

## State and persistence
Runtime state is in MMIO registers, clock/reset state, bus registration, and the spinlock. PHY register state persists in hardware.

## Dependencies and integration points
It depends on bits, spinlocks, clocks, devices, IO memory, and phylib. It integrates X-Gene Ethernet MAC variants with MDIO/PHY infrastructure.

## Risks and test signals
Risks include duplicate macro definitions, incorrect bitfield width shifts, wrong CSR base for RGMII versus XFI, busy polling timeouts, and missing locking around MAC access. Test RGMII reads/writes, PHY registration, reset/clock enable, timeout handling, and concurrent MAC register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-xgene.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mei_aux.h -->
# sources/distributed-fs/ceph-client/include/linux/mei_aux.h

## Purpose
This header defines the auxiliary-bus wrapper used to expose Intel MEI-related auxiliary devices.

## Important APIs, types, and functions
`struct mei_aux_device` embeds `struct auxiliary_device` and carries IRQ number, MMIO BAR resource, extended operational memory resource, and `slow_firmware` timeout hint. `auxiliary_dev_to_mei_aux_dev()` converts from auxiliary device to wrapper.

## Control flow
MEI parent code creates an auxiliary device, fills resources and flags, and registers it on the auxiliary bus. Auxiliary drivers recover the wrapper with the conversion macro and use the IRQ/resource metadata during probe.

## State and persistence
State is device-model runtime metadata and resource descriptors. The header stores no global state.

## Dependencies and integration points
It depends on the Linux auxiliary bus and resource structures. It integrates MEI with auxiliary consumers such as graphics/PXP-related devices.

## Risks and test signals
Risks include resource lifetime errors, slow firmware timeouts not being honored, invalid IRQs, and incorrect container conversion. Test auxiliary probe/remove, resource mapping, IRQ setup, and slow-firmware timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mei_aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mei_cl_bus.h -->
# sources/distributed-fs/ceph-client/include/linux/mei_cl_bus.h

## Purpose
This header defines the Intel MEI client bus interface, including MEI client device/driver types, registration helpers, synchronous I/O, callbacks, DMA mapping, and GSC command support.

## Important APIs, types, and functions
`struct mei_cl_device` links a Linux device to the MEI bus, ME host client, MEI client handle, name, RX and notification work/callbacks, match/add flags, and driver private data. `struct mei_cl_driver` provides an ID table and probe/remove callbacks. APIs include driver register/unregister, `mei_cldev_send`, `mei_cldev_recv`, timeout and vtag variants, callback registration, UUID/version/MTU queries, drvdata helpers, enable/disable/enabled, `mei_cldev_send_gsc_command`, and DMA map/unmap helpers.

## Control flow
Drivers register with `mei_cldev_driver_register` or `module_mei_cl_driver`, bind to matching MEI clients, enable the client, send/receive messages synchronously or with timeouts, and register asynchronous RX/notification callbacks executed from work items. Remove disables I/O and clears driver state.

## State and persistence
Runtime state includes bus list membership, match/add flags, RX/notification work, callbacks, MEI client handles, private data, enable state, and DMA mappings. Firmware client identity persists in ME firmware but not in this header.

## Dependencies and integration points
It depends on Linux device model, UUIDs, module device tables, workqueues, scatterlists, and MEI core internals. It integrates MEI host-client protocols, GSC command paths, and ME firmware notifications with client drivers.

## Risks and test signals
Risks include callbacks racing device removal, send/receive timeout mismatches, vtag misuse, DMA buffer leaks, MTU violations, and enable/disable ordering errors. Test probe/remove, enable failure, blocking and timeout I/O, RX and notification callbacks, vtag round trips, GSC scatterlist commands, and DMA map/unmap cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mei_cl_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mem_encrypt.h -->
# sources/distributed-fs/ceph-client/include/linux/mem_encrypt.h

## Purpose
This header provides common memory-encryption address conversion helpers, especially for AMD SME/SEV-style encryption masks.

## Important APIs, types, and functions
When architecture memory encryption is enabled it includes `<asm/mem_encrypt.h>`. With `CONFIG_AMD_MEM_ENCRYPT`, `__sme_set()` ORs `sme_me_mask` into an address-like value and `__sme_clr()` removes it. `dma_addr_encrypted`, `dma_addr_unencrypted`, and `dma_addr_canonical` normalize DMA address conversions, with identity fallbacks when unsupported.

## Control flow
Callers wrap physical/DMA/PTE-like values when they need encrypted, unencrypted, or canonical forms. Architecture headers can override the DMA helper macros before generic fallbacks are defined.

## State and persistence
The only external state is architecture-provided encryption mask state such as `sme_me_mask`. The header itself stores none.

## Dependencies and integration points
It depends on architecture Kconfig and arch memory-encryption declarations. It integrates page-table setup, DMA mapping, and platform code with encryption-aware address formats.

## Risks and test signals
Risks include double-applying or failing to clear encryption masks, using helpers on non-address bitfields, and inconsistent arch overrides. Test encrypted and unencrypted DMA mappings, canonicalization, disabled-config identity behavior, and PTE/address mask boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mem_encrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memblock.h -->
# sources/distributed-fs/ceph-client/include/linux/memblock.h

## Purpose
This header defines the early-boot memblock allocator and memory-region registry used before the full page allocator is available.

## Important APIs, types, and functions
Core types are `enum memblock_flags`, `struct memblock_region`, `struct memblock_type`, and global `struct memblock memblock`. APIs cover adding/removing memory, reserving and freeing physical ranges, marking flags such as hotplug/nomap/mirror/driver-managed/noinit/kernel/kexec-handover scratch, iterating ranges, NUMA node assignment, physical and virtual early allocation, memory limits, size queries, address membership checks, PFN conversion helpers, early hash allocation, memtest, and optional KHO scratch-only mode.

## Control flow
Architecture boot code populates `memblock.memory` from firmware maps, reserves kernel/initrd/device ranges in `memblock.reserved`, marks special attributes, and allocates early data structures from available ranges under `current_limit` and direction policy. Iteration macros walk memory, reserved, free, physical, and PFN ranges, optionally excluding flags or reserved regions. After boot, memblock metadata is discarded unless `CONFIG_ARCH_KEEP_MEMBLOCK` keeps it.

## State and persistence
Memblock state is global in-memory boot state: sorted region arrays, counts, totals, flags, node IDs, allocation direction, and allocation limit. It persists only as long as memblock is kept; physical memory reservations and nomap decisions affect later memory initialization.

## Dependencies and integration points
It depends on init annotations, mm types, DMA limits, PFN macros, NUMA, kmemleak/hash allocation, early memtest, and architecture boot code. It feeds zone setup, resource reservation, sparsemem, hotplug metadata, and early allocators.

## Risks and test signals
Risks include overlapping or unsorted ranges, off-by-one PFN conversion for unaligned reservations, resizing before `memblock_allow_resize()`, incorrect flag filtering in iterators, allocation above accessible limits, NUMA coverage gaps, and premature discard. Test firmware map parsing, reserve/free overlap, nomap and mirror marking, bottom-up/top-down allocation, NUMA node ranges, memory limit enforcement, KHO scratch mode, and 32-bit physical address limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memblock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memcontrol.h -->
# sources/distributed-fs/ceph-client/include/linux/memcontrol.h

## Purpose
This header defines the memory cgroup public and internal interfaces for charging pages and kernel objects, tracking per-cgroup VM statistics/events, lruvec selection, writeback attribution, socket memory pressure, shrinker metadata, zswap accounting, and cgroup v1 compatibility.

## Important APIs, types, and functions
It defines `enum memcg_stat_item`, `enum memcg_memory_event`, `struct mem_cgroup_reclaim_cookie`, and under `CONFIG_MEMCG` the main `struct mem_cgroup`, `struct mem_cgroup_per_node`, `struct obj_cgroup`, threshold structures, reclaim iterators, and writeback foreign-dirty tracking. Important APIs include `mem_cgroup_charge`, `mem_cgroup_uncharge`, swapin and hugetlb charging, folio memcg/object-cgroup accessors, `mem_cgroup_lruvec`, lruvec lock helpers, cgroup ID/private-ID lookup, reclaim iteration, protection helpers, stats and event counters, OOM printing/group selection, high-limit handling, socket charge helpers, kmem/object charge helpers, zswap charge helpers, and cgroup v1 OOM/swap hooks. Large sections provide no-op or node-level fallbacks when memory cgroups are disabled.

## Control flow
Allocation paths charge folios or kernel objects to the active/task memcg, update page counters and folio `memcg_data`, and later uncharge on free or migration. Reclaim obtains the correct `lruvec` for a memcg/node pair, applies min/low protection unless reclaim targets the same memcg, and records events/statistics. Writeback compares dirtying memcg with writeback ownership to track foreign dirtying. Socket and kmem paths use static keys to avoid overhead when disabled. Disabled builds collapse charges/events to success/no-op and use node lruvecs directly.

## State and persistence
Memcg state persists with cgroup lifetime: page counters, memory/swap/zswap limits and events, VM stats, per-node lruvecs, shrinker info, object-cgroup references, ID mappings, writeback domains, deferred split queues, socket pressure, v1 thresholds, OOM flags, and eventfd lists. Folio `memcg_data` carries runtime binding and flags. Reparenting handles objects that outlive a cgroup.

## Dependencies and integration points
It depends on cgroups, page counters, VM events/stats, folios/pages, LRU/reclaim, writeback, eventfd, vmpressure, shrinkers, zswap, sockets, slab object extensions, BPF static keys, and cgroup v1/v2 policy files. It is a central integration point between mm, filesystem writeback, networking, slab, swap, and userspace cgroup controls.

## Risks and test signals
Risks include folio/object binding instability without the documented locks or RCU, refcount leaks during objcg reparenting, inaccurate low/min protection under parallel reclaim, stale lruvec locks after reparenting, disabled-config behavior hiding accounting bugs, writeback attribution races, high-limit throttling latency, and NMI-safe stat configuration differences. Test page and kmem charge/uncharge, folio migration/split, memcg deletion with live objects, reclaim protection, lruvec relock batching, OOM group reporting, events/stat flushing, socket pressure on 32-bit and 64-bit, cgroup writeback foreign dirtying, zswap limits, and CONFIG_MEMCG=n builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memcontrol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memfd.h -->
# sources/distributed-fs/ceph-client/include/linux/memfd.h

## Purpose
This header exposes internal memfd helpers for file sealing, folio allocation, mmap seal checks, anonymous memfd file creation, and seal management.

## Important APIs, types, and functions
`MEMFD_ANON_NAME` names anonymous memfd files. When `CONFIG_MEMFD_CREATE` is enabled, APIs include `memfd_fcntl`, `memfd_alloc_folio`, `memfd_check_seals_mmap`, `memfd_alloc_file`, `memfd_get_seals`, and `memfd_add_seals`. Disabled builds return `-EINVAL`, error pointers, or allow mmap checks as no-op.

## Control flow
System call and file operation paths dispatch seal-related fcntls, allocate shmem-backed folios, validate mmap permissions against seals while potentially updating VMA flags, and create anonymous memfd files. Disabled configurations reject creation and seal operations.

## State and persistence
Memfd state lives in file/inode seals and backing shmem pages for the lifetime of the file. It is not persistent across reboot unless exported by another subsystem.

## Dependencies and integration points
It depends on Linux file, folio, VM flag, and shmem/memfd internals. It integrates `memfd_create`, fcntl sealing, mmap, and file-backed memory users.

## Risks and test signals
Risks include seal checks missing writable mappings, stale VMA flags, incorrect disabled-config return behavior, and folio allocation at wrong indices. Test all seal combinations, mmap transitions, fcntl get/add paths, file creation flags, and CONFIG_MEMFD_CREATE=n stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory-failure.h -->
# sources/distributed-fs/ceph-client/include/linux/memory-failure.h

## Purpose
This header defines a registration interface for mapping poisoned PFNs back to address spaces and VM offsets during memory-failure handling.

## Important APIs, types, and functions
`struct pfn_address_space` embeds an interval tree node, an `address_space *mapping`, and a `pfn_to_vma_pgoff` callback. `register_pfn_address_space()` and `unregister_pfn_address_space()` are available with `CONFIG_MEMORY_FAILURE`; disabled builds return `-EOPNOTSUPP` or no-op.

## Control flow
Subsystems that manage PFN-backed mappings register an interval with a callback so memory-failure code can translate a poisoned PFN into the affected VMA page offset and notify or kill users appropriately.

## State and persistence
Registered intervals are runtime memory-failure lookup state. No persistent data is stored by the header.

## Dependencies and integration points
It depends on interval trees, address spaces, VMAs, PFNs, and memory-failure configuration. It integrates DAX/device memory style mappings with hwpoison handling.

## Risks and test signals
Risks include stale interval registrations, wrong PFN-to-offset translation, disabled-config callers ignoring `-EOPNOTSUPP`, and races with unmap/remove. Test register/unregister, poisoned PFNs inside and outside intervals, VMA offset conversion, and module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory-failure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory-tiers.h -->
# sources/distributed-fs/ceph-client/include/linux/memory-tiers.h

## Purpose
This header defines NUMA memory-tier metadata and APIs for abstract memory distance, DRAM defaults, node demotion, and performance-to-tier mapping.

## Important APIs, types, and functions
Constants define tier chunk sizing and default DRAM abstract distance. `struct memory_dev_type` tracks memory types, tier siblings, driver list membership, abstract distance, node mask, and kref. NUMA APIs include `alloc_memory_type`, `put_memory_type`, node type init/clear, adistance notifier registration, `mt_calc_adistance`, `mt_set_default_dram_perf`, `mt_perf_to_adistance`, type allocation/list helpers, demotion target helpers, `node_get_allowed_targets`, and `node_is_toptier`; non-NUMA builds return stubs.

## Control flow
Memory providers allocate or find memory types based on abstract distance, assign nodes to types, and register adistance/performance data. NUMA migration code queries demotion targets and top-tier status to move pages from faster to slower memory tiers under pressure.

## State and persistence
Runtime state includes memory type lists, tier sibling links, node masks, krefs, default DRAM type/nodes, and demotion enablement. It is rebuilt at boot/hotplug and not stored persistently.

## Dependencies and integration points
It depends on nodemasks, krefs, mm zones, notifier blocks, NUMA, NUMA migration, and HMAT/access-coordinate style performance data. It integrates hotplug, reclaim/demotion, CXL/driver-managed memory, and NUMA policy.

## Risks and test signals
Risks include abstract-distance bucket misclassification, stale node masks on hotplug, notifier ordering errors, demotion loops, and stub behavior on non-NUMA builds. Test memory type allocation/release, DRAM performance defaults, hotplug node type changes, demotion target calculation with allowed masks, and NUMA_MIGRATION disabled paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory-tiers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory.h -->
# sources/distributed-fs/ceph-client/include/linux/memory.h

## Purpose
This header defines generic memory-block and memory-group device model structures used for memory hotplug and sysfs topology.

## Important APIs, types, and functions
`struct memory_group` groups memory blocks for a memory device or NUMA node and tracks present kernel/movable pages. `enum memory_block_state` names sysfs-visible and internal online/offline transitions. `struct memory_block` represents a hotpluggable memory block with section number, state, online type, nid, zone, device, altmap, group linkage, and hwpoison counter. APIs include memory block sizing, notifier registration, memory notification, memory block device create/remove/find/walk, memory group register/unregister/find/walk, ID conversion helpers, `memory_block_advise_max_size`, and global `text_mutex`.

## Control flow
Hotplug code creates memory block devices for physical ranges, exposes state through sysfs, notifies registered callbacks during online/offline transitions, groups blocks by memory device, and removes block devices on hotremove. Disabled hotplug builds provide benign stubs.

## State and persistence
Runtime state is in memory block devices, group lists and counters, device locks, online state, zone association, and optional hwpoison counts. It reflects physical memory topology and sysfs state rather than persistent storage.

## Dependencies and integration points
It depends on node, mutex, memory hotplug, device model, sparsemem sections, altmaps, and notifier blocks. It integrates drivers/base memory sysfs, CXL/HMAT/memory tiers, KSM, cpusets, slab, and code-patching `text_mutex` users.

## Risks and test signals
Risks include state transition races, wrong block size/order, multi-zone blocks with NULL zone, group counter drift, notifier priority interactions, and hotplug-disabled call paths. Test online/offline sysfs transitions, notifier ordering, group registration, block walking, section-to-block conversions, hwpoison accounting, and advised max size behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory/ti-aemif.h -->
# sources/distributed-fs/ceph-client/include/linux/memory/ti-aemif.h

## Purpose
This header defines chip-select timing data and validation/programming APIs for TI AEMIF asynchronous external memory interfaces.

## Important APIs, types, and functions
`struct aemif_cs_timings` holds turnaround, read hold/strobe/setup, and write hold/strobe/setup values expressed as clock cycles minus one. APIs are `aemif_set_cs_timings()` and `aemif_check_cs_timings()`.

## Control flow
Board or memory drivers populate timing values, optionally validate them, then program a selected chip select through `aemif_set_cs_timings()`.

## State and persistence
Timing state persists in AEMIF controller registers while powered. The header stores no runtime state.

## Dependencies and integration points
It depends on integer types and the opaque `struct aemif_device`. It integrates memory/flash/NAND style devices with TI AEMIF controller drivers.

## Risks and test signals
Risks include off-by-one timing conversion, chip-select index mistakes, invalid timing ranges, and programming timings while a device is active. Test boundary timing validation, each chip select, read/write waveform correctness, and controller suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory/ti-aemif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory_hotplug.h -->
# sources/distributed-fs/ceph-client/include/linux/memory_hotplug.h

## Purpose
This header defines the core memory hotplug and hotremove interfaces for adding, onlining, offlining, and removing physical memory ranges and their metadata.

## Important APIs, types, and functions
`enum mmop` describes offline/default/kernel/movable online operations. Hotplug builds define `mhp_t` flags `MHP_MERGE_RESOURCE`, `MHP_MEMMAP_ON_MEMORY`, and `MHP_NID_IS_MGID`, plus `struct mhp_params` for altmap, pgprot, and dev_pagemap. APIs cover `pfn_to_online_page`, pluggable range queries, memmap-on-memory support, zone span locks, present page count adjustment, memmap init/deinit, online/offline pages, online page callbacks, node online/offline, architecture add/remove memory, adding pages/sections/memory/resources/driver-managed memory, online memory locking, hotplug begin/done, zone selection, linear mappings, and pgdat resizing. Disabled builds provide stubs.

## Control flow
Hotplug callers validate ranges, create mappings and memmap, add sparse sections, create memory block devices, then online pages into a selected zone. Hotremove offlines pages, isolates/removes sections, tears down linear mappings, and may offline nodes. Global hotplug locks serialize online memory operations and zone/pgdat span updates.

## State and persistence
Runtime state includes zone spans, pgdat node sizes, sparsemem sections, online page callbacks, default online type, movable-node setting, memory resources, and memmap-on-memory metadata. Physical memory presence persists in firmware/device state; kernel state is rebuilt on boot/hotplug.

## Dependencies and integration points
It depends on mm zones, spinlocks, notifiers, resources, altmaps, dev_pagemap, sparsemem, architecture mapping hooks, and memory block sysfs. It integrates CXL/NVDIMM/device memory, memory tiers, NUMA, reclaim, and platform hotplug.

## Risks and test signals
Risks include zone span lock misuse, invalid memmap-on-memory alignment, resource merge pointer invalidation, node/group ID confusion with `MHP_NID_IS_MGID`, offline failures due to pinned pages, and disabled-config stubs hiding unsupported operations. Test add/online/offline/remove, movable and kernel online types, memmap-on-memory, driver-managed memory, altmap ranges, resource merge, node on/offline, and concurrent hotplug serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory_hotplug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mempolicy.h -->
# sources/distributed-fs/ceph-client/include/linux/mempolicy.h

## Purpose
This header defines NUMA memory policy structures and APIs for task, VMA, shared-memory, hugepage, migration, and slab allocation policy.

## Important APIs, types, and functions
Under `CONFIG_NUMA`, `struct mempolicy` stores reference count, mode, flags, node masks, home node, rebinding masks, and RCU cleanup. `struct shared_policy` and `struct sp_node` manage rb-tree policy ranges for shared mappings. APIs include policy get/put/dup/equal, shared-policy init/set/free/lookup, VMA policy duplication and lookup, task policy lookup, NUMA default/init, task/mm rebind, hugepage node selection, nodemask initialization, OOM-domain checks, slab node selection, policy zone tracking, page migration, tmpfs policy parse/string formatting, migratability checks, misplaced-page detection, task policy release, preferred-many helper, policy zone applicability, and node performance updates. Non-NUMA builds stub to defaults.

## Control flow
Allocation paths obtain the applicable VMA or task policy, choose nodes according to bind/interleave/preferred modes, and release conditional references. Shared mappings use rb-tree lookups by page offset. Rebinding updates policies after cpuset changes, and NUMA balancing uses `mpol_misplaced()` to decide migrations.

## State and persistence
Policies persist in tasks, mm/VMA structures, or shared-policy trees until replaced or freed. Reference counts and RCU delay object lifetime. No on-disk persistence is defined, although tmpfs can parse policy strings.

## Dependencies and integration points
It depends on scheduler, mm zones, slab, rbtree, spinlocks, nodemasks, pagemap, UAPI mempolicy constants, cpusets, hugepages, tmpfs, and NUMA balancing. It integrates syscalls, VMA management, reclaim/oom, migration, and memory tiers/performance.

## Risks and test signals
Risks include refcount leaks, shared-policy range overlap bugs, stale policies after cpuset rebind, invalid nodemasks, policy-zone mistakes with movable memory, and disabled-NUMA behavior masking policy calls. Test each MPOL mode, shared mappings, fork/VMA duplication, cpuset rebind, hugepage allocation, migration pages syscall, tmpfs parsing, and NUMA=n builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mempolicy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mempool.h -->
# sources/distributed-fs/ceph-client/include/linux/mempool.h

## Purpose
This header defines the generic kernel memory pool interface that guarantees forward progress by keeping a minimum number of preallocated elements.

## Important APIs, types, and functions
`mempool_alloc_t` and `mempool_free_t` are element callbacks. `mempool_t` contains lock, minimum/current element counts, element array, pool data, callbacks, and wait queue. APIs include `mempool_init`, `mempool_init_node`, `mempool_exit`, create/destroy, resize, single and bulk allocation/free, preallocated-only allocation, and helper callback pairs for slab caches, kmalloc sizes, and page orders.

## Control flow
Consumers initialize or create a pool with a minimum reserve. Allocation first tries the underlying allocator and can fall back to preallocated elements; freeing replenishes the reserve or returns elements to the underlying allocator and wakes waiters. Resize adjusts reserve depth.

## State and persistence
State is runtime-only in the pool lock, element array, counts, and wait queue. Preallocated memory persists until pool exit/destroy.

## Dependencies and integration points
It depends on scheduler, allocation hooks/profiling, wait queues, slabs, kmalloc, and page allocator callbacks. It is widely used by block/filesystem paths that need allocations under memory pressure.

## Risks and test signals
Risks include incorrect `min_nr`, sleeping allocation contexts, callback mismatch between alloc/free, resize races, double free, and draining pools while users remain. Test allocation under simulated memory pressure, bulk operations, resize up/down, slab/kmalloc/page pools, `mempool_initialized`, and destroy after all elements are returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mempool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memregion.h -->
# sources/distributed-fs/ceph-client/include/linux/memregion.h

## Purpose
This header defines simple memory-region ID allocation and architecture cache-invalidation hooks for large physical memory regions.

## Important APIs, types, and functions
`struct memregion_info` records a target NUMA node and physical range. `memregion_alloc()` and `memregion_free()` are available with `CONFIG_MEMREGION`; stubs return `-ENOMEM` or no-op. `cpu_cache_invalidate_memregion()` and `cpu_cache_has_invalidate_memregion()` are available with architecture support; otherwise invalidation warns and returns `-ENXIO`. `cpu_cache_invalidate_all()` invalidates all target regions via length `-1`.

## Control flow
Memory-region providers allocate IDs for ranges and, when physical memory contents may change in a cache-incoherent way, call the cache invalidation helper. Architectures without efficient support reject such invalidation.

## State and persistence
Runtime state for allocated region IDs is held by the memregion implementation. Cache invalidation affects CPU caches but stores no durable state.

## Dependencies and integration points
It depends on types, errno, range, bug/warn helpers, and architecture support. It integrates NVDIMM/CXL/device-memory operations that need broad cache maintenance.

## Risks and test signals
Risks include assuming invalidation writes back dirty data, using all-region invalidation unintentionally, unsupported architectures only warning, and ID leaks. Test allocation/free, unsupported stubs, architecture-supported invalidation over large ranges, and secure-erase/dynamic-region workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memregion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memremap.h -->
# sources/distributed-fs/ceph-client/include/linux/memremap.h

## Purpose
This header defines APIs and metadata for remapping physical memory into the kernel, especially ZONE_DEVICE/dev_pagemap memory such as DAX, private/coherent device memory, generic device memory, and PCI peer-to-peer DMA memory.

## Important APIs, types, and functions
`struct vmem_altmap` describes reserved/free pages used for vmemmap metadata. `enum memory_type` classifies ZONE_DEVICE usage. `struct dev_pagemap_ops` provides `folio_free`, `migrate_to_ram`, `memory_failure`, and `folio_split` callbacks. `struct dev_pagemap` tracks altmap, percpu ref, completion, type, flags, vmemmap shift, ops, owner, and one or more ranges. Helpers identify page types, access/set device-private data, query altmaps, vmemmap size, memory-failure support, and split callbacks. ZONE_DEVICE APIs include `zone_device_page_init`, `memremap_pages`, `memunmap_pages`, devm variants, `get_dev_pagemap`, `pgmap_pfn_valid`, and `memremap_compat_align`; disabled builds warn or return stubs.

## Control flow
Device-memory drivers fill `dev_pagemap`, map ranges with `memremap_pages()` or devm variant, and receive lifecycle callbacks as folios are freed, migrated, split, or hit by memory failure. Users identify page type with inline helpers and release mappings with `put_dev_pagemap()`/unmap paths.

## State and persistence
Runtime state includes page map ranges, percpu reference lifetime, completion, altmap allocation accounting, vmemmap order, owner pointer, and per-page `pgmap`/zone-device data. Device memory contents may persist depending on hardware, but mapping metadata is runtime.

## Dependencies and integration points
It depends on mm zones, ranges, resources, IO port definitions, percpu refcounts, completions, folios, devm resources, HMM, DAX, PCI P2PDMA, memory failure, and memory hotplug.

## Risks and test signals
Risks include missing `migrate_to_ram` for private memory, pinning semantics for coherent/device memory, altmap accounting errors, refcount leaks, invalid PFN checks, split callback propagation, and disabled ZONE_DEVICE fallback misuse. Test each memory type, map/unmap lifetime, altmap-backed vmemmap, folio split/free, migration to RAM, memory failure fallback, P2PDMA detection, and CONFIG_ZONE_DEVICE=n callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memremap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memstick.h -->
# sources/distributed-fs/ceph-client/include/linux/memstick.h

## Purpose
This header defines the Sony MemoryStick core protocol structures, command/TPC constants, host/card/driver abstractions, request format, and bus registration APIs.

## Important APIs, types, and functions
Packed hardware register structures include status, ID, parameter, extra data, legacy register map, PRO parameter/IO registers, and register address selection. Enums define TPC transfer codes and MemoryStick/MemoryStick PRO commands. `struct memstick_device_id` describes media matching. `struct memstick_request` carries TPC, direction/card-interrupt/long-data flags, interrupt status, error, and either scatterlist or inline data. `struct memstick_dev`, `struct memstick_host`, and `struct memstick_driver` model card, host controller, and media driver callbacks. APIs cover driver registration, host allocation/add/remove/free, change detection, suspend/resume, request initialization, next/new request scheduling, RW address setup, and drvdata/private helpers.

## Control flow
Host drivers allocate and add a host, detect media changes, and service pending requests via their `request` callback. Media drivers bind by ID, provide request-generation callbacks, and use `memstick_new_req()`/`memstick_next_req()` to drive command sequences. The core handles card interrupts, retries, completion, power/interface parameters, and suspend/resume coordination.

## State and persistence
Runtime state includes host lock, capabilities, current card, retry count, removal flag, media checker work, current request, completion, register-address layout, and driver callbacks. Card flash contents persist on media; bus/core state does not.

## Dependencies and integration points
It depends on workqueues, scatterlists, completions, mutexes, device model, and PM messages. It integrates MemoryStick host controller drivers with storage or IO media drivers.

## Risks and test signals
Risks include packed-structure endian/layout assumptions, inline data length limits, request callback races during removal, retry handling, card interrupt expectations, and suspend while requests are active. Test legacy and PRO cards, storage and IO categories, host capability negotiation, request SG and inline paths, media removal, retries/errors, suspend/resume, and 4/8-bit interface switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memstick.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/88pm80x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/88pm80x.h

## Purpose
This header defines register constants, chip/platform data, subchip state, IRQ helpers, PM helpers, and init/deinit declarations for Marvell 88PM80x PMIC MFD devices.

## Important APIs, types, and functions
It declares chip type enums for PM800/PM805/PM860, regulator IDs for PM800 bucks/LDOs, many register offsets and bit masks for status, wakeup, low power, GPIO, headset, PWM, RTC, GPADC, and PM805 audio/interrupt blocks. Data structures include `struct pm80x_rtc_pdata`, `struct pm80x_subchip`, `struct pm80x_chip`, and `struct pm80x_platform_data`. Helpers `pm80x_request_irq()` and `pm80x_free_irq()` map PMIC IRQ numbers through regmap IRQ data. PM helpers `pm80x_dev_suspend()` and `pm80x_dev_resume()` maintain wakeup IRQ bits when `CONFIG_PM` is enabled. External declarations include `pm80x_pm_ops`, `pm80x_regmap_config`, `pm80x_init`, and `pm80x_deinit`.

## Control flow
The MFD core initializes I2C/regmap pages and regmap IRQ data, then child platform drivers use platform data and register constants to control RTC, regulators, GPADC, onkey, or audio features. Child drivers request threaded IRQs through the helper, which converts PMIC interrupt indices to Linux virqs. Suspend/resume records child wakeup IRQs in `wu_flag`.

## State and persistence
Runtime state lives in `pm80x_chip`: device/client pointers, companion/subchip pages, regmaps, IRQ chip data, chip type, IRQ mode, wakeup bitmask, and lock. Hardware PMIC registers persist while powered and may affect wakeup or RTC behavior across suspend.

## Dependencies and integration points
It depends on platform devices, interrupts, regmap/regmap-irq, atomics/spinlocks, I2C and regulator platform data. It integrates the PM80x MFD parent with regulator, RTC, input/onkey, GPIO/GPADC, and audio child drivers.

## Risks and test signals
Risks include register-page confusion, invalid virq mapping when `irq_data` is absent, wakeup bit index overflow from platform IRQs, PM805/PM800 mask naming inconsistencies, duplicate register definitions, and child drivers using undefined regulator slots. Test PM800 and PM805 probe, regmap page access, regulator ID mapping, IRQ request/free, wakeup suspend/resume, RTC alarm bits, GPADC reads, GPIO/headset modes, and deinit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/88pm80x.h -->
