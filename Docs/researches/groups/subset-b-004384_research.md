# subset-b-004384 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/tg3.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/tg3.h

Purpose: central hardware definition header for the Broadcom Tigon3/TG3 Ethernet driver. It maps the PCI configuration mirror, memory-mapped device register blocks, SRAM/NVRAM/OTP/APE layouts, PHY/MII registers, DMA descriptor formats, status/statistics blocks, driver feature flags, and the main `struct tg3` private device state used by the C implementation.

Important APIs/types/functions: there are no callable functions, but the header defines the driver's ABI to the device. Key structures are `struct tg3_tx_buffer_desc`, `struct tg3_rx_buffer_desc`, `struct tg3_ext_rx_buffer_desc`, `struct tg3_hw_status`, `struct tg3_hw_stats`, `struct tg3_ocir`, `struct ring_info`, `struct tg3_tx_ring_info`, `struct tg3_link_config`, `struct tg3_bufmgr_config`, `struct tg3_ethtool_stats`, `struct tg3_rx_prodring_set`, `struct tg3_napi`, `struct tg3_firmware_hdr`, and `struct tg3`. Important macro groups include PCI/vendor/device/subdevice IDs, chip/ASIC revision constants, mailbox registers, MAC/RX/TX mode bits, descriptor flags, RSS/PTP bits, DMA engine registers, SRAM mailbox/state fields, NVRAM/flash vendor and page geometry, APE shared-memory offsets, PHY IDs, PHY flags, and accessor macros `tg3_chip_rev_id`, `tg3_asic_rev`, and `tg3_chip_rev`.

Control flow: this file contributes declarative control inputs rather than executable flow. Driver code uses its register offsets and bit masks during probe, chip reset, firmware loading, NVRAM probing, ring setup, link negotiation, interrupt processing, PTP timestamping, statistics collection, suspend/WOL, and error recovery. The descriptor comments define the TX setup sequence: select host-memory send BDs through `GRC_MODE_HOST_SENDBDS`, program `NIC_SRAM_SEND_RCB`, allocate DMA-visible rings, and then advance mailbox producer indices for NIC fetching.

State and persistence behavior: persistent device configuration is represented through NVRAM/EEPROM/OTP layout definitions, bootcode/version fields, VPD offsets, flash vendor encodings, APE shared memory, and NIC SRAM driver/firmware mailboxes. Runtime state is represented by DMA rings, producer/consumer indices, hardware status blocks, hardware statistics blocks, `tg3_flags`, NAPI per-vector state, cached register values, link settings, PTP state, firmware pointers, NVRAM geometry, APE heartbeat state, and PCI error recovery flags. Many structures mirror hardware layout and contain endian-sensitive field ordering.

Dependencies and integration points: depends on Linux networking, PCI, DMA mapping, NAPI, ethtool, PTP, PHY/MDIO, firmware loading, hwmon, timers, workqueues, and byte-order conventions supplied by the `.c` file includes. The register and descriptor contracts are consumed primarily by `tg3.c` and ethtool/PHY helpers. APE and NVRAM definitions integrate with management firmware and boot ROM. PHY constants integrate with MII and phylib operations.

Risks: the file encodes hardware ABI details where incorrect offsets, bit masks, endian layouts, or structure padding can corrupt DMA rings, mis-handle interrupts, break firmware handshakes, or write wrong flash regions. The single `enum TG3_FLAGS` must stay below bitmap capacity and maintain assumptions in feature tests. Some aliases intentionally reuse bit values across chip families, so callers must gate writes by ASIC revision. Persistent-memory definitions carry high risk because NVRAM/flash write-protect and vendor/page-size fields control destructive operations.

Test signals: useful signals include successful probe across supported PCI IDs, `ethtool -S` statistics sanity, RX/TX traffic under checksum/TSO/VLAN/RSS/PTP paths, interrupt mode coverage for INTx/MSI/MSI-X, NVRAM/VPD read-only diagnostics, WOL suspend/resume, link negotiation across copper/serdes/FET PHYs, and fault-injection around DMA/status-block errors. Static compile checks also catch structure/member references from implementation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/tg3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/unimac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/unimac.h

Purpose: compact register definition header for Broadcom UniMAC blocks. It names offsets and bit fields used to configure a UniMAC Ethernet MAC for transmit/receive enablement, link speed, promiscuous mode, flow control, CRC/pause handling, loopback, Energy Efficient Ethernet, VLAN tag handling, and FIFO/status controls.

Important APIs/types/functions: no functions or structures are defined. Important macros include `UMAC_CMD` with `CMD_TX_EN`, `CMD_RX_EN`, `CMD_SPEED_*`, `CMD_PROMISC`, `CMD_SW_RESET`, `CMD_AUTO_CONFIG`, loopback and pause bits; address and frame registers `UMAC_MAC0`, `UMAC_MAC1`, `UMAC_MAX_FRAME_LEN`; status/config registers `UMAC_MODE`, `UMAC_FRM_TAG0`, `UMAC_FRM_TAG1`; and EEE/FIFO control registers `UMAC_EEE_CTRL`, `UMAC_EEE_LPI_TIMER`, `UMAC_EEE_WAKE_TIMER`, `UMAC_PAUSE_CTRL`, `UMAC_TX_FLUSH`, `UMAC_RX_FIFO_STATUS`, and `UMAC_TX_FIFO_STATUS`.

Control flow: this is declarative hardware metadata. MAC setup code composes `UMAC_CMD` bits to reset, choose speed, enable TX/RX, set filtering and pause behavior, then uses the address, max-frame, tag, EEE, and FIFO registers during link changes or power-management transitions.

State and persistence behavior: the header defines volatile MMIO state only. There is no stored driver state and no persistence beyond the hardware register values programmed by the consuming driver.

Dependencies and integration points: intended for Broadcom Ethernet MAC drivers that use a UniMAC register block. It integrates with Linux netdev link setup, multicast/promiscuous configuration, pause/EEE configuration, and hardware reset paths in the corresponding implementation files.

Risks: bit definitions are shared hardware contracts; a wrong speed field, reset bit, or EEE bit can leave the MAC disabled, negotiating at the wrong speed, discarding control frames, or entering low-power states incorrectly. `CMD_SW_RESET_OLD` and `CMD_SW_RESET` indicate revision-specific reset behavior that callers must select carefully.

Test signals: validate with link-up/link-down transitions at 10/100/1000/2500 speeds, promiscuous and multicast filtering changes, pause-frame behavior, EEE enable/disable, loopback where supported, and FIFO status/flush behavior after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/unimac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/Kconfig

Purpose: top-level Kconfig menu gate for QLogic/Brocade BR-series Ethernet devices.

Important APIs/types/functions: defines `config NET_VENDOR_BROCADE`, a boolean vendor selector defaulting to `y` when PCI is available. When enabled, it sources `drivers/net/ethernet/brocade/bna/Kconfig`, which exposes the actual `BNA` driver option.

Control flow: Kconfig evaluation first checks `depends on PCI`; if the vendor item is disabled, all child BR-series driver questions are skipped. If enabled, the BNA driver configuration is included.

State and persistence behavior: no runtime state. Persistent effect is the generated kernel `.config`, where `NET_VENDOR_BROCADE` controls visibility of child symbols.

Dependencies and integration points: integrates with the kernel networking vendor Kconfig hierarchy and depends on PCI support. It delegates driver-specific selection to the bna subdirectory.

Risks: changing the default, dependency, or `source` path can hide the BNA driver from configuration or expose it on unsupported non-PCI builds. The help text names QLogic BR-series cards, reflecting Brocade/QLogic branding.

Test signals: `make menuconfig` or `scripts/kconfig` should show the vendor menu under Ethernet drivers when PCI is enabled, and `CONFIG_BNA` should be reachable only when `NET_VENDOR_BROCADE=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/Makefile

Purpose: top-level kbuild entry for QLogic/Brocade BR-series Ethernet drivers.

Important APIs/types/functions: contains a single object rule, `obj-$(CONFIG_BNA) += bna/`, which descends into the BNA driver directory when the driver symbol is enabled.

Control flow: during kernel build, kbuild evaluates `CONFIG_BNA`; if built-in or module, it visits `drivers/net/ethernet/brocade/bna/` and uses that subdirectory's Makefile to compose `bna.o`.

State and persistence behavior: no runtime state. Build output depends on the persistent kernel config and generated object/module files.

Dependencies and integration points: integrates with the parent Ethernet Makefile and the child `bna/Makefile`. It relies on Kconfig to define `CONFIG_BNA`.

Risks: a wrong object directory or symbol name would omit the driver even when configured. Because the file only delegates, most build-order risk is in the child Makefile.

Test signals: `make M=drivers/net/ethernet/brocade` or a full kernel build with `CONFIG_BNA=m/y` should enter the `bna` directory and produce the driver object/module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/Kconfig

Purpose: driver-specific Kconfig option for the QLogic BR-series 1010/1020/1860 10Gb CEE-capable Ethernet driver.

Important APIs/types/functions: defines `config BNA` as a tristate option with prompt text and `depends on PCI`. The help text says module builds produce a module named `bna`.

Control flow: once the parent vendor menu is active, the user or defconfig may select `BNA=y` or `BNA=m`, subject to PCI availability. That symbol drives the top-level and child Makefiles.

State and persistence behavior: no runtime state. Persistent state is the generated `CONFIG_BNA` selection that controls whether the BNA code is omitted, built in, or built as a module.

Dependencies and integration points: integrates with kernel Kconfig, the parent Brocade Kconfig, and the kbuild Makefiles. The runtime driver itself also depends on PCI APIs, firmware/message infrastructure, netdev, ethtool, and debugfs through source files listed in the Makefile.

Risks: missing dependency constraints can expose compile failures on unsupported architectures; over-constraining hides valid builds. The support URL is informational and may not reflect current vendor branding.

Test signals: Kconfig should accept `CONFIG_BNA=m` on PCI-capable builds, and `modinfo bna` should exist after module compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/Makefile

Purpose: kbuild composition file for the BNA network driver module/object.

Important APIs/types/functions: `obj-$(CONFIG_BNA) += bna.o` defines the final built unit. `bna-objs` aggregates `bnad.o`, `bnad_ethtool.o`, `bnad_debugfs.o`, `bna_enet.o`, `bna_tx_rx.o`, `bfa_msgq.o`, `bfa_ioc.o`, `bfa_ioc_ct.o`, `bfa_cee.o`, and `cna_fwimg.o`.

Control flow: kbuild compiles each listed object and links them into `bna.o` when `CONFIG_BNA` is enabled. The object list reflects the driver layering: Linux netdev front end, ethtool/debugfs, Ethernet/TX/RX core, firmware message queue, IOC/hardware-specific IOC, CEE, and embedded firmware image.

State and persistence behavior: no runtime state in this file. Build artifacts persist under the kernel build tree as object files and optionally `bna.ko`.

Dependencies and integration points: integrates with `CONFIG_BNA`, the parent Makefile, and all source files named in `bna-objs`. It also implies that `bfa_ioc.c`, `bfa_cee.c`, and `cna_fwimg.c` are linked into the same module and can share internal symbols.

Risks: object ordering can matter for initialization sections and symbol resolution. Omitting `cna_fwimg.o` would break firmware image lookup, and omitting `bfa_ioc_ct.o` would break ASIC-specific IOC hooks.

Test signals: module link should resolve all `bfa_nw_*`, `bna_*`, and firmware-image symbols; `CONFIG_BNA=m` should produce one `bna.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cee.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cee.c

Purpose: implements the BNA driver's CEE/DCBX/LLDP mailbox client. It allocates DMA-backed buffers for CEE attributes and statistics, sends firmware mailbox requests, converts firmware byte order, tracks pending operations, and notifies callers or registered modules when IOC failure cancels a request.

Important APIs/types/functions: exported functions are `bfa_nw_cee_meminfo`, `bfa_nw_cee_mem_claim`, `bfa_nw_cee_get_attr`, and `bfa_nw_cee_attach`. Internal helpers include `bfa_cee_format_cee_cfg`, `bfa_cee_stats_swap`, `bfa_cee_format_lldp_cfg`, `bfa_cee_attr_meminfo`, `bfa_cee_stats_meminfo`, `bfa_cee_get_attr_isr`, `bfa_cee_get_stats_isr`, `bfa_cee_reset_stats_isr`, `bfa_cee_isr`, and `bfa_cee_notify`.

Control flow: attach registers `bfa_cee_isr` for message class `BFI_MC_CEE` and registers IOC notifications. `bfa_nw_cee_get_attr` checks IOC operational state, rejects concurrent attribute requests with `BFA_STATUS_DEVBUSY`, stores caller buffers/callbacks, builds a `BFI_CEE_H2I_GET_CFG_REQ`, points firmware at `attr_dma.pa`, and queues the mailbox through `bfa_nw_ioc_mbox_queue`. Mailbox ISR dispatches firmware responses by message ID to attribute, stats, or reset-stats completion handlers. IOC disabled/failed notifications synthesize failed completions for any pending operation.

State and persistence behavior: `struct bfa_cee` owns pending booleans, last statuses, callback pointers/arguments, DMA descriptors for attributes and stats, caller-visible `attr` and `stats` pointers, and mailbox command storage. The CEE state is runtime-only; persistent CEE configuration lives in firmware/hardware and is queried into DMA buffers. Firmware returns some fields in network/big-endian order, so completion paths copy and convert before invoking callbacks.

Dependencies and integration points: depends on `bfa_cee.h`, CEE data definitions in `bfa_defs_cna.h`, BFI CEE message definitions in `bfi_cna.h`, and IOC services from `bfa_ioc.h`. It integrates with the BNA adapter via IOC mailbox registration and notification queues. Higher-level ethtool/debugfs code can request CEE attributes via the exported API.

Risks: only `get_attr` is exported in the header although ISR paths for stats/reset exist; if other code later queues stats commands, pending flags and callbacks must be set consistently. The code uses `BUG_ON` for invalid state and unknown CEE response IDs, which can panic the kernel on malformed firmware behavior. Pending operations are not protected by local locks here, so callers must serialize access as implied by the IOC mailbox contract. Byte-order mistakes in CEE structs can surface as incorrect LLDP/DCBX state.

Test signals: call `bfa_nw_cee_get_attr` when IOC is operational and verify callback status plus converted LLDP TTL/system-capability fields. Check `BFA_STATUS_IOC_FAILURE` when IOC is down, `BFA_STATUS_DEVBUSY` for overlapping requests, and failed callback completion on IOC disable/failure. Firmware response tests should cover unknown message IDs and non-OK statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cee.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cee.h

Purpose: declares the BNA CEE module API and its per-module state structure.

Important APIs/types/functions: callback typedefs are `bfa_cee_get_attr_cbfn_t`, `bfa_cee_get_stats_cbfn_t`, and `bfa_cee_reset_stats_cbfn_t`. `struct bfa_cee_cbfn` stores callbacks and arguments. `struct bfa_cee` stores IOC linkage, notification node, pending flags/statuses, DMA buffers, caller-visible attribute/stat pointers, and mailbox commands. Public functions are `bfa_nw_cee_meminfo`, `bfa_nw_cee_mem_claim`, `bfa_nw_cee_attach`, and `bfa_nw_cee_get_attr`.

Control flow: users allocate a `struct bfa_cee`, ask for DMA memory size, claim a DMA block, attach to an IOC, and then issue asynchronous attribute requests. Completion flows through callbacks stored in the structure and through IOC notification handling in the implementation.

State and persistence behavior: all fields are runtime state. The DMA pointers in `attr_dma` and `stats_dma` must remain valid for firmware access while requests are active. Pending booleans prevent overlapping operation types.

Dependencies and integration points: includes `bfa_defs_cna.h` for CEE structures/status enums and `bfa_ioc.h` for DMA, mailbox, and IOC notify definitions. Integrates into the BNA module as a mailbox client.

Risks: the header exposes mutable internals to callers, so misuse can corrupt callback state or DMA pointers. The API exports `get_attr` but not stats/reset request entry points despite carrying stats state, creating an asymmetric interface. Callers must not free DMA memory or IOC structures before detach/failure paths are quiesced.

Test signals: compile-time users should include this header without circular include failure. Runtime tests should attach to IOC, claim correct memory size, and complete attribute requests with callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cs.h

Purpose: common-service helpers for the BFA/BNA driver stack, primarily finite-state-machine support and a small wait-counter utility.

Important APIs/types/functions: `BFA_SM_TABLE` generates state-machine table types and `*_sm_to_state` functions for IOC, IOCPF, message queues, and BNA Ethernet/TX/RX state machines. `BFA_SM`, `bfa_fsm_t`, `bfa_fsm_state_decl`, `bfa_fsm_set_state`, `bfa_fsm_send_event`, and `bfa_fsm_cmp_state` implement the local FSM style. `struct bfa_wc` plus `bfa_wc_init`, `bfa_wc_up`, `bfa_wc_down`, and `bfa_wc_wait` implement a callback-triggered wait counter.

Control flow: modules declare state handlers with `bfa_fsm_state_decl`, transition with `bfa_fsm_set_state`, and dispatch events with `bfa_fsm_send_event`. Entry functions run immediately on state change. State tables translate function pointers into stable status enums for external reporting. The wait counter starts at one, increments for outstanding sub-operations, and invokes `wc_resume` when the count reaches zero.

State and persistence behavior: FSM state is stored as a function pointer in each owning object; tables are static metadata. `struct bfa_wc` is in-memory coordination state only. No persistence.

Dependencies and integration points: includes `cna.h` for shared driver types and relies on `bfa_sm_fault` being provided elsewhere. The macros are used by `bfa_ioc.c`, `bfa_msgq.c`, and BNA Ethernet/TX/RX modules.

Risks: function-pointer FSMs are compact but make invalid-event handling rely on `bfa_sm_fault`, often fatal. `*_sm_to_state` assumes every active state appears in a null-terminated or sentinel-safe table; the visible tables in users must be complete. Wait-counter functions do not use atomics or locking, so they are suitable only under caller-provided serialization.

Test signals: state transition unit tests or trace logs should show entry functions firing once per transition and state-to-enum mapping matching exported attributes. Wait-counter tests should verify resume happens exactly when the last outstanding operation completes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs.h

Purpose: shared public definition header for BFA adapter, IOC, manufacturing, PCI, mode, and flash data structures used by the BNA/QLogic BR-series driver stack.

Important APIs/types/functions: defines size constants such as `BFA_VERSION_LEN`, adapter string lengths, and IOC string lengths. Key types include `struct bfa_adapter_attr`, `struct bfa_ioc_driver_attr`, `struct bfa_ioc_pci_attr`, `enum bfa_ioc_state`, `struct bfa_fw_ioc_stats`, `struct bfa_ioc_drv_stats`, `struct bfa_ioc_stats`, `enum bfa_ioc_type`, `struct bfa_ioc_attr`, `struct bfa_mfg_block`, `enum bfa_mode`, `struct bfa_flash_part_attr`, and `struct bfa_flash_attr`. It also defines adapter capability bits, PCI device/subsystem IDs, ASIC ID helpers, and flash partition constants.

Control flow: no executable flow. Runtime code fills these structures when firmware returns IOC attributes, manufacturing data, and flash partition tables. `bfa_ioc.c` uses the IOC state enum for state reporting and uses flash partition structures in flash query responses.

State and persistence behavior: structures describe both runtime status (`bfa_ioc_attr`, stats) and persistent manufacturing/flash data (`bfa_mfg_block`, VPD embedded via `bfa_defs_mfg_comm.h`, flash partition attributes). The manufacturing block is explicitly packed and documents big-endian numerical fields.

Dependencies and integration points: includes `cna.h`, `bfa_defs_status.h`, and `bfa_defs_mfg_comm.h`. Integrates with firmware message structures, adapter attribute reporting, ethtool/debugfs, flash management, and PCI probe logic.

Risks: structure layout and field widths are part of firmware/userspace-facing contracts; padding or endian mistakes can corrupt displayed adapter attributes or flash partition parsing. Capability and mode enums must stay synchronized with firmware definitions. Manufacturing fields are persistent identity data, so any writer must enforce checksums and bounds.

Test signals: compare `bfa_nw_ioc_get_attr` output against known adapter data, verify card type and capability decoding for CT/CT2 devices, and validate flash query conversion with realistic partition tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_cna.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_cna.h

Purpose: CNA/CEE data definition header for port statistics and Converged Enhanced Ethernet query results.

Important APIs/types/functions: defines `struct bfa_port_fc_stats`, `struct bfa_port_eth_stats`, `union bfa_port_stats_u`, LLDP/DCBX constants, `struct bfa_cee_lldp_str`, `struct bfa_cee_lldp_cfg`, `enum bfa_cee_dcbx_version`, `enum bfa_cee_lls`, `struct bfa_cee_dcbx_cfg`, `enum bfa_cee_status`, `struct bfa_cee_attr`, and `struct bfa_cee_stats`.

Control flow: no executable flow. Firmware fills these packed structures into DMA memory; `bfa_cee.c` copies and converts selected fields before returning data to callers. Port statistics can be consumed by adapter statistics paths.

State and persistence behavior: all structures represent runtime counters or negotiated remote LLDP/DCBX/CEE state. Counters are cumulative until reset by firmware. The LLDP/DCBX attributes reflect remote peer-advertised state and current link CEE status.

Dependencies and integration points: includes `bfa_defs.h` for common BFA types and status dependencies. Integrated by the CEE mailbox client and any ethtool/debugfs/statistics presentation code.

Risks: `__packed` data is firmware ABI; misalignment-sensitive CPU access or missing byte-order conversion can produce wrong values. Stats are 32-bit in `bfa_cee_stats`, so wraparound is possible on active links. Fixed LLDP string buffers require consumers to honor `len` and avoid assuming NUL termination.

Test signals: LLDP/DCBX dumps should show sane remote chassis/port/system strings, TTL, PFC and priority maps. Statistics should increment under LLDP/DCBX activity and reset through firmware paths where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_cna.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_mfg_comm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_mfg_comm.h

Purpose: shared manufacturing and VPD constants/types for BFA/BNA adapters.

Important APIs/types/functions: defines manufacturing block version constants, `BFA_MFG_SERIALNUM_SIZE`, `STRSZ`, card type enum values, `bfa_mfg_is_mezz`, GPIO/card-property mapping macro `bfa_mfg_adapter_prop_init_gpio`, VPD length/header/vendor constants, VPD vendor enum, and packed `struct bfa_mfg_vpd`.

Control flow: most content is declarative, except `bfa_mfg_adapter_prop_init_gpio`, a macro that decodes GPIO strap/card identity into adapter properties and card type. The macro marks prototypes, sets port count and speed property fields, and classifies unsupported/invalid values.

State and persistence behavior: describes persistent manufacturing identity and VPD data stored in adapter flash/NVRAM. `struct bfa_mfg_vpd` contains version/signature/checksum/vendor/length and a 512-byte data array. Consumers copy this into adapter attributes.

Dependencies and integration points: includes `bfa_defs.h`, creating a circular-looking include relationship that is protected by include guards. It expects BFI adapter property macros such as `BFI_ADAPTER_SETP`, `BFI_ADAPTER_PROTO`, `BFI_ADAPTER_TTV`, and `BFI_ADAPTER_UNSUPP` from lower headers included through `bfa_defs.h`/`cna.h`.

Risks: card type and VPD constants must match firmware/manufacturing data. The GPIO macro intentionally falls through from `CB_GPIO_TTV` to two-port 8G handling; accidental `break` changes behavior. `STRSZ` rounds string storage to 4-byte boundaries, so callers must use defined lengths and avoid string overrun assumptions.

Test signals: adapter attribute queries should classify mezzanine cards, prototypes, port count, and speed correctly for known card types. VPD parsing should validate signatures, vendor tags, and length/checksum before display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_mfg_comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_status.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_status.h

Purpose: defines the shared BFA status code enum returned by IOC, flash, CEE, diagnostics, firmware, and higher-level management APIs.

Important APIs/types/functions: `enum bfa_status` enumerates `BFA_STATUS_OK` through `BFA_STATUS_MAX`, including common errors (`FAILED`, `EINVAL`, `ENOMEM`, `DEVBUSY`, `IOC_FAILURE`, `IOC_NON_OP`), flash errors, link/port errors, CNA/team/VLAN errors, boot/firmware errors, and many domain-specific management statuses. `enum bfa_eproto_status` defines protocol error sub-status values.

Control flow: no executable flow. Other modules switch on or return these values to report asynchronous and synchronous API outcomes. For this subset, `bfa_cee.c` returns `IOC_FAILURE`/`DEVBUSY` and callback statuses, while `bfa_ioc.c` returns or stores IOC/flash-related statuses.

State and persistence behavior: no state. Numeric values are an ABI-like contract across driver modules, firmware-adjacent code, and any tooling that decodes status numbers.

Dependencies and integration points: standalone header included by `bfa_defs.h` and then widely by IOC/CEE/flash definitions and implementations.

Risks: renumbering values can break log decoding, userspace tooling, or firmware-aligned assumptions. Comments mention auto-generated error messages, so comment formatting may matter to external generators even though no generator is present in this file.

Test signals: compile-time coverage from all users, plus runtime paths returning expected values for busy, invalid length, IOC non-operational, firmware mismatch, and flash failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc.c

Purpose: implements the BNA driver's IOC (I/O Controller) lifecycle, firmware boot/version management, mailbox transport, heartbeat failure recovery, debug firmware trace capture, adapter attribute reporting, and flash partition operations. It is the main control plane between the Linux driver and BR-series adapter firmware.

Important APIs/types/functions: public IOC APIs include `bfa_nw_ioc_attach`, `bfa_nw_ioc_detach`, `bfa_nw_ioc_pci_init`, `bfa_nw_ioc_meminfo`, `bfa_nw_ioc_mem_claim`, `bfa_nw_ioc_enable`, `bfa_nw_ioc_disable`, `bfa_nw_ioc_mbox_queue`, `bfa_nw_ioc_mbox_isr`, `bfa_nw_ioc_mbox_regisr`, `bfa_nw_ioc_error_isr`, `bfa_nw_ioc_is_disabled`, `bfa_nw_ioc_is_operational`, `bfa_nw_ioc_get_attr`, `bfa_nw_ioc_notify_register`, `bfa_nw_ioc_fwver_get`, `bfa_nw_ioc_fwver_cmp`, `bfa_nw_ioc_get_mac`, debug trace APIs, timeout APIs, and semaphore helpers. Public flash APIs include `bfa_nw_flash_meminfo`, `bfa_nw_flash_attach`, `bfa_nw_flash_memclaim`, `bfa_nw_flash_get_attr`, `bfa_nw_flash_update_part`, and `bfa_nw_flash_read_part`. Major internal groups are IOC FSM handlers, IOCPF FSM handlers, hardware semaphore/LMEM/LPU helpers, firmware version comparison, flash raw-read helpers, mailbox send/get/dispatch, heartbeat monitor/recovery, and adapter-attribute formatting.

Control flow: `bfa_nw_ioc_attach` initializes mailbox/notify queues and enters reset. `bfa_nw_ioc_pci_init` selects CT/CT2 hardware interfaces and port personality from PCI IDs/subsystem/class. `bfa_nw_ioc_enable` sends `IOC_E_ENABLE`, driving the IOC FSM from reset to enabling, while the IOCPF FSM checks firmware compatibility, obtains hardware and firmware locks, joins synchronization, initializes hardware/firmware if needed, sends enable, and reports `IOC_E_ENABLED`. IOC then requests attributes and enters operational state after `BFI_IOC_I2H_GETATTR_REPLY`. Operational state starts a heartbeat timer, polls mailbox progress, and transitions to failure/retry or fail on heartbeat/hardware errors. Disable drives firmware disable, synchronization leave, mailbox flush, callbacks, and disabled notification. Mailbox ISR reads LPU messages, dispatches IOC messages internally, and dispatches other message classes to registered handlers such as CEE and flash.

State and persistence behavior: `struct bfa_ioc` owns runtime FSM pointers, PCI identity, timers, heartbeat count, notification queue, debug trace buffer, firmware/adapter attribute DMA memory, mailbox queue/handlers, hardware register pointers, ASIC/personality state, port mode/capability, and stats. Persistent or semi-persistent adapter state is accessed through firmware image headers in SMEM, flash firmware image at `BFA_FLASH_PART_FWIMG_ADDR`, manufacturing/VPD data in IOC attributes, and flash partitions. Firmware version comparison chooses between running SMEM firmware, embedded driver image chunks from `cna_fwimg.c`, and flash firmware. Debug trace capture can persist a saved firmware trace in driver memory after failure.

Dependencies and integration points: includes `bfa_ioc.h`, `bfi_reg.h`, and `bfa_defs.h`. It relies on hardware-specific hooks installed by `bfa_nw_ioc_set_ct_hwif`/`bfa_nw_ioc_set_ct2_hwif`, firmware image providers `bfa_cb_image_get_chunk`/`bfa_cb_image_get_size`, BFI mailbox definitions, Linux timers, MMIO accessors, byte-order helpers, PCI IDs, linked-list APIs, and callback functions supplied by the BNA driver. It is the shared service used by CEE, flash, message queue, netdev, ethtool, and debugfs code.

Risks: the FSMs use `BUG_ON`/`bfa_sm_fault` for invalid events, so unexpected firmware messages or bad sequencing may panic. Hardware semaphore handling and synchronization span multiple PCI functions; lock release bugs can wedge firmware initialization. Firmware version selection is subtle: incompatible or older SMEM firmware is rejected, flash can supersede embedded firmware, and byte-swapped headers are compared. Raw flash reads use polling and fixed timeouts; wrong offsets or lengths can fail firmware selection, while write APIs must avoid protected manufacturing partitions. Mailbox queuing assumes caller serialization and silently drops queued command callbacks on flush. Heartbeat recovery can auto-reboot firmware unless disabled globally, affecting in-flight clients.

Test signals: validate probe/enable/disable for CT and CT2 devices, firmware mismatch and flash-better-than-driver paths, IOC timeout and heartbeat-failure recovery, mailbox dispatch for IOC/CEE/flash classes, attribute conversion and `bfa_nw_ioc_get_attr`, flash query/read/write chunking with IOC failure cancellation, debug trace capture after failure, and semaphore timeout/hardware mapping error paths. Build tests should link with `bfa_ioc_ct.o` and `cna_fwimg.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc.h

Purpose: public header for BNA IOC, mailbox, DMA, hardware-interface, notification, timeout, firmware-image, and flash service APIs.

Important APIs/types/functions: key constants include `BFA_IOC_TOV`, `BFA_IOC_HWSEM_TOV`, `BFA_IOC_HB_TOV`, `BFA_IOC_POLL_TOV`, `BNA_DBG_FWTRC_LEN`, `BFA_DMA_ALIGN_SZ`, SMEM sizes, and flash chunk helpers. Key types are `struct bfa_pcidev`, `struct bfa_dma`, `struct bfa_ioc_regs`, `struct bfa_mbox_cmd`, `struct bfa_ioc_mbox_mod`, callback typedefs and `struct bfa_ioc_cbfn`, `enum bfa_ioc_event`, `struct bfa_ioc_notify`, `struct bfa_iocpf`, `struct bfa_ioc`, `struct bfa_ioc_hwif`, `struct bfa_flash`, and `bfa_cb_flash`. Inline helpers set DMA addresses in BFI big-endian format via `bfa_dma_be_addr_set` and `bfa_alen_set`.

Control flow: consumers attach and initialize IOC state, provide PCI info, claim DMA memory, enable/disable IOC, register mailbox handlers/notifications, and service interrupts/timeouts by calling the declared functions. Hardware-specific code fills `struct bfa_ioc_hwif`; common code invokes those hooks for PLL init, register mapping, firmware locks, synchronization, failure notification, and firmware-state access. Flash callers attach, claim DMA memory, then issue asynchronous query/read/update operations with callbacks.

State and persistence behavior: `struct bfa_ioc` describes all runtime IOC state, including timers, hardware register mappings, firmware attributes, notification queues, mailbox handlers, ASIC/port configuration, and adapter capabilities. `struct bfa_flash` tracks an asynchronous flash operation, DMA bounce buffer, partition/offset/residue, callback, and IOC notification node. Persistent state is accessed through firmware/flash APIs but not stored by the header itself.

Dependencies and integration points: includes `bfa_cs.h` for FSM support, `bfi.h` for firmware message contracts, and `cna.h` for shared driver/kernel definitions. The declarations are used by `bfa_ioc.c`, hardware-specific IOC implementation files, CEE, flash users, BNA netdev code, and firmware image providers.

Risks: this header exposes internal state and hardware hooks widely, so module code can mutate fields without API guards. DMA address helpers intentionally encode addresses for firmware; using normal CPU endian values would break mailbox DMA. Timer constants define recovery behavior and can affect firmware boot reliability. The `bfa_ioc_hwif` contract must be completely populated for each ASIC generation or IOC operations will dereference null hooks.

Test signals: compile with CT and CT2 hardware backends, exercise IOC attach/pci-init/mem-claim/enable/disable, register a mailbox class and verify dispatch, and run flash/CEE clients through IOC failure notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc.h -->
