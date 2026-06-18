# subset-b-004501 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x550.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x550.c

## Purpose
`ixgbe_x550.c` is the hardware-specific operations layer for Intel ixgbe X550, X550EM_x, and x550em_a controllers. It plugs X550-specific MAC, PHY, EEPROM, I2C/link, firmware-host-interface, flow-control, SFP, reset, low-power, and malicious-driver-detection behavior into the generic ixgbe core through `struct ixgbe_info` tables at the end of the file.

## Important APIs, types, and functions
- Exported device descriptors: `ixgbe_X550_info`, `ixgbe_X550EM_x_info`, `ixgbe_x550em_x_fw_info`, `ixgbe_x550em_a_info`, and `ixgbe_x550em_a_fw_info` bind MAC type, invariant setup, operation tables, mailbox ops, and model values.
- Exported helpers: `ixgbe_set_fw_drv_ver_x550()`, `ixgbe_set_source_address_pruning_x550()`, `ixgbe_set_ethertype_anti_spoofing_x550()`, `ixgbe_enable_mdd_x550()`, `ixgbe_disable_mdd_x550()`, `ixgbe_restore_mdd_vf_x550()`, and `ixgbe_handle_mdd_x550()`.
- Operation tables: `mac_ops_X550`, `mac_ops_X550EM_x`, `mac_ops_X550EM_x_fw`, `mac_ops_x550em_a`, `mac_ops_x550em_a_fw`, EEPROM ops, PHY ops, and `link_ops_x550em_x`.
- Firmware PHY path: `ixgbe_fw_phy_activity()`, `ixgbe_get_phy_id_fw()`, `ixgbe_identify_phy_fw()`, `ixgbe_setup_fw_link()`, `ixgbe_reset_phy_fw()`, and `ixgbe_check_overtemp_fw()`.
- EEPROM path: host-interface read/write/buffer/checksum/update helpers around `FW_READ_SHADOW_RAM_CMD`, `FW_WRITE_SHADOW_RAM_CMD`, and `FW_SHADOW_RAM_DUMP_CMD`.
- Link and PHY paths: CS4227/CS4223 SFP support, IOSF sideband accessors, KR/iXFI/SFI/SGMII setup, external Base-T LASI interrupt handling, LPLU entry, MDIO clock setup, and X550EM reset.

## Control flow and integration
Probe-time code in the generic driver selects one exported `ixgbe_info` and calls its invariant function. The generic code then uses the operation tables in this file as virtual methods. `ixgbe_reset_hw_X550em()` is the central reset flow for embedded variants: stop adapter, clear pending TX, set MDIO speed, initialize and identify PHY ops, optionally un-stall external Base-T PHY firmware, configure SFP modules, reset PHY, choose MAC reset type based on link state and `force_full_reset`, reacquire permanent MAC address, initialize receive address registers, and restore mux/MDIO details.

Link setup is media dependent. Fiber/SFP uses SFP identification plus CS4227/CS4223 line-side programming. Copper Base-T may set an internal KR/iXFI path to match the external PHY. Backplane uses KR/KX advertisement and restart. Firmware-controlled PHYs marshal setup and status through `ixgbe_fw_phy_activity()` rather than direct MDIO register access.

## State and persistence behavior
The file mutates persistent hardware-facing state in `struct ixgbe_hw`: PHY type, PHY ID/revision, advertised speeds, EEE capabilities, semaphore masks, link address, MAC operation pointers, EEPROM word size/type, control word cache, management interface selection, permanent MAC, flow-control state, and `mac.set_lben`. It also writes persistent NVM shadow RAM and can trigger flash updates through firmware. Hardware registers affected include RX enable, spoofing controls, source address pruning bitmaps, IOSF sideband control/data, MDIO/PHY registers, ESDP mux bits, MDD registers, and WQBR queue-block registers.

## Dependencies
The implementation depends on ixgbe common, X540, mailbox, PHY, type, and register definitions plus Linux kernel primitives for delays, bit operations, endianness conversion, and MMIO. Major external integration points are firmware host-interface commands, MDIO, I2C combined transactions, CS4227/CS4223 retimers, port expanders, PF/VF virtualization registers, and generic ixgbe reset/link/EEPROM helper functions.

## Risks
- Semaphore and token paths are correctness-critical. Missed release paths can deadlock PHY, EEPROM, or I2C access across ports.
- Several flows intentionally ignore or overwrite earlier `status` values after later writes; regression tests should watch for lost errors in setup/reset sequences.
- Firmware PHY setup depends on strict command layout and endian conversion. Bad size, checksum, or retry behavior can silently prevent link.
- SFP and CS4227 support is highly variant-specific; wrong lane or slice calculations can affect another port.
- MDD queue-to-VF mapping depends on MRQC mode and queue grouping constants.

## Test signals
Useful signals include successful probe across all exported X550 variants, EEPROM checksum validate/update, link up/down on SFP, KR, SGMII, Base-T and firmware PHY devices, reset under active link and no-link cases, LASI over-temperature/link-change interrupts, source pruning and anti-spoofing behavior under SR-IOV, MDD detection/restoration with VFs, and fault injection for host-interface, IOSF, MDIO, and semaphore failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x550.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x550.h

## Purpose
This header exposes the small public surface of the X550-specific ixgbe implementation to the rest of the driver. It intentionally hides the large internal operation-table and PHY/link helper set from `ixgbe_x550.c`.

## Important APIs and types
- Includes `ixgbe_type.h` for `struct ixgbe_hw`, `u32`, and common ixgbe type definitions.
- Declares exported model values: `ixgbe_mvals_x550em_a`.
- Declares firmware driver-version reporting: `ixgbe_set_fw_drv_ver_x550()`.
- Declares SR-IOV filtering controls: `ixgbe_set_source_address_pruning_x550()` and `ixgbe_set_ethertype_anti_spoofing_x550()`.
- Declares malicious-driver-detection controls: enable, disable, restore one VF, and collect malicious VF bitmap.

## Control flow and integration
Other ixgbe compilation units include this header when they need to call X550-specific helper functions without depending on the private implementation. The prototypes mirror functions exported from `ixgbe_x550.c` and are used by shared SR-IOV, mailbox, or PF management paths.

## State and persistence behavior
The header itself has no state. Its functions operate on `struct ixgbe_hw` and write hardware state: firmware-visible driver version, PF/VF spoofing registers, source address pruning bitmaps, MDD enablement, and queue block/restore state.

## Dependencies
It depends on `ixgbe_type.h` and compile-time agreement with the operation implementations in `ixgbe_x550.c`.

## Risks
Prototype drift would break cross-file calls or hide ABI changes inside the driver. The public functions mostly touch virtualization and firmware-facing hardware state, so callers must pass valid VF/pool indices and a properly initialized `struct ixgbe_hw`.

## Test signals
Build coverage with X550 support enabled is the main header test. Runtime validation comes from SR-IOV anti-spoofing/source-pruning tests, MDD interrupt handling, and firmware driver-version reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x550.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_xsk.c

## Purpose
`ixgbe_xsk.c` implements AF_XDP zero-copy support for ixgbe. It binds an `xsk_buff_pool` to a queue, allocates user-memory-backed RX buffers, runs XDP on received frames, constructs SKBs for `XDP_PASS`, transmits AF_XDP descriptors on the XDP TX ring, and returns completed frames to the AF_XDP core.

## Important APIs, types, and functions
- Pool lookup/setup: `ixgbe_xsk_pool()`, `ixgbe_xsk_pool_setup()`, internal enable/disable helpers.
- RX allocation and cleaning: `ixgbe_alloc_rx_buffers_zc()`, `ixgbe_clean_rx_irq_zc()`, `ixgbe_xsk_clean_rx_ring()`.
- XDP execution: `ixgbe_run_xdp_zc()` handles `XDP_REDIRECT`, `XDP_TX`, `XDP_DROP`, `XDP_PASS`, and invalid/aborted actions.
- TX path: `ixgbe_xmit_zc()`, `ixgbe_clean_xdp_tx_irq()`, `ixgbe_xsk_clean_tx_ring()`, and `ixgbe_xsk_wakeup()`.
- External APIs used include `xsk_pool_dma_map()`, `xsk_buff_alloc()`, `xsk_tx_peek_desc()`, `xsk_tx_release()`, `xsk_tx_completed()`, `xdp_do_redirect()`, and NAPI wakeup helpers.

## Control flow and integration
Pool enable validates queue bounds, DMA maps the AF_XDP pool, disables the target ring if the interface is running, marks the queue in `adapter->af_xdp_zc_qps`, re-enables the ring, and wakes NAPI. Disable performs the inverse and unmaps DMA. RX refill pulls `xdp_buff` objects from the pool and posts their DMA addresses into hardware descriptors. RX cleaning reads completed descriptors, handles multi-buffer discard cases, syncs DMA for CPU, runs XDP, either redirects/transmits/drops/frees the buffer, or builds an SKB and passes it into the normal receive path.

TX zero-copy peeks user descriptors from the AF_XDP pool, syncs raw DMA for device, fills ixgbe advanced TX descriptors, advances `next_to_use`, rings the tail, and releases descriptors to the pool. TX completion distinguishes normal XDP frames from AF_XDP frames by `tx_bi->xdpf`; AF_XDP frames are counted and reported through `xsk_tx_completed()`.

## State and persistence behavior
Runtime state is stored in queue bitmaps, `rx_ring->xsk_pool`, ring descriptor arrays, `next_to_use`, `next_to_clean`, `rx_buffer_info[].xdp`, discard flags, `tx_buffer_info`, per-ring stats, and AF_XDP need-wakeup flags. No on-disk persistence exists, but DMA mappings and hardware descriptor state must stay synchronized across ring disable/enable and cleanup.

## Dependencies
The file depends on ixgbe ring/NAPI helpers, XDP/BPF APIs, AF_XDP socket driver APIs, DMA attributes, memory barriers, and netdev carrier/state helpers.

## Risks
- Queue validation must match both real RX/TX queue counts and XDP queue counts, or user memory can be bound to a wrong ring.
- Descriptor memory ordering is critical around RX writeback and tail updates.
- `XDP_PASS` copies UMEM-backed data into a new SKB; allocation failures must leave the pool and descriptor ring recoverable.
- Need-wakeup logic affects busy-poll/user wakeups and can cause stalls if set or cleared incorrectly.
- TX completion must not return AF_XDP frames through `xdp_return_frame()` or leak normal XDP frame DMA mappings.

## Test signals
Exercise AF_XDP zero-copy bind/unbind on running and stopped devices, RX `XDP_PASS`, `DROP`, `TX`, and `REDIRECT`, need-wakeup mode, TX completion and wakeup, queue bounds failures, interface reset while pools are attached, and stress runs that wrap ring indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/Makefile

## Purpose
This Makefile defines how the Intel 82599/X540/X550/E610 VF driver object is built by Kbuild.

## Important APIs and build rules
- `obj-$(CONFIG_IXGBEVF) += ixgbevf.o` builds the VF driver when the main config option is enabled.
- `ixgbevf-y := vf.o mbx.o ethtool.o ixgbevf_main.o` defines the always-linked objects.
- `ixgbevf-$(CONFIG_IXGBEVF_IPSEC) += ipsec.o` conditionally links IPsec offload support.

## Control flow and integration
Kbuild aggregates the listed objects into `ixgbevf.o`. Runtime entry points come from `ixgbevf_main.o`, with hardware support in `vf.o`, mailbox support in `mbx.o`, ethtool support in `ethtool.o`, and optional XFRM/IPsec offload in `ipsec.o`.

## State and persistence behavior
There is no runtime state. Build-time state is controlled by kernel configuration symbols.

## Dependencies
The file depends on Kbuild variable conventions and the availability of the referenced source objects in the same directory.

## Risks
If `CONFIG_IXGBEVF_IPSEC` is enabled without required XFRM/crypto dependencies, link or compile errors would surface. Removing an object here can silently drop a feature from the built driver.

## Test signals
Build with `CONFIG_IXGBEVF=y/m`, with and without `CONFIG_IXGBEVF_IPSEC`, and verify resulting module symbols include ethtool and optional IPsec hooks as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/defines.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/defines.h

## Purpose
`defines.h` centralizes VF-side device IDs, link-speed values, descriptor layouts, descriptor status/error bits, queue limits, interrupt masks, RSS packet types, transmit offload command bits, DCA bits, and ixgbevf-local error codes. It is the low-level register/descriptor contract used by the VF driver.

## Important APIs, types, and constants
- Device IDs cover 82599, X540, X550, X550EM_x, X550EM_a, Hyper-V variants, and E610 VF IDs.
- `typedef u32 ixgbe_link_speed` plus 100M, 1G, and 10G link speed masks.
- Queue and descriptor constraints: max VF TX/RX queues, traffic classes, descriptor multiples, and buffer granularity.
- Descriptor structures: `union ixgbe_adv_tx_desc`, `union ixgbe_adv_rx_desc`, and `struct ixgbe_adv_tx_context_desc`.
- RX/TX status and command bits include checksum, VLAN, IPsec packet type/status, advanced descriptor type, TSO, context descriptor, payload length, and IPsec encryption flags.

## Control flow and integration
This header has no executable flow; it is consumed by VF data path, ethtool register dump/test code, RSS code, IPsec offload, and ring setup. Constants are used to interpret device writebacks and to construct transmit descriptors.

## State and persistence behavior
The header defines the shape of MMIO-visible and DMA-visible state. Hardware writes RX descriptor status/error/length/VLAN fields into memory matching these unions, and the driver writes TX descriptor command/address/context fields using these definitions.

## Dependencies
It depends on Linux integer/endian types and bit macros brought in by surrounding includes. It must stay consistent with hardware specifications and PF mailbox expectations.

## Risks
Incorrect bit masks or descriptor field definitions can corrupt DMA interpretation, break checksum/IPsec offloads, mis-detect packet types, or cause queue enablement failures. Duplicate macro names such as RX/TX enable masks intentionally match hardware concepts but require care during edits.

## Test signals
Compile coverage, ethtool register tests, normal RX/TX traffic, checksum offload validation, VLAN traffic, RSS hash reporting, IPsec descriptor offload, and descriptor ring wrap stress are the main validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ethtool.c

## Purpose
`ethtool.c` exposes ixgbevf diagnostics and tunables through `struct ethtool_ops`: driver info, register dumps, ring sizing, stats strings/data, self tests, interrupt coalescing, RSS metadata, link settings, and private flags.

## Important APIs, types, and functions
- Stats model: `struct ixgbe_stats`, `ixgbevf_gstrings_stats`, queue stats naming, and `ixgbevf_get_ethtool_stats()`.
- Register dump/test: `ixgbevf_get_regs_len()`, `ixgbevf_get_regs()`, `struct ixgbevf_reg_test`, `reg_pattern_test()`, `reg_set_and_check()`, and `ixgbevf_reg_test()`.
- Ring control: `ixgbevf_get_ringparam()` and `ixgbevf_set_ringparam()`.
- Diagnostics: `ixgbevf_diag_test()` and `ixgbevf_link_test()`.
- Coalescing and RSS: `ixgbevf_get_coalesce()`, `ixgbevf_set_coalesce()`, `ixgbevf_get_rxfh()`, key/indir-size helpers.
- Private flag: `legacy-rx` toggled through `ixgbevf_get_priv_flags()` and `ixgbevf_set_priv_flags()`.

## Control flow and integration
`ixgbevf_set_ethtool_ops()` installs a static ops table on the netdev. Ring resize validates and aligns requested descriptor counts, takes the reset bit, allocates replacement rings while the device is still running, brings the interface down, swaps resources, updates adapter counts, restarts the device, and frees temporary resources. Offline self-test closes or resets the device, performs register tests, resets again, and reopens if needed. RSS retrieval uses cached X550 VF state for newer MACs and mailbox reads under `mbx_lock` for older devices.

## State and persistence behavior
The file reads and mutates `struct ixgbevf_adapter`: message level, ring counts, ring resource contents, stats, state bits, interrupt throttle settings, RSS key/indir tables, and private flags. It also reads and writes VF MMIO registers during tests and register dumps. Changes persist for the driver lifetime and may trigger device reinitialization.

## Dependencies
It depends on Linux ethtool/netdevice/PCI/vmalloc APIs, ixgbevf ring setup/free/open/close/reset helpers, mailbox RSS helpers, MMIO accessors, u64 stats synchronization, and VF register definitions.

## Risks
- Ring resizing while running has many cleanup paths; missed frees or copied XDP RX queue state would leak resources or corrupt XDP registration.
- Offline register tests write device registers and must not run on removed hardware.
- Coalescing rejects TX settings on mixed RX/TX vectors; future vector layout changes must preserve this rule.
- Stats string count must match stats data order exactly.
- Private flag changes reset the interface and can disrupt traffic.

## Test signals
Run `ethtool -i`, `-d`, `-S`, `-g/-G`, `-c/-C`, `-t online/offline`, RSS queries, and private-flag toggles on supported VFs. Validate ring resize under running/stopped interfaces, allocation failure injection, removed-device checks, and stats string/data length consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ipsec.c

## Purpose
`ipsec.c` implements VF-side XFRM/IPsec crypto offload for ixgbevf. The VF validates XFRM states, keeps local RX/TX security-association tables, asks the PF to program or delete real hardware SA entries through mailbox messages, annotates TX descriptors for offload, and marks RX packets as successfully crypto-processed.

## Important APIs, types, and functions
- PF mailbox helpers: `ixgbevf_ipsec_set_pf_sa()` and `ixgbevf_ipsec_del_pf_sa()`.
- SA lifecycle: `ixgbevf_ipsec_add_sa()`, `ixgbevf_ipsec_del_sa()`, `ixgbevf_ipsec_restore()`, and `ixgbevf_ipsec_find_empty_idx()`.
- RX lookup: `ixgbevf_ipsec_find_rx_state()` uses an RCU hash keyed by SPI.
- Key validation: `ixgbevf_ipsec_parse_proto_keys()` accepts only `rfc4106(gcm(aes))` with 128-bit ICV and a supported key/salt layout.
- Data path hooks: `ixgbevf_ipsec_tx()` fills `ixgbevf_ipsec_tx_data` and TX flags, while `ixgbevf_ipsec_rx()` builds secpath/xfrm offload status from RX descriptor packet type bits.
- Initialization/teardown: `ixgbevf_init_ipsec_offload()` and `ixgbevf_stop_ipsec_offload()`.

## Control flow and integration
Initialization checks mailbox API/PF feature support, allocates `struct ixgbevf_ipsec`, RX/TX tables with 1024 entries each, installs `xfrmdev_ops`, and enables ESP-related netdev features. State add validates protocol, transport mode, crypto-offload type, no compression for RX, table capacity, algorithm/key shape, and then requests PF programming. The returned PF SA handle is stored in the local table and exposed through `xs->xso.offload_handle`.

On TX, the driver locates the outbound xfrm state from the SKB, maps the offload handle to the local TX SA table, stores the PF SA index for the context descriptor, sets IPsec/checksum flags, selects ESP/IP version/encryption bits, and computes non-GSO ESP trailer length. On RX, descriptor packet-type bits identify IPv4/IPv6 plus AH/ESP, the SPI and destination address find the matching RX state, and the SKB secpath is marked `CRYPTO_DONE`/`CRYPTO_SUCCESS`.

## State and persistence behavior
State is in `adapter->ipsec`, `rx_tbl`, `tx_tbl`, RX RCU hash table, `num_rx_sa`, `num_tx_sa`, PF SA handles, XFRM offload handles, and adapter counters `tx_ipsec`/`rx_ipsec`. Hardware state persists in the PF-managed SA tables and must be restored after VF reset through `ixgbevf_ipsec_restore()`.

## Dependencies
The file depends on XFRM device offload APIs, crypto AEAD metadata, IP/AH/ESP headers, SKB secpath helpers, ixgbevf mailbox locking and send/poll functions, descriptor flags from `defines.h`, and feature negotiation through `adapter->pf_features`.

## Risks
- `ixgbevf_ipsec_restore()` requests PF reprogramming but does not update stored `pfsa` handles on success, so PF handle stability is assumed across reset.
- RX secpath failure after `xfrm_state_hold()` can leak a reference unless ownership is handled elsewhere.
- SA delete trusts offload handles enough to index tables after subtracting base offsets; corrupted handles can be dangerous.
- The algorithm/key parser is intentionally narrow; unsupported modern algorithms will be rejected.
- Mailbox failures leave local and PF state boundaries sensitive to partial add/delete behavior.

## Test signals
Validate XFRM state add/delete for inbound/outbound ESP and AH, unsupported mode/protocol/algorithm rejection with extack messages, mailbox PF failure paths, reset and restore, TX descriptor flag/context generation including GSO/non-GSO ESP trailer lengths, RX secpath marking for IPv4 and IPv6, and SA table exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ipsec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ipsec.h

## Purpose
`ipsec.h` defines ixgbevf's IPsec offload data model shared between the VF header, IPsec implementation, and TX/RX data paths.

## Important APIs, types, and constants
- Capacity and index bases: 1024 SAs, RX base 0, TX base 1024.
- Authentication and RX mode bits: 128-bit auth, valid, ESP, decrypt, and IPv6 flags.
- `struct rx_sa`, `struct tx_sa`, and `struct rx_ip_sa` describe local SA metadata.
- `struct ixgbevf_ipsec_tx_data` carries descriptor-time TX offload flags, trailer length, and PF SA index.
- `struct ixgbevf_ipsec` owns RX/TX table pointers, table counts, and the RX hash table.
- `struct sa_mbx_msg` is the compact VF-to-PF mailbox payload for SA programming.

## Control flow and integration
The header is included by `ixgbevf.h`; when `CONFIG_IXGBEVF_IPSEC` is enabled, data path prototypes use these structures. `ipsec.c` allocates and fills the table structures and casts mailbox buffers to `struct sa_mbx_msg` when communicating with the PF.

## State and persistence behavior
The structures hold XFRM state pointers, keys, salt, address, mode bits, PF SA handles, local usage flags, and RCU hash nodes. This is volatile driver state; PF hardware SA state is represented by `pfsa` handles and restored after VF reset.

## Dependencies
It depends on kernel hash-list types, XFRM state declarations through includers, endian integer types, and mailbox size/layout agreement with PF code.

## Risks
Mailbox layout changes must remain synchronized with PF expectations. Key material is stored in kernel memory tables until teardown/delete, so zeroing and lifetime handling matter. The local table capacity and base-index arithmetic must match `ipsec.c`.

## Test signals
Build with IPsec enabled, add/delete enough SAs to exercise RX/TX index bases and table limits, validate mailbox payloads for IPv4/IPv6, and check reset restore preserves expected PF SA handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ipsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ixgbevf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ixgbevf.h

## Purpose
`ixgbevf.h` is the central private header for the ixgbe VF driver. It defines ring buffers, queue vectors, adapter state, descriptor helpers, queue limits, XDP/IPsec integration points, feature flags, state bits, and cross-file function prototypes.

## Important APIs, types, and functions
- Ring data structures: `ixgbevf_tx_buffer`, `ixgbevf_rx_buffer`, `ixgbevf_ring`, `ixgbevf_ring_container`, and `ixgbevf_q_vector`.
- Adapter root object: `struct ixgbevf_adapter` contains queue arrays, XDP rings, netdev/PCI/hardware pointers, mailbox lock, stats, service work/timer, RSS state, flags, and optional IPsec state.
- Ring state helpers: XDP ring flags, large-buffer/build-skb flags, TX hang flags, descriptor unused calculation, descriptor address macros, and tail write helper.
- Constants: queue counts, descriptor bounds/defaults, RSS sizes, RX buffer sizes, interrupt throttle values, jumbo frame size, DMA attributes, and TX flag bits.
- Cross-file prototypes: open/close/up/down/reset, resource setup/free, stats update, ethtool ops install, EITR write, mailbox poll/write, and IPsec hooks or stubs.

## Control flow and integration
Most ixgbevf source files include this header and operate through the structures defined here. The main driver allocates and owns `struct ixgbevf_adapter`; ethtool mutates ring counts and flags; data path code advances ring indices and uses descriptor macros; mailbox code serializes PF communication through `mbx_lock`; optional IPsec hooks compile to no-op stubs when disabled.

## State and persistence behavior
The adapter structure is the runtime persistence root for the VF lifetime. It stores queue topology, ring descriptor memory and DMA addresses, interrupt moderation settings, netdev state, hardware state, PF feature negotiation, RSS configuration, service state bits, link status, XDP program/rings, and optional IPsec tables. Ring state persists across NAPI polls and is reset or rebuilt by resource setup/teardown and interface reset flows.

## Dependencies
The header depends on Linux netdevice, timer, IO, VLAN, u64 stats, XDP, bit operations, and ixgbevf hardware headers `vf.h` and `ipsec.h`. It must stay aligned with descriptor definitions in `defines.h` and implementation assumptions in `ixgbevf_main.c`, `ethtool.c`, `mbx.c`, and `ipsec.c`.

## Risks
- Layout changes to `ixgbevf_adapter` can affect code relying on the first field being `active_vlans`.
- Queue array bounds are fixed and must match PF-negotiated queue counts.
- Descriptor helper arithmetic assumes ring indices are maintained correctly and one descriptor remains unused.
- Optional IPsec stubs must match real prototypes exactly to keep non-IPsec builds safe.
- XDP, RSS, and interrupt fields are shared across reset, ethtool, and data path code, making locking/state-bit discipline important.

## Test signals
Full driver build with and without `CONFIG_IXGBEVF_IPSEC`, probe/remove, interface reset, RX/TX traffic, XDP attach/detach, ethtool ring/stat/coalesce operations, RSS queries, mailbox feature negotiation, TX hang detection, and IPsec-enabled builds all validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ixgbevf.h -->
