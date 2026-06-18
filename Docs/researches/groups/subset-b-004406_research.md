# subset-b-004406 Research

Grouped research for Chelsio VF networking and inline crypto files. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/sge.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/sge.c

## Purpose
Implements the Chelsio T4/T5/T6 SR-IOV VF Scatter Gather Engine data path: Ethernet TX submission, RX response processing, free-list refill, interrupt/NAPI handling, queue allocation/freeing, and SGE timer maintenance. It is the VF driver's high-throughput DMA ring owner and bridges Linux `sk_buff`/NAPI/netdev queues to Chelsio firmware work requests and hardware doorbells.

## Important APIs, Types, And Functions
Internal descriptor state is represented by `struct tx_sw_desc` for retained TX skbs/SGLs and `struct rx_sw_desc` for RX page, DMA address, and low-bit flags (`RX_LARGE_BUF`, `RX_UNMAPPED_BUF`). Helper APIs include `txq_avail()`, `fl_cap()`, `fl_starving()`, `map_skb()`, `unmap_sgl()`, `free_tx_desc()`, `refill_fl()`, `alloc_ring()`, `sgl_len()`, `flits_to_desc()`, `write_sgl()`, `ring_tx_db()`, and `ring_fl_db()`.

Exported driver entry points are `t4vf_eth_xmit()`, `t4vf_ethrx_handler()`, `t4vf_sge_intr_msix()`, `t4vf_intr_handler()`, `t4vf_sge_alloc_rxq()`, `t4vf_sge_alloc_eth_txq()`, `t4vf_free_sge_resources()`, `t4vf_sge_start()`, `t4vf_sge_stop()`, and `t4vf_sge_init()`. These are called by the surrounding cxgb4vf adapter setup, netdev operations, interrupt setup, and teardown paths.

## Control Flow
TX starts in `t4vf_eth_xmit()`: it validates packet size and MTU, chooses the queue from `skb_get_queue_mapping()`, inserts the VF VLAN tag if required, reclaims completed descriptors, computes firmware work-request flits, checks credits, maps the skb for DMA, builds `fw_eth_tx_pkt_vm_wr` plus LSO or normal `cpl_tx_pkt_core`, optionally adds checksum/VLAN controls, writes a DSGL, records the skb in the last descriptor, advances producer state, updates netdev TX timestamp, and rings the TX doorbell. Queue pressure stops the netdev subqueue and requests firmware egress queue updates.

RX flows through `napi_rx_handler()` into `process_responses()`. The response loop checks generation bits, distinguishes FL-buffer packet responses from CPL-only messages, constructs a `pkt_gl` gather list from free-list pages, syncs the final buffer for CPU access, calls the response queue handler, advances response descriptors, and refills the free list when enough space is available. `t4vf_ethrx_handler()` converts packet gather lists to skbs, chooses GRO for good TCP packets with RX checksum and GRO enabled, otherwise builds a normal skb, sets checksum/VLAN metadata, and hands it to `netif_receive_skb()`.

Interrupt flow is split between MSI-X and MSI. MSI-X schedules the target response queue NAPI directly. MSI uses `process_intrq()` to process forwarded interrupt messages from an interrupt queue, map ingress queue IDs back through `s->ingr_map`, and schedule NAPI on the real response queue.

Queue allocation uses firmware mailbox commands inline in this Linux-facing SGE layer. `t4vf_sge_alloc_rxq()` allocates coherent response/free-list rings, fills `FW_IQ_CMD`, registers NAPI, stores absolute/context IDs, initializes BAR2 doorbell addresses, and pre-fills FLs. `t4vf_sge_alloc_eth_txq()` allocates coherent TX rings and software descriptors, sends `FW_EQ_ETH_CMD`, then initializes TX counters and queue identifiers.

## State And Persistence
Persistent runtime state lives in `adapter->sge`, per-queue `pidx/cidx/in_use/gen/offset`, DMA coherent rings, software descriptor arrays, free-list page references, NAPI state, timers, and netdev queue stop/restart counters. The file does not persist across reboot; all state is reconstructed during device open/reset. DMA ownership is carefully tracked: TX skbs are retained until hardware completion; RX page ownership is transferred to skbs via page refs, unmapped from DMA before CPU use, and restored on handler backpressure.

Timers provide recovery state: `sge_rx_timer_cb()` tracks starving free lists via `starving_fl` bitmaps and schedules NAPI for refill, while `sge_tx_timer_cb()` periodically reclaims completed TX descriptors to avoid stalls when no new traffic arrives.

## Dependencies And Integration Points
The file depends on Linux networking/DMA/NAPI APIs, Chelsio firmware structures from `t4fw_api.h`, CPL messages from `t4_msg.h`, register/value definitions from the PF common headers, and cxgb4vf common helpers in `t4vf_common.h`/`t4vf_defs.h`. It calls `t4vf_wr_mbox()`, `t4vf_bar2_sge_qregs()`, `t4vf_fl_pkt_align()`, `t4vf_iq_free()`, and `t4vf_eth_eq_free()` from `t4vf_hw.c`. It integrates upward with netdev TX, RX handlers, MSI/MSI-X interrupt registration, adapter open/close, and ethtool/debug counters through queue stats.

## Risks
Ring wrap handling is complex in `write_sgl()`, `unmap_sgl()`, inline copy paths, and BAR2 write-combining doorbells; off-by-one errors can corrupt descriptors or leak DMA mappings. RX free-list low-bit encoding must remain compatible with hardware buffer-size bits. Firmware capability differences between T4/T5/T6 affect doorbell fields, burst sizes, status-page lengths, and packet alignment. Memory pressure paths rely on starving-bit recovery and NAPI rescheduling, so refill regressions can deadlock RX. TX reclaim policy intentionally delays skb destruction for performance, which makes the timer important for sparse traffic workloads.

## Test Signals
Useful signals include successful probe/open with SGE parameter validation, TX/RX traffic under TSO/checksum/VLAN/GRO, queue stop/restart counters, absence of DMA API warnings, NAPI budget behavior, pktgen or sparse UDP tests for TX timer reclaim, low-memory RX refill tests, MSI and MSI-X interrupt modes, T4/T5/T6 BAR2 fallback coverage, and firmware mailbox queue allocation/free error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/sge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_common.h

## Purpose
Defines the VF common interface between cxgb4vf OS-specific code, SGE code, and firmware/hardware access code. It centralizes chip identity encoding, adapter parameter structures, link state representation, RSS/VF resource models, mailbox logging structures, and prototypes for firmware mailbox operations.

## Important APIs, Types, And Functions
The header defines chip helpers (`CHELSIO_CHIP_CODE`, `CHELSIO_CHIP_VERSION`, `CHELSIO_PCI_ID_VER`, `is_t4()`), firmware length macro `FW_LEN16()`, and public data structures: `t4vf_port_stats`, `link_config`, `dev_params`, `sge_params`, `vpd_params`, `arch_specific_params`, `rss_params`, `rss_vi_config`, `vf_resources`, `adapter_params`, `mbox_cmd`, and `mbox_cmd_log`.

Inline utilities include `is_x_10g_port()`, `mbox_cmd_log_entry()`, `for_each_port`, core-clock conversion helpers, `t4vf_wr_mbox()`, `t4vf_wr_mbox_ns()`, and `hash_mac_addr()`. Function declarations expose the hardware layer implemented primarily in `t4vf_hw.c` and consumed by adapter setup, SGE, MAC/VLAN/RSS operations, and link handling.

## Control Flow
This header has no executable control flow beyond inlines, but it shapes driver initialization. Adapter setup fills `adapter_params`; SGE init reads `params.sge`; port init fills `link_config`; mailbox users call `t4vf_wr_mbox()` or the non-sleeping wrapper; address-filter management uses `hash_mac_addr()` when exact filters are unavailable. The declared functions form the VF lifecycle: wait for readiness, prepare adapter, query resources/SGE/VPD/device/RSS, allocate/enable/free VIs, configure RX mode/MAC filters/RSS, allocate/free queues, and process firmware replies.

## State And Persistence
The state modeled here is per-adapter runtime state stored inside `struct adapter` after including `adapter.h`. It is not persisted externally. The mailbox log is a ring buffer in memory with host-endian command snapshots, jiffies timestamps, sequence numbers, and access/execute times. Link state tracks capabilities, advertised capabilities, peer capabilities, actual speed/FEC/pause, autonegotiation, and link-down reason.

## Dependencies And Integration Points
The header includes PF common `t4_hw.h` and firmware API definitions from `t4fw_api.h`, then includes local `adapter.h`, making it a cross-module contract. Its structures are consumed by `sge.c`, `t4vf_hw.c`, adapter management, ethtool-style statistics, and OS notification hooks such as `t4vf_os_link_changed()`. It also encodes VF-specific constraints such as PF-provisioned SGE parameters and VF resource caps.

## Risks
Because this is a shared contract header, field layout or semantic changes can break multiple compilation units. `hash_mac_addr()` must match hardware inexact-filter hashing. Clock conversion helpers depend on valid `vpd.cclk`. `is_x_10g_port()` and link capability masks assume firmware capability encodings. Mailbox command logging assumes `MBOX_LEN` matches firmware mailbox size expectations.

## Test Signals
Compilation across cxgb4vf files is the first signal. Runtime signals include successful parameter discovery, correct ethtool link reporting, correct MAC hash fallback behavior, stable mailbox debug output, and working T4/T5/T6 probe paths using the same `adapter_params` contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_defs.h

## Purpose
Defines the VF-visible Chelsio register map and slice-to-module mapping constants used by the VF driver to address SGE, MPS, PL, CIM, and mailbox data registers. It provides the address constants used by mailbox, readiness, interrupt, and doorbell code.

## Important APIs, Types, And Functions
The file exposes base addresses (`T4VF_SGE_BASE_ADDR`, `T4VF_MPS_BASE_ADDR`, `T4VF_PL_BASE_ADDR`, `T4VF_MBDATA_BASE_ADDR`, `T6VF_MBDATA_BASE_ADDR`, `T4VF_CIM_BASE_ADDR`), register-map bounds, per-module VF register offsets (`SGE_VF_KDOORBELL`, `SGE_VF_GTS`, `PL_VF_WHOAMI`, `CIM_VF_EXT_MAILBOX_CTRL`, etc.), the `T4VF_MOD_MAP()` macro, and `NUM_CIM_VF_MAILBOX_DATA_INSTANCES`.

## Control Flow
There is no runtime control flow. These constants are compiled into hardware access paths. `sge.c` uses SGE VF doorbell/GTS offsets for queue updates; `t4vf_hw.c` uses PL `WHOAMI` for readiness and CIM mailbox registers for firmware command exchange. The compile-time `#error` enforces that the VF mailbox base matches the PF CIM mailbox data convention.

## State And Persistence
No state is stored here. The definitions describe the fixed or PF-programmed VF register aperture through which runtime driver state is synchronized with the adapter.

## Dependencies And Integration Points
The header depends on `../cxgb4/t4_regs.h` for PF register constants and is included by `sge.c` and `t4vf_hw.c`. It integrates directly with the hardware/firmware ABI: wrong values affect register reads, mailbox writes, queue doorbells, and interrupt rearming.

## Risks
Register-map constants are high-risk because errors produce silent device misprogramming. T6 mailbox data moved from `T4VF_MBDATA_BASE_ADDR` to `T6VF_MBDATA_BASE_ADDR`, so chip-version selection in users must stay aligned. The trailing include guard comment appears misspelled, but the actual guard macro is consistent and functional.

## Test Signals
Probe readiness via `PL_VF_WHOAMI`, successful mailbox commands, queue doorbell operation, and interrupt rearming are practical integration tests. Build-time enforcement of mailbox-base equivalence provides a static signal for T4/T5 register compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_hw.c

## Purpose
Implements VF firmware/hardware common operations: device readiness, serialized mailbox command transport, adapter/port/resource discovery, SGE parameter queries, BAR2 queue-register mapping, RSS and VI programming, MAC/VLAN ACL/filter commands, statistics collection, queue free commands, link-status interpretation, and asynchronous firmware reply handling.

## Important APIs, Types, And Functions
Core mailbox routines are `t4vf_wait_dev_ready()`, `get_mbox_rpl()`, `t4vf_record_mbox()`, and `t4vf_wr_mbox_core()`. Link capability helpers include `fwcaps16_to_caps32()`, `fwcap_to_cc_pause()`, `fwcap_to_cc_fec()`, `fwcap_to_speed()`, `fwcap_to_fwspeed()`, and `init_link_config()`.

Public hardware APIs include `t4vf_port_init()`, `t4vf_fw_reset()`, `t4vf_set_params()`, `t4vf_fl_pkt_align()`, `t4vf_bar2_sge_qregs()`, `t4vf_get_pf_from_vf()`, `t4vf_get_sge_params()`, `t4vf_get_vpd_params()`, `t4vf_get_dev_params()`, `t4vf_get_rss_glb_config()`, `t4vf_get_vfres()`, RSS VI read/write/range configuration, VI allocate/free/enable/identify, RX mode control, MAC filter allocation/free/change/hash programming, `t4vf_get_port_stats()`, `t4vf_iq_free()`, `t4vf_eth_eq_free()`, `t4vf_update_port_info()`, `t4vf_handle_fw_rpl()`, `t4vf_prep_adapter()`, and VF MAC/VLAN ACL reads.

## Control Flow
Initialization begins with `t4vf_prep_adapter()`, which waits for the VF register aperture, infers chip generation from PCI ID, sets default debug-safe parameters, and records architecture-specific values. Later setup calls parameter discovery routines through mailbox commands. `t4vf_wr_mbox_core()` serializes callers on `adapter->mlist`, waits for the caller to reach the front, verifies driver ownership of the mailbox, writes big-endian firmware command words to VF mailbox data registers, flushes cross-domain writes with readbacks, transfers ownership to firmware, polls with sleep or spin delays, copies replies, logs non-stat commands, and returns negative firmware status.

Port initialization negotiates whether firmware supports 32-bit port capabilities, reads VI information, sets the OS MAC address, optionally reads physical port info when VF read caps allow it, and initializes software link state. Runtime link updates flow through `t4vf_update_port_info()` or asynchronous `t4vf_handle_fw_rpl()`, then `t4vf_handle_get_port_info()` translates firmware fields, detects module/link changes, updates `link_config`, logs link-down reasons, and calls OS notification hooks.

RSS, VI, MAC, and queue helper functions are mostly firmware command builders. They translate host-native structures into firmware command layouts, split large operations where firmware accepts limited entries, and convert replies back into CPU-endian driver state.

## State And Persistence
State is stored in `adapter->params`, `port_info`, the mailbox queue/list/log, VF resource caps, RSS configuration, exact/inexact MAC filter state as known by firmware, and link configuration. The hardware/firmware owns durable state only for the lifetime of the VF or until PF/firmware reset; the driver reconstructs local state during probe/reinit. Mailbox log entries are an in-memory ring useful for debugging recent firmware interactions.

## Dependencies And Integration Points
This file depends on Linux PCI/ethtool headers, Chelsio VF definitions, PF common register/value definitions, and firmware API structs. It is consumed by SGE allocation/free paths, adapter probe/open, ethtool link/stat code, netdev address/RSS/RX-mode operations, and OS callbacks (`t4_os_set_hw_addr()`, `t4vf_os_link_changed()`, `t4vf_os_portmod_changed()`). It also integrates with PF-provisioned VF resources and firmware capability differences across T4/T5/T6.

## Risks
Mailbox serialization and ownership are critical; races or missing flushes can corrupt firmware commands. Several functions assume firmware command ABI limits such as seven params per query/set, 32 RSS table entries per command, and exact MAC command array sizes. Capability translation must correctly handle old 16-bit and new 32-bit firmware formats. BAR2 queue-register calculations are chip and PF-page-layout dependent. Error handling must leave queue/MAC/RSS state consistent when firmware partially accepts operations, especially MAC filter allocation where `-ENOMEM` can still return partial success.

## Test Signals
Strong signals include successful probe against T4, T5, and T6 VFs; mailbox debug logs with sane access/execute timings; correct fallback for old firmware lacking capabilities; successful SGE parameter discovery and BAR2 doorbells; ethtool link/speed/FEC/pause updates; RSS indirection programming; MAC exact/hash fallback behavior; VI allocation/free and RX-mode changes; port statistics reads; and firmware async link event handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/Kconfig

## Purpose
Defines Kconfig switches for Chelsio inline crypto support under the Chelsio T4 driver family. It gates the inline TLS TOE driver, IPsec XFRM TX crypto offload, and kernel TLS device offload subdrivers.

## Important APIs, Types, And Functions
The public build symbols are `CHELSIO_INLINE_CRYPTO`, `CRYPTO_DEV_CHELSIO_TLS`, `CHELSIO_IPSEC_INLINE`, and `CHELSIO_TLS_DEVICE`. Their dependencies encode required kernel subsystems: `CHELSIO_T4`, `TLS`, `TLS_TOE`, `XFRM_OFFLOAD`, `INET_ESP_OFFLOAD || INET6_ESP_OFFLOAD`, and `TLS_DEVICE`. `CHELSIO_TLS_DEVICE` selects `CRYPTO_LIB_AES`.

## Control Flow
The file is declarative. When `CHELSIO_INLINE_CRYPTO` is enabled, the nested symbols become visible. The selected tristate values drive Makefile recursion into `chtls/`, `ch_ipsec/`, and `ch_ktls/`.

## State And Persistence
Kconfig state is persisted in the kernel build configuration (`.config`) and determines whether code is built-in, modular, or omitted. It has no runtime state.

## Dependencies And Integration Points
The parent Chelsio Kconfig sources this file from `drivers/net/ethernet/chelsio/Kconfig`. The symbols are consumed by `inline_crypto/Makefile` and the subdirectory Makefiles. Runtime integration is with cxgb4 ULD registration, xfrmdev operations, TLS TOE, and TLS device offload.

## Risks
Dependency mistakes can expose drivers without required kernel interfaces or hide valid combinations. The top-level `CHELSIO_INLINE_CRYPTO` is `bool` and defaults to yes when `CHELSIO_T4` is enabled, so downstream tristates still control actual module builds. Feature naming overlaps TLS TOE (`chtls`) and kernel TLS device (`ch_ktls`), making config/test matrices easy to confuse.

## Test Signals
Kernel config tests should cover disabled inline crypto, each subdriver as module, and built-in combinations. Build signals include correct object recursion and absence of missing symbol errors for TLS/XFRM/AES dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/Makefile

## Purpose
Routes Chelsio inline crypto build symbols to the appropriate subdirectories.

## Important APIs, Types, And Functions
The Makefile maps `CONFIG_CRYPTO_DEV_CHELSIO_TLS` to `chtls/`, `CONFIG_CHELSIO_IPSEC_INLINE` to `ch_ipsec/`, and `CONFIG_CHELSIO_TLS_DEVICE` to `ch_ktls/`.

## Control Flow
Kbuild evaluates the `obj-$(CONFIG_...)` assignments and descends into enabled subdirectories. There is no runtime behavior.

## State And Persistence
Build state is represented by generated kernel objects/modules under the active kernel build tree. The source file itself persists only build routing.

## Dependencies And Integration Points
This Makefile is reached from `drivers/net/ethernet/chelsio/Makefile` when `CONFIG_CHELSIO_INLINE_CRYPTO` is enabled. It integrates with subdirectory Makefiles that set include paths and module object composition.

## Risks
Wrong symbol-to-directory mapping would silently omit or include the wrong crypto subdriver. Because the top-level inline crypto switch is separate from these tristates, build coverage must include all combinations.

## Test Signals
`make M=drivers/net/ethernet/chelsio/inline_crypto` with each config symbol enabled should build the expected module directories and no others.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/Makefile

## Purpose
Builds the Chelsio inline IPsec module from `chcr_ipsec.o` and supplies include paths for cxgb4 and Chelsio crypto headers.

## Important APIs, Types, And Functions
The Makefile sets `ccflags-y` to include `drivers/net/ethernet/chelsio/cxgb4` and `drivers/crypto/chelsio`, then maps `CONFIG_CHELSIO_IPSEC_INLINE` to module `ch_ipsec.o` with `ch_ipsec-objs := chcr_ipsec.o`.

## Control Flow
Kbuild compiles `chcr_ipsec.c` into the `ch_ipsec` module or built-in object depending on the tristate value. There is no runtime control flow in this file.

## State And Persistence
State is limited to build artifacts. The include path choice persists the source-level dependency on cxgb4 ULD and Chelsio crypto key-context helper headers.

## Dependencies And Integration Points
This build file integrates the IPsec source with cxgb4 symbols and crypto helper headers such as `chcr_core.h`, `chcr_algo.h`, and `chcr_crypto.h`. It is included via `inline_crypto/Makefile`.

## Risks
Include path drift can break compilation if cxgb4 or drivers/crypto/chelsio headers move. Module naming must remain aligned with Kconfig help text and ULD registration name.

## Test Signals
Building `CONFIG_CHELSIO_IPSEC_INLINE=m` should produce `ch_ipsec.ko`; built-in mode should link `chcr_ipsec.o` without unresolved cxgb4/crypto symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/chcr_ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/chcr_ipsec.c

## Purpose
Implements Chelsio T6 inline IPsec ESP TX crypto offload as a cxgb4 upper-layer driver. It registers xfrmdev callbacks for SA lifecycle management and a ULD TX handler that converts outbound ESP skbs into Chelsio crypto work requests using AES-GCM key context and CPL security PDU descriptors.

## Important APIs, Types, And Functions
The module registers `ch_ipsec_uld_info` with `cxgb4_register_uld(CXGB4_ULD_IPSEC, ...)` and exposes xfrmdev operations through `ch_ipsec_xfrmdev_ops`. Device context is tracked in global `uld_ctx_list` under `dev_mutex`.

Key functions include `ch_ipsec_uld_add()`, `ch_ipsec_uld_state_change()`, `ch_ipsec_xfrm_add_state()`, `ch_ipsec_xfrm_del_state()`, `ch_ipsec_xfrm_free_state()`, `ch_ipsec_advance_esn_state()`, `ch_ipsec_setauthsize()`, `ch_ipsec_setkey()`, `calc_tx_sec_flits()`, `copy_esn_pktxt()`, `copy_cpltx_pktxt()`, `copy_key_cpltx_pktxt()`, `ch_ipsec_crypto_wreq()`, and `ch_ipsec_xmit()`.

## Control Flow
Module init registers the ULD. When cxgb4 attaches, `ch_ipsec_uld_add()` stores low-level adapter information, and state changes add/remove the context from the global list. On xfrm state add, `ch_ipsec_xfrm_add_state()` validates that the SA is ESP, IPv4/IPv6, transport/tunnel, AEAD AES-GCM with supported ICV/key lengths, no encapsulation/compression/TFC padding, `seqiv` geniv, and crypto offload type. It then pins the module, allocates `ipsec_sa_entry`, derives auth truncation mode, detects ESN, extracts key/salt, computes GHASH H by AES encrypting zero, builds the hardware key context header, and stores the SA pointer in `x->xso.offload_handle`.

Outbound data enters `ch_ipsec_xmit()` from the cxgb4 ULD TX hook. It validates the offload handle and single secpath, reclaims completed TX descriptors, calculates flits/descriptor credits, maps non-immediate skbs, builds a `FW_ULPTX_WR` with `CPL_TX_SEC_PDU`, copies key context, CPL TX packet context, optional ESN AAD/IV, then either inlines packet bytes or writes an SGL. It records retained skbs in TX software descriptors, advances queue producer state, and rings the cxgb4 TX doorbell.

Module exit removes live contexts from `uld_ctx_list`, resets adapter IPsec stats, frees ULD contexts, and unregisters the ULD.

## State And Persistence
Per-SA state lives in `struct ipsec_sa_entry` attached to `xfrm_state.xso.offload_handle`; it stores auth mode, ESN flag, encryption key length, key-context length, auth tag size, key-context header, salt, and key plus GHASH H material. Per-device state is the ULD context list and cxgb4 adapter stats (`ch_ipsec_stats.ipsec_cnt`). TX queue state is shared with cxgb4 SGE rings and software descriptors. State is in-memory only and is freed on xfrm state free or module exit.

## Dependencies And Integration Points
The file depends on Linux xfrm/ESP offload APIs, crypto AES/hash helpers, cxgb4 ULD registration, cxgb4 SGE helper exports (`cxgb4_reclaim_completed_tx()`, `cxgb4_map_skb()`, `cxgb4_write_sgl()`, `cxgb4_inline_tx_skb()`, `cxgb4_ring_tx_db()`), Chelsio CPL/ULPTX firmware structures, and crypto key-context macros from drivers/crypto/chelsio headers. cxgb4 main netdev xfrmdev ops delegate SA lifecycle calls to this ULD, and cxgb4 SGE dispatches IPsec TX skbs to `tx_handler`.

## Risks
SA validation is narrow: only AES-GCM key lengths 128/256 plus 32-bit salt and ICV 96/128 are accepted, while `ch_ipsec_setauthsize()` has an ICV_8 case that cannot be reached through current validation. `ch_ipsec_xfrm_add_state()` ignores the return from `ch_ipsec_setkey()`, which risks installing an SA with incomplete key context if key setup fails. ESN handling builds synthetic AAD/IV data and adjusts cipher offsets; offset mistakes can produce invalid packets. TX ring wrap and immediate/SGL paths are sensitive to descriptor math. `ch_ipsec_uld_state_change()` removes list entries without taking `dev_mutex` on down/detach paths, which is a concurrency point to review against cxgb4 ULD state-change serialization.

## Test Signals
Signals include module load/unload and ULD registration, xfrm state add rejection messages for unsupported algorithms/modes, successful AES-GCM ESP offload for IPv4/IPv6 transport and tunnel, ESN and non-ESN packet validation against a peer, TX ring pressure behavior, DMA API checks on mapped SGLs, `ip xfrm` offload lifecycle tests, adapter debugfs IPsec counter changes, and fallback behavior when offload handles are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/chcr_ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/chcr_ipsec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/chcr_ipsec.h

## Purpose
Defines the Chelsio inline IPsec module interface, module metadata, ULD context, IPsec work-request layout, ESN AAD/IV payload, and per-SA hardware key context state used by `chcr_ipsec.c`.

## Important APIs, Types, And Functions
The header declares module identity macros (`CHIPSEC_DRV_MODULE_NAME`, `CHIPSEC_DRV_VERSION`, `CHIPSEC_DRV_DESC`), `struct ipsec_uld_ctx`, `struct chcr_ipsec_req`, `struct chcr_ipsec_wr`, `ESN_IV_INSERT_OFFSET`, `struct chcr_ipsec_aadiv`, and `struct ipsec_sa_entry`.

`struct chcr_ipsec_req` embeds `ulp_txpkt`, `ulptx_idata`, `cpl_tx_sec_pdu`, and `_key_ctx` in the exact order emitted to hardware. `struct ipsec_sa_entry` stores hmac/auth control, ESN flag, encryption key length, key context length, auth size, key context header, salt, and key/GHASH material.

## Control Flow
No runtime control flow is defined here. The structures are populated by SA setup and TX work-request construction in `chcr_ipsec.c`.

## State And Persistence
`ipsec_uld_ctx` persists per attached cxgb4 lower-layer device while the ULD is active. `ipsec_sa_entry` persists per offloaded xfrm state until `xdo_dev_state_free`. Both are in-memory kernel objects; no external persistence exists.

## Dependencies And Integration Points
The header pulls in cxgb4 hardware, message, and ULD headers plus Chelsio crypto core/algo/header definitions. It is tightly coupled to firmware CPL/ULPTX layout and to the crypto helper definition of `_key_ctx`, `MAX_SALT`, AES key sizes, and key-context macros.

## Risks
Structure layout must match hardware work-request expectations; reordering or padding changes are unsafe. The key buffer is sized as `2 * AES_MAX_KEY_SIZE`, which must remain large enough for padded AES key material plus GHASH H. Module version/name strings are used in logging and module metadata and should stay aligned with Kconfig/Makefile naming.

## Test Signals
Compilation with the cxgb4 and Chelsio crypto include paths is the primary static signal. Runtime validation comes indirectly from successful IPsec SA setup and packet encryption/decryption interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/chcr_ipsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/Makefile

## Purpose
Builds the Chelsio kernel TLS device-offload module from `chcr_ktls.o` with access to cxgb4 headers.

## Important APIs, Types, And Functions
The Makefile sets `ccflags-y` to include `drivers/net/ethernet/chelsio/cxgb4`, maps `CONFIG_CHELSIO_TLS_DEVICE` to `ch_ktls.o`, and sets `ch_ktls-objs := chcr_ktls.o`.

## Control Flow
Kbuild compiles and links the kTLS offload object when `CONFIG_CHELSIO_TLS_DEVICE` is enabled as built-in or module. There is no runtime logic.

## State And Persistence
State is limited to build artifacts. The file persists the module name and dependency on cxgb4 internal headers.

## Dependencies And Integration Points
It is reached from `inline_crypto/Makefile` and complements `inline_crypto/Kconfig`, whose `CHELSIO_TLS_DEVICE` symbol depends on TLS/TLS_DEVICE and selects AES crypto library support. Runtime integration is implemented in `chcr_ktls.c`, while `chcr_common.h` supplies shared helper definitions.

## Risks
The object mapping must stay aligned with the actual implementation file and Kconfig help text. Missing include paths would break access to cxgb4 queue and adapter structures used by kTLS offload.

## Test Signals
Building with `CONFIG_CHELSIO_TLS_DEVICE=m` should produce `ch_ktls.ko`; built-in mode should link without unresolved cxgb4/TLS symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_common.h

## Purpose
Provides shared Chelsio kTLS crypto constants, AES-GCM key-context layout, and small TX ring helper inlines used by the kernel TLS offload implementation.

## Important APIs, Types, And Functions
The header defines kTLS/crypto constants such as `CHCR_MAX_SALT`, key size selectors, cipher/auth modes, TLS/generic protocol versions, `AES_BLOCK_LEN`, and key-context bitfield macros. `struct ktls_key_ctx` models the hardware key context containing header, salt, IV/auth word, and AES-GCM key/tag-sized storage. `FILL_KEY_CTX_HDR()` builds the big-endian key context header.

Queue helper inlines are `chcr_copy_to_txd()`, `chcr_txq_avail()`, `chcr_txq_advance()`, `chcr_eth_txq_stop()`, `chcr_sgl_len()`, and `chcr_flits_to_desc()`.

## Control Flow
There is no standalone control flow. kTLS TX code calls these helpers while building hardware work requests. `chcr_copy_to_txd()` copies data into a TX descriptor ring with wrap-around handling and pads to a 16-byte boundary. The queue helpers compute credits, advance producer state, stop netdev queues, compute DSGL flits, and convert flits to TX descriptors.

## State And Persistence
The header does not own state. It manipulates caller-owned `sge_txq`/`sge_eth_txq` runtime fields (`in_use`, `pidx`, queue stop count) and produces key-context words embedded in TX work requests. TLS key material persists wherever the kTLS implementation stores `ktls_key_ctx`.

## Dependencies And Integration Points
It includes `cxgb4.h` for SGE queue structures and constants. It is used by `chcr_ktls.c` and must remain consistent with firmware `CPL_TX_SEC_PDU` expectations and Linux TLS AES-GCM key sizes. The helper logic mirrors similar SGE functions in cxgb4/cxgb4vf transmit paths.

## Risks
Descriptor wrap and padding in `chcr_copy_to_txd()` are correctness-critical. Key-context bitfield macros must match firmware ABI and endian expectations. `chcr_flits_to_desc()` warns on exceeding `SGE_MAX_WR_LEN / 8`, but callers must still prevent oversized work requests. The key array size assumes AES-GCM 128/256 material and tag sizing used by Linux TLS definitions.

## Test Signals
Build coverage for `chcr_ktls.c`, TLS device add/delete, encrypted TLS TX with 128-bit and 256-bit AES-GCM, descriptor wrap stress, queue stop/restart behavior, and hardware packet authentication/decryption by a peer are practical validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_common.h -->
