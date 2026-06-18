# subset-b-004437 Research

Grouped research for Huawei/Hisilicon Ethernet driver sources. Each file section is source-tree-aligned and wrapped for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_main.c

## Purpose
Implements the HNS3 virtual-function acceleration-engine driver (`hclgevf`) for Huawei/Hisilicon NIC VFs. It registers a PCI-backed `hnae3_ae_algo`, initializes VF PCI resources, command queues, MSI/MSI-X vectors, mailbox communication with the PF, RSS/VLAN/GRO/queue configuration, and exposes the AE operations used by the HNAE3 NIC and RoCE clients.

## Important APIs, Types, And Functions
Primary exported/internal entry points are `hclgevf_cmd_send()`, `hclgevf_ae_get_hdev()`, `hclgevf_reset_task_schedule()`, `hclgevf_mbx_task_schedule()`, `hclgevf_update_speed_duplex()`, and `hclgevf_update_port_base_vlan_info()`. The large `hclgevf_ops` table wires the driver into HNAE3 with init/uninit, start/stop, reset, vector mapping, MAC/VLAN/RSS/channel/statistics/register-dump, GRO, MTU, media, link-mode, and promisc callbacks. Device lifetime is organized around `hclgevf_init_hdev()`, `hclgevf_reset_hdev()`, `hclgevf_uninit_hdev()`, `hclgevf_init_ae_dev()`, and `hclgevf_uninit_ae_dev()`.

## Control Flow
Module init creates a workqueue and registers `ae_algovf`; AE init allocates `struct hclgevf_dev`, enables PCI, initializes command queues, queries VF resources/specs, allocates vectors, initializes service state and misc IRQ, fetches PF-provided configuration over mailbox, allocates TQPs, initializes RSS/VLAN/GRO, clears PF vport tables, initializes devlink, and schedules periodic service. Runtime control flows through vector 0 interrupts: reset events set reset-pending bits and schedule reset work, while mailbox events drain command receive descriptors and defer async mailbox work. The periodic service task sends keepalives, updates stats, requests link/link-mode state when PF push is not enabled, retries failed VLAN deletes, syncs MAC tables, and applies pending promisc changes.

## State And Persistence
All state is in memory under `struct hclgevf_dev`: PCI/MMIO bases, command-queue state, reset bitmaps/counters, service/task bits, mailbox response and async queue, MAC pending lists, RSS shadow config, VLAN delete-failure bitmap, vector accounting, client handles, and devlink pointer. Persistent device state is owned by PF/firmware and programmed through command queue or mailbox requests; the driver maintains shadow state to replay RSS, VLAN, GRO, RX descriptor layout, promisc, and MAC operations after reset. Reset statistics persist only for the lifetime of the device instance.

## Dependencies And Integration Points
Depends on HNAE3 core types (`hnae3_handle`, `hnae3_ae_dev`, `hnae3_client`), common HCLGE command/RSS/TQP helpers, mailbox ABI definitions, PCI/MSI APIs, RTNL locking, workqueues, timers, and the VF register dump/devlink helpers. It integrates with the NIC client via `init_instance`, `reset_notify`, `link_status_change`, and queue/vector operations; with RoCE through a separate `hnae3_handle` and vector/memory base setup; and with the PF through mailbox opcodes for basic info, queues, MAC/VLAN/promisc, reset, keepalive, link status, and port-base VLAN updates.

## Risks
The reset path is concurrency-heavy: it uses reset-state bitmaps, a semaphore, service work, timer-delayed IRQ handling, RTNL locks, and mailbox/command-queue disable bits. Races here can leave vectors disabled, clients half-uninitialized, or resets retried indefinitely. MAC list sync intentionally moves entries out of a spinlock before PF mailbox calls; failures must be moved back correctly or software/hardware filters diverge. VLAN delete failures are bitmap-retried, so reset-fail states can temporarily disagree with hardware. RSS and channel changes must keep `rss_size`, TC layout, and indirection table consistent. The service task re-runs reset/mailbox handlers after periodic work because periodic scheduling can otherwise delay urgent work.

## Test Signals
Useful validation signals are probe/remove on supported VF PCI IDs, successful `hnae3_register_ae_algo()` path, mailbox basic-info and queue queries, IRQ vector allocation, link up/down callbacks, ethtool RSS/channel/GRO/MTU/register-dump paths through HNAE3, MAC/VLAN add/delete replay across reset, PF-pushed link/VLAN/promisc async messages, VF/PF/FLR reset injection, command-queue disable handling, and RoCE client registration on RoCE-capable VFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_main.h

## Purpose
Defines the main data model, register offsets, constants, state bits, and cross-file prototypes for the HNS3 VF driver. It is the shared contract between `hclgevf_main.c`, mailbox handling, register dumping, command helpers, and HNAE3 client integration.

## Important APIs, Types, And Functions
Key types are `struct hclgevf_dev`, `struct hclgevf_hw`, `struct hclgevf_mac`, `struct hclgevf_misc_vector`, `struct hclgevf_rst_stats`, `struct hclgevf_mac_addr_node`, and `struct hclgevf_mac_table_cfg`. The `enum hclgevf_states` bitmap is central to reset, service, mailbox, link, promisc, and removal gating. Prototypes expose mailbox send/handlers, link/speed updates, reset/mailbox task scheduling, port-base VLAN updates, and handle-to-device lookup.

## Control Flow
This header does not execute logic, but it shapes all VF control paths. Register macros define how queues, interrupt vectors, reset status, GRO, RX descriptor layout, and device memory offsets are accessed. Inline helpers and state constants let implementation files gate service work, IRQ setup, reset processing, and mailbox response waits.

## State And Persistence
`struct hclgevf_dev` owns all runtime state: PCI resources, HNAE3 handles for NIC/RoCE, RSS config, reset pending/requested state, reset counters, vector accounting arrays, mailbox synchronous response state, async mailbox ring, delayed service work, TQP array, MAC/VLAN software shadows, feature flags, and devlink. None of these fields are persisted outside the kernel instance; hardware state is reconstructed from these shadows after resets.

## Dependencies And Integration Points
Includes Linux networking/VLAN/devlink headers and HNS3 shared headers (`hclge_mbx.h`, `hclgevf_cmd.h`, `hnae3.h`, common RSS and TQP stats). Register offsets are consumed by `hclgevf_main.c` and `hclgevf_regs.c`; prototypes are consumed by `hclgevf_mbx.c` and register/devlink modules.

## Risks
The state bitmap packs device and task state into one `unsigned long`, so new states must avoid semantic overlap and must be updated with proper barriers where readers race with service work. Register offset constants are hardware ABI; incorrect changes can corrupt queues or interrupt control. Device-memory offset macros assume BAR4 is split between RoCE and NIC.

## Test Signals
Compile coverage is important because this header defines shared structs and prototypes. Runtime signals include successful queue register programming, vector address derivation, reset status polling, service task scheduling, mailbox response matching, and devlink/register dump consumers accessing `struct hclgevf_dev` fields consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_mbx.c

## Purpose
Implements VF-to-PF mailbox send, synchronous response matching, command receive queue draining, and deferred handling of PF-to-VF async notifications for HNS3 VFs.

## Important APIs, Types, And Functions
Main public functions are `hclgevf_send_mbx_msg()`, `hclgevf_mbx_handler()`, and `hclgevf_mbx_async_handler()`. Internal helpers include `hclgevf_reset_mbx_resp_status()`, `hclgevf_get_mbx_resp()`, `hclgevf_handle_mbx_response()`, `hclgevf_handle_mbx_msg()`, and `hclgevf_cmd_crq_empty()`.

## Control Flow
Synchronous sends acquire `mbx_resp.mbx_mutex`, increment a nonzero match ID, send a command descriptor, then poll up to 500 milliseconds for `received_resp`, aborting if the command queue is disabled. Incoming CRQ descriptors are validated, traced, and classified. PF response messages update the synchronous response buffer immediately with memory barriers; async link/reset/link-mode/VLAN/promisc messages are copied into the ARQ ring and handled later by the service task.

## State And Persistence
Synchronous response state lives in `hdev->mbx_resp`: received flag, origin message, errno-translated response status, match ID, and additional response data. Async state lives in `hdev->arq` with head/tail/count and a bounded message array. No state persists beyond the device instance; mailbox traffic updates `hclgevf_dev` fields such as link, speed, duplex, reset pending bits, supported/advertising modes, PF-push-link flag, and port-base VLAN state.

## Dependencies And Integration Points
Uses HCLGE mailbox structures/opcodes, command descriptors, HNS3 tracepoints, command queue register helpers, and exported update functions from `hclgevf_main.c`. The PF is the authoritative peer for configuration responses and async events; the service workqueue provides the slow-path context for async mailbox processing.

## Risks
Response matching is sensitive to match-ID support and memory ordering; stale `received_resp` or mismatched origin codes return I/O errors. The ARQ ring drops messages when full, so link/reset/VLAN events can be lost under stress. `hclgevf_get_mbx_resp()` copies response data before final origin-code validation, so callers should treat nonzero status as invalid. Async handling exits early when command queue is disabled, leaving queued messages for a later pass.

## Test Signals
Exercise mailbox request/response opcodes, PFs with and without match-ID support, timeout paths, command-queue-disable aborts, invalid CRQ descriptors, ARQ full behavior, PF-pushed link status/modes, reset assertion messages, port-base VLAN updates, and tracepoint emission for send/get descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_regs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_regs.c

## Purpose
Provides ethtool/HNAE3 register dump support for HNS3 VFs. It calculates dump length and serializes command queue, common VF, per-ring, and per-TQP interrupt registers into a TLV-structured buffer.

## Important APIs, Types, And Functions
Exports `hclgevf_get_regs_len()` and `hclgevf_get_regs()`. Internal data includes register address arrays for CMDQ, common, ring, and TQP interrupt groups; packed `struct hclgevf_reg_header` and `struct hclgevf_reg_tlv`; and helpers `hclgevf_reg_get_header()` and `hclgevf_reg_get_tlv()`.

## Control Flow
Length calculation sums a fixed header, CMDQ/common groups, one ring group per TQP, and one TQP interrupt group per used non-misc MSI vector. Dump generation writes the magic header, emits each TLV tag/length, then reads registers from VF MMIO or queue-specific `tqp->io_base` regions. The firmware version is returned through the ethtool version pointer.

## State And Persistence
No persistent state is modified. The generated dump is a snapshot of MMIO register values plus a magic header marking VF layout. It relies on live `hdev->num_tqps`, `hdev->num_msi_used`, `hdev->htqp`, and `hdev->fw_version`.

## Dependencies And Integration Points
Uses register offsets from `hclgevf_main.h`, prototypes from `hclgevf_regs.h`, HNAE3 handle lookup from `hclgevf_ae_get_hdev()`, and common HCLGE command queue register constants. It is plugged into `hclgevf_ops.get_regs_len` and `hclgevf_ops.get_regs`.

## Risks
The dump length must match exactly what `hclgevf_get_regs()` writes; vector or queue count mismatches can overrun or under-fill the caller buffer. Per-ring reads subtract `HCLGEVF_TQP_REG_OFFSET` from `tqp->io_base`, so any TQP base layout change must be reflected here. The packed TLV ABI is consumed externally by diagnostic tools.

## Test Signals
Run `ethtool -d` or equivalent HNAE3 register dump on VFs with different queue/vector counts. Validate magic number, TLV lengths, total byte count, firmware version, and stable behavior during reset or command-queue-disabled windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_regs.h

## Purpose
Declares the HNS3 VF register dump interface used by the main AE ops table.

## Important APIs, Types, And Functions
Forward-declares `struct hnae3_handle` and exposes `hclgevf_get_regs_len()` plus `hclgevf_get_regs()`.

## Control Flow
This header has no runtime control flow. It allows `hclgevf_main.c` to wire register dump callbacks without depending on `hclgevf_regs.c` internals.

## State And Persistence
No state is owned here. Implementations read live hardware and `hclgevf_dev` state when called.

## Dependencies And Integration Points
Depends only on `<linux/types.h>` and the HNAE3 handle type. Integrated by `hclgevf_main.c` through `hclgevf_ops`.

## Risks
Signature drift would break the AE ops callback contract. Because the header hides dump buffer layout, consumers must rely on length/version behavior documented by the implementation.

## Test Signals
Compile coverage and successful register dump invocation through HNAE3/ethtool callbacks are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_trace.h

## Purpose
Defines tracepoints for HNS3 VF mailbox traffic and command queue descriptors under trace system `hns3`.

## Important APIs, Types, And Functions
Trace events are `hclge_vf_mbx_get`, `hclge_vf_mbx_send`, `hclge_vf_cmd_send`, and `hclge_vf_cmd_get`. The latter two are generated from `DECLARE_EVENT_CLASS(hclge_vf_cmd_template)`. `CREATE_TRACE_POINTS` is set in `hclgevf_mbx.c`.

## Control Flow
Tracepoint fast-assign blocks capture PCI name, netdev name, VF ID, opcode/subcode, descriptor flags/retval, and raw mailbox or command descriptor data. `hclgevf_main.c` invokes command trace hooks before/after command sends, and `hclgevf_mbx.c` invokes mailbox tracepoints when the NIC client is registered.

## State And Persistence
No driver state is changed. Events persist only in the kernel tracing ring buffers configured by the operator.

## Dependencies And Integration Points
Depends on Linux tracepoint infrastructure and HNS3 mailbox/descriptor structs. Integrated by command queue ops (`hclgevf_cmq_ops`) and mailbox send/receive code.

## Risks
Tracepoint fields dereference `hdev->nic.kinfo.netdev->name`; callers must only trace when netdev/client state is valid. Raw descriptor/mailbox arrays can expose low-level command data, so tracing should be treated as diagnostic output. Field layout changes affect user-space trace consumers.

## Test Signals
Build with tracepoints enabled, enable the `hns3` events in ftrace/perf, then exercise mailbox and command queue paths. Confirm send/get event counts and decoded data match command descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns_mdio.c

## Purpose
Implements the Hisilicon HNS MDIO platform driver. It registers a Linux `mii_bus` with Clause 22 and Clause 45 read/write operations, supports DT and ACPI discovery, and performs controller clock/reset sequencing.

## Important APIs, Types, And Functions
Primary platform hooks are `hns_mdio_probe()` and `hns_mdio_remove()` through `module_platform_driver()`. MDIO bus callbacks are `hns_mdio_read_c22()`, `hns_mdio_write_c22()`, `hns_mdio_read_c45()`, `hns_mdio_write_c45()`, and `hns_mdio_reset()`. Internal helpers manipulate MMIO fields, poll readiness with `hns_mdio_wait_ready()`, issue commands with `hns_mdio_cmd_write()`, and poll syscon clock/reset state via `mdio_sc_cfg_reg_write()`.

## Control Flow
Probe allocates driver state and `mii_bus`, maps the MDIO register resource, assigns callbacks, and registers the bus via `of_mdiobus_register()` for DT or `mdiobus_register()` for ACPI. DT probes optionally parse `subctrl-vbase` to obtain syscon and reset/clock register offsets, falling back to legacy constants when needed. Clause 45 accesses perform address phase then data/read phase, polling controller readiness between phases; Clause 22 accesses issue a single operation after readiness polling. Remove unregisters the bus.

## State And Persistence
`struct hns_mdio_device` holds MMIO base, optional syscon regmap, and sub-control register offsets. Hardware register state persists in the MDIO controller and syscon; software state is devm-managed and released with the platform device.

## Dependencies And Integration Points
Uses Linux MDIO/PHY framework, platform device resources, OF/ACPI matching, syscon/regmap, and device-managed allocation/mapping. Downstream PHY drivers access this bus through standard `mii_bus` callbacks.

## Risks
Busy-wait loops use `MDIO_TIMEOUT` without sleeps, which can burn CPU if hardware is stuck. DT syscon parsing expects fixed args and still succeeds without syscon until reset is requested; reset can later fail with `-ENODEV`. ACPI probe masks all PHYs from auto-probing and uses polling IRQs. Clause 45 sequence correctness depends on controller command semantics and readiness polling.

## Test Signals
Probe/remove under both DT compatible strings and ACPI ID `HISI0141`, PHY discovery on DT, manual C22/C45 reads/writes through PHY tools, reset sequencing with syscon present/missing, timeout/error paths when MDIO start never clears, and suspend/resume or reprobe behavior if the platform uses it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/Kconfig

## Purpose
Adds the top-level Huawei Ethernet vendor menu and sources the per-driver Kconfig files for `hinic` and `hinic3`.

## Important APIs, Types, And Functions
Defines `config NET_VENDOR_HUAWEI` as a boolean vendor gate defaulting to `y`. When enabled, it sources `drivers/net/ethernet/huawei/hinic/Kconfig` and `drivers/net/ethernet/huawei/hinic3/Kconfig`.

## Control Flow
Kconfig menu flow is simple: if the vendor gate is disabled, all nested Huawei NIC driver prompts are skipped; if enabled, child driver options become visible.

## State And Persistence
The persistent output is kernel configuration state in `.config`. This file does not create runtime state.

## Dependencies And Integration Points
Integrated by the kernel networking Kconfig tree. It gates both the researched `hinic` driver and the sibling `hinic3` subtree.

## Risks
Changing the vendor default or source paths can hide drivers from configuration. The vendor gate does not itself build code; users may incorrectly expect `NET_VENDOR_HUAWEI=y` to enable a driver.

## Test Signals
Run Kconfig/menuconfig and verify Huawei devices menu visibility, child `HINIC`/`HINIC3` prompts, and generated `.config` behavior when the vendor gate is toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/Makefile

## Purpose
Connects Huawei Ethernet subdirectories to the kernel build.

## Important APIs, Types, And Functions
Uses `obj-$(CONFIG_HINIC) += hinic/` and `obj-$(CONFIG_HINIC3) += hinic3/`.

## Control Flow
Kbuild descends into each subdirectory only when its config symbol is enabled.

## State And Persistence
No runtime state. Build artifacts are generated in the selected subdirectories according to Kbuild.

## Dependencies And Integration Points
Depends on Kconfig symbols supplied by the Huawei driver Kconfig files and the enclosing kernel networking Makefile.

## Risks
Incorrect object directory names break builds even when Kconfig options are enabled. This file intentionally has no direct object list, so all per-driver object composition must stay in child Makefiles.

## Test Signals
Build with `CONFIG_HINIC=m/y` and `CONFIG_HINIC3=m/y`; verify Kbuild enters the expected subdirectories and does not build them when symbols are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/Kconfig

## Purpose
Defines the kernel configuration option for the Huawei HiNIC PCIe Ethernet driver.

## Important APIs, Types, And Functions
Defines `config HINIC` as a tristate prompt "Huawei Intelligent PCIE Network Interface Card". It depends on `PCI_MSI` and either `X86` or `ARM64`, and selects `NET_DEVLINK`.

## Control Flow
When dependencies are satisfied and the user selects `HINIC`, the driver can be built in or as a module. Selecting it also enables devlink support needed by `hinic_devlink.c`.

## State And Persistence
The persistent state is the `CONFIG_HINIC` setting in kernel configuration.

## Dependencies And Integration Points
Tied to Kbuild through `huawei/Makefile` and `hinic/Makefile`. The `NET_DEVLINK` select supports firmware flash and health reporter integration.

## Risks
The architecture dependency excludes other platforms even if PCI MSI exists. Removing `NET_DEVLINK` would break devlink symbols. The help text says default module, but actual default is user/config driven because no `default m` is present.

## Test Signals
Kconfig dependency checks on x86/arm64 with PCI MSI, module and built-in builds, and verification that devlink symbols are available when `HINIC` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/Makefile

## Purpose
Defines the composite object list for the HiNIC driver module.

## Important APIs, Types, And Functions
Builds `hinic.o` when `CONFIG_HINIC` is enabled. `hinic-y` aggregates main netdev, TX/RX, port, hardware device/IO/QP/CMDQ/WQ/MGMT/API/EQ/IF/mbox/SR-IOV, common helpers, ethtool, devlink, and debugfs objects.

## Control Flow
Kbuild compiles each listed object and links them into the single `hinic` driver.

## State And Persistence
No runtime state. It controls build composition and therefore which translation units provide symbols to the module.

## Dependencies And Integration Points
Integrated by `drivers/net/ethernet/huawei/Makefile`. The researched files `hinic_common.c`, `hinic_ethtool.c`, `hinic_devlink.c`, `hinic_hw_api_cmd.c`, and `hinic_debugfs.c` are all included here.

## Risks
Object ordering generally matters less for linking but missing an object causes unresolved symbols or lost features. Adding source files without updating this list leaves them unbuilt.

## Test Signals
Build `CONFIG_HINIC=m` and verify `hinic.ko` links with ethtool, devlink, debugfs, mailbox, and hardware API command symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_common.c

## Purpose
Provides small shared helpers for HiNIC endian conversion and scatter-gather DMA address handling.

## Important APIs, Types, And Functions
Exports `hinic_cpu_to_be32()`, `hinic_be32_to_cpu()`, `hinic_set_sge()`, and `hinic_sge_to_dma()`.

## Control Flow
The endian helpers iterate over the provided buffer in 32-bit words, converting each element in place. SGE helpers split a `dma_addr_t` into upper/lower 32-bit fields plus length, and reconstruct a DMA address from those fields.

## State And Persistence
No persistent state. All functions mutate caller-provided memory or return derived values.

## Dependencies And Integration Points
Depends on Linux types and byteorder helpers, and the `struct hinic_sge` definition in `hinic_common.h`. Used by hardware command/data paths that exchange big-endian structures with the device.

## Risks
Endian helpers truncate `len` to whole `u32` elements; trailing bytes are intentionally ignored. Callers must ensure buffer alignment/size are appropriate. SGE conversion assumes 64-bit DMA address semantics even on platforms where `dma_addr_t` may be narrower.

## Test Signals
Unit-style validation of endian conversion on representative buffers, DMA address round trips through `hinic_set_sge()`/`hinic_sge_to_dma()`, and integration tests in command paths that require big-endian wire format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_common.h

## Purpose
Declares shared HiNIC utility macros, the scatter-gather entry structure, and helper prototypes.

## Important APIs, Types, And Functions
Defines `UPPER_8_BITS()`, `LOWER_8_BITS()`, `struct hinic_sge`, and prototypes for endian and SGE helpers.

## Control Flow
No runtime control flow. The macros are inline expressions used by callers needing byte extraction.

## State And Persistence
No state is owned. `struct hinic_sge` is a caller-owned serialized representation of a DMA segment.

## Dependencies And Integration Points
Depends on `<linux/types.h>`. Included by `hinic_common.c` and other HiNIC hardware data-path/control-path files.

## Risks
The byte macros do not cast inputs and may evaluate expressions once but rely on caller-provided integer width. `struct hinic_sge` layout is a hardware/software ABI and should remain stable.

## Test Signals
Compile coverage across all consumers and SGE wire-format validation in DMA command paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_debugfs.c

## Purpose
Creates HiNIC debugfs trees exposing SQ, RQ, and PF function-table diagnostic fields.

## Important APIs, Types, And Functions
Public functions include `hinic_sq_debug_add/rem()`, `hinic_rq_debug_add/rem()`, `hinic_func_table_debug_add/rem()`, per-tree init/uninit helpers, `hinic_dbg_init/uninit()`, and global `hinic_dbg_register_debugfs()/hinic_dbg_unregister_debugfs()`. Internal readers are `hinic_dbg_get_sq_info()`, `hinic_dbg_get_rq_info()`, `hinic_dbg_get_func_table()`, and `hinic_dbg_cmd_read()`.

## Control Flow
Global driver init creates a top-level debugfs root. Per-device init creates a PCI-name directory, then SQ/RQ/function-table subdirectories. Queue add functions create one directory per queue ID and read-only files for field IDs. Reads recover `struct hinic_debug_priv` from the private field pointer, dispatch by debug type, and return a hex value. PF-only function-table reads issue `HINIC_PORT_CMD_RD_LINE_TBL` management commands.

## State And Persistence
Debug state is in `struct hinic_debug_priv` objects linked from queue or device structures and in debugfs dentries stored in `struct hinic_dev`. Values are live snapshots of queue workqueue indices, hardware completion pointers, MSI-X entries, or PF function-table fields. No values are persisted.

## Dependencies And Integration Points
Depends on Linux debugfs, HiNIC queue structures, `hinic_port_msg_cmd()`, and `hinic_dev.h` debug fields. It is built into the `hinic` composite module and called from main/queue lifecycle code.

## Risks
Debugfs creation return values are not deeply checked, so missing files may not abort device operation. `sprintf()` into 16-byte queue directory names is safe for `u16` IDs but still unchecked. Function-table access allocates and sends a management command on every read, so repeated reads can burden firmware. Removal differs for function-table roots versus queue roots, requiring lifecycle pairing.

## Test Signals
Mount debugfs, verify top-level/device/SQs/RQs/func_table directories, read all queue files while traffic runs, add/remove queues, PF vs VF behavior for function table, and removal without stale dentries or use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_debugfs.h

## Purpose
Declares HiNIC debugfs interfaces and function-table wire structures used for diagnostic reads.

## Important APIs, Types, And Functions
Defines table IDs, `HINIC_FUNCTION_CONFIGURE_TABLE_SIZE`, `struct hinic_cmd_lt_rd`, and `struct tag_sml_funcfg_tbl`. Declares SQ/RQ/function-table debug add/remove, subtree init/uninit, per-device debug init/uninit, and global debugfs registration helpers.

## Control Flow
No runtime control flow. The function-table bitfield layout determines how `hinic_debugfs.c` decodes management command data.

## State And Persistence
No owned state. The declared structures represent transient management command request/response data and decoded firmware table entries.

## Dependencies And Integration Points
Includes `hinic_dev.h` for `struct hinic_dev` and queue debug fields. Consumed by debugfs implementation and queue/device lifecycle code.

## Risks
The bitfield layout in `tag_sml_funcfg_tbl` is compiler/layout sensitive and must match firmware expectations. Debugfs prototypes expose lifecycle responsibilities to callers; missing remove calls can leave stale debug entries.

## Test Signals
Compile with debugfs enabled, PF function-table read correctness, and lifecycle tests for queue/device add/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_dev.h

## Purpose
Defines the main software state for the HiNIC netdev driver and related runtime flags/config structures.

## Important APIs, Types, And Functions
Key definitions are `HINIC_DRV_NAME`, MTU limits, `enum hinic_flags`, `struct hinic_rx_mode_work`, `struct hinic_rss_type`, `enum hinic_rss_hash_type`, `struct hinic_intr_coal_info`, debug enums/privates, `struct hinic_dev`, and `struct hinic_devlink_priv`.

## Control Flow
This header has no executable flow, but `struct hinic_dev` is the central object passed through netdev, ethtool, debugfs, SR-IOV, TX/RX, workqueue, and devlink paths.

## State And Persistence
`struct hinic_dev` tracks netdev/hardware pointers, message verbosity, queue counts/depths, flags, management lock, VLAN bitmap, RX mode workqueue, TX/RX queue arrays, RSS template/key/indirection state, interrupt coalescing arrays, SR-IOV info, loopback test buffers/state, debugfs dentries, devlink pointer, and link-ext-state booleans. State is runtime-only, with hardware/firmware as the external authority for many settings.

## Dependencies And Integration Points
Includes netdevice, semaphore, workqueue, bitops, hardware device, TX/RX, and SR-IOV headers. It is included by ethtool, debugfs, devlink, and main driver code.

## Risks
Many subsystems share this struct; field lifecycle must match netdev open/close, queue allocation, debugfs creation, and devlink registration. Flags are non-atomic `unsigned int` bit masks in several paths, so caller context and locking matter. Loopback test pointers are valid only while diagnostic tests run.

## Test Signals
Compile coverage across all HiNIC objects, netdev probe/open/close/remove, ethtool RSS/coalescing/channel operations, debugfs lifecycle, devlink health reporter creation, SR-IOV enable/disable, and loopback diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_devlink.c

## Purpose
Implements HiNIC devlink support for firmware flash updates and health reporter dumps for hardware and firmware faults.

## Important APIs, Types, And Functions
Public functions are `hinic_devlink_alloc/free/register/unregister()` and `hinic_health_reporters_create/destroy()`. Firmware update flow uses `check_image_valid()`, `check_image_integrity()`, `check_image_device_type()`, `hinic_flash_fw()`, `hinic_firmware_update()`, and `hinic_devlink_flash_update()`. Health dumping uses `fault_report_show()`, `chip_fault_show()`, `mgmt_watchdog_report_show()`, `hinic_hw_reporter_dump()`, and `hinic_fw_reporter_dump()`.

## Control Flow
Devlink flash update receives a firmware object, validates magic, section count, total length, required section set for cold update, and board type. Flashing then iterates firmware sections, skips boot, translates A/B text/data section types, chunks each section into up to 1536-byte fragments, marks first/last fragment flags, copies payload after the 1024-byte image header, and sends `HINIC_PORT_CMD_UPDATE_FW` management commands. Health reporters are created for `hw` and `fw`; dump callbacks format fault event or management watchdog payloads into devlink fmsg pairs/binary blobs.

## State And Persistence
Devlink state is held in `struct hinic_devlink_priv`: hardware pointer and reporter handles. Firmware flashing persists new firmware into device storage via firmware management commands. Health dump state is transient and supplied as reporter context.

## Dependencies And Integration Points
Depends on Linux devlink/netlink/firmware APIs, HiNIC port management commands, board-info query, hardware device types, and structures from `hinic_devlink.h`. `hinic/Kconfig` selects `NET_DEVLINK` to satisfy this.

## Risks
Firmware image parsing casts raw bytes directly to header structs and trusts declared section offsets after length validation; malformed but internally consistent offsets can still stress device command handling. `check_image_device_type()` returns boolean values through an `int`, which is harmless but semantically inconsistent. Flashing is cold-update only from the devlink entry point. Reporter dumps assume private context points to a valid fault/watchdog payload.

## Test Signals
Use `devlink dev flash` with valid firmware, wrong magic, duplicate/missing sections, wrong board type, oversized/partial images, and management command failures including `HINIC_FW_DISMATCH_ERROR`. Trigger hardware and firmware reporter dumps and verify fmsg fields for each fault type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_devlink.h

## Purpose
Defines HiNIC firmware image constants, section enums, image/header structures, and devlink/health reporter prototypes.

## Important APIs, Types, And Functions
Important constants include `MAX_FW_TYPE_NUM`, `HINIC_MAGIC_NUM`, `UPDATEFW_IMAGE_HEAD_SIZE`, `MAX_FW_FRAGMENT_LEN`, `FW_UPDATE_COLD/HOT`, `UP_TYPE_A/B`, and required-section bitmasks. Defines `enum hinic_fw_type`, `struct fw_section_info_st`, `struct fw_image_st`, and `struct host_image_st`.

## Control Flow
No runtime flow here. The enums and bitmasks drive `hinic_devlink.c` validation and section-type translation during firmware updates.

## State And Persistence
No owned state. Structures represent on-disk firmware headers and an in-memory normalized host image.

## Dependencies And Integration Points
Includes devlink and `hinic_dev.h`. Exported prototypes are consumed by the main HiNIC driver to allocate/register devlink and create health reporters.

## Risks
Firmware header structs are ABI-sensitive; layout or size changes can break image validation. Bitmask expressions use `1 << type` and require section enum values to remain within supported bit widths. Required-section masks define update policy and should be changed only with firmware compatibility knowledge.

## Test Signals
Compile coverage, firmware image validation tests for all section masks, and devlink registration/health reporter lifecycle validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_ethtool.c

## Purpose
Implements ethtool operations for HiNIC PFs and VFs: link settings, driver info, ring depth, interrupt coalescing, pause, channels, RSS, statistics, diagnostics, LED identification, module EEPROM, and link extended state.

## Important APIs, Types, And Functions
The file culminates in `hinic_ethtool_ops`, `hinicvf_ethtool_ops`, and `hinic_set_ethtool_ops()`. Major function groups include link settings (`hinic_get_link_ksettings()`, `hinic_set_link_ksettings()`), ring/coalescing (`hinic_get/set_ringparam()`, `hinic_get/set_coalesce()`, per-queue variants), pause/channels, RSS (`hinic_get/set_rxfh()`, `hinic_get/set_rxfh_fields()`), stats (`hinic_get_ethtool_stats()`, `hinic_get_strings()`, `hinic_get_sset_count()`), diagnostics (`hinic_diag_test()`, `do_lp_test()`, `hinic_run_lp_test()`), LED, module info/EEPROM, and link-ext-state.

## Control Flow
Getters translate firmware/hardware data into ethtool structures: port capabilities, link modes, pause state, queue depths, coalescing units, RSS templates, function/port/queue stats, and module data. Setters validate requested values, update driver shadow state, send management commands, and in some cases restart the netdev. Ring-depth changes close/open a running interface. Channel changes update `nic_cap.num_qps` and restart if needed. Coalescing converts ethtool usec/frame values to hardware units and writes per-queue MSI-X interrupt config when the interface is up.

## State And Persistence
Driver state touched includes queue depths, queue count, RSS template/key/indirection user buffers, RSS hash engine/type, interrupt coalescing arrays, pause shadow config under `nic_cfg.cfg_mutex`, loopback test buffers/flags, and link extended state booleans. Hardware/firmware persists link, pause, coalescing, RSS, LED, and loopback settings through management commands, while software shadows preserve user RSS/coalescing choices.

## Dependencies And Integration Points
Depends on ethtool/netdevice APIs, PCI, SFP identifiers, TX/RX queue stats, HiNIC port management commands, hardware device state, RSS helpers, and main netdev `hinic_open()`, `hinic_close()`, and loopback transmit path. VF ops intentionally omit setters/features not supported for VFs, such as pause, physical ID, diagnostics, module EEPROM, and set link settings.

## Risks
Several setters return `-EFAULT` for underlying command failures, which can obscure exact firmware error causes. Ring/channel changes restart the interface and can leave updated software values if reopen fails. Coalescing only applies nonzero requested fields and warns when hardware units round to zero; callers should understand unit quantization. RSS user buffers are lazily allocated and retained. Loopback tests disable carrier/TX, allocate large buffers, transmit crafted packets, and compare received data; errors must restore loopback mode and queue/carrier state. Link mode uses legacy `u64` masks copied into linkmode bitmaps, limiting future expansion.

## Test Signals
Exercise `ethtool -i`, `-k/-g/-G`, `-c/-C`, per-queue coalescing, `-a/-A`, `-l/-L`, `-x/-X`, RSS fields via `-N/-n`, `-S`, `-t` internal/external loopback, `-p`, `-m`, and link extended state. Test PF and VF differences, netdev-up/down behavior, reopen failure handling, unsupported speed/autoneg, unsupported RSS hash functions, and firmware command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_api_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_api_cmd.c

## Purpose
Implements the HiNIC hardware API command chain used to send DMA-backed management commands to the management CPU.

## Important APIs, Types, And Functions
Exports `hinic_api_cmd_write()`, `hinic_api_cmd_init()`, and `hinic_api_cmd_free()`. Internal flow is built from command preparation (`prepare_cell_ctrl()`, `prepare_api_cmd()`, `prepare_cell()`), ring accounting (`chain_busy()`, `set_prod_idx()`, `get_hw_cons_idx()`), completion (`api_cmd_status_update()`, `wait_for_status_poll()`, `wait_for_api_cmd_completion()`), hardware init/cleanup (`api_cmd_hw_restart()`, `api_cmd_ctrl_init()`, status/head/num-cell setters, `api_cmd_chain_hw_init()`), and DMA allocation/destruction helpers for cells and command buffers.

## Control Flow
Initialization creates one power-of-two chain (`HINIC_API_CMD_WRITE_TO_MGMT_CPU`) with 32 cells. Each cell is coherent DMA memory linked into a circular list and has a separate 2048-byte coherent command buffer. Hardware is cleaned, status DMA address installed, chain restarted, control register configured for XOR checking and cell size, number of cells programmed, and head pointer written. A write command takes the chain semaphore, verifies space, prepares current cell control/descriptor/checksums in big-endian format, copies command data into the DMA buffer, increments producer index, issues a write memory barrier, writes hardware PI, advances `curr_node`, then polls write-back status until consumer index catches producer index or times out.

## State And Persistence
`struct hinic_api_cmd_chain` holds chain type, producer/consumer indexes, semaphore, cell contexts, write-back status DMA area, head/current cell pointers, and hardware interface pointer. Hardware state persists in CSR registers and the device-visible DMA ring until cleanup. Software state is devm/coherent-DMA allocated and released on device teardown.

## Dependencies And Integration Points
Depends on PCI DMA APIs, semaphores, jiffies/msleep polling, memory barriers, byteorder helpers, HINIC CSR macros, hardware interface read/write helpers, and node IDs. Higher-level management command paths use `hinic_api_cmd_write()` to reach the management CPU.

## Risks
The public write function does not check `size` against the 2048-byte command buffer, so callers must guarantee bounded commands. Completion is polling-based with a 1 second timeout and 20 ms sleeps; slow firmware can cause errors. Producer/consumer index handling relies on `num_cells` being a power of two. DMA allocation unwind must stay correct because each cell has two coherent allocations. Endianness and XOR checksum fields are hardware ABI-sensitive.

## Test Signals
Initialize/free under probe/remove, send representative management commands, force chain full/busy, timeout completion, checksum/CPLD error reporting, DMA allocation failure unwinds, repeated writes under concurrency to validate semaphore serialization, and hardware reset/reinit of the chain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_api_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_api_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_api_cmd.h

## Purpose
Defines the hardware API command chain register bitfields, descriptor/cell/status structures, chain attributes, runtime chain object, and public command-chain API.

## Important APIs, Types, And Functions
Important macros set/clear/get fields for producer index, chain request/control, cell control, descriptor, and status registers. Key types are `enum hinic_api_cmd_chain_type`, `struct hinic_api_cmd_chain_attr`, `struct hinic_api_cmd_status`, `struct hinic_api_cmd_cell`, `struct hinic_api_cmd_cell_ctxt`, and `struct hinic_api_cmd_chain`. Prototypes expose `hinic_api_cmd_write()`, `hinic_api_cmd_init()`, and `hinic_api_cmd_free()`.

## Control Flow
No executable control flow, but the bitfield macros are used by `hinic_hw_api_cmd.c` to program CSRs and build big-endian device descriptors. The chain type enum currently exposes a write-to-management-CPU chain at value 2.

## State And Persistence
The runtime chain struct holds producer/consumer state, a semaphore, DMA contexts, write-back status, and current/head cells. The hardware cell/status structs define device-visible persistent state while the chain is active.

## Dependencies And Integration Points
Includes Linux types/semaphore and `hinic_hw_if.h` for hardware interface and node identifiers. Consumed by API command implementation and higher-level hardware management paths.

## Risks
Bit shifts/masks are hardware ABI; incorrect edits break command submission. Some macros are untyped and depend on caller width. Structure layout must match firmware expectations, including 64-bit hardware addresses and big-endian conversion by the implementation.

## Test Signals
Compile coverage, command-chain initialization, descriptor field decode in hardware traces, and management command success/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_api_cmd.h -->
