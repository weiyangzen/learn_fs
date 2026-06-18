# subset-b-004425 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth.c

## Purpose
Implements the Freescale/NXP QE UCC Gigabit Ethernet netdevice driver. It binds an Open Firmware platform device, configures UCC Fast/QE register state, allocates QE MURAM parameter blocks and external buffer descriptor rings, connects phylink, and moves packets through the Linux networking stack with NAPI.

## Important APIs, Types, And Functions
The driver centers on `struct ucc_geth_private` and `struct ucc_geth_info` from `ucc_geth.h`. Entry points are `ucc_geth_probe()`, `ucc_geth_remove()`, `ucc_geth_open()`, `ucc_geth_close()`, `ucc_geth_start_xmit()`, `ucc_geth_irq_handler()`, `ucc_geth_poll()`, `ucc_geth_suspend()`, and `ucc_geth_resume()`. Initialization helpers include `ucc_struct_init()`, `ucc_geth_startup()`, `ucc_geth_alloc_tx()`, `ucc_geth_alloc_rx()`, `rx_bd_buffer_set()`, and `init_*` register encoders. Link integration is through `ugeth_mac_ops`, especially `ugeth_mac_link_up()`, `ugeth_mac_link_down()`, and `ugeth_mac_config()`.

## Control Flow
Probe reads device-tree UCC number, clocks, register resource, IRQ, PHY mode, optional TBI node, and creates a `net_device` with NAPI, phylink, ethtool, timeout work, and netdev ops. Open attaches PHY, initializes the UCC/MAC, requests the IRQ, starts phylink, enables NAPI, and starts the queue. Startup validates queue/ring parameters, initializes UCC Fast, maps UCC registers, allocates Tx/Rx BD rings, allocates many QE MURAM PRAM blocks, fills InitEnet thread entries/SNUMs, loads Rx buffers, and issues `QE_INIT_TX_RX`. Tx maps an skb into a Tx BD, advances ring indices, and optionally rings Tx-on-demand/scheduler state. IRQ masks RX/TX events and schedules NAPI; NAPI reclaims Tx BDs, receives completed Rx BDs, refills buffers, then rearms events.

## State And Persistence
Runtime state is in memory and device registers: BD rings, skb arrays, ring pointers, QE MURAM offsets, SNUM ownership, phylink state, multicast hash lists, statistics PRAM, WoL flags, and timeout work. No durable storage is used. Cleanup is `ucc_geth_stop()` plus `ucc_geth_memclean()`, which frees UCC Fast state, MURAM blocks, InitEnet SNUM/thread entries, skb rings, hash lists, and ioremaps.

## Dependencies And Integration Points
Depends on Linux netdev/NAPI/DMA/skbuff APIs, phylink/PHY/OF helpers, platform driver APIs, QE/UCC Fast SoC support, and optional PM/netpoll. It shares ethtool support with `ucc_geth_ethtool.c` via `uec_set_ethtool_ops()`.

## Risks
The startup path has many staged allocations; partial failure relies on the caller invoking stop/cleanup. DMA mappings are mostly tracked through BDs, so mismatched ring status or missing unmap can leak mappings. Tx ring wrap assumes power-of-two ring lengths through `TX_RING_MOD_MASK(size)`. `ugeth_graceful_stop_*()` do not return timeout failures despite waiting. Link-mode reconfiguration quiesces NAPI and IRQs, which needs careful ordering to avoid lost interrupts or deadlocks. Suspend/resume behavior diverges depending on whether QE survives sleep.

## Test Signals
Useful signals are successful platform probe/register_netdev, open/close cycles with phylink up/down, packet Tx/Rx under NAPI, multicast/promiscuous mode updates, ethtool stats/register reads, ring size validation, suspend/resume with and without MAC WoL, and fault injection through allocation/DMA-map failures in startup and Rx refill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth.h

## Purpose
Internal interface and hardware contract for the QE UCC Gigabit Ethernet driver. It defines the UCC register layout, bit fields, QE parameter RAM structures, buffer descriptor flags, defaults, and the main driver-private state shared by `ucc_geth.c` and `ucc_geth_ethtool.c`.

## Important APIs, Types, And Functions
Key types are `struct ucc_geth` for memory-mapped MAC registers, `struct ucc_geth_info` for configuration/defaults, and `struct ucc_geth_private` for live netdevice state. Hardware-facing PRAM structs include Tx/Rx thread data, send queue descriptors, scheduler state, firmware statistics, interrupt coalescing tables, Rx BD queue entries, global Tx/Rx PRAM, InitEnet command parameters, 82xx address filtering, and statistics snapshots. Exported declarations are `uec_set_ethtool_ops()` and `init_flow_control_params()`.

## Control Flow
The header itself has no executable flow, but its layout drives driver sequencing: defaults are copied into `ucc_geth_info`, validated by `ucc_struct_init()`, encoded into registers and PRAM by `ucc_geth_startup()`, and consumed by Tx/Rx fast paths. Ring lengths, queue counts, alignment constants, SNUM entry limits, and event masks define the legal transitions for startup, interrupt handling, and teardown.

## State And Persistence
Defines volatile hardware state, not persisted data. `struct ucc_geth_private` records register mappings, MURAM pointers/offsets, skb arrays, BD cursors, multicast hash bookkeeping, phylink state, WoL state, and debug level. The register/PRAM structs are packed to match hardware layout and are accessed through endian-aware MMIO helpers.

## Dependencies And Integration Points
Includes Linux list/phylink/Ethernet headers and Freescale QE/UCC headers. The constants mirror QE firmware expectations: InitEnet entries, RISC allocation masks, BD status bits, UCC event bits, TBI PHY registers, and UPSMR/MACCFG fields.

## Risks
Packed hardware layout and manual offsets are brittle across hardware revisions. Several masks/shift values assume big-endian register interpretation. Ring modulo macros require power-of-two lengths although validation only enforces minimum/alignment for Rx and minimum for Tx. `struct ucc_geth_private` contains fields no longer heavily used (`mii_info`, `conf_skbs`, address register arrays), increasing maintenance risk.

## Test Signals
Compile coverage should catch layout symbol drift against QE headers. Runtime signals include successful InitEnet, correct ethtool register/stat sizes, valid phylink mode changes using the MACCFG/UPSMR definitions, and clean allocation/free of every MURAM-backed pointer in `struct ucc_geth_private`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth_ethtool.c

## Purpose
Provides ethtool operations for the QE UCC Ethernet driver: link settings via phylink, pause parameters, message level, register dumps, ring sizing, statistics strings/data, driver info, timestamp info, and optional Wake-on-LAN configuration.

## Important APIs, Types, And Functions
`uec_set_ethtool_ops()` installs `uec_ethtool_ops`. Link and pause handlers delegate to `phylink_ethtool_*`. Ring handlers read/write `ug_info->bdRingLenRx/Tx[0]`. Stats are backed by three string tables: hardware MAC stats, Tx firmware stats, and Rx firmware stats. `uec_get_ethtool_stats()` reads from UCC registers and firmware statistics PRAM. PM builds add `uec_get_wol()` and `uec_set_wol()`.

## Control Flow
Etthool requests enter the netdevice's ops table, fetch `struct ucc_geth_private`, and either delegate to phylink or read/update cached driver configuration. Ring changes validate minimum/alignment and reject updates while the netdev is running. Stats count and strings are conditional on `ug_info->statisticsMode`; data read follows the same ordering so userspace names line up with values. WoL first asks phylink/PHY, then falls back to MAC magic-packet support only when QE stays alive during sleep.

## State And Persistence
Changes persist only in live driver memory: message level, pause flags, ring lengths for next open, and WoL flags in `ugeth`. Stats are live hardware/firmware counters. No disk state exists.

## Dependencies And Integration Points
Integrates with `ucc_geth.h`, phylink, ethtool core, PM wakeup APIs, and QE sleep capability helpers. It depends on `ucc_geth.c` to allocate statistics PRAM before stats are meaningful.

## Risks
The file documents a first-queue-only limitation; multi-queue expansion would need broader ring handling. `uec_get_strings()` does not switch on `stringset`, assuming only stats callers after count gating. Register and stat reads can return zero if PRAM/register pointers are unavailable, which is safe but may mask inactive hardware. Ring changes while down require a manual reopen to take effect.

## Test Signals
Run `ethtool -i`, `-d`, `-S`, `-g/-G`, pause get/set, link mode get/set, and WoL get/set under PM-capable and non-PM builds. Verify stats names and counts match, ring validation rejects invalid values and `-EBUSY` while running, and pause/WoL changes alter later MAC initialization/suspend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/xgmac_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/xgmac_mdio.c

## Purpose
Implements the Freescale/NXP QorIQ 10G MDIO platform driver for FMan XGMAC/MEMAC MDIO controllers. It registers an `mii_bus` supporting Clause 22 and Clause 45 accesses over memory-mapped MDIO registers.

## Important APIs, Types, And Functions
`struct tgec_mdio_controller` maps the hardware registers; `struct mdio_fsl_priv` holds the MMIO base, optional clock, requested MDC frequency, endianness, and erratum flags. Bus callbacks are `xgmac_mdio_read_c22()`, `xgmac_mdio_write_c22()`, `xgmac_mdio_read_c45()`, and `xgmac_mdio_write_c45()`. Probe configures `mii_bus` and registers it through OF or ACPI.

## Control Flow
Probe obtains the memory resource, allocates a managed `mii_bus`, maps BAR/register memory without exclusive request, determines endianness and errata properties, optionally suppresses preamble, optionally programs MDC divider from `clock-frequency`, then registers the bus with OF or ACPI firmware nodes. Each read/write selects Clause 22 or Clause 45 encoding, waits for the bus to be idle, writes port/dev/register fields, initiates transfer, waits for completion, and returns data or error.

## State And Persistence
State is the live MMIO controller and `mii_bus` private data. MDC divider and preamble suppression persist only in controller registers while powered. There is no remove callback because devm and platform-driver lifetime handle registration cleanup in this source snapshot.

## Dependencies And Integration Points
Uses Linux MDIO/PHY, OF MDIO, ACPI MDIO, clock, platform, and MMIO APIs. Device-tree compatibles are `fsl,fman-xmdio` and `fsl,fman-memac-mdio`; ACPI ID is `NXP0006`. PHY drivers above this bus perform actual link management.

## Risks
Polling loops use a fixed iteration count with `cpu_relax()` rather than time-based delays, so behavior depends on CPU speed. Erratum A009885 disables local interrupts around read completion to meet a 16-MDC-cycle window; mishandling can affect latency. A011043 suppresses read-error handling. Divider programming rejects out-of-range values but leaves existing hardware state.

## Test Signals
Probe on OF and ACPI systems, `mdiobus` registration, Clause 22/45 read/write against known PHYs, timeout/error behavior with absent PHYs, endianness property coverage, MDC divider programming with valid and invalid clocks, suppress-preamble behavior, and erratum-specific read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/xgmac_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/Kconfig

## Purpose
Defines the top-level Kconfig menu for Fungible network devices and exposes the shared `FUN_CORE` service module plus the nested Ethernet driver configuration.

## Important APIs, Types, And Functions
The configuration symbols are `NET_VENDOR_FUNGIBLE` and `FUN_CORE`. `NET_VENDOR_FUNGIBLE` is a vendor menu gate defaulting to yes. `FUN_CORE` is a hidden tristate selected by device drivers and selects `SBITMAP`.

## Control Flow
When the vendor option is enabled, Kconfig makes `FUN_CORE` available and sources `drivers/net/ethernet/fungible/funeth/Kconfig`. Selecting `FUN_ETH` later selects `FUN_CORE`, causing the shared core module to build.

## State And Persistence
The file contributes build-time configuration only. It does not create runtime state or persistent data.

## Dependencies And Integration Points
Integrates with the kernel networking driver Kconfig hierarchy. `FUN_CORE` depends indirectly on `SBITMAP` because the core admin command tag allocator uses `struct sbitmap_queue`.

## Risks
Because `FUN_CORE` has no prompt, it must be selected correctly by leaf drivers. Disabling `NET_VENDOR_FUNGIBLE` hides the entire subtree and can make the Ethernet driver unavailable.

## Test Signals
Kconfig tests should verify vendor menu visibility, `FUN_ETH=m/y` selects `FUN_CORE=m/y`, and generated `.config` includes `SBITMAP` when the Fungible Ethernet driver is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/Makefile

## Purpose
Routes top-level Fungible network driver build objects into the core and Ethernet subdirectories according to Kconfig symbols.

## Important APIs, Types, And Functions
Build entries are `obj-$(CONFIG_FUN_CORE) += funcore/` and `obj-$(CONFIG_FUN_ETH) += funeth/`.

## Control Flow
During kbuild, enabling `CONFIG_FUN_CORE` descends into `funcore/`; enabling `CONFIG_FUN_ETH` descends into `funeth/`. The latter also selects the former in Kconfig, so both usually build for Ethernet support.

## State And Persistence
Build metadata only; no runtime state.

## Dependencies And Integration Points
Depends on the sibling subdirectory Makefiles to define actual module objects. It integrates with the kernel's recursive `obj-y/obj-m` build mechanism.

## Risks
Misaligned Kconfig and Makefile symbols can skip required modules. Current mapping is simple, but `FUN_ETH` relies on `FUN_CORE` selection for linkable exported core symbols.

## Test Signals
Build `CONFIG_FUN_CORE=m`, `CONFIG_FUN_ETH=m`, and built-in variants. Confirm `funcore.o` and `funeth.o` are emitted with expected module dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/Makefile

## Purpose
Defines the Fungible core service module build composition.

## Important APIs, Types, And Functions
`obj-$(CONFIG_FUN_CORE) += funcore.o` builds the module, and `funcore-y := fun_dev.o fun_queue.o` links PCI/admin-device services with queue/ring services.

## Control Flow
kbuild compiles `fun_dev.c` and `fun_queue.c` into one `funcore.o` object when `CONFIG_FUN_CORE` is enabled.

## State And Persistence
Build metadata only. Runtime state is in the compiled sources.

## Dependencies And Integration Points
The resulting module exports symbols consumed by `funeth`, including device enable/disable, admin command submission, queue allocation/creation, IRQ reservation, and service scheduling.

## Risks
Adding a core source file without updating `funcore-y` would silently omit it. Symbol export/license compatibility matters because the module is dual BSD/GPL while several exports are GPL-only.

## Test Signals
Build coverage should confirm `funcore.o` includes both source objects and that `modpost` resolves exported symbols used by `funeth`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_dev.c

## Purpose
Provides shared PCI-function services for Fungible devices: BAR mapping, DMA mask setup, NVMe-like controller enable/disable, admin queue setup, admin command submission, resource helpers, MSI-X allocation/reservation, and deferred service work.

## Important APIs, Types, And Functions
Public exports include `fun_dev_enable()`, `fun_dev_disable()`, `fun_submit_admin_cmd()`, `fun_submit_admin_sync_cmd()`, `fun_get_res_count()`, `fun_res_destroy()`, `fun_bind()`, `fun_reserve_irqs()`, `fun_release_irqs()`, `fun_serv_stop()`, `fun_serv_restart()`, and `fun_serv_sched()`. Internal command state uses `struct fun_cmd_ctx` and `struct fun_sync_cmd_ctx`.

## Control Flow
`fun_dev_enable()` maps BAR0, sets 64-bit DMA masks, enables the PCI memory device, sanitizes controller ready state, records CAP/doorbell geometry, initializes service work, allocates MSI-X, initializes the IRQ bitmap, enables the admin queue, queries queue limits, saves PCI state, and stores driver data. Admin queue setup allocates a `fun_queue`, command contexts, sbitmap tags, IRQ 0, writes AQA/ASQ/ACQ, enables the controller, and optionally creates/posts an RQ. Async submission obtains a tag, fills CID/context, copies the request into the SQ, advances the tail, and rings the SQ doorbell. CQ completion dispatches events or command callbacks and releases tags. Sync submission waits with timeout and suppresses later commands on timeout.

## State And Persistence
State is live PCI/MMIO and memory state in `struct fun_dev`: BAR, doorbells, CAP/CC shadows, admin queue, tag bitmap, command contexts, firmware upgrade handle, IRQ bitmap, service flags, and callbacks. No durable state is written; PCI state is saved for kernel/device recovery.

## Dependencies And Integration Points
Uses PCI/MSI-X, DMA, NVMe register definitions, sbitmap queues, wait/completion APIs, workqueues, and `fun_queue`/`fun_hci` command formats. `funeth` subclasses this via `struct fun_ethdev`.

## Risks
Admin command timeout calls `fun_admin_stop()`, suppressing future commands and requiring higher-level recovery. Callback data uses atomic exchange/cmpxchg to resolve completion races, so callers must keep context valid until abandoned or completed. IRQ reservation trusts callers to release exact indices. Device ready polling depends on NVMe CAP timeout semantics. Cleanup ordering must destroy firmware handles before disabling the admin queue.

## Test Signals
Probe/remove cycles, admin queue interrupt completions, sync command success/failure/timeout, resource count queries, bind/destroy commands, IRQ reserve/release exhaustion, service work scheduling/stop/restart, and fault injection at every enable-stage label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_dev.h

## Purpose
Declares the Fungible core device abstraction used by PCI function drivers. It exposes admin command callbacks, service callbacks, doorbell helpers, device state, initialization parameters, and exported core APIs.

## Important APIs, Types, And Functions
Important types are `struct fun_dev`, `struct fun_dev_params`, `fun_admin_callback_t`, `fun_admin_event_cb`, and `fun_serv_cb`. Doorbell helpers are `fun_db_addr()`, `fun_sq_db_addr()`, and `fun_cq_db_addr()`. Declared APIs cover admin commands, resource count/destroy/bind, device enable/disable, IRQ reserve/release, and service scheduling.

## Control Flow
Consumers fill `struct fun_dev_params` with admin queue sizes, minimum MSI-X needs, event callback, and service callback before calling `fun_dev_enable()`. After enable, drivers submit HCI admin requests, allocate queues/IRQs, and use service callbacks for process-context work. Disable reverses state through `fun_dev_disable()`.

## State And Persistence
`struct fun_dev` stores all live function state: device pointer, BAR and doorbell addresses, admin queue and tag allocator, command contexts, suppress flag, CAP/CC shadows, queue limits, firmware handle, IRQ bitmap/lock, and work item. This state is process-kernel memory only.

## Dependencies And Integration Points
Includes `fun_hci.h` for command structures and Linux sbitmap/spinlock/workqueue types. It is included by funcore queue code and the Ethernet driver.

## Risks
The header exposes mutable internals rather than opaque accessors, so consumers can accidentally corrupt queue limits, IRQ maps, or command suppression state. Doorbell helpers assume valid BAR mapping and NVMe-style alternating SQ/CQ doorbells.

## Test Signals
Compile consumers against the header, verify doorbell address calculations for a known stride, and exercise the full `fun_dev_enable()`/admin-command/IRQ-reservation/`fun_dev_disable()` lifecycle through `funeth`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_hci.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_hci.h

## Purpose
Defines the host-controller interface wire format for Fungible devices. It contains admin opcodes, request/response common headers, resource create/destroy/read/write commands, queue creation descriptors, port commands, RSS/VI/Ethernet commands, software upgrade, kTLS, data operation descriptors, Ethernet Tx/Rx descriptors, CQE metadata, and ADI configuration.

## Important APIs, Types, And Functions
Core structures include `fun_admin_req_common`, `fun_admin_rsp_common`, `fun_admin_epcq_req`, `fun_admin_epsq_req`, `fun_admin_port_req/rsp`, `fun_admin_rss_req`, `fun_admin_vi_req`, `fun_admin_eth_req`, `fun_admin_swu_req/rsp`, `fun_admin_ktls_*`, `fun_req_common`, `fun_rsp_common`, `fun_cqe_info`, `fun_eth_tx_req`, and `fun_eth_cqe`. Macros such as `FUN_ADMIN_REQ_COMMON_INIT2`, `FUN_ADMIN_EPCQ_CREATE_REQ_INIT`, `FUN_ADMIN_EPSQ_CREATE_REQ_INIT`, and many field extractors centralize endian packing.

## Control Flow
Other sources instantiate these structs, fill them through init macros, submit them on admin or I/O queues, then parse responses by common header and subop union. Queue creation commands are issued by `fun_queue.c`; generic resource and bind commands by `fun_dev.c`; port/RSS/VI/Ethernet/ADI/kTLS command formats are consumed by the Ethernet driver.

## State And Persistence
This header defines serialized device protocol state, not storage. Almost every multi-byte field is big-endian because it is sent to or received from device firmware. Data operation descriptors describe immediate, gather, scatter, SGL, and RQ-buffer data movement.

## Dependencies And Integration Points
Depends on Linux integer/endian helpers being available to consumers. It integrates the core queue/admin layer with funeth features: port capabilities/speed/FEC, RSS tables, Ethernet offloads, Rx checksum classification, TLS offload, VF ADI attributes, and firmware upgrade handles.

## Risks
Protocol structs are packed by convention through fixed field types and unions; any size or endian mistake breaks firmware compatibility. Flexible arrays require callers to allocate exact sizes and set `len8` correctly. The file has broad blast radius because many drivers share the same constants. Unknown firmware revisions may add opcodes or fields not represented here.

## Test Signals
Build-time size/offset checks would be valuable. Runtime signals include successful admin queue creation, port create/read/write, RSS creation, VI/Eth creation, queue creation, kTLS setup, and parsing of Rx CQEs/offload classifications with known firmware responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_hci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_queue.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_queue.c

## Purpose
Implements Fungible queue allocation, DMA ring memory management, admin commands for SQ/CQ/RQ creation, CQ processing, receive-buffer queue handling, and IRQ request/free helpers.

## Important APIs, Types, And Functions
Exports include `fun_alloc_ring_mem()`, `fun_free_ring_mem()`, `fun_sq_create()`, `fun_cq_create()`, `fun_alloc_queue()`, `fun_free_queue()`, `fun_create_rq()`, `fun_request_irq()`, `fun_free_irq()`, and `fun_process_cq()`. Internal helpers allocate SQ/CQ/RQ rings, fill RQ pages, gather RQ-buffer responses, and update RQ positions.

## Control Flow
Queue allocation creates a `struct fun_queue`, assigns initial SQ/CQ/RQ IDs, allocates coherent CQ and SQ rings, optionally allocates and fills an RQ ring with mapped pages, initializes phase/tag state, and assigns implicit admin queue doorbells for queue 0. Device-visible SQ/CQ/RQ creation is done later through HCI admin commands. CQ processing walks entries while phase bits match, applies `dma_rmb()`, advances head/phase, optionally gathers response data from RQ buffers, invokes the registered callback, refills consumed RQ entries, and arms the CQ doorbell.

## State And Persistence
Queue state includes coherent DMA ring memory, optional software descriptor rings, page-backed RQ buffers, DMA addresses, doorbell pointers, heads/tails, phase, interrupt coalescing settings, callback data, IRQ handler metadata, and queue IDs. State is live only and freed through `fun_free_queue()`.

## Dependencies And Integration Points
Uses DMA coherent/page mapping APIs, PCI IRQ vectors, Linux IRQ APIs, `fun_dev` doorbell helpers/admin submission, and HCI queue/data-operation formats. `fun_dev.c` uses it for the admin queue; `funeth` uses it for I/O queues.

## Risks
CQ parsing depends on correct phase-bit ordering and descriptor sizes. RQ buffer accounting is subtle: fragmented responses advance buffers and sync DMA in steps. `fun_data_from_rq()` may return NULL after consuming data, converting completion status to ENOMEM. Queue free must unmap all RQ pages. IRQ names are bounded at 24 bytes and may truncate long device names.

## Test Signals
Allocate/free queues with and without RQ, create SQ/CQ/RQ admin resources, process CQ phase wrap, receive CQE-in-RQBUF single and fragmented responses, IRQ request/free, DMA mapping failure injection, and doorbell writes after CQ/RQ processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_queue.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_queue.h

## Purpose
Declares the shared queue abstraction for Fungible devices, including DMA ring state, doorbells, callback hooks, queue allocation parameters, inline helpers, and queue/IRQ APIs.

## Important APIs, Types, And Functions
Key types are `struct fun_queue`, `struct fun_rq_info`, `struct fun_queue_alloc_req`, and `cq_callback_t`. Inline helpers are `fun_sqe_at()`, `funq_sq_post_tail()`, `funq_cqe_info()`, `funq_rq_post()`, and `fun_set_cq_callback()`. The header also exposes SQ/CQ destroy macros and function prototypes implemented in `fun_queue.c`.

## Control Flow
Callers construct `fun_queue_alloc_req`, allocate with `fun_alloc_queue()`, create device resources with `fun_cq_create()`/`fun_sq_create()`/`fun_create_rq()`, post SQ tails using the helper, process completions through `fun_process_cq()`, and free IRQs/queues during teardown.

## State And Persistence
`struct fun_queue` holds all per-queue live state: DMA addresses, ring pointers, RQ pages, doorbells, IDs, depths, heads/tails, descriptor sizes, RQ buffer cursor, coalescing parameters, flags, writeback pointer, callback, IRQ handler data, vector, phase, and display name.

## Dependencies And Integration Points
Includes Linux interrupt and MMIO helpers and depends on HCI types included indirectly through `fun_dev.h`. Used by funcore admin queue code and funeth data queues.

## Risks
The include guard contains a spelling error (`_FUN_QEUEUE_H`) but is self-consistent. Inline pointer arithmetic assumes byte-addressable `void *` extension supported by kernel C. Doorbell helpers require valid MMIO pointers and correct queue depth wrapping by callers.

## Test Signals
Compile coverage of all consumers, queue allocation parameter validation, SQ tail wrap, CQE info offset correctness, RQ doorbell posting, and callback invocation through processed completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/Kconfig

## Purpose
Defines the Fungible Ethernet driver Kconfig symbol.

## Important APIs, Types, And Functions
`FUN_ETH` is a tristate prompted as "Fungible Ethernet device driver". It depends on `PCI_MSI` and on compatible TLS settings, selects `NET_DEVLINK`, and selects `FUN_CORE`.

## Control Flow
When enabled, kbuild compiles the `funeth` module and ensures the core service module and devlink support are enabled. The TLS dependency allows the driver when TLS device offload support is enabled or when `TLS_DEVICE=n`.

## State And Persistence
Build-time configuration only.

## Dependencies And Integration Points
Connects the Ethernet driver to PCI MSI, optional kTLS device offload, devlink, and `funcore`.

## Risks
The TLS expression can be confusing and should be tested across TLS built-in/module/disabled combinations. Because `FUN_CORE` is selected, core build issues surface when Ethernet is enabled.

## Test Signals
Kconfig matrix builds for `FUN_ETH=y/m/n`, with `TLS_DEVICE` enabled and disabled, should verify expected module composition and dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/Makefile

## Purpose
Builds the Fungible Ethernet driver module and sets include paths for the shared funcore headers and local funeth headers.

## Important APIs, Types, And Functions
`ccflags-y` adds `../funcore` and the current directory. `funeth-y` links `funeth_main.o`, `funeth_rx.o`, `funeth_tx.o`, `funeth_devlink.o`, and `funeth_ethtool.o`; `funeth-$(CONFIG_TLS_DEVICE)` conditionally adds `funeth_ktls.o`.

## Control Flow
kbuild compiles these objects into `funeth.o` when `CONFIG_FUN_ETH` is enabled. TLS offload code is included only when kernel TLS device support is configured.

## State And Persistence
Build metadata only.

## Dependencies And Integration Points
Integrates funeth with funcore headers, local Tx/Rx/ethtool/devlink modules, and optional kTLS support.

## Risks
Any source file added to the driver must be included here or it will be omitted. Include paths make local and funcore headers easy to include but can hide accidental header name collisions.

## Test Signals
Module builds with and without `CONFIG_TLS_DEVICE`, link success against funcore exports, and expected object membership in `funeth.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/fun_port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/fun_port.h

## Purpose
Defines numeric indexes for Fungible port MAC and FEC statistics as exposed by firmware and consumed by funeth stats/ethtool code.

## Important APIs, Types, And Functions
Enums are `port_mac_rx_stats`, `port_mac_tx_stats`, and `port_mac_fec_stats`. Each enum maps stable statistic names such as octets, frames, pause frames, error classes, packet-size buckets, per-priority PFC counters, and FEC correctable/uncorrectable counters to array indexes ending in `*_STATS_MAX`.

## Control Flow
The header has no runtime flow. Consumers use these indexes into `funeth_priv->stats` DMA memory and ethtool stat-name arrays to report counters.

## State And Persistence
No owned state. It defines the schema for firmware-populated port statistic arrays.

## Dependencies And Integration Points
Used by `funeth_ethtool.c` and likely `funeth_main.c` stats paths. It must stay in sync with firmware/port command definitions from `fun_hci.h`.

## Risks
Changing enum values or order breaks stats interpretation. Counters are sparse protocol contract indexes rather than arbitrary local ordering, so adding stats should preserve existing numeric assignments.

## Test Signals
Verify ethtool stats read expected indexes, `*_STATS_MAX` matches allocated stats DMA area, and known traffic increments the corresponding RX/TX/FEC counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/fun_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth.h

## Purpose
Primary internal header for the Fungible Ethernet driver. It defines admin queue sizes, default queue depths/coalescing, maximum MTU, device-private state, queue-set state, virtual port state, and cross-file function declarations.

## Important APIs, Types, And Functions
Key types are `struct fun_ethdev`, which subclasses `struct fun_dev`; `struct funeth_priv`, the `netdev_priv` state; `struct fun_qset`, a replaceable grouping of Rx/Tx/XDP queues; and `struct fun_vport_info` for SR-IOV virtual port policy. Declared APIs include port read/write, RSS configuration, queue replacement/count changes, ring count updates, ethtool setup, and Tx binding.

## Control Flow
`funeth_main.c` allocates a `fun_ethdev`, enables the embedded `fun_dev`, creates netdevices, initializes `funeth_priv`, and uses the declared helpers across Tx/Rx/ethtool/devlink modules. Queue sets allow reconfiguration by allocating a new set, transitioning it through states, and replacing live RCU queue pointers.

## State And Persistence
All state is runtime memory: PCI/netdev pointers, RCU queue arrays, IRQ xarray, link/capability data protected by seqcount, ethtool queue/coalescing settings, cumulative queue counters, RSS key/table and DMA config, stats DMA area, XDP program, devlink port, hardware timestamp config, kTLS counters, and virtual port settings.

## Dependencies And Integration Points
Includes Linux Ethernet, timestamp, mutex, seqcount, xarray, devlink, and funcore headers. Integrates with funeth Tx/Rx, ethtool, devlink, XDP, RSS, SR-IOV, stats, and optional TLS paths.

## Risks
The private state has many concurrent access domains: RTNL/state mutex, RCU queue pointers, seqcount link state, xarray IRQs, and atomic TLS counters. Queue replacement and XDP transitions must synchronize carefully. RSS/stats DMA buffers require exact allocation/free ordering.

## Test Signals
Probe/remove, netdev open/close, queue resizing, ethtool coalescing/ring/RSS operations, XDP attach/detach, SR-IOV VF configuration, devlink port registration, hardware timestamp get/set, stats DMA reads, and kTLS counters when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_devlink.c

## Purpose
Provides thin devlink allocation and registration wrappers for the Fungible Ethernet driver.

## Important APIs, Types, And Functions
Defines an empty `devlink_ops` table and wrapper functions `fun_devlink_alloc()`, `fun_devlink_free()`, `fun_devlink_register()`, and `fun_devlink_unregister()`. Allocation reserves private space sized as `struct fun_ethdev`.

## Control Flow
The main Ethernet probe path calls allocation to get a devlink object with embedded driver-private storage, registers it with devlink after initialization, unregisters during teardown, and frees the object when no longer needed.

## State And Persistence
The devlink object owns runtime kernel state and private storage for `struct fun_ethdev`. No persistent state or devlink parameters are defined in this file.

## Dependencies And Integration Points
Includes `funeth.h` and `funeth_devlink.h`; depends on `NET_DEVLINK` selected by Kconfig. `struct funeth_priv` also contains a `devlink_port` for per-port integration handled elsewhere.

## Risks
Because `devlink_ops` is empty, user-visible devlink functionality is limited to registration/port plumbing. The private allocation size couples devlink object lifetime to the Ethernet device wrapper.

## Test Signals
Probe/remove should show balanced devlink alloc/register/unregister/free. Devlink core should list the device/ports without custom ops, and teardown should be clean under failure paths before and after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_devlink.c -->
