# Research: subset-b-004588

Grouped source research for Netronome/Corigine NFP driver files. Each section is source-tree aligned and delimited for reconciliation into one per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/dp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/dp.c

## Purpose
Implements the NFDK datapath for the NFP NIC driver: normal SKB transmit, TX completion, RX buffer recycling, RX metadata parsing, XDP TX/pass/drop handling, NAPI polling, and control-vNIC tasklet traffic. This is the concrete `nfp_dp_ops` datapath used by `nfdk/rings.c` and selected by `nfp_net_alloc()` when firmware reports the NFDK datapath ABI.

## Important APIs, Types, and Functions
- `nfp_nfdk_tx()` is the netdev transmit entry point for NFDK devices. It builds host TX descriptors, maps SKB head/frags, adds optional metadata, handles TSO, checksum, TLS/IPsec hooks, queue stopping, and QCP kick batching.
- `nfp_nfdk_tx_complete()` reclaims transmitted SKBs by comparing software `rd_p` with hardware/QCP completion, unmaps DMA, updates `tx_pkts`, `tx_bytes`, and wakes stopped queues.
- `nfp_nfdk_rx()` consumes completed RX descriptors, parses prepend metadata, applies XDP, redirects control/repr packets, constructs SKBs, handles checksum/VLAN/IPsec, and submits via GRO or egress redirection.
- `nfp_nfdk_poll()` is the NAPI poll function and ties TX completion, RX polling, interrupt unmasking, and adaptive DIM sampling together.
- `nfp_nfdk_ctrl_tx_one()` and `nfp_nfdk_ctrl_poll()` implement control-vNIC TX/RX through the same descriptor format, with a tasklet queue and app control-message dispatch.
- Helpers such as `nfp_nfdk_tx_maybe_close_block()`, `nfp_nfdk_prep_tx_meta()`, `nfp_nfdk_parse_meta()`, `nfp_nfdk_rx_give_one()`, and `nfp_nfdk_tx_xdp_buf()` are the high-risk mechanics for descriptor block boundaries, metadata layout, freelist ownership, and zero-copy XDP reuse.

## Control Flow
TX starts in `nfp_nfdk_tx()`: the driver checks ring space, optionally pushes metadata for HW port mux, VLAN insertion, and IPsec, closes a 256-byte descriptor block with NOP descriptors if the packet would cross a block or exceed a block data budget, DMA maps head/frags, emits data descriptors, emits a metadata descriptor, optionally emits a TSO descriptor, timestamps the SKB, advances `wr_p` and `wr_ptr_add`, and flushes QCP writes when `xmit_more` allows. Errors after partial mapping unwind mapped buffers, count `tx_errors`, flush pending descriptors, and free the SKB.

RX starts when NAPI calls `nfp_nfdk_rx()`. For each descriptor with `PCIE_DESC_RX_DD`, it calculates metadata and packet offsets from `rx_offset`, synchronizes DMA for CPU, parses chained metadata, optionally runs the XDP program, routes control-port payloads to `nfp_app_ctrl_rx_raw()`, resolves representor destination with `nfp_app_dev_get()`, builds an SKB, allocates and posts a replacement buffer, unmaps the old RX buffer, fills hash/mark/protocol/checksum/VLAN/IPsec state, then passes the packet to GRO or `dev_queue_xmit()` for redirection. XDP_TX reuses the RX buffer as a TX buffer and later recycles it in `nfp_nfdk_xdp_complete()`.

Control-vNIC flow uses IRQ tasklets rather than NAPI. `nfp_nfdk_ctrl_poll()` locks the control vector, completes TX, drains queued SKBs through `nfp_nfdk_ctrl_tx_one()`, then polls RX up to a fixed budget and either unmasks IRQs or reschedules itself.

## State and Persistence Behavior
The file mutates volatile datapath state only: ring pointers `wr_p`, `rd_p`, `qcp_rd_p`, descriptor contents, DMA mappings, queued SKBs, and per-vector u64 stats protected by `u64_stats_sync`. RX buffer ownership alternates among hardware freelist, SKB/page fragment, XDP TX ring, and freshly allocated replacement buffers. No disk persistence exists, but firmware-visible BAR/QCP state persists until reset or `nfp_net_clear_config_and_disable()` in common code resets rings.

## Dependencies and Integration Points
Depends on `nfp_net.h` structures, `nfp_net_dp.h` DMA/ring helpers, metadata constants from `nfp_net_ctrl.h`, app routing from `nfp_app.h`, TLS/IPsec helpers from `crypto/`, Linux NAPI/XDP/SKB/DMA APIs, and NFDK descriptor definitions from `nfdk.h`. It is wired into the driver through `nfp_nfdk_ops` in `rings.c` and `nfp_nfdk_netdev_ops` in `nfp_net_common.c`.

## Risks
Descriptor accounting is fragile because NFDK packets must not cross descriptor block boundaries and because first descriptors have a smaller head length field than gather descriptors. DMA error unwinding is sensitive to pointer ordering. RX metadata parsing treats unknown fields as a soft stop and must keep metadata length and packet offsets consistent. XDP_TX recycles RX buffers through TX completion, so pointer tags in `nfp_nfdk_tx_buf` must remain aligned and cleared. Control-message budget exhaustion can reschedule tasklets indefinitely if firmware floods malformed or excessive messages.

## Test Signals
Useful checks include TX/RX under small and jumbo MTUs, fragmented SKBs near `NFDK_TX_DESC_GATHER_MAX`, TSO/USO, VLAN insertion/stripping, checksum modes, metadata port redirection, representor RX, XDP PASS/DROP/TX with tail adjustment, IPsec/TLS offload paths when configured, queue stop/wake under saturation, and forced DMA allocation/mapping failures. Runtime signals are `tx_errors`, `tx_busy`, checksum counters, `rx_replace_buf_alloc_fail`, WARN_ONCE block-overflow messages, NAPI budget behavior, and packet loss after ring reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/ipsec.c

## Purpose
Adds a small NFDK TX helper for IPsec checksum flagging when `CONFIG_NFP_NET_IPSEC` is enabled. It adjusts descriptor metadata flags after IPsec preparation has identified an offloaded packet.

## Important APIs, Types, and Functions
- `nfp_nfdk_ipsec_tx(u64 flags, struct sk_buff *skb)` checks `xfrm_input_state(skb)` and the skb IP header, then ORs `NFDK_DESC_TX_L3_CSUM` for IPv4 and `NFDK_DESC_TX_L4_CSUM` when the offload device advertises `NETIF_F_HW_ESP_TX_CSUM`.

## Control Flow
`nfp_nfdk_tx()` in `nfdk/dp.c` calls this helper only after IPsec metadata was prepared. The helper reads XFRM state and IP version, modifies the existing NFDK metadata flags, and returns the updated flags used in the TX metadata descriptor.

## State and Persistence Behavior
No persistent or owned state. It reads skb/XFRM state and device feature bits and returns a modified flag word.

## Dependencies and Integration Points
Depends on Linux XFRM state, SKB IP header helpers, NFDK descriptor flag definitions in `nfdk.h`, and `nfp_net` IPsec feature negotiation. It is declared conditionally in `nfdk.h`; when IPsec is disabled, the inline stub returns flags unchanged.

## Risks
The helper assumes `xfrm_input_state(skb)` is valid on the offloaded TX path and that `ip_hdr(skb)` is meaningful for the packet. Incorrect call ordering or malformed skb headers could set wrong checksum flags.

## Test Signals
Exercise ESP TX checksum offload for IPv4 and IPv6, compare descriptor flags, and verify fallback behavior when `NETIF_F_HW_ESP_TX_CSUM` is absent. Build coverage should include both `CONFIG_NFP_NET_IPSEC=y` and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/nfdk.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/nfdk.h

## Purpose
Defines the NFDK TX descriptor format, NFDK ring sizing constants, software TX buffer representation, and public NFDK datapath entry points used by common NFP netdev code.

## Important APIs, Types, and Functions
- Descriptor constants define TX descriptor block size, stop thresholds, maximum data per head/descriptor/block, gather limit, descriptor type values, EOP bit, checksum/encap flags, and metadata layout fields.
- `struct nfp_nfdk_tx_desc` overlays DMA, TSO, metadata, raw, and word-level descriptor interpretations.
- `struct nfp_nfdk_tx_buf` stores software state associated with TX descriptors: SKB, fragment pointer, DMA address, XDP pointer tags, and TSO packet/real-length accounting.
- `nfp_nfdk_headlen_to_segs()` converts a linear head length into required NFDK descriptors, accounting for the smaller first-descriptor head data field.
- Declares `nfp_nfdk_poll()`, `nfp_nfdk_tx()`, `nfp_nfdk_ctrl_tx_one()`, `nfp_nfdk_ctrl_poll()`, and `nfp_nfdk_rx_ring_fill_freelist()`.

## Control Flow
This header has no runtime flow, but its constants encode the constraints enforced by `dp.c` and `rings.c`: TX rings use twice the nominal packet descriptor count, each simple packet reserves data plus metadata descriptors, and packets may need padding to the next descriptor block.

## State and Persistence Behavior
The header defines in-memory structures shared between driver and firmware DMA rings. The lower bits of `nfp_nfdk_tx_buf.val` are used as driver-only tags for XDP buffer provenance and must be stripped before hardware sees DMA addresses.

## Dependencies and Integration Points
Included by NFDK datapath and ring setup files. It depends on Linux bitops/types and forward declarations from `nfp_net.h`. Its IPsec declaration is conditional on `CONFIG_NFP_NET_IPSEC`.

## Risks
Any mismatch with firmware descriptor ABI breaks TX/RX. The bitfield constants are tightly coupled with `FIELD_PREP()` use in `dp.c`. Pointer tagging assumes alignment leaves low bits free; changes to allocation alignment or architecture assumptions could invalidate XDP recycling.

## Test Signals
Compile-time coverage should catch struct references, but ABI correctness needs runtime TX descriptor inspection, firmware compatibility testing across NFDK ABI versions, TSO/gather boundary tests, and XDP_TX recycling tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/nfdk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/rings.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/rings.c

## Purpose
Provides NFDK-specific ring allocation, reset, debug dump, and `nfp_dp_ops` registration. It adapts common `nfp_net` ring lifecycle code to NFDK descriptor sizes and capabilities.

## Important APIs, Types, and Functions
- `nfp_nfdk_tx_ring_alloc()` allocates coherent NFDK TX descriptors and software `ktxbufs`, sets `cnt` to `dp->txd_cnt * NFDK_TX_DESC_PER_SIMPLE_PKT`, and applies XPS affinity for stack TX queues.
- `nfp_nfdk_tx_ring_reset()` walks outstanding non-XDP SKBs, unmaps head/frags, accounts for TSO extra descriptors and block padding, frees SKBs, zeroes descriptors, resets pointers, and resets the netdev TX queue.
- `nfp_nfdk_tx_ring_free()` releases `ktxbufs` and coherent descriptor memory.
- `nfp_nfdk_print_tx_descs()` emits descriptor/debug state to seq_file including host and device read/write pointer markers.
- `nfp_nfdk_ops` binds NFDK version, capability mask, DMA mask, NAPI/control poll functions, TX path, ring lifecycle callbacks, and debug printing.

## Control Flow
Common open/reconfig code calls `tx_ring_alloc` before enabling firmware and `tx_ring_reset`/`tx_ring_free` during close or failed reconfiguration. `nfp_nfdk_ops` is selected by `nfp_net_alloc()` based on the firmware datapath version and subsequently drives all datapath polymorphism.

## State and Persistence Behavior
Manages volatile ring memory, DMA addresses, descriptor counters, queue pointer mirrors, and queue accounting. It does not persist state beyond the lifetime of a vNIC open/reconfiguration cycle. Reset is designed to be idempotent after firmware disable.

## Dependencies and Integration Points
Depends on common `nfp_net` structures, `nfp_net_dp` helpers, NFDK descriptor definitions, DMA coherent allocation, seq_file debugfs output, and netdev XPS queue APIs. The capability mask intersects firmware-advertised features before common netdev feature setup.

## Risks
Reset must compute the same descriptor counts as transmit, including block padding and TSO metadata, or it can leak DMA mappings or free wrong SKBs. Empty `tx_ring_bufs_alloc/free` callbacks are intentional for NFDK but may surprise common code expecting per-buffer allocation.

## Test Signals
Open/close cycles, failed open unwinds, MTU/ring-count reconfiguration, debugfs descriptor dumps, TX timeout recovery, and ring reset with in-flight TSO/fragments are the main signals. Memory leak and DMA API debug are valuable here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/rings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_abi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_abi.h

## Purpose
Defines firmware ABI names, offsets, commands, and structures for the PF runtime-symbol mailbox and shared buffer/devlink shared-buffer operations.

## Important APIs, Types, and Functions
- Mailbox symbols and offsets: `NFP_MBOX_SYM_NAME`, `NFP_MBOX_CMD`, `NFP_MBOX_RET`, `NFP_MBOX_DATA_LEN`, `NFP_MBOX_DATA`, and minimum size.
- `enum nfp_mbox_cmd` defines PF mailbox operations for shared buffer pool get/set and PCIe-side ABM enable/disable.
- Shared buffer symbol names and structures mirror firmware/devlink data: `struct nfp_shared_buf`, `struct nfp_shared_buf_pool_id`, `struct nfp_shared_buf_pool_info_get`, and `struct nfp_shared_buf_pool_info_set`.

## Control Flow
No executable flow. `nfp_main.c` uses the mailbox constants in `nfp_mbox_cmd()`, while devlink/shared-buffer code uses the packed structures and command ids to exchange data with firmware.

## State and Persistence Behavior
Defines the wire format for firmware-owned persistent/runtime state. The driver does not own persistence here; it serializes requests into the runtime symbol mailbox and reads firmware responses.

## Dependencies and Integration Points
Integrated with PF runtime-symbol access, devlink shared buffer callbacks, ABM app support, and firmware ABI. Uses Linux fixed-size little-endian types for cross-endian clarity.

## Risks
ABI drift between firmware and driver can corrupt mailbox commands or interpret pool units incorrectly. The structures are not explicitly marked packed, so layout assumptions rely on natural alignment matching firmware ABI.

## Test Signals
Devlink shared buffer pool get/set, ABM enable/disable, firmware versions with and without PF mailbox support, and endian/layout validation are key. Runtime failures surface as mailbox `-EOPNOTSUPP`, `-EBUSY`, `-ETIMEDOUT`, or firmware-returned errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app.c

## Purpose
Implements the NFP application abstraction: mapping firmware app IDs to driver app types, allocating app containers, dispatching common netdev/app callbacks, managing representor pointer publication, and handling app-level start/stop notifier registration.

## Important APIs, Types, and Functions
- `apps[]` maps `enum nfp_app_id` values to app implementations (`app_nic`, `app_bpf`, `app_flower`, `app_abm`) under build-time config.
- `nfp_app_alloc()` validates app support, allocates `struct nfp_app`, and binds PF/CPP/PCI/type pointers.
- `nfp_app_start()` sets the control vNIC, calls app `.start`, and registers a netdevice notifier; `nfp_app_stop()` unregisters and calls `.stop`.
- `nfp_app_from_netdev()` resolves app pointers from either data vNICs or representors.
- `nfp_app_ctrl_msg_alloc()`, stats wrappers, NDO init/uninit wrappers, and representor helpers provide null-safe dispatch to app callbacks.
- `nfp_app_reprs_set()` publishes representor arrays with RCU under RTNL, with devlink-lock assertions available in the header.

## Control Flow
PF probe reads a firmware app ID, allocates the app, initializes app-specific state, creates vNICs, and eventually starts the app with a control vNIC. Netdev events pass through `nfp_app_netdev_event()`, which handles common feature propagation to representors before delegating to app-specific event handlers.

## State and Persistence Behavior
Owns the runtime `struct nfp_app` and app-private pointer. Representor arrays are RCU-published and protected by the devlink instance lock plus RTNL for update visibility. No disk persistence; app state exists for the PF lifecycle.

## Dependencies and Integration Points
Depends on app implementations, `nfp_main` PF structure, `nfp_net`, `nfp_net_repr`, `nfp_port`, devlink locking, RCU, RTNL, and skb allocation. It is a hub between PCI probe/common netdev code and feature-specific apps.

## Risks
Incorrect app ID support or missing mandatory callbacks blocks probe. Feature propagation iterates representors under RTNL/RCU assumptions. Apps with raw control RX must also provide normal control RX, enforced by `WARN_ON`.

## Test Signals
Probe each supported app type, build with BPF/flower/ABM toggles, create/destroy representors, trigger `NETDEV_FEAT_CHANGE`, verify app `.start` failure unwinds `.stop`, and validate control message allocation headroom behavior for apps using metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app.h

## Purpose
Declares the NFP application interface used by app implementations and common driver code. It defines app IDs, callback tables, app container state, inline dispatch helpers, control-message tracing wrappers, devlink/eswitch/SR-IOV hooks, and shared NIC app callbacks.

## Important APIs, Types, and Functions
- `enum nfp_app_id` identifies core NIC, BPF NIC, flower NIC, and active buffer management NIC firmware apps.
- `struct nfp_app_type` is the main callback contract for init/clean, vNIC lifecycle, representors, MTU/statistics, start/stop, netdev events, control messages, TC/BPF/XDP, SR-IOV, eswitch mode, and device lookup.
- `struct nfp_app` stores PF/CPP/PCI backpointers, control vNIC, RCU representor arrays, app type, control MTU, netdev notifier, and app-private data.
- Inline helpers null-check and dispatch callback families, including `nfp_app_vnic_alloc()`, `nfp_app_repr_open()`, `nfp_app_setup_tc()`, `nfp_app_xdp_offload()`, `nfp_app_sriov_enable()`, and `nfp_app_dev_get()`.
- Control TX/RX wrappers trace devlink hardware messages and call `nfp_ctrl_tx()`, `__nfp_ctrl_tx()`, or app RX callbacks.

## Control Flow
Common code treats apps polymorphically through this header. Probe allocates and initializes an app, vNIC setup calls app allocation/init callbacks, netdev operations call NDO/TC/BPF/MTU wrappers, control datapath calls control RX/TX wrappers, and devlink/SR-IOV operations delegate to app-specific hooks when present.

## State and Persistence Behavior
Defines runtime-only state. `reprs[]` is RCU-protected and app lock assertions are tied to the devlink instance lock. Control message wrappers only trace and dispatch; persistence is in firmware/app state outside this header.

## Dependencies and Integration Points
Includes devlink trace support and representor definitions. It is included by most NFP common/app modules and connects Linux netdev, devlink, TC, BPF, XDP, SR-IOV, representors, and firmware control messaging.

## Risks
Callback return defaults vary (`0`, `-EINVAL`, `-EOPNOTSUPP`, `NULL`) and callers must interpret them correctly. App lock assumptions matter for representor access. `nfp_app_ctrl_has_meta()` assumes non-null app in some callers; control-vNIC users must only call it after app allocation.

## Test Signals
Compile all config permutations, exercise absent callbacks, verify devlink hwmsg tracepoints on control messages, test TC/BPF/XDP offload fallback errors, SR-IOV enable/disable delegation, and representor lookup/redirection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app_nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app_nic.c

## Purpose
Provides shared NIC-app vNIC allocation helpers for binding a data vNIC to a physical NFP port and initializing its MAC address.

## Important APIs, Types, and Functions
- `nfp_app_nic_vnic_init_phy_port()` allocates an `NFP_PORT_PHYS_PORT`, initializes it from the PF ETH table by id, and returns whether the port was marked invalid.
- `nfp_app_nic_vnic_alloc()` calls the physical-port initializer and, for valid ports, reads the MAC address into the netdev using `nfp_net_get_mac_addr()`.

## Control Flow
App vNIC allocation calls this helper during PF/vNIC setup. If there is no ETH table, it silently leaves the vNIC without a physical port. If port initialization fails, it frees the allocated port and propagates the error. If the port is invalid, allocation returns success but skips MAC setup.

## State and Persistence Behavior
Mutates `nn->port` and netdev MAC address. The port object is owned by the vNIC/app lifecycle and later freed by common/app cleanup. No persistent storage.

## Dependencies and Integration Points
Depends on NSP/ETH table data, `nfp_port_alloc()`, `nfp_port_init_phy_port()`, `nfp_port_free()`, and common MAC retrieval. Used by app implementations that expose physical NIC ports.

## Risks
The return convention from `nfp_app_nic_vnic_init_phy_port()` is subtle: positive means invalid port but not fatal. Callers must preserve that behavior to avoid failing probe for intentionally invalid ports.

## Test Signals
Probe with no ETH table, valid ETH table, invalid ports, and failing `nfp_port_init_phy_port()`. Verify port object cleanup and MAC address assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app_nic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_asm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_asm.c

## Purpose
Implements helper routines for encoding and modifying NFP microengine instructions and software register operands, plus ECC generation for ustore instructions. It supports code generation/patching used by NFP BPF/offload logic elsewhere in the driver.

## Important APIs, Types, and Functions
- `cmd_tgt_act[]` maps abstract command target operations to token/target-command encodings.
- `br_get_offset()`, `br_set_offset()`, and `br_add_offset()` read and modify branch offsets spanning low/high address fields.
- `immed_get_value()`, `immed_set_value()`, and `immed_add_value()` decode and adjust immediate instruction operands when encoding constraints allow.
- `swreg_to_unrestricted()` and `swreg_to_restricted()` convert software register handles into hardware operand encodings, tracking operand swaps, A/B destination, write-both, immediate-8, and LM extension bits.
- `nfp_ustore_check_valid_no_ecc()` validates instruction width before ECC; `nfp_ustore_calc_ecc_insn()` appends ECC parity bits.

## Control Flow
Instruction builders call these helpers while emitting or relocating NFP instructions. Operand conversion validates incompatible register combinations, may swap A/B operands to satisfy hardware register-bank constraints, and returns populated encoding structs. ECC calculation iterates fixed polynomial masks and appends seven parity bits above the 45-bit instruction payload.

## State and Persistence Behavior
No mutable global state except the constant command map and ECC polynomial table. Functions operate on caller-provided instruction words and output structs. Generated instruction streams may later be loaded to firmware/hardware, but this file does not persist them.

## Dependencies and Integration Points
Depends on `nfp_asm.h`, Linux bitfield helpers, bitops, and logging. Integrated with JIT/offload code that emits NFP microcode, especially BPF-related components.

## Risks
Encoding errors can generate invalid microcode. Some error cases log and return zero encodings instead of propagating errno from lower helpers, so callers must validate top-level returns. Immediate modification only supports non-inverted, unshifted, full-width immediates.

## Test Signals
Unit-style encode/decode tests for branch offsets, immediates, each software register type, LM modes, restricted/unrestricted operand conflicts, and ECC parity vectors. Negative tests should verify invalid immediates/registers return errors or emit expected diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_asm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_asm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_asm.h

## Purpose
Defines the NFP microengine instruction encoding constants, register abstractions, operand conversion structures, branch/immediate helper prototypes, command target encodings, CSR constants, ECC helpers, and multiply instruction fields.

## Important APIs, Types, and Functions
- Instruction masks cover branch, branch-bit, branch-ALU, byte/ALU/shift/load-field/command/local-CSR/carb/multiply encodings.
- `nfp_is_br()` identifies branch instructions by base/mask.
- Enums define branch conditions, immediate width/shift, shift/ALU ops, command modes/context swap, local CSR write source, register types, LM modes, command target map, multiply type/step, and operand destination bank.
- `swreg` and inline constructors (`reg_a`, `reg_b`, `reg_both`, `reg_nnr`, `reg_xfer`, `reg_imm`, `reg_lm`, etc.) define a driver-internal register representation independent of operand format.
- `struct nfp_insn_ur_regs` and `struct nfp_insn_re_regs` carry converted operand encodings for unrestricted and restricted instruction forms.

## Control Flow
No runtime flow beyond inline helpers. Instruction generation code composes constants and calls `nfp_asm.c` functions declared here to produce hardware instruction words.

## State and Persistence Behavior
No state. The header is a declarative ABI/encoding contract between code generators and hardware instruction format.

## Dependencies and Integration Points
Depends on Linux bitfield, bug, and types headers. Used by NFP assembler/JIT code in the driver, especially BPF offload paths. `cmd_tgt_act[]` is exported from `nfp_asm.c`.

## Risks
Constants must exactly match NFP hardware. The `swreg` bitwise typedef helps avoid accidental raw integer misuse, but many macros still allow constructing invalid logical combinations that later conversion must reject. `__enc_swreg_lm()` only WARNs on invalid local-memory parameters.

## Test Signals
Build coverage for BPF/offload configs, static tests that instruction masks produce expected encodings, and round-trip tests for software register helpers. Hardware/JIT tests should detect wrong op fields through rejected programs or incorrect packet processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_devlink.c

## Purpose
Implements devlink operations for NFP PFs: physical port split/unsplit, shared buffer pool operations, eswitch mode delegation, firmware/board info reporting, flash update, and devlink port registration.

## Important APIs, Types, and Functions
- `nfp_devlink_port_split()` and `nfp_devlink_port_unsplit()` validate ETH port lane topology and call `nfp_devlink_set_lanes()` through NSP config transactions.
- Shared buffer callbacks call `nfp_shared_buf_pool_get()` and `nfp_shared_buf_pool_set()`.
- `nfp_devlink_eswitch_mode_get/set()` delegate to app callbacks.
- `nfp_devlink_info_get()` publishes serial number, running/stored NSP versions, and fixed HWInfo versions.
- `nfp_devlink_flash_update()` calls `nfp_flash_update_common()`.
- `nfp_devlink_port_register()` populates physical devlink port attributes, switch ID from CPP serial, lane/split info, and registers port ops.

## Control Flow
Devlink core invokes `nfp_devlink_ops`. Port split/unsplit takes RTNL to copy a stable `nfp_eth_table_port`, starts NSP ETH config, applies split lane count, commits, and refreshes the port table if changed. Info get opens NSP, optionally reads version buffer, publishes version keys, closes NSP, then adds HWInfo-derived fixed versions.

## State and Persistence Behavior
Port split/unsplit modifies firmware/NSP-managed hardware port configuration. Flash update writes persistent firmware image through NSP. Devlink port registration creates runtime devlink objects tied to `struct nfp_port`.

## Dependencies and Integration Points
Depends on devlink, RTNL, NSP ETH/versions/flash APIs, HWInfo, app eswitch callbacks, shared-buffer code, and port structures. It is registered by PF devlink allocation in `nfp_main.c`.

## Risks
Lane special cases for 100G CXP to 2x40G are topology-specific. NSP access failures must report extack accurately. Serial number construction concatenates vendor/part/serial into a temporary buffer and depends on all three HWInfo fields. Port registration assumes a valid physical `nfp_port` and ETH table copy.

## Test Signals
`devlink dev info`, flash update failure/success paths, split/unsplit invalid counts, already-unsplit errors, shared-buffer get/set, eswitch mode get/set for apps that support it, and devlink port attributes/switch ID validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_hwmon.c

## Purpose
Registers an hwmon device for NFP sensors exposed by NSP, providing chip temperature and assembly power readings plus static max/critical thresholds.

## Important APIs, Types, and Functions
- `nfp_hwmon_sensor_id()` maps hwmon temp/power channels to NSP sensor IDs.
- `nfp_hwmon_read()` returns constant thresholds or reads live sensor values with `nfp_hwmon_read_sensor()` if the NSP sensor mask advertises the sensor.
- `nfp_hwmon_is_visible()` exposes read-only temp and power attributes.
- `nfp_hwmon_register()` conditionally registers `hwmon_device_register_with_info()` when HWMON is reachable and NSP sensor data exists.
- `nfp_hwmon_unregister()` unregisters the hwmon device on PF cleanup.

## Control Flow
PF probe calls register after network probe succeeds. Registration skips cleanly when HWMON is unavailable, NSP identify data is absent, or no sensors are advertised. Reads are routed by hwmon core to the static ops table.

## State and Persistence Behavior
Stores the registered hwmon device pointer in `pf->hwmon_dev`. Sensor values are read from NSP at request time; thresholds are constants. No persistence.

## Dependencies and Integration Points
Depends on Linux hwmon, NSP sensor IDs/read API, PF state in `nfp_main.h`, and `pf->nspi->sensor_mask`.

## Risks
Sensor channel mapping is fixed: one temperature channel and three power channels derived from `NFP_SENSOR_ASSEMBLY_POWER + channel`. If firmware changes channel ordering, readings could be mislabeled. Registration silently skips in several cases, so absence may be expected rather than fatal.

## Test Signals
Probe with/without CONFIG_HWMON, missing NSP info, zero sensor mask, partial sensor mask, and active temperature/power reads. Validate sysfs attributes and threshold values in millidegrees/microwatts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_main.c

## Purpose
Implements the NFP PF PCI driver lifecycle: device ID matching, PCI enable/resource setup, CPP/NSP initialization, firmware selection/loading/unloading, runtime-symbol mailbox operations, SR-IOV configuration, devlink/PF allocation, vNIC probe/remove delegation, hwmon registration, and module init/exit.

## Important APIs, Types, and Functions
- `nfp_pci_probe()` is the PF probe path. It enables PCI, sets DMA mask, reserves regions, allocates devlink/PF state, creates workqueue, opens CPP, reads HWInfo, waits board-ready, initializes NSP/firmware, reads MIP/rtsyms, validates SR-IOV limits, configures HWInfo, probes net vNICs, and registers hwmon.
- `__nfp_pci_shutdown()`, `nfp_pci_remove()`, and `nfp_pci_shutdown()` unwind runtime state and optionally unload firmware.
- `nfp_fw_load()` implements firmware load policy from NSP HWInfo, optional reset, disk firmware lookup, stored firmware fallback, and unload-on-remove tracking.
- `nfp_net_fw_find()` searches firmware by serial/interface, PCI name, then card/media model.
- `nfp_mbox_cmd()` serializes PF mailbox commands via runtime symbol offsets.
- `nfp_pcie_sriov_enable/disable/configure()` coordinates PCI SR-IOV and app-specific VF setup under devlink lock.
- `nfp_main_init()` registers PF and VF PCI drivers and debugfs; exit unregisters them.

## Control Flow
Probe is staged with a strict goto unwind ladder. Firmware initialization opens NSP, waits for management firmware, reads ports and NSP identity, applies firmware load policy, and marks whether this driver instance should unload firmware later. After runtime symbols and app capability data are available, `nfp_net_pci_probe()` owns vNIC/app construction. Remove/shutdown reverses registration, disables SR-IOV, removes vNICs, frees firmware metadata, optionally resets firmware, destroys workqueue/CPP/devlink/PCI resources.

## State and Persistence Behavior
Owns the PF-wide `struct nfp_pf` lifetime through devlink private data. Mutates persistent firmware/flash state when loading stored/disk firmware or flashing through shared helper. Runtime state includes CPP handle, HWInfo, ETH table, NSP identify info, MIP/rtsym table, mailbox symbol pointer, firmware-loaded flags, VF limits/count, dumpspec, workqueue, vNIC/port lists, and hwmon pointer.

## Dependencies and Integration Points
Depends on Linux PCI/devlink/firmware/SR-IOV APIs, NFP CPP/nfpcore/NSP/rtsym/HWInfo/MIP layers, app abstractions, common netdev probe/remove, hwmon, debugfs, and ABI constants from `nfp_abi.h`. Exports helpers used by devlink, shared-buffer, app, and vNIC code.

## Risks
Firmware policy handling is complex: multiple PFs/interfaces may share loading responsibility, and `unload_fw_on_remove` is intentionally conservative. Mailbox command polling can timeout or race if firmware does not clear command state. Probe unwind must match every successful allocation. SR-IOV disable refuses assigned VFs, leaving hardware enabled but driver state partially constrained.

## Test Signals
PF probe/remove/shutdown across supported PCI IDs, firmware found/not found/load-from-flash policies, reset policies, board initialization timeout, NSP unavailable, runtime symbol missing/small mailbox, SR-IOV enable over limit/disable with assigned VFs, flash update, and module init failure after PF driver registration but before VF driver registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_main.h

## Purpose
Declares PF-wide NFP driver state, firmware dump structures, and cross-module helpers for PCI probe/remove, hwmon, runtime-symbol access, PF mailbox commands, flash update, dumps, shared buffers, devlink params, and link-rate conversion.

## Important APIs, Types, and Functions
- `struct nfp_dumpspec` stores firmware dump TLV data.
- `struct nfp_pf` is the PF container with PCI/CPP/app handles, BAR mappings, mailbox symbol, MSI-X entries, SR-IOV state, firmware metadata, HWInfo/ETH/NSP tables, hwmon/debugfs, vNIC/port lists, workqueue, refresh work, shared buffers, and counts.
- Declares exported helpers including `nfp_net_pci_probe/remove()`, `nfp_hwmon_register/unregister()`, `nfp_pf_rtsym_read_optional()`, `nfp_pf_map_rtsym()`, `nfp_mbox_cmd()`, `nfp_flash_update_common()`, dump helpers, shared-buffer helpers, devlink params, and speed/link-rate conversions.

## Control Flow
No executable flow. This header defines the PF state contract used by probe, devlink, app, netdev, hwmon, dump, and shared-buffer modules.

## State and Persistence Behavior
`struct nfp_pf` centralizes mutable PF runtime state. Fields that may change after probe are documented as protected by the devlink instance lock. Persistent device/firmware state is accessed through handles in this struct but not stored on disk here.

## Dependencies and Integration Points
Depends on Linux PCI, workqueue, ethtool, devlink, list types, and many forward-declared NFP core structs. It is included by almost every PF-level source file in this subset.

## Risks
The PF struct has broad ownership and locking requirements. Misusing fields that require devlink lock can race with port refresh, SR-IOV, or devlink operations. The comment has a typo ("proble") but the locking contract is clear.

## Test Signals
Build coverage across modules, lockdep for devlink-locked fields, probe/remove leak checks, and validation of declared helpers through devlink/hwmon/shared-buffer/dump paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net.h

## Purpose
Defines the core data structures, constants, BAR/QCP accessors, ring/vector state, datapath state, vNIC state, flow steering entries, mailbox async-message entries, and exported common netdev APIs for the NFP network device driver.

## Important APIs, Types, and Functions
- Constants define control/QCP BAR indices, queue/vector limits, default descriptor counts, RX headroom/non-data sizing, VXLAN port count, MSI-X vector layout, and descriptor helper macros.
- `struct nfp_net_tx_ring`, `struct nfp_net_rx_ring`, and `struct nfp_net_r_vector` hold per-ring/per-vector pointers, DMA state, queues, NAPI/tasklet state, XDP/XSK state, IRQ data, DIM, and stats.
- `struct nfp_net_dp` is the mutable datapath configuration cloned during reconfiguration: ring arrays, counts, MTU, buffer size, XDP program, ctrl bits, DMA direction, ops, and XSK pools.
- `struct nfp_net` is the full vNIC object: datapath, capabilities, RSS, IRQs, reconfig state machine, BAR locks, coalesce settings, QCP bars, TLS/IPsec state, mailbox state, debugfs, app/port pointers, async mailbox work, and flow steering.
- Inline BAR and QCP accessors (`nn_readl`, `nn_writel`, `nfp_qcp_wr_ptr_add`, etc.) centralize MMIO access.
- Prototypes expose allocation/init/clean, control open/close, firmware reconfig, mailbox, IRQ, TLS, ring reconfig, flow steering, RSS/coalesce, debugfs, and netdev ops.

## Control Flow
This header underpins the common lifecycle: allocation fills `nfp_net`, init reads capabilities and initializes netdev/control state, open prepares vectors/rings and enables firmware, NAPI/datapath updates rings/vectors, reconfiguration clones and swaps `nfp_net_dp`, and clean/free tears down registered resources.

## State and Persistence Behavior
Most state is volatile kernel runtime state mirrored to firmware through control BARs and QCP queues. The reconfiguration fields serialize synchronous and posted firmware updates. Stats are per-vector and protected with seqlocks. TLS/IPsec/mailbox/flow-steering fields track offloaded firmware resources but are cleaned during netdev teardown.

## Dependencies and Integration Points
Depends on Linux netdevice, PCI, interrupts, DIM, workqueue, XDP, semaphore, and NFP control ABI. Integrates NFD3/NFDK datapath ops, app layer, crypto offloads, XSK, devlink/debugfs, and firmware BAR configuration.

## Risks
This is a high-coupling header: layout or semantic changes affect every datapath and lifecycle file. Ring pointer math assumes power-of-two descriptor counts via `D_IDX`. BAR access locking is caller-managed; missing `nn_ctrl_bar_lock()` can corrupt mailbox/reconfig operations. Reconfig and async mailbox state require careful flush/wait during clean.

## Test Signals
Broad build coverage, lockdep around BAR/devlink locks, open/close/reconfig stress, queue-count changes, XDP/XSK toggles, RSS/coalesce operations, TLS/IPsec offload enable/disable, flow steering add/delete, and debugfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_common.c

## Purpose
Implements common PF/VF vNIC behavior independent of NFD3 versus NFDK datapath: firmware reconfiguration, mailbox access, IRQ/vector setup, open/close, ring reconfiguration, MTU/features/RSS/coalesce, multicast/VLAN/flow steering, XDP/XSK hooks, netdev ops, UDP tunnel sync, allocation/init/clean, TLS/IPsec initialization, and stats.

## Important APIs, Types, and Functions
- Reconfig machinery: `__nfp_net_reconfig()`, `nfp_net_reconfig()`, `nfp_net_reconfig_post()`, timer-based async reconfig, and mailbox wrappers serialize firmware updates through BAR update fields and QCP config queue.
- IRQ/lifecycle: `nfp_net_irqs_alloc/assign/disable()`, auxiliary IRQ request/free, `nfp_net_open_alloc_all()`, `nfp_net_set_config_and_enable()`, `nfp_net_clear_config_and_disable()`, `nfp_net_netdev_open()`, `nfp_net_netdev_close()`, `nfp_ctrl_open()`, and `nfp_ctrl_close()`.
- Offload/config: RSS key/table writing, coalesce/DIM work, `nfp_net_set_features()`, feature fix/check, bridge mode, UDP tunnel sync, XDP driver/HW setup, XSK setup delegation, TLS TX fallback/undo, VLAN filter mailbox, multicast mailbox, and flow steering add/delete.
- Object lifecycle: `nfp_net_alloc()`, `nfp_net_free()`, `nfp_net_init()`, `nfp_net_clean()`, `nfp_net_read_caps()`, and `nfp_net_netdev_init()`.
- Exports two netdev ops tables: `nfp_nfd3_netdev_ops` and `nfp_nfdk_netdev_ops`, differing mainly in start_xmit and XSK wakeup support.

## Control Flow
Allocation reads firmware version, selects datapath ops, validates DMA mask, initializes queue counts, locks, TLV caps, and common control mailbox. Init reads firmware capabilities, computes MTU/freelist size, initializes RSS/coalesce/control bits, disables firmware rings, initializes netdev features/offloads, TLS/IPsec, vectors, async mailbox work, flow steering list, and registers netdev.

Open requests auxiliary and queue IRQs, prepares RX/TX rings through datapath ops, assigns rings to vectors, configures queue counts, enables physical port, writes RSS/coalesce/ring/MAC/MTU/freelist config, fills RX freelists, enables firmware, enables NAPI/IRQs and TX queues, then reads link status. Close disables IRQs/NAPI/TX, unsyncs multicast if needed, disables firmware and rings, disables port, frees rings and IRQs.

Ring/MTU/XDP reconfiguration clones `nfp_net_dp`, adjusts counts and DMA offsets, validates XDP/XSK constraints, prepares new resources if running, closes stack, disables firmware, swaps datapath, tries to enable new config, attempts rollback on failure, frees old resources, and reopens stack.

## State and Persistence Behavior
Maintains volatile vNIC state mirrored into firmware via BARs. Reconfig state (`reconfig_posted`, timer, sync-present flag) merges async updates while allowing synchronous callers to take ownership. Async mailbox messages are queued in memory and flushed during clean. Flow steering rules are stored in `nn->fs.list` and removed from firmware during clean. Feature bits are mirrored between `netdev->features`, `nn->dp.ctrl`, and firmware.

## Dependencies and Integration Points
Depends on Linux netdev/ethtool/VLAN/bridge/BPF/XDP/XSK/TLS/XFRM/DIM/PCI APIs, NFP control ABI, datapath ops, app callbacks, port operations, crypto/TLS/IPsec helpers, SR-IOV helpers, common control mailbox, and ring helpers. It is the central integration file for `nfp_net.h`.

## Risks
Firmware reconfig serialization is subtle; posted updates can be merged, cancelled, or taken over by sync callers. Open/close and ring reconfig have many partial-resource unwind paths. Feature negotiation must keep firmware ctrl bits and netdev advertised features consistent, especially mutually exclusive VLAN stripping and TSO/TXVLAN limitations. `nfp_net_ring_reconfig()` rollback can fail, leaving firmware communication broken. Async multicast mailbox work may outlive netdev changes unless flushed correctly.

## Test Signals
Probe/init with NFD3 and NFDK firmware, netdev open/close loops, `ip link set mtu`, ethtool ring/RSS/coalesce changes, feature toggles, VLAN add/del, multicast list churn, XDP attach/detach and XSK pool setup, TLS/IPsec configs, flow steering rules, bridge VEPA/VEB, VXLAN port sync, forced firmware reconfig timeout/error, and cleanup with pending async mailbox work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ctrl.c

## Purpose
Parses firmware TLV capabilities from the vNIC control BAR into `struct nfp_net_tlv_caps`, including ME frequency, mailbox location, representor capability, common control-message types, crypto/TLS ops, and vNIC stats offsets.

## Important APIs, Types, and Functions
- `nfp_net_tlv_caps_reset()` initializes defaults: 1200 MHz ME frequency, legacy mailbox base, and legacy mailbox value size.
- `nfp_net_tls_parse_crypto_ops()` validates crypto TLV length, reads crypto ops, stores crypto enable offset, and records whether the RX stream-scan variant was parsed.
- `nfp_net_tlv_caps_parse()` walks TLV headers from `NFP_NET_CFG_TLV_BASE` to BAR end, validates alignment/bounds, handles known types, warns on experimental types, ignores optional unknown TLVs, and rejects required unknown TLVs.

## Control Flow
`nfp_net_alloc()` calls the parser after selecting datapath ops. The parser resets defaults, exits successfully if no TLV header exists, otherwise loops until an END TLV with zero length. Each TLV advances past the header, validates length, updates capability fields, and advances by payload length.

## State and Persistence Behavior
Only fills caller-owned `nfp_net_tlv_caps`. Firmware TLV memory is read-only from the driver perspective. Defaults preserve compatibility with firmware that lacks TLV capability blocks.

## Dependencies and Integration Points
Depends on NFP control BAR TLV constants from `nfp_net_ctrl.h`, device logging, MMIO reads, and `nfp_net.h` capability storage. Parsed values drive mailbox bounds, IRQ moderation timing, representor support, TLS/crypto setup, common control mailbox, and vNIC stats.

## Risks
Misaligned or oversized TLVs abort vNIC allocation. `vnic_stats_cnt = length / 10` is unusual and relies on firmware record sizing. Legacy and new crypto TLVs interact: an RX stream-scan TLV suppresses later legacy parsing. Required unknown TLVs intentionally fail probe, so firmware/driver version compatibility depends on correct required bits.

## Test Signals
Firmware with no TLV, valid END TLV, malformed lengths, oversized payloads, required unknown TLV, MBOX zero-length disabling mailbox, crypto TLV length errors, both crypto TLV variants, and misaligned VNIC stats TLV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ctrl.c -->
