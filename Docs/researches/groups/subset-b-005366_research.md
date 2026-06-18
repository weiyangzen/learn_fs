# Research: subset-b-005366

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman.c

## Purpose
Implements the DPAA QMan software portal runtime and the exported frame queue, congestion group, enqueue, dequeue, and allocator APIs used by QMan clients. It manages cache-enabled and cache-inhibited portal rings, per-CPU affine portals, QMan management commands, frame queue state transitions, interrupt dispatch, message-ring processing, and cleanup of stale or leaked hardware resources.

## Important APIs, types, and functions
The file defines the portal-private ring state for EQCR, DQRR, MR, and MC through `struct qm_eqcr`, `struct qm_dqrr`, `struct qm_mr`, `struct qm_mc`, and low-level `struct qm_portal`. The public runtime object is `struct qman_portal`, which embeds the low-level portal, interrupt source mask, `vdqcr_owned`, static dequeue command state, portal config, congestion-group snapshot and callbacks, and work items.

Exported APIs include portal tuning and polling (`qman_dqrr_set_ithresh`, `qman_portal_set_iperiod`, `qman_p_poll_dqrr`, `qman_p_irqsource_add`, `qman_p_irqsource_remove`), affine lookup (`qman_affine_cpus`, `qman_affine_channel`, `qman_get_affine_portal`), frame queue lifecycle (`qman_create_fq`, `qman_init_fq`, `qman_schedule_fq`, `qman_retire_fq`, `qman_oos_fq`, `qman_destroy_fq`), data movement (`qman_enqueue`, `qman_volatile_dequeue`), congestion groups (`qman_create_cgr`, `qman_delete_cgr_safe`, `qman_update_cgr_safe`, `qman_query_cgr_congested`), and resource pools (`qman_alloc_fqid_range`, `qman_release_fqid`, `qman_alloc_pool_range`, `qman_release_pool`, `qman_alloc_cgrid_range`, `qman_release_cgrid`).

## Control flow and state behavior
Portal creation initializes EQCR in valid-bit production mode, DQRR in push/dequeue-consume mode, MR in valid-bit production plus CI consume mode, and MC response tracking. It then requests the portal IRQ, checks that EQCR, DQRR, and MR are clean or drainable, initializes SDQCR defaults, and registers the portal as CPU-affine. Interrupts flow through `portal_isr`: fast DQRR availability is handled inline by `__poll_portal_fast`, while slow events schedule per-CPU work for congestion and message-ring processing. The fast poll loop demultiplexes scheduled versus volatile dequeues, invokes each FQ's `dqrr` callback, consumes or parks DQRR entries according to the callback result, and clears volatile dequeue ownership on completion.

Frame queue state is mirrored in `struct qman_fq` flags and `state`. Management commands transition OOS, parked, scheduled, retired, and changing states; asynchronous FQRN, FQRL, and FQPN messages complete state transitions in `qm_mr_process_task`. `fq_table` is a valloced lookup table with two slots per FQID, allowing full-service and `NO_MODIFY` references. Dynamic FQID release has an explicit memory ordering comment: the table entry is cleared before `gen_pool_free` to avoid reallocation while a stale pointer remains visible.

## Dependencies and integration points
The code depends on `qman_priv.h`, `include/soc/fsl/qman.h`, DPAA cache helpers, genalloc pools seeded by `qman_ccsr.c`, platform portal config from `qman_portal.c`, Linux IRQ, workqueue, waitqueue, DMA, SMP, and optional PAMU stashing. It exposes symbols consumed by network, crypto, and other DPAA users.

## Risks and test signals
The highest risk areas are lockless portal ring tracking, callback reentrancy, volatile dequeue ownership, cleanup loops that poll hardware state, and management-command timeouts. `qman_enqueue` currently returns `0` even when no EQCR entry is available, which callers cannot distinguish from success. Cleanup paths are hardware-dependent and can busy-wait while draining DQRR/MR. Tests in `qman_test_api.c` and `qman_test_stash.c` exercise enqueue/dequeue, retirement, OOS, FQID cleanup, DMA stashing, and multi-CPU callback routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_ccsr.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_ccsr.c

## Purpose
Initializes and owns the global QMan CCSR register block. It discovers the QMan IP revision, maps global control registers, initializes reserved FQD and PFDR memory, enables global error reporting, seeds QMan gen_pool allocators, and exposes revision-dependent channel constants and cleanup status to the portal layer.

## Important APIs, types, and functions
Global exported state includes `qman_ip_rev`, `qm_channel_pool1`, and `qm_channel_caam`. Main helpers include `qm_set_memory`, `qm_init_pfdr`, `qm_set_pfdr_threshold`, `qm_set_sfdr_threshold`, `qm_set_corenet_initiator`, `qman_resource_init`, `qman_is_probed`, `qman_requires_cleanup`, `qman_done_cleanup`, `__qman_liodn_fixup`, and `qman_set_sdest`. `fsl_qman_probe` is the platform-driver entry point for `"fsl,qman"`.

The file defines error bit names and decoders for ECIR, ECIR2, EADR, and EDATA registers. `qman_isr` logs hardware error causes, logs additional portal/FQID/ECC context when capture registers indicate valid detail, disables noisy PFDR low-watermark and enqueue-blocked interrupts, and clears handled status bits.

## Control flow and state behavior
Probe maps the CCSR resource, reads `REG_IP_REV_1`, rejects unsupported revision 1.0, normalizes supported major/minor values into `QMAN_REVxx`, and adjusts pool/CAAM channel bases for rev3 hardware. It initializes FQD and PFDR private memory through `qbman_init_private_mem`; if BAR registers were already programmed with the same addresses, `qm_set_memory` returns a reuse signal and sets `__qman_requires_cleanup`. Fresh PFDR memory is initialized with an MCR command. After thresholds and scheduling defaults are programmed, the error IRQ is registered and enabled, gen_pools are created, FQID/pool/CGR ranges are seeded, the FQ lookup table is allocated, and the portal workqueue is created.

## Dependencies and integration points
This file provides the allocator and revision foundation for `qman.c` and `qman_portal.c`. It relies on reserved-memory setup via `qbman_init_private_mem`, platform resources and IRQs, Linux genalloc, and big-endian MMIO. Optional PPC compatibility paths zero legacy device-tree memory and flush dcache for noncoherent QMan access.

## Risks and test signals
Risks concentrate around reserved memory address/size validity, stale hardware state after kexec, revision-specific register layouts, and broad error IRQ enablement. `qman_resource_init` loops over `cgrid_num` while building `qm_pools_sdqcr`, so rev-specific pool and CGR counts should be checked carefully. Observable test signals are probe success, `qman_is_probed() == 1`, allocator range availability, error IRQ logs with decoded context, and portal cleanup running only when `qman_requires_cleanup()` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_ccsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_portal.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_portal.c

## Purpose
Binds QMan portal platform devices to CPU-affine `qman_portal` instances. It maps each portal's cache-enabled and cache-inhibited register windows, chooses a CPU, configures PAMU/stashing destination state, creates the affine portal, handles CPU hotplug retargeting, and performs stale frame-queue cleanup after kexec-style reuse.

## Important APIs, types, and functions
The file exports `qman_dma_portal` and `qman_portals_probed`. `portal_set_cpu` configures optional PAMU L1 stash and calls `qman_set_sdest`. `init_pcfg` applies LIODN fixup, creates the affine portal, enables configured interrupt sources, initializes all CGRs once the possible CPU portal set is populated, and selects the DMA portal. `qman_offline_cpu` and `qman_online_cpu` retarget IRQ affinity and SDEST when CPUs change state. `qman_portal_probe` owns platform resource parsing and portal initialization.

## Control flow and state behavior
Portal probe first waits for the global QMan CCSR driver via `qman_is_probed`; a zero return defers probing and a negative value fails. It allocates `struct qm_portal_config`, reads CE and CI resources, reads `cell-index` as the portal channel, obtains the IRQ, maps CE with `memremap` and CI with `ioremap`, and copies the pool SDQCR mask. Under `qman_lock`, it assigns the first not-yet-used possible CPU. Extra unassigned portals are mapped but skipped. Assigned portals set a 40-bit DMA mask and call `init_pcfg`.

After all portals are probed, if the CCSR layer detected preprogrammed private memory, this file iterates all FQIDs and calls `qman_shutdown_fq` to return hardware to reset-like state, then calls `qman_done_cleanup` to enable IRQs and clear cleanup state.

## Dependencies and integration points
Depends on `qman.c` for portal creation, IRQ-source programming, CGR initialization, and FQ cleanup; on `qman_ccsr.c` for global probe state, pool masks, LIODN/SDEST programming, and cleanup flags; on device tree compatible `"fsl,qman-portal"`; and optionally on PAMU/IOMMU stashing support.

## Risks and test signals
Hotplug retargeting assumes another online CPU exists when offlining a portal CPU. Probe error paths unmap CE/CI resources but do not destroy an already created portal after later cleanup failure. Cleanup iterates every possible FQID and can be slow or fail if hardware queues cannot drain. Test signals include one portal per possible CPU, `qman_portals_probed() == 1`, IRQ affinity updates on CPU hotplug, and successful stale-FQ cleanup when CCSR memory was reused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_portal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_priv.h -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_priv.h

## Purpose
Private QMan header shared by the CCSR, portal, core, and test implementations. It defines management-command result layouts not exposed in the public header, congestion-group bitset helpers, portal configuration, revision constants, private allocator globals, SDQCR/VDQCR constants, and internal cross-file function prototypes.

## Important APIs, types, and functions
Important types are `struct qm_mcr_querywq`, `struct qm_mcr_querycongestion`, `struct qm_mcr_querycgr`, `struct qman_cgrs`, and `struct qm_portal_config`. Inline helpers decode query results (`qm_mcr_querywq_get_chan`, `qm_mcr_querycgr_i_get64`, `qm_mcr_querycgr_a_get64`) and manipulate congestion-group bitsets (`qman_cgrs_init`, `qman_cgrs_fill`, `qman_cgrs_get`, `qman_cgrs_cp`, `qman_cgrs_and`, `qman_cgrs_xor`).

The header declares shared functions such as `qman_wq_alloc`, `__qman_liodn_fixup`, `qman_set_sdest`, `qman_create_affine_portal`, `qman_destroy_affine_portal`, `qman_query_fq`, `qman_alloc_fq_table`, `qman_get_qm_portal_config`, `qm_get_fqid_maxcnt`, `qman_shutdown_fq`, `qman_requires_cleanup`, `qman_done_cleanup`, and `qman_enable_irqs`.

## Control flow and state behavior
This file does not execute runtime control flow itself, but it defines the shared contracts that keep portal and CCSR state aligned. `struct qm_portal_config` carries mapped CE/CI portal windows, device, IOMMU domain, CPU, IRQ, dedicated channel, and accessible pool mask from probe into core portal creation. `struct qman_cgrs` mirrors the eight-word query-congestion result format, so bitset operations can be used directly against management-command output.

## Dependencies and integration points
It includes `dpaa_sys.h`, the public `<soc/fsl/qman.h>`, DMA mapping, and IOMMU headers, and optionally PAMU stash declarations. Its constants are consumed heavily by `qman.c`, `qman_ccsr.c`, and `qman_portal.c`.

## Risks and test signals
Risk comes from ABI-like coupling to hardware result structures and public QMan definitions. Endianness is mixed: some query fields are big-endian while congestion bitsets are treated as raw `u32` words, so callers must use the helper functions. Tests indirectly validate this header by exercising CGR callbacks, SDQCR/VDQCR constants, and portal config paths in the QMan tests and platform probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test.c

## Purpose
Small loadable QMan test module wrapper. It conditionally runs the stash test and API test at module initialization based on `CONFIG_FSL_QMAN_TEST_STASH` and `CONFIG_FSL_QMAN_TEST_API`.

## Important APIs, types, and functions
`test_init` is the module entry point. It runs one iteration, calling `qman_test_stash()` first when enabled and `qman_test_api()` second when enabled, stopping on the first error. `test_exit` is empty because the individual tests perform their own cleanup before returning. The file declares module metadata and uses `module_init`/`module_exit`.

## Control flow and state behavior
State is limited to local `loop` and `err` variables. No persistent module state is retained after tests finish. A nonzero return from either test fails module load, making failures visible to kmod and boot logs.

## Dependencies and integration points
Includes `qman_test.h`, which brings in QMan private definitions and the two test declarations. It depends on the QMan platform and portal drivers having successfully initialized before the module is loaded.

## Risks and test signals
Because tests execute during module load and can call `WARN_ON`, they are intrusive and hardware-dependent. The main signal is whether module insertion succeeds. Kernel logs from the underlying tests provide detail on failed enqueue/dequeue, retirement, DMA mapping, or stash behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test.h -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test.h

## Purpose
Shared header for QMan test modules. It includes the private QMan implementation header so the tests can use both public APIs and internal portal constants.

## Important APIs, types, and functions
Declares `int qman_test_stash(void);` and `int qman_test_api(void);`. It otherwise relies on `qman_priv.h` for QMan types, frame descriptor helpers, SDQCR/VDQCR constants, and callback enums.

## Control flow and state behavior
The header contains no executable state. Its effect is compile-time coupling of the test sources to private QMan internals.

## Dependencies and integration points
It is included by `qman_test.c`, `qman_test_api.c`, and `qman_test_stash.c`. Because it includes private headers rather than only public interfaces, the tests can validate lower-level behavior but also track internal layout changes closely.

## Risks and test signals
The main risk is overcoupling tests to private implementation details. Any private header refactor can break test builds even if the public API remains stable. Successful compilation and module load validate that the private test contract still matches the QMan implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test_api.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test_api.c

## Purpose
Functional test of the QMan frame queue API. It creates a dynamic local FQ, enqueues synthetic frame descriptors, validates volatile and scheduled dequeue paths, retires and takes the FQ out of service, and destroys it.

## Important APIs, types, and functions
`qman_test_api` drives the scenario. `fd_init`, `fd_inc`, and `fd_neq` build and compare deterministic `struct qm_fd` values. `do_enqueues` repeatedly calls `qman_enqueue`. Callback functions `cb_dqrr`, `cb_ern`, and `cb_fqs` validate dequeue order and retirement messages. Static waitqueue flags `retire_complete` and `sdqcr_complete` synchronize async callbacks with the main test.

## Control flow and state behavior
The test initializes `fd` and `fd_dq`, creates a dynamic FQ with callbacks, initializes it as local parked, performs a till-empty volatile dequeue, performs a partial volatile dequeue followed by another volatile dequeue for the remaining frames, then schedules the FQ and waits for SDQCR-driven callbacks to drain it. It retires the FQ, waits for FQS callback completion, checks `QMAN_FQ_STATE_BLOCKOOS`, issues OOS, and destroys the FQ. Callback state advances `fd_dq` in lockstep with dequeued frames and wakes the waitqueue when expected conditions are met.

## Dependencies and integration points
Uses exported QMan APIs from `qman.c`, constants from `qman_priv.h` and the public QMan header, and the portal interrupt/polling machinery that invokes DQRR and MR callbacks.

## Risks and test signals
The test assumes callbacks arrive and frame descriptors are preserved except for PPID. If an enqueue fails because EQCR has no space, the core API may still return `0`, weakening this test's ability to detect congestion. Strong signals are waitqueue completion, no `WARN_ON`, matching FD sequence, and successful retire/OOS/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test_stash.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test_stash.c

## Purpose
Stress test for QMan context/data stashing and multi-CPU portal routing. It creates a ring of per-CPU "hot potato" handlers, forwards one DMA-backed frame across CPUs through QMan FQs, mutates and validates frame data at each hop, and verifies that stashed handler context and frame data are usable in DQRR callbacks.

## Important APIs, types, and functions
`struct hp_handler` contains stashed RX FQ, TX FQ, mixers, DMA address, frame pointer, FQIDs, and CPU identity. `struct hp_cpu` tracks each CPU's handler list and iterator. `on_all_cpus` runs setup and teardown helpers on each online CPU using temporary kthreads. Main helpers include `allocate_frame_data`, `process_frame_data`, `create_per_cpu_handlers`, `init_phase2`, `init_phase3`, `init_handler`, `send_first_frame`, and `destroy_per_cpu_handlers`. DQRR callbacks are `normal_dqrr` and `special_dqrr`.

## Control flow and state behavior
`qman_test_stash` skips single-CPU systems. Otherwise it creates an aligned slab for handlers, allocates and DMA maps deterministic frame data, creates handlers on every CPU, links RX FQIDs to previous TX FQIDs, assigns LFSR mixers, initializes each RX FQ on its target CPU with `QM_FQCTRL_CTXASTASHING`, and creates TX no-modify FQs. The special handler sends the first frame. Each callback validates the frame by XORing the previous handler mixer, then applies its own mixer before enqueueing to the next handler. The special callback counts complete loops and wakes the main waitqueue at `HP_LOOPS`.

## Dependencies and integration points
Depends on `qman_dma_portal` for DMA mapping, affine portal targeting for local FQ initialization, QMan enqueue/dequeue callbacks, Linux kthreads, SMP calls, DMA APIs, waitqueues, and slab alignment. It exercises FQID allocation and release through QMan gen_pools.

## Risks and test signals
Failure cleanup is incomplete in several early-error paths; allocated DMA memory, handlers, or FQIDs may leak after a mid-test failure. The test assumes all online CPUs can run setup kthreads promptly and that portal affinity matches CPU identity. Signals are final loop completion, absence of corrupt frame warnings, no enqueue failures, and successful retirement/OOS/destruction of all RX FQs plus TX FQ destruction and FQID release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test_stash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/Kconfig

## Purpose
Defines build-time configuration for the Freescale/NXP QUICC Engine and related CPM/QE communication blocks.

## Important options
`QUICC_ENGINE` enables the QE framework on OF and MMIO-capable PPC, ARM, ARM64, or compile-test builds, and selects generic allocator and CRC32 support. `UCC_SLOW`, `UCC_FAST`, and `UCC` are helper symbols selected by serial, Ethernet, HDLC, TDM, QMC, or TSA users. `CPM_TSA` and `CPM_QMC` expose tristate support for time-slot assigner and multichannel controller. `QE_TDM` is selected by `FSL_UCC_HDLC`. `QE_USB` follows `USB_FSL_QE`.

## Control flow and state behavior
This file has no runtime state. It controls which objects in the QE Makefile are compiled and therefore which exported helper APIs exist for downstream drivers.

## Dependencies and integration points
The options connect SoC support code to serial, Ethernet, HDLC, USB, TSA, and QMC drivers. `QUICC_ENGINE` must be enabled for `qe.o`, `qe_common.o`, `qe_ic.o`, and `qe_io.o`; `QE_GPIO` is not defined here but is consumed by the Makefile from elsewhere in the kernel configuration.

## Risks and test signals
Misconfigured defaults can silently omit helper objects needed by dependent drivers. Since `UCC_SLOW`, `UCC_FAST`, and `UCC` are bool helpers with defaults, compile coverage should include representative configurations for serial QE, UCC Ethernet, QE TDM, CPM TSA, CPM QMC, and USB QE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/Makefile

## Purpose
Maps QE and CPM configuration symbols to built object files.

## Important build rules
`CONFIG_QUICC_ENGINE` builds `qe.o`, `qe_common.o`, `qe_ic.o`, and `qe_io.o`. `CONFIG_CPM` also builds `qe_common.o` for shared CPM MURAM support. Feature symbols add `tsa.o`, `qmc.o`, `ucc.o`, `ucc_slow.o`, `ucc_fast.o`, `qe_tdm.o`, `usb.o`, and the GPIO pair `gpio.o qe_ports_ic.o`.

## Control flow and state behavior
There is no runtime control flow. The Makefile determines which exported symbols are available and which platform drivers register at init time.

## Dependencies and integration points
The object grouping mirrors the Kconfig dependencies and shares `qe_common.o` between CPM and QE. `CONFIG_QE_GPIO` intentionally builds both gpiolib support and the port interrupt controller, so GPIO interrupt users require both objects to be present.

## Risks and test signals
Because `qe_common.o` appears under both `CONFIG_QUICC_ENGINE` and `CONFIG_CPM`, build combinations should confirm it is linked exactly as expected. Test signals are successful builds for QE-only, CPM-only, QE GPIO, TDM, TSA/QMC, USB, and UCC configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/gpio.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/gpio.c

## Purpose
Implements a gpiolib driver for QE parallel I/O banks and a legacy QE pin multiplexing API. It exposes QE PIO pins as GPIOs while preserving firmware-programmed dedicated-function register state so clients can switch pins between GPIO and peripheral modes.

## Important APIs, types, and functions
`struct qe_gpio_chip` wraps `struct gpio_chip`, MMIO registers, a spinlock, shadow `cpdata`, and saved PIO register state. GPIO operations are `qe_gpio_get`, `qe_gpio_set`, `qe_gpio_set_multiple`, `qe_gpio_dir_in`, and `qe_gpio_dir_out`. Legacy pin APIs are exported as `qe_pin_request`, `qe_pin_free`, `qe_pin_set_dedicated`, and `qe_pin_set_gpio`. Probe registers a 32-pin bank for compatible `"fsl,mpc8323-qe-pario-bank"`.

## Control flow and state behavior
Probe allocates the chip, maps the bank registers, snapshots `cpdata`, direction, assignment, and open-drain registers, then registers the gpiochip. GPIO writes update shadow `cpdata` under lock before writing the big-endian data register. Direction changes call `__par_io_config_pin`. `qe_pin_request` obtains a nonexclusive GPIO descriptor only to find the owning chip and local offset, then releases the descriptor and returns a custom `qe_pin`. `qe_pin_set_dedicated` restores per-pin saved direction, assignment, data, and open-drain bits; `qe_pin_set_gpio` reconfigures the pin as GPIO input.

## Dependencies and integration points
Depends on gpiolib descriptors and chips, platform OF matching, QE PIO register definitions, and `__par_io_config_pin` from `qe_io.c`. The custom pin API is a compatibility bridge for drivers that have not moved to pinctrl.

## Risks and test signals
`qe_gpio_set_multiple` mutates the caller-provided mask with `__test_and_clear_bit`, matching some gpiolib patterns but worth checking if reused. `qe_pin_request` uses `gc->base` to compute offsets despite dynamic GPIO bases; descriptor-native offsets would be safer. Test signals include GPIO get/set/direction operations, restoration of firmware dedicated function after GPIO use, and correct rejection of non-QE GPIO descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe.c

## Purpose
Core QUICC Engine management implementation. It discovers and maps QE registers, resets the engine, initializes SNUMs and SDMA, issues QE commands, configures BRG clocks, parses clock names, uploads QE firmware/microcode, and exposes firmware and hardware-capacity information.

## Important APIs, types, and functions
Exports include `qe_immr`, `cmxgcr_lock`, `qe_reset`, `qe_issue_cmd`, `qe_get_brg_clk`, `qe_setbrg`, `qe_clock_source`, `qe_get_snum`, `qe_put_snum`, `qe_upload_firmware`, `qe_get_firmware_info`, `qe_get_num_of_risc`, and `qe_get_num_of_snums`. Private helpers include `qe_get_device_node`, `get_qe_base`, `qe_snums_init`, `qe_sdma_init`, `qe_upload_microcode`, and the PPC resume hook.

## Control flow and state behavior
`qe_init` runs at `subsys_initcall`, finds `"fsl,qe"`, and calls `qe_reset`. Reset maps `qe_immr` if necessary, initializes SNUM tables, issues a reset command, initializes MURAM, and configures SDMA temporary buffers. `qe_issue_cmd` serializes command register access with `qe_lock`, formats command fields according to reset, page assignment, RISC assignment, USB, or normal command semantics, and polls for `QE_CR_FLG` to clear.

SNUM allocation uses a bitmap protected by `qe_lock`; the SNUM table comes from `fsl,qe-snums` or legacy static arrays selected by `fsl,qe-num-snums`. Firmware upload validates magic, version, microcode count, length, and CRC, optionally splits I-RAM, uploads each microcode blob with auto-increment writes, programs traps, enables trap registers, and snapshots firmware info for later query. `qe_get_firmware_info` can also synthesize state from a firmware child node provided by firmware/bootloader.

## Dependencies and integration points
Depends on device tree QE bindings, `qe_common.c` MURAM APIs, CRC32, big-endian MMIO, PPC errata helpers, suspend support, and public QE headers. Downstream UCC, TDM, serial, Ethernet, USB, and QMC drivers consume its exported command, clock, SNUM, and firmware APIs.

## Risks and test signals
`qe_issue_cmd` returns `ret == 0`, so success is `1` and timeout is `0`, which is unusual for kernel APIs and can confuse callers. Firmware upload trusts structure packing and big-endian offsets and should be fuzzed through invalid length/count/CRC cases. Test signals include successful subsystem init, SNUM exhaustion/release behavior, BRG programming for errata-affected SoCs, firmware CRC rejection, and resume reset behavior on PPC 85xx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_common.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_common.c

## Purpose
Provides shared CPM/QE MURAM allocation and address conversion helpers. It discovers the MURAM data region from device tree, maps it, backs allocations with a gen_pool, tracks allocated blocks for size-aware freeing, and exports managed and unmanaged allocation APIs.

## Important APIs, types, and functions
Exports `cpm_muram_init`, `cpm_muram_alloc`, `cpm_muram_free`, `devm_cpm_muram_alloc`, `cpm_muram_alloc_fixed`, `devm_cpm_muram_alloc_fixed`, `cpm_muram_addr`, `cpm_muram_offset`, `cpm_muram_dma`, and `cpm_muram_free_addr`. `struct muram_block` stores allocation offset and size in `muram_block_list`. `cpm_muram_alloc_common` centralizes gen_pool allocation, zeroing, and list tracking.

## Control flow and state behavior
Initialization finds `"fsl,cpm-muram-data"` or legacy `"data-only"`, creates a gen_pool, translates the zero address to establish the physical base, adds all resource ranges with a `GENPOOL_OFFSET`, and maps the full physical span. Allocations are serialized by `cpm_muram_lock`, allocate a tracking node with `GFP_ATOMIC`, use either first-fit alignment or fixed-offset gen_pool algorithms, subtract `GENPOOL_OFFSET`, zero the MMIO memory, and record the block. Frees search the list for the offset, recover the size, free the gen_pool range, and drop the tracking node.

## Dependencies and integration points
Shared by QE reset/SDMA setup and CPM/QE communication drivers that need internal multi-user RAM. It depends on OF address translation, `genalloc`, big-endian or MMIO-safe zeroing, and devres for managed variants.

## Risks and test signals
If `cpm_muram_free` is called with an unknown offset, `size` remains zero and `gen_pool_free` is still called with zero length; behavior should be checked against gen_pool expectations. The global block list is not initialized from preexisting firmware allocations, so fixed allocations must align with device-tree ranges. Test signals include successful MURAM discovery, aligned allocation, fixed allocation conflict handling, devm release on driver detach, and correct DMA address conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_ic.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_ic.c

## Purpose
Implements the main QUICC Engine interrupt controller as a Linux irq_domain with cascaded high and low parent IRQ handlers.

## Important APIs, types, and functions
`struct qe_ic` stores mapped registers, irq_domain, irq_chip, and parent high/low virqs. `struct qe_ic_info` maps hardware source numbers to mask bits, mask registers, priority code, and priority register. `qe_ic_unmask_irq`, `qe_ic_mask_irq`, and `qe_ic_irq_chip` implement the child irq_chip. Domain operations are `qe_ic_host_match`, `qe_ic_host_map`, and `irq_domain_xlate_onetwocell`. Cascade handlers are `qe_ic_cascade_low`, `qe_ic_cascade_high`, and `qe_ic_cascade_muxed_mpic`.

## Control flow and state behavior
Probe maps the controller registers, copies the base irq_chip, obtains low and optional high parent IRQs, creates a 64-entry linear domain, clears CICR, and installs chained handlers. Child IRQ mask/unmask operations update either `QEIC_CIMR` or `QEIC_CRIMR` under `qe_ic_lock`; masking uses `mb()` before re-enabling interrupts to reduce spurious interrupts. Cascaded handlers read `CIVEC` or `CHIVEC`, translate the six-bit source through the domain, call `generic_handle_irq`, and EOI the parent chip.

## Dependencies and integration points
Registers as a platform driver for `"fsl,qe-ic"` or type `"qeic"` at `subsys_initcall`. It integrates device-tree interrupt specifiers with Linux irq_domain and parent interrupt controllers such as MPIC.

## Risks and test signals
Only sources with nonzero `qe_ic_info[hw].mask` can map; reserved IRQs fail. The muxed cascade path calls parent `irq_eoi` unconditionally, while the separate low/high handlers check for it. Test signals include successful mapping of valid sources, rejection of reserved sources, correct interrupt delivery through high and low vectors, and lack of interrupt storms after masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_ic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_io.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_io.c

## Purpose
Provides low-level QE parallel I/O configuration helpers for legacy users. It maps the PAR IO register array, configures pin direction/open-drain/assignment fields, writes pin data, and applies `pio-map` device-tree tables.

## Important APIs, types, and functions
Exports `par_io_init`, `__par_io_config_pin`, `par_io_config_pin`, `par_io_data_set`, and `par_io_of_config`. Global state is `par_io`, the mapped base pointer, and `num_par_io_ports`.

## Control flow and state behavior
`par_io_init` maps the register resource from a device node and reads optional `num-ports`. `__par_io_config_pin` computes one-bit and two-bit masks for a pin, updates open drain, direction, and assignment registers using big-endian MMIO, and ignores `has_irq`. `par_io_config_pin` validates initialization and port range before configuring a pin. `par_io_data_set` validates port and pin and sets or clears the data bit. `par_io_of_config` follows `pio-handle`, reads `pio-map`, validates six-cell entries, and applies each mapping.

## Dependencies and integration points
Used by `gpio.c` and older QE/UCC clients. Depends on QE PIO register layout from public headers, OF resource translation, and legacy device-tree properties `pio-handle` and `pio-map`.

## Risks and test signals
`par_io_data_set` does not check `par_io` for NULL, unlike `par_io_config_pin`. Read-modify-write sequences are not globally locked here, so concurrent users can race unless higher layers serialize. `has_irq` is accepted but unused. Test signals include correct pin mux register values after `pio-map`, invalid map length rejection, and GPIO driver direction changes through `__par_io_config_pin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_ports_ic.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_ports_ic.c

## Purpose
Implements a cascaded interrupt controller for QE I/O port interrupts, exposing 32 port interrupt lines through a linear irq_domain.

## Important APIs, types, and functions
`struct qepic_data` stores the mapped register base and irq_domain. The irq_chip `qepic` provides `qepic_mask`, `qepic_unmask`, `qepic_end`, and `qepic_set_type`. `qepic_get_irq` reads pending events and translates the first set bit to a virq. `qepic_cascade` handles the parent interrupt. `qepic_probe` maps resources, creates the domain, and installs the chained handler for compatible `"fsl,mpc8323-qe-ports-ic"`.

## Control flow and state behavior
Mask/unmask update `CEPIMR`, EOI writes the bit to `CEPIER`, and type programming updates `CEPICR` for falling-edge versus both-edge/none behavior. The cascade reads `CEPIER`; if no pending bit exists it returns `-1`, otherwise it maps `32 - ffs(event)` to a child IRQ and passes it to `generic_handle_irq`.

## Dependencies and integration points
Built with `CONFIG_QE_GPIO` alongside `gpio.o`. It integrates QE port events with Linux irq_domain and depends on the parent platform IRQ from device tree.

## Risks and test signals
`qepic_cascade` calls `generic_handle_irq(qepic_get_irq(desc))` without checking for `-1`, so a spurious parent interrupt can pass an invalid IRQ. Only falling-edge and both-edge/none are supported. Test signals include child IRQ delivery for each port bit, mask/unmask behavior in `CEPIMR`, EOI clearing in `CEPIER`, and safe behavior under spurious parent interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_ports_ic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_tdm.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_tdm.c

## Purpose
Provides helper routines for QE UCC TDM configuration. It parses TDM-related device-tree properties, fills `ucc_tdm` and `ucc_tdm_info`, and initializes SI RAM entries plus SI mode registers for E1/T1 timeslot routing.

## Important APIs, types, and functions
Exports `ucc_of_parse_tdm` and `ucc_tdm_init`. Private helpers are `set_tdm_framer`, which maps `"e1"` and `"t1"` to enum values, and `set_si_param`, which adjusts SI mode fields for internal loopback.

## Control flow and state behavior
`ucc_of_parse_tdm` reads `fsl,rx-sync-clock`, `fsl,tx-sync-clock`, TX/RX timeslot masks, `fsl,tdm-id`, optional internal loopback, `fsl,tdm-framer-type`, and `fsl,siram-entry-id`. It converts clocks through `qe_clock_source`, rejects invalid or missing required properties, stores masks and mode into `utdm`, and mirrors TDM port into `ut_info->uf_info.tdm_num`.

`ucc_tdm_init` determines 24 T1 or 32 E1 timeslots, computes the UCC channel select, writes TX and RX SIRAM entries as valid or closed based on timeslot masks, marks the final TX and RX entries with `SIR_LAST`, builds the SIxMR value from SIRAM entry id, loopback/normal mode, and `si_info` flags, and writes the correct SIxMR register for TDM ports 0 through 3.

## Dependencies and integration points
Depends on public QE TDM headers, `qe_clock_source` from `qe.c`, big-endian MMIO, UCC fast info structures, and device-tree bindings used by UCC HDLC/TDM clients.

## Risks and test signals
The function logs and returns errors for missing properties, but one indentation block around invalid TX sync clock should be reviewed for readability. `ucc_tdm_init` only supports TDM ports 0-3 and only E1/T1 slot counts. Test signals include parsing valid E1 and T1 nodes, rejecting invalid clock/framer properties, correct SIRAM valid/closed entries for masks, and loopback SIxMR bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_tdm.c -->
