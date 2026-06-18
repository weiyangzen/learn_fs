# subset-b-004525 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_mcu.c

## Purpose
This file implements the MediaTek WED WO MCU control path. It loads WO firmware into reserved memory regions, starts the WO CPU, builds MCU command SKBs, sends them through the WO CCIF TX queue, waits for sequence-matched responses, and handles unsolicited firmware events such as log dumps, profiling records, and RX counter updates.

## Important APIs and Functions
- `mtk_wed_mcu_send_msg()` is the serialized command entry point. It allocates an MCU message, pushes `struct mtk_wed_mcu_hdr`, sends through `mtk_wed_wo_queue_tx_skb()`, and optionally waits on `wo->mcu.wait`.
- `mtk_wed_mcu_msg_update()` is the higher-level WED device entry point. It checks RX capability and dispatches WO module commands.
- `mtk_wed_mcu_rx_event()` queues response SKBs on `wo->mcu.res_q`; `mtk_wed_mcu_rx_unsolicited_event()` consumes asynchronous events.
- `mtk_wed_mcu_init()` initializes MCU synchronization state, loads firmware, and polls `MTK_WED_DUMMY_CR_FWDL` until firmware clears the download marker.
- Firmware loading is split between `mtk_wed_mcu_load_firmware()`, `mtk_wed_get_memory_region()`, and `mtk_wed_mcu_run_firmware()`.

## Control Flow
Initialization maps reserved-memory regions named `wo-emi`, `wo-ilm`, `wo-data`, and `wo-boot`, writes a firmware-download marker into WED scratch space, selects a firmware name from hardware version/index and compatible string, copies trailer-described firmware regions to matching physical regions, writes the WO boot address, clears MCU reset bits, and waits for firmware acknowledgement. Runtime commands are serialized by `wo->mcu.mutex`; responses are dequeued until the expected sequence is found, with out-of-order responses returning `-EAGAIN`.

## State and Persistence
The file maintains global static `mem_region[]` metadata, including mapped IO addresses and `consumed` flags for shared regions. Per-WO MCU state lives in `wo->mcu`: sequence counter, timeout, response queue, mutex, and waitqueue. Firmware state persists in reserved memory and device registers outside this file.

## Dependencies and Integration Points
It depends on `mtk_wed_wo.c` for queue transmission and RX delivery, `mtk_wed_wo.h` for MCU message and firmware metadata layouts, `mtk_wed_regs.h` for scratch and boot registers, device tree reserved-memory names, Linux firmware loading, unaligned little-endian helpers, and WLAN callbacks such as `wed->wlan.update_wo_rx_stats`.

## Risks and Test Signals
Risks include malformed firmware trailers causing bad length arithmetic, global `mem_region[]` state being shared across hardware instances, unmatched response sequence SKBs being dropped after parse, and missing reserved-memory nodes silently yielding zero-sized regions. Useful tests are boot on MT7981/MT7986/MT7988 variants, firmware load failure paths, response timeout behavior, unsolicited RX counter parsing with short buffers, and concurrent command serialization under RX event pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_ops.c

## Purpose
This file provides the exported global WED operations hook used by MediaTek SoC networking code. It defines `mtk_soc_wed_ops` as an RCU-protected pointer to `struct mtk_wed_ops` and exports it to GPL modules.

## Important APIs and Types
- `const struct mtk_wed_ops __rcu *mtk_soc_wed_ops` is the shared operations table pointer.
- `EXPORT_SYMBOL_GPL(mtk_soc_wed_ops)` makes the hook available to other kernel objects.

## Control Flow
There is no executable control flow in this file. Producers and consumers elsewhere are expected to publish and dereference the pointer with RCU discipline.

## State and Persistence
The only state is the global pointer. Its value persists for the lifetime of the loaded module/kernel image and acts as a cross-driver registration point.

## Dependencies and Integration Points
It includes the public MediaTek WED SoC header, which defines `struct mtk_wed_ops`. It integrates with WED provider and consumer drivers through symbol linkage rather than direct calls.

## Risks and Test Signals
The main risk is misuse outside RCU read-side protection or publishing without the expected synchronization. Test signals are sparse: build/link coverage, module load/unload paths, and runtime WED attach/detach paths that exercise the external symbol are the practical validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_regs.h

## Purpose
This header is the MediaTek WED register and descriptor contract. It defines WED, WPDMA, WDMA, RRO/RROQM/RTQM, RX buffer manager, AMSDU, PCIe mirror, interrupt, DMA, reset, MIB, and descriptor bitfields used by the WED implementation.

## Important APIs and Types
- `struct mtk_wdma_desc` defines the packed four-word WDMA descriptor layout.
- `MTK_WED_RESET`, `MTK_WED_CTRL`, `MTK_WED_GLO_CFG`, and related bitfields describe major WED engine reset/enable/busy controls.
- `MTK_WED_RING_TX()`, `MTK_WED_RING_RX()`, `MTK_WDMA_RING_TX()`, and similar macros compute ring register offsets.
- WPDMA/WDMA interrupt, prefetch, reset-index, coherent MIB, and DMA global configuration macros are used by setup, teardown, and diagnostics.
- RRO and AMSDU definitions expose v3 receive reorder and aggregation hardware programming surfaces.

## Control Flow
The header has no runtime control flow. It shapes control flow in users by providing register addresses, masks, and field encodings that decide how drivers poll busy bits, reset engines, program rings, and read counters.

## State and Persistence
All state represented here is hardware state. Driver code persists values in device registers, DMA descriptors, and hardware counters using these offsets and masks.

## Dependencies and Integration Points
It assumes kernel bit helpers such as `BIT()` and `GENMASK()`. It is included by WED core, WO MCU, and WO queue code. The macros align the Ethernet DMA path with Wi-Fi offload DMA, PCIe interrupt routing, RX reorder offload, and hardware MIB/statistics paths.

## Risks and Test Signals
Risks are register drift between WED hardware versions, duplicated definitions such as `MTK_WED_PCIE_CFG_BASE`, field-width mistakes, and accidental use of v2/v3-only bits on older chips. Good validation signals are register programming traces during WED bring-up, DMA ring traffic, reset recovery, interrupt routing, MIB reads, and compile coverage across supported MediaTek SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_wo.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_wo.c

## Purpose
This file implements the MediaTek WED WO CCIF queue and interrupt transport used by the MCU layer. It maps the WO CCIF syscon, allocates TX/RX descriptor rings, manages DMA-backed page-fragment buffers, handles RX interrupts in a tasklet, and exposes `mtk_wed_wo_queue_tx_skb()` for MCU command transmission.

## Important APIs and Functions
- `mtk_wed_wo_init()` allocates `struct mtk_wed_wo`, initializes hardware queues and interrupts, then starts the MCU firmware path.
- `mtk_wed_wo_deinit()` disables interrupts and frees queue resources.
- `mtk_wed_wo_queue_tx_skb()` copies an SKB into a preallocated TX DMA buffer, updates the descriptor, kicks the queue, and frees the SKB.
- `mtk_wed_wo_rx_run_queue()` converts completed RX fragments into SKBs and routes response vs unsolicited MCU messages.
- Internal helpers cover MMIO reads/writes, IRQ masking/ack, ring refill/dequeue/reset, and queue cleanup.

## Control Flow
Initialization obtains the `mediatek,wo-ccif` phandle, resolves a regmap, maps an IRQ, sets up a tasklet, requests the IRQ, allocates TX and RX coherent descriptor rings, refills buffers, writes ring base/size registers, and enables interrupts. The IRQ handler masks interrupts and schedules the tasklet. The tasklet reads pending channels, disables handled masks, drains RX descriptors, hands valid MCU packets to `mtk_wed_mcu_rx_event()` or `mtk_wed_mcu_rx_unsolicited_event()`, refills RX buffers, kicks hardware, acknowledges RX, and reenables interrupts.

## State and Persistence
Per-device state is stored in `struct mtk_wed_wo`: `q_tx`, `q_rx`, regmap/IRQ/tasklet state, and MCU state initialized by `mtk_wed_mcu_init()`. Queue state includes descriptor DMA address, head/tail indexes, queued count, buffer size, page-frag cache, and per-entry DMA mapping metadata. Hardware state persists in CCIF registers and descriptor memory.

## Dependencies and Integration Points
It integrates with device tree, syscon regmap, IRQ core, DMA mapping, SKB allocation, page-frag cache, `mtk_wed_mcu.c`, and register definitions from `mtk_wed_wo.h` and `mtk_wed_regs.h`.

## Risks and Test Signals
Risks include TX ring full handling returning `-ENOMEM`, DMA address truncation to 32-bit descriptor fields, RX buffer starvation under GFP_ATOMIC pressure, tasklet/IRQ ordering bugs, and deinit after partial init. Test signals include successful firmware command/response exchange, RX unsolicited event delivery, IRQ masking/reenable behavior, DMA mapping error injection, and repeated init/deinit cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_wo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_wo.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_wo.h

## Purpose
This header defines the MediaTek WED WO firmware, MCU message, CCIF queue, and per-device transport data structures shared by `mtk_wed_mcu.c` and `mtk_wed_wo.c`.

## Important APIs and Types
- `struct mtk_wed_mcu_hdr` is the MCU wire header with version, command, length, sequence, flags, status, and reserved payload area.
- `struct mtk_wed_fw_region` and `struct mtk_wed_fw_trailer` describe firmware layout metadata parsed from WO firmware binaries.
- `struct mtk_wed_wo_queue_desc`, `struct mtk_wed_wo_queue_entry`, and `struct mtk_wed_wo_queue` describe CCIF DMA rings.
- `struct mtk_wed_wo` ties hardware, TX/RX queues, MCU response synchronization, and MMIO IRQ state together.
- `mtk_wed_mcu_check_msg()` validates MCU packet version and length before dispatch.

## Control Flow
The header declares the init/deinit, MCU send/update, RX event, unsolicited event, and TX SKB functions that form the WO transport lifecycle. It also defines command flags such as response-needed and response message indicators that drive dispatch decisions in the C files.

## State and Persistence
State is primarily per-WO instance: queue descriptors and buffers, MCU wait/response queue/sequence, and regmap IRQ mask/tasklet metadata. Firmware state is represented through reserved-memory region names and firmware binary names.

## Dependencies and Integration Points
It depends on SKB and netdevice kernel types, MediaTek WED hardware forward declarations, firmware files for MT7981/MT7986/MT7988, CCIF register offsets, and MCU boot reset bits.

## Risks and Test Signals
Risks include ABI mismatch with firmware message headers, hard-coded command length/ring size limits, packed descriptor alignment assumptions, and global firmware names drifting from linux-firmware packaging. Test signals are compiler layout checks through normal builds, firmware boot, MCU message validation failures, and runtime RX/TX ring operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_wo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/Kconfig

## Purpose
This Kconfig file gates Mellanox Ethernet/RDMA networking drivers behind the `NET_VENDOR_MELLANOX` vendor option and includes the Kconfig files for mlx4, mlx5, mlxsw, mlxfw, and mlxbf_gige.

## Important Configuration
- `NET_VENDOR_MELLANOX` is a bool defaulting to `y`, dependent on `PCI || I2C`.
- The `if NET_VENDOR_MELLANOX` block controls visibility of all sourced Mellanox subdriver options.

## Control Flow
Kconfig evaluation exposes or hides the nested driver menus. The option itself does not directly build code; it allows selection of specific Mellanox drivers.

## State and Persistence
The persistent output is kernel configuration state in `.config`, which determines which Makefile objects are later compiled.

## Dependencies and Integration Points
It integrates with the top-level Ethernet vendor menu and delegates actual driver options to child Kconfig files.

## Risks and Test Signals
Risk is mainly accidental menu invisibility if dependencies or source paths drift. Test signals are `make menuconfig` visibility, `olddefconfig`, and builds with Mellanox vendor disabled or enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/Makefile

## Purpose
This Makefile maps Mellanox Kconfig symbols to subdirectories built by kbuild.

## Important Build Rules
- `obj-$(CONFIG_MLX4_CORE) += mlx4/`
- `obj-$(CONFIG_MLX5_CORE) += mlx5/core/`
- `obj-$(CONFIG_MLXSW_CORE) += mlxsw/`
- `obj-$(CONFIG_MLXFW) += mlxfw/`
- `obj-$(CONFIG_MLXBF_GIGE) += mlxbf_gige/`

## Control Flow
Kbuild evaluates the config-dependent object assignments and descends only into selected subtrees.

## State and Persistence
No runtime state exists. The file contributes to build graph state determined by `.config`.

## Dependencies and Integration Points
It depends on the Mellanox child directories and their local Makefiles. It connects vendor-level config symbols to concrete compilation.

## Risks and Test Signals
Risks include symbol or directory rename drift. Test signals are allmodconfig/allnoconfig builds and targeted builds for each Mellanox driver family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/Kconfig

## Purpose
This file defines mlx4 core and Ethernet driver configuration, including optional Data Center Bridging support, debug output, and old generation PCI ID support.

## Important Configuration
- `MLX4_EN` is the Ethernet driver tristate. It depends on PCI, networking, Ethernet, INET, and optional PTP clock support; it selects `PAGE_POOL` and `MLX4_CORE`.
- `MLX4_EN_DCB` enables DCB support when `MLX4_EN && DCB` are available.
- `MLX4_CORE` is the underlying mlx4 core tristate, selecting auxiliary bus and devlink support.
- `MLX4_DEBUG` and `MLX4_CORE_GEN2` toggle verbose diagnostics and old device ID support.

## Control Flow
Kconfig dependency resolution ensures the Ethernet driver pulls in core support and only exposes DCB when the generic DCB stack exists.

## State and Persistence
The chosen options persist in kernel configuration and affect which objects and features are compiled.

## Dependencies and Integration Points
This file integrates mlx4 with PCI, netdevice, PTP, DCB, page pool, auxiliary bus, and devlink subsystems.

## Risks and Test Signals
Risks include missing dependency selections for features used by the Makefile or source, and user-visible configuration combinations that compile but lack runtime support. Test signals are config matrix builds around `MLX4_EN`, `MLX4_EN_DCB`, `PTP_1588_CLOCK_OPTIONAL`, and `DCB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/Makefile

## Purpose
This Makefile defines the mlx4 core and mlx4 Ethernet module object composition.

## Important Build Rules
- `mlx4_core-y` aggregates allocator, command, CQ/EQ, firmware, ICM, interface, main, multicast, memory registration, port, profile, QP, reset, sense, SRQ, resource tracker, and crash dump code.
- `mlx4_en-y` aggregates Ethernet main, TX/RX, ethtool, port, CQ, resource, netdev, selftest, and clock files.
- `mlx4_en-$(CONFIG_MLX4_EN_DCB) += en_dcb_nl.o` conditionally adds DCB netlink support.

## Control Flow
Kbuild builds `mlx4_core.o` when `CONFIG_MLX4_CORE` is set and `mlx4_en.o` when `CONFIG_MLX4_EN` is set. DCB support is compiled only under its Kconfig option.

## State and Persistence
There is no runtime state. The file persists module composition and therefore controls which symbols are linked.

## Dependencies and Integration Points
It integrates with mlx4 Kconfig symbols and the kernel module build system.

## Risks and Test Signals
Risks include missing objects when source files add external symbols, or DCB symbols referenced without the conditional object. Test signals are module builds with and without `CONFIG_MLX4_EN_DCB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/alloc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/alloc.c

## Purpose
This file provides core mlx4 allocation utilities: bitmap-backed object IDs, priority zone allocation, DMA queue buffers, doorbell pages, and compound hardware queue resources.

## Important APIs and Functions
- `mlx4_bitmap_alloc*()`, `mlx4_bitmap_free*()`, `mlx4_bitmap_init()`, and `mlx4_bitmap_cleanup()` manage reusable numeric resources with reserved ranges, round-robin behavior, alignment, and skip masks.
- `mlx4_zone_allocator_create()`, `mlx4_zone_add_one()`, `mlx4_zone_alloc_entries()`, and related free/remove helpers layer priority and fallback semantics over bitmaps.
- `mlx4_buf_alloc()` and `mlx4_buf_free()` allocate coherent queue memory either as one direct block or page list.
- `mlx4_db_alloc()` and `mlx4_db_free()` allocate doorbell records from coherent pages with order-0/order-1 bitmap splitting.
- `mlx4_alloc_hwq_res()` and `mlx4_free_hwq_res()` combine doorbell, buffer, MTT allocation, and MTT programming for hardware queues.

## Control Flow
Bitmap allocation searches from `last`, wraps by advancing `top`, marks bits, and decrements availability. Zone allocation first tries the requested zone, then optional lower/equal/higher priority fallbacks based on flags. Queue resource allocation is staged with rollback labels: doorbell, direct buffer, MTT init, then MTT write.

## State and Persistence
State is in `struct mlx4_bitmap`, zone allocator lists, doorbell page directories on `priv->pgdir_list`, DMA coherent memory, and MTT entries programmed into device memory translation tables. Locks include bitmap spinlocks, zone allocator spinlock, and `priv->pgdir_mutex`.

## Dependencies and Integration Points
It depends on Linux bitmap, DMA mapping, vmalloc/slab helpers, mlx4 private structures, MTT helpers, PCI device DMA context, and exported symbols used by CQ/QP/SRQ/Ethernet code.

## Risks and Test Signals
Risks include bitmap wrap bugs, zone list priority corruption, freeing ranges with wrong offset/mask, direct DMA allocation alignment assumptions, and doorbell order coalescing mistakes. Test signals include resource exhaustion tests, repeated allocation/free cycles, multi-function resource partitioning, CQ/QP bring-up, and DMA API debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/catas.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/catas.c

## Purpose
This file implements mlx4 catastrophic/internal error detection and recovery. It polls firmware error state, detects PF/VF communication-channel internal errors, captures crash dumps for PFs, resets the device or asks the PF to reset a VF, and notifies clients.

## Important APIs and Functions
- `mlx4_start_catas_poll()` maps the PF catastrophic error buffer and starts a timer.
- `poll_catas()` detects slave comm-channel internal errors, PF catas buffer nonzero state, or persistent internal-error marks.
- `mlx4_enter_error_state()` performs reset handling and dispatches `MLX4_DEV_EVENT_CATASTROPHIC_ERROR`.
- `mlx4_reset_master()` and `mlx4_reset_slave()` implement PF and VF reset flows.
- `mlx4_catas_init()`/`mlx4_catas_end()` manage the single-thread health workqueue.

## Control Flow
The timer periodically polls. On error it queues `catas_work`, which calls `mlx4_handle_error_state()`. The handler enters error state, resets hardware, wakes pending command completions, dispatches events, and if interfaces are up attempts `mlx4_restart_one()` under devlink and interface-state locking.

## State and Persistence
Persistent device state is held in `dev->persist->state`, `interface_state`, workqueue/work item, and the mapped `priv->catas_err.map`. Module parameter `internal_err_reset` controls whether reset flow is active.

## Dependencies and Integration Points
It integrates with PCI config access, mlx4 reset/restart, devlink locking, command completion wakeups, crash dump collection, event dispatch, timers, and workqueues.

## Risks and Test Signals
Risks include reset while PCI channel is offline, BUG_ON on unrecoverable reset failure, race with device deletion, and missed health-buffer mapping. Test signals include injected firmware health errors, VF reset request/ack toggles, PCI EEH/offline paths, devlink restart logs, and client catastrophic event reception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/catas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/cmd.c

## Purpose
This is the mlx4 firmware command engine and SR-IOV command mediation layer. It posts commands through HCR registers or the VF communication channel, switches between polling and event completions, translates firmware statuses, manages command mailboxes, processes virtual HCR requests from slaves, initializes multi-function communication state, and exposes VF administration APIs.

## Important APIs and Functions
- `__mlx4_cmd()` is the central command dispatcher used by wrappers. It chooses native HCR polling/events or VF virtual-command path.
- `mlx4_cmd_poll()` and `mlx4_cmd_wait()` implement native polling and event completion over HCR.
- `mlx4_comm_cmd_poll()`, `mlx4_comm_cmd_wait()`, and `mlx4_slave_cmd()` implement slave-to-master communication channel commands.
- `mlx4_master_process_vhcr()` reads a slave vHCR/inbox, applies `cmd_info[]` policy, executes wrappers or native commands, writes outbox/status, and optionally generates a completion EQE.
- `mlx4_multi_func_init()` and `mlx4_multi_func_cleanup()` map communication pages and set up master/slave SR-IOV state.
- Exported VF APIs include `mlx4_set_vf_mac()`, `mlx4_set_vf_vlan()`, `mlx4_set_vf_rate()`, `mlx4_set_vf_spoofchk()`, `mlx4_get_vf_config()`, `mlx4_set_vf_link_state()`, and stats/SMI helpers.

## Control Flow
Native commands acquire command semaphores, wait for HCR readiness, write input/output parameters and opcode with memory ordering, then either poll the go bit or wait for a command event token. Multi-function slaves fill a shared vHCR and notify the PF; the PF workqueue decodes command-channel toggles, validates the expected boot/reset/VHCR sequence, processes commands through `cmd_info[]`, and writes status back. Error paths translate firmware status to errno and may enter internal error reset flow for fatal closing-command failures or timeouts.

## State and Persistence
State spans `priv->cmd` semaphores, HCR mapping, command context array, token mask/free list, mailbox DMA pool, polling/event mode, and communication toggles. Multi-function state spans mapped comm pages, per-slave state, admin and operational VF state, QoS managers, registered VLAN/MAC indexes, event EQ records, workqueues, and resource tracker state. VF admin settings persist in driver memory and often take effect on VF restart unless immediate update is possible.

## Dependencies and Integration Points
It integrates with firmware command opcodes, `fw.c` wrappers, resource tracker, RDMA subnet management packets, PCI MMIO, DMA pool mailboxes, devlink/internal reset handling, EQ command events, VLAN/MAC registration, QoS VPP firmware commands, network VF netlink APIs, and mlx4 Ethernet/RDMA resource consumers.

## Risks and Test Signals
Risks include command timeout recovery races, toggles becoming unsynchronized across FLR or misbehaving VMs, permission gaps in vHCR wrappers, mailbox DMA failures, inconsistent admin vs operational VF state, and fatal reset paths during close. Test signals include polling/event mode switching, SR-IOV VF boot handshake, VF command denial/allowance, FLR recovery, command timeout injection, VF VLAN/QoS/spoof/link configuration, and pending command wakeups on catastrophic error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/cq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/cq.c

## Purpose
This file implements mlx4 core completion queue management: CQ number allocation, ICM mapping, firmware state transitions, CQ resize/moderation, completion/event dispatch, tasklet deferral, and CQ table lifecycle.

## Important APIs and Functions
- `mlx4_cq_alloc()` allocates a CQN, inserts the CQ into the radix tree, builds a CQ context mailbox, optionally initializes CQEs, and transitions the CQ from software to hardware ownership.
- `mlx4_cq_free()` transitions hardware back to software, removes the radix-tree entry, synchronizes IRQs, waits for refcount completion, and frees ICM.
- `mlx4_cq_completion()` and `mlx4_cq_event()` look up CQs by number and invoke completion or async event callbacks.
- `mlx4_cq_modify()` and `mlx4_cq_resize()` issue firmware modify commands.
- `mlx4_init_cq_table()` and `mlx4_cleanup_cq_table()` manage the CQ radix tree and bitmap.

## Control Flow
Completion events are normally dispatched by EQ code into `mlx4_cq_completion()`, which increments `arm_sn` and invokes the CQ completion callback. The default callback queues the CQ onto an EQ tasklet list with a refcount. The tasklet drains queued CQs for a bounded time and reschedules if work remains.

## State and Persistence
State includes the core CQ radix tree, bitmap of CQN ownership, ICM table references, per-CQ refcount/completion, arm sequence, EQ vector/IRQ, UAR, and tasklet list node. Hardware CQ state is persisted through firmware SW2HW/HW2SW/MODIFY commands.

## Dependencies and Integration Points
It depends on `mlx4_cmd*()` firmware commands, ICM tables, MTT addresses, EQ vectors, radix tree, RCU, IRQ synchronization, and CQ consumers such as mlx4_en and RDMA.

## Risks and Test Signals
Risks include use-after-free around interrupt dispatch, radix-tree stale entries, CQE initialization failures for user CQs, vector bounds mistakes, and multi-function resource mapping errors. Test signals include CQ create/destroy stress, interrupt affinity/vector tests, resize/moderation operations, user CQ creation, and IRQ synchronization under teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/crdump.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/crdump.c

## Purpose
This file collects mlx4 firmware crash dumps into devlink regions. It snapshots PCI CR space and the firmware health buffer when crash dumping is enabled and supported.

## Important APIs and Functions
- `mlx4_crdump_init()` creates devlink regions `cr-space` and `fw-health`.
- `mlx4_crdump_collect()` maps PCI BAR0, obtains a devlink snapshot id, enables CR-space access, collects both regions, restores access state, and unmaps.
- `mlx4_crdump_collect_crspace()` copies BAR0 CR space into a vmalloc buffer and creates a devlink snapshot.
- `mlx4_crdump_collect_fw_health()` snapshots the health buffer.
- `mlx4_crdump_end()` destroys devlink regions.

## Control Flow
Collection is skipped if firmware lacks a health buffer address or snapshots are disabled. Otherwise, BAR0 is mapped, volatile CR access is blocked, the firmware CR filter is temporarily relaxed, region snapshots are created, and all access bits are restored before unmapping.

## State and Persistence
`dev->persist->crdump` stores devlink region pointers and the `snapshot_enable` flag. Snapshot data persists in devlink until consumed or evicted by the region's snapshot limit. A static boolean tracks whether the CR enable bit was set before dumping.

## Dependencies and Integration Points
It integrates with devlink regions/snapshots, PCI BAR resources, firmware health buffer capabilities, and catastrophic error recovery in `catas.c`.

## Risks and Test Signals
Risks include large BAR allocation failure, failure to restore CR filter state, static CR enable state shared across devices, and snapshot create failures leaking diagnostic coverage. Test signals include devlink region visibility, snapshot creation after injected firmware error, disabled snapshot behavior, and allocation failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/crdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_clock.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_clock.c

## Purpose
This file implements mlx4 Ethernet hardware timestamp and PHC support. It converts device cycle counter values to nanoseconds, extracts CQE timestamps, registers a PTP clock, and implements PTP adjust/get/set callbacks.

## Important APIs and Functions
- `mlx4_en_init_timestamp()` initializes `cyclecounter`, `timecounter`, seqlock, nominal multiplier, and registers the PHC.
- `mlx4_en_remove_timestamp()` unregisters the PHC.
- `mlx4_en_get_cqe_ts()` reconstructs a 48-bit timestamp from CQE fields.
- `mlx4_en_get_hwtstamp()` and `mlx4_en_fill_hwtstamps()` convert device cycles into SKB hardware timestamps.
- PTP callbacks `mlx4_en_phc_adjfine()`, `mlx4_en_phc_adjtime()`, `mlx4_en_phc_gettime()`, and `mlx4_en_phc_settime()` update/read the timecounter under seqlock.

## Control Flow
Initialization is once per shared `mlx4_en_dev`, even if called for multiple netdev ports. Runtime RX/TX timestamp paths read the timecounter under a seqlock. Periodic overflow checks call `timecounter_read()` before the 48-bit cycle counter can wrap.

## State and Persistence
State lives in `mdev->cycles`, `mdev->clock`, `mdev->clock_lock`, `mdev->nominal_c_mult`, `mdev->last_overflow_check`, `mdev->ptp_clock_info`, and `mdev->ptp_clock`. PHC registration persists until removed.

## Dependencies and Integration Points
It depends on mlx4 device clock reads, Linux clocksource/timecounter helpers, PTP clock framework, SKB timestamp structures, and hwtstamp configuration in the Ethernet driver.

## Risks and Test Signals
Risks include wraparound if overflow work is delayed, incorrect multiplier/shift for unusual core clocks, CQE timestamp reconstruction edge cases around low-word zero, and concurrent PHC adjustments. Test signals include `ptp4l`/`phc2sys`, hardware timestamp RX/TX tests, PHC get/set/adj operations, and long-running wraparound coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_cq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_cq.c

## Purpose
This file adapts core mlx4 completion queues for the mlx4 Ethernet driver. It allocates Ethernet CQ buffers, activates them with IRQ/EQ/NAPI bindings, sets completion callbacks for TX/RX, and tears them down.

## Important APIs and Functions
- `mlx4_en_create_cq()` allocates the Ethernet CQ structure and hardware queue resources on a requested NUMA node.
- `mlx4_en_activate_cq()` assigns EQ vectors, initializes doorbells and buffers, enables timestamping when configured, calls core `mlx4_cq_alloc()`, and attaches NAPI.
- `mlx4_en_deactivate_cq()` detaches NAPI and frees the core CQ.
- `mlx4_en_destroy_cq()` frees hardware queue resources and releases assigned EQs.
- `mlx4_en_set_cq_moder()` and `mlx4_en_arm_cq()` expose moderation and arming.

## Control Flow
Create only allocates memory and DMA resources. Activate binds the CQ to a netdev and vector, handling RX vector assignment and TX vector reuse from RX CQs. Depending on CQ type, it installs `mlx4_en_tx_irq` or `mlx4_en_rx_irq`, adds NAPI, and links NAPI to netdev queue IDs. Deactivate reverses NAPI and hardware CQ state.

## State and Persistence
State includes `struct mlx4_en_cq` fields for size, buffer, CQ index, ring, type, vector, IRQ affinity mask, NAPI, and embedded core `mcq`. Doorbell and buffer state comes from `mlx4_hwq_resources`.

## Dependencies and Integration Points
It integrates with core CQ allocation in `cq.c`, queue resources from `alloc.c`, EQ assignment, netdev NAPI APIs, TX/RX polling functions, timestamp configuration, and IRQ affinity.

## Risks and Test Signals
Risks include EQ leak on activation errors, TX relying on RX CQ vector availability, NAPI teardown ordering, and timestamp enable mismatches. Test signals include interface open/close, queue count changes, IRQ affinity inspection, NAPI poll activity, CQ moderation changes, and hwtstamp enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_dcb_nl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_dcb_nl.c

## Purpose
This file implements mlx4 Ethernet DCB netlink operations. It exposes CEE and IEEE DCBX controls for PFC, ETS, application priority, max-rate scheduling, and QCN congestion control.

## Important APIs and Functions
- `mlx4_en_dcbnl_ops` and `mlx4_en_dcbnl_pfc_ops` are exported operation tables consumed by netdev DCBNL registration.
- CEE helpers get/set PFC state/config, DCB enable state, app priority, and `setall` pause/PFC programming.
- IEEE helpers get/set ETS, PFC, maxrate, QCN parameters, and QCN stats.
- `mlx4_en_ets_validate()` validates traffic class mapping and ETS bandwidth sums.
- `mlx4_en_config_port_scheduler()` maps IEEE TSA/bandwidth/rate settings to firmware scheduler parameters.

## Control Flow
Netlink callbacks read or mutate `mlx4_en_priv` configuration, validate requested ETS/QCN/rate state, then issue firmware commands such as `mlx4_SET_PORT_general()`, `mlx4_SET_PORT_PRIO2TC()`, `mlx4_SET_PORT_SCHEDULER()`, and congestion-control mailbox commands. DCBX mode changes reset ETS/PFC state or apply CEE settings depending on the selected mode.

## State and Persistence
Driver state includes `priv->dcbx_cap`, `priv->flags`, `priv->cee_config`, `priv->ets`, `priv->maxrate`, `priv->cndd_state`, port profile pause/PFC bitmaps, and stats bitmap. Hardware state persists in port pause/PFC, scheduler, priority-to-TC, max-rate, and QCN firmware configuration.

## Dependencies and Integration Points
It depends on the kernel DCBNL API, `fw_qos.h`, mlx4 firmware port commands, congestion-control opcodes, netdev private state, and DCB application priority helpers.

## Risks and Test Signals
Risks include invalid DCBX mode transitions, ETS bandwidth sums not equal to 100 for ETS classes, rate unit rounding surprises, mailbox allocation failures, and QCN support only when firmware advertises it. Test signals include `dcbtool`/`lldptool`/`ip link` DCB operations, PFC pause behavior, ETS scheduling validation, maxrate programming, QCN get/set/stat paths, and builds with `CONFIG_MLX4_EN_DCB` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_dcb_nl.c -->
