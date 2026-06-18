# Research: subset-b-005947

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nexthop.h -->
# sources/distributed-fs/ceph-client/include/net/nexthop.h

Purpose: defines the generic nexthop object model shared by IPv4 FIB, IPv6 FIB, FDB routes, resilient nexthop groups, and switchdev/offload notification consumers.

Important APIs and types: `struct nexthop`, `struct nh_info`, `struct nh_group`, `struct nh_grp_entry`, `struct nh_res_table`, and `struct nh_res_bucket` model single and grouped nexthops. `struct nh_config` is the netlink/control-plane parse product. Notifier payloads describe single nexthops, groups, resilient tables/buckets, and group hardware statistics. Helpers include `nexthop_find_by_id()`, `nexthop_get()/put()`, `nexthop_select_path()`, `nexthop_fib_nhc()`, IPv6/FDB result helpers, and offload flag/stat update APIs.

Control flow: route lookups hold RCU or RTNL, select a single nexthop from a group, then expose the embedded `fib_nh_common`, `fib_nh`, or `fib6_nh`. Netlink changes replace RCU pointers and notify listeners; resilient groups maintain bucket tables and migration/upkeep state.

State and persistence: all state is netns-local kernel memory: rb-tree membership, FIB user lists, FDB users, group backrefs, refcounts, resilient bucket timestamps, hardware packet counters, and offload/trap state. Persistence is delegated to userspace route configuration.

Dependencies and integration points: depends on netdevice, netlink, IPv4/IPv6 FIB internals, RCU/refcounting, notifier blocks, switchdev-style offloads, and rtnetlink nexthop configuration.

Risks and test signals: risks include stale RCU dereferences, unbalanced refcounts, resilient bucket migration mistakes, mixed IPv4/IPv6 group handling, and notifier/offload drift. Test nexthop create/replace/delete, multipath selection, blackhole/FDB nexthops, device removal, IPv6 route interaction, resilient bucket replacement, and hardware stats reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nexthop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/digital.h -->
# sources/distributed-fs/ceph-client/include/net/nfc/digital.h

Purpose: declares the NFC Digital Protocol stack driver-facing interface for initiator and target mode RF framing, command exchange, polling, NFC-DEP state, and CRC handling.

Important APIs and types: RF/framing enums define hardware configuration values. `struct digital_tg_mdaa_params` carries automatic anti-collision listen-mode responses. `struct nfc_digital_ops` supplies synchronous configure hooks and asynchronous send/listen hooks. `struct nfc_digital_dev` stores the backing `nfc_dev`, supported protocols, headroom/tailroom, poll technology rotation, command queues, delayed polling, NFC-DEP counters, payload limits, CRC helpers, and driver data. Allocation/registration/free helpers wrap the stack lifecycle.

Control flow: drivers allocate/register a digital device with ops, the stack configures RF technology and framing, queues serialized commands, and requires each asynchronous op to complete through `nfc_digital_cmd_complete_t`, including timeout/error responses as `ERR_PTR()`.

State and persistence: runtime state is in-memory only: current protocol/RF tech, DEP PNI/DID/RWT, chained skb, command queue, saved skb, and polling index. No durable device state is stored.

Dependencies and integration points: integrates with `net/nfc/nfc.h`, `sk_buff`, workqueues, mutexes, and NFC core target/data-exchange APIs.

Risks and test signals: high-risk behavior is missing async completion, wrong timeout handling, CRC ownership mismatch, and target-mode RF detection errors. Test initiator polling, target listen/listen_mdaa/listen_md, aborts, timeout callbacks, CRC-capability matrices, chaining, and unregister with queued work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/digital.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/hci.h -->
# sources/distributed-fs/ceph-client/include/net/nfc/hci.h

Purpose: defines the NFC HCI device abstraction, pipe/gate constants, command/event helpers, and driver callbacks for NFC controllers using the ETSI HCI protocol.

Important APIs and types: `struct nfc_hci_ops` covers device open/close, session load/readiness, complete-buffer transmit, polling, DEP link management, target discovery, initiator/target data exchange, secure element operations, firmware download, and vendor events/commands. `struct nfc_hci_dev` stores NFC core device, LLC instance, gate-to-pipe mappings, tx/rx queues, timers, pending command, callback context, general bytes, version fields, and quirks. Public helpers allocate/register devices, connect/disconnect gates, get/set parameters, send commands/events, reset pipes, receive frames, and convert results.

Control flow: lower LLC/driver receive paths call frame/response/command/event entry points; upper NFC operations issue HCI commands through pipe/gate routing and serialize pending command state with timers/work.

State and persistence: session identity, pipe table, gate map, queued messages, pending command, firmware/version metadata, and async callbacks are in-memory controller-session state. Persistence depends on controller session loading.

Dependencies and integration points: depends on NFC core and LLC, skbuff queues, timers, workqueues, and secure element APIs.

Risks and test signals: risks include pipe map corruption, command timer races, incomplete lower-layer transmit, shutdown with queued messages, and quirk-specific clear behavior. Test HCI open/session load, pipe creation/reset, parameter get/set, event dispatch, DEP up/down, SE IO, firmware download, and LLC failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/hci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/llc.h -->
# sources/distributed-fs/ceph-client/include/net/nfc/llc.h

Purpose: exposes the NFC Link Layer Control manager abstraction that connects HCI framing to a selected lower link implementation such as `nop` or `shdlc`.

Important APIs and types: `LLC_NOP_NAME` and `LLC_SHDLC_NAME` select implementations. Callback types route received skbs to HCI, transmitted skbs to the driver, and failures upward. `struct nfc_llc` is opaque; public functions allocate/free, start/stop, receive from driver, transmit from HCI, and initialize/exit registered LLC providers.

Control flow: HCI allocates an LLC by name, starts it after device open, sends HCI packets through `nfc_llc_xmit_from_hci()`, and lower drivers feed frames into `nfc_llc_rcv_from_drv()`. The LLC invokes callbacks for decoded delivery or failure.

State and persistence: state is implementation-private runtime link state, including queues/windowing for SHDLC. No persistent configuration lives here.

Dependencies and integration points: includes HCI and skbuff headers and sits between NFC HCI core and physical/controller transport drivers.

Risks and test signals: risk is lifecycle mismatch across HCI unregister, link-layer retransmission/failure propagation, and skb ownership errors. Test allocation by name, start/stop idempotence, receive/transmit paths, bad frames, and failure callback teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/llc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/nci.h -->
# sources/distributed-fs/ceph-client/include/net/nfc/nci.h

Purpose: defines NCI wire constants, header manipulation macros, opcodes, command/response/notification layouts, and RF/NFCEE protocol structures for NFC Controller Interface packets.

Important APIs and types: constants cover statuses, RF tech/modes, bit rates, protocols, interfaces, config tags, reset/deactivate types, GIDs, SPI headroom, and packet sizes. Header structs `nci_ctrl_hdr` and `nci_data_hdr` plus macros `nci_mt()`, `nci_pbf()`, `nci_opcode_*()`, and `nci_conn_id()` parse/construct packet headers. Packed structs describe core reset/init/config/connection commands, RF discovery/map/select/deactivate commands, NFCEE management, reset/init/config responses, credit/error notifications, RF discovery/activation/deactivation notifications, and NFCEE discovery TLVs.

Control flow: NCI core builds command payloads with these layouts, parses controller responses/notifications by opcode, and translates RF discovery/activation data into generic NFC targets and connection state.

State and persistence: this header stores no state; it specifies transient on-wire packet formats.

Dependencies and integration points: depends on NFC core size constants and is consumed by `nci_core.h` and transport drivers.

Risks and test signals: risks are packed-layout drift, variable-length array bounds, NCI 1.x/2.x parsing differences, endian mistakes, and duplicate opcode definitions. Test controller init/reset, RF discovery for A/B/F/V, activation params, NFCEE discovery, credits, malformed lengths, and NCI v2 init responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/nci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/nci_core.h -->
# sources/distributed-fs/ceph-client/include/net/nfc/nci_core.h

Purpose: declares the NCI core runtime device model, driver callbacks, connection/HCI support, request machinery, and SPI/UART transport helper interfaces.

Important APIs and types: `enum nci_flag` and `enum nci_state` model initialization, up/down, discovery, poll/listen activation, and data exchange. `struct nci_ops` provides driver hooks for transport open/close/send, setup, firmware, RF protocol mapping, secure elements, and HCI callbacks. `struct nci_dev` stores NFC core device, NCI/HCI state, connection lists, timers, workqueues, command/rx/tx queues, request completion fields, discovered targets, controller capabilities, reassembly buffers, and activation metadata. SPI and UART helper structs define transport state and callbacks.

Control flow: drivers allocate/register an NCI device, core reset/init and setup run as serialized requests, command/data queues feed transport send, rx workers dispatch rsp/ntf/data packets, and connection credits gate data flow.

State and persistence: runtime-only controller state includes NCI version/features, supported interfaces, active targets, NFCEE/HCI pipe state, current connection parameters, queues, timers, and driver data.

Dependencies and integration points: integrates generic NFC core, NCI wire formats, HCI-over-NCI, SPI, TTY/UART, skbuff queues, workqueues, timers, completions, and secure element callbacks.

Risks and test signals: risks include request timeout races, credit accounting errors, data reassembly leaks, state transition bugs, and transport close while work is pending. Test reset/init, set-config, discovery/select/deactivate, logical connection create/close, data exchange, HCI session init, SPI CRC mode, UART line discipline setup, and unregister teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/nci_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/nfc.h -->
# sources/distributed-fs/ceph-client/include/net/nfc/nfc.h

Purpose: defines the generic kernel NFC device API used by digital, HCI, NCI, and controller drivers to expose polling, target activation, DEP, secure element, firmware, and vendor-command functionality.

Important APIs and types: `struct nfc_ops` is the main driver callback table. `struct nfc_target` describes discovered peer identifiers and activation data. `struct nfc_se` and `struct nfc_evt_transaction` model secure elements and SE transactions. `struct nfc_vendor_cmd` supports vendor netlink commands. `struct nfc_dev` stores target lists, device model state, polling/active target flags, DEP state, rfkill, generic netlink command context, secure elements, vendor commands, check-presence work/timer, and ops.

Control flow: drivers allocate/register `nfc_dev`; userspace netlink operations call ops; drivers report target discovery/loss, DEP link state, target-mode data, firmware completion, secure element events, and driver failures back to core helpers.

State and persistence: all state is kernel runtime device state. Secure element list and target generations are not persistent; controller firmware may persist outside this API.

Dependencies and integration points: depends on Linux NFC UAPI, device model, skbuffs, rfkill, generic netlink, timers/work, raw NFC sockets, and upper stack wrappers.

Risks and test signals: risks include active target lifetime, vendor reply misuse outside `doit()`, concurrent polling/dev_down, rfkill teardown, and check-presence races. Test registration/unregistration, polling, activation/deactivation, DEP link up/down, transceive callbacks, SE add/remove/transaction, firmware completion, raw socket tap, and vendor command replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nfc/nfc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nl802154.h -->
# sources/distributed-fs/ceph-client/include/net/nl802154.h

Purpose: declares the internal generic netlink command and attribute numbers for IEEE 802.15.4 WPAN PHY/device management, scanning, association, beacons, and optional experimental security configuration.

Important APIs and types: `enum nl802154_commands` defines GET/SET/NEW/DEL operations for PHYs, interfaces, channels, PAN/short addresses, CCA, retries, backoff, LBT, ACK defaults, netns moves, scanning, beacons, association, and security objects. Attribute enums describe PHY/interface properties, scan parameters/results, coordinator data, CCA modes/options, boolean capabilities, address modes, peer types, and experimental key/security-level/device attributes.

Control flow: nl802154 policy and command handlers use these numeric IDs to parse userspace requests and emit notifications. The comments warn order is ABI-sensitive even though this file is not shipped as UAPI here.

State and persistence: no state is stored; the enums name netlink fields that operate on cfg802154/mac802154 runtime objects and optional security tables.

Dependencies and integration points: depends only on Linux types but integrates with generic netlink, WPAN PHY capabilities, MAC scanning/beaconing/association, netns migration, and optional security code.

Risks and test signals: risks include enum renumbering ABI breaks, policy drift when adding attributes, experimental security config mismatches, and invalid scan/channel combinations. Test netlink dumps/sets, scan trigger/abort/done, beacon start/stop, association flows, capability reporting, netns moves, and experimental security object CRUD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nl802154.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nsh.h -->
# sources/distributed-fs/ceph-client/include/net/nsh.h

Purpose: defines Network Service Header structures, masks, constants, and skb helpers used to push/pop and parse service function chaining metadata.

Important APIs and types: `struct nshhdr` represents the base/service-path header plus MD type 1 fixed context or MD type 2 TLV metadata. `struct nsh_md1_ctx` and `struct nsh_md2_tlv` model metadata formats. Masks/shifts decode version, flags, TTL, length, MD type, SPI, and SI. Helpers return the skb NSH header, header length, version, flags, TTL, and update flags/TTL/length fields. `nsh_push()` and `nsh_pop()` manipulate encapsulation.

Control flow: datapath code positions the network header on NSH, validates length/type, decrements or sets TTL/SI elsewhere, and uses push/pop around encapsulation and decapsulation.

State and persistence: no persistent state; all data is per-packet header state in skb linear data.

Dependencies and integration points: depends on skbuff accessors and byte-order helpers; integrates with tunnel/classifier actions and service function chaining encapsulation.

Risks and test signals: risks include malformed length causing out-of-bounds access, MD type 2 TLV padding mistakes, incorrect endian masking, TTL loop-detection errors, and skb headroom/tailroom failures. Test push/pop round trips, MD1 and MD2 lengths, max header length, OAM/unknown protocol handling, TTL edge cases, and malformed packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/nsh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/page_pool/helpers.h -->
# sources/distributed-fs/ceph-client/include/net/page_pool/helpers.h

Purpose: provides driver-facing inline helpers for page_pool allocation, fragment allocation, netmem allocation, refcounting, recycling, DMA address access, DMA sync, and stats access.

Important APIs and types: wrappers include `page_pool_dev_alloc_pages()`, `page_pool_dev_alloc_frag()`, `page_pool_alloc_netmem()`, `page_pool_dev_alloc_netmem*()`, `page_pool_alloc_va()`, `page_pool_put_page()`, `page_pool_put_full_page()`, `page_pool_recycle_direct()`, `page_pool_free_va()`, `page_pool_get_dma_addr*()`, `page_pool_dma_sync_for_cpu()`, `page_pool_dma_sync_netmem_for_cpu()`, `page_pool_get()/put()`, `page_pool_nid_changed()`, and `page_pool_is_unreadable()`. Fragment helpers manipulate `pp_ref_count` over page/netmem references.

Control flow: RX drivers allocate from the pool on the NAPI hot path, optionally split pages into fragments, attach buffers to skbs/XDP, and return them through put/recycle helpers. Last-reference detection determines whether the pool recycles directly, enqueues to ring, or releases mappings.

State and persistence: updates in-flight fragment refs, pool user refcount, allocation cache, fragment offset, DMA metadata, and optional stats. No durable state.

Dependencies and integration points: depends on `page_pool/types.h`, DMA mapping, netmem, skb recycling, XDP memory, NAPI safe context, and optional page pool stats.

Risks and test signals: risks include wrong `dma_sync_size`, using direct recycling outside safe context, unreadable netmem VA access, negative fragment refs, DMA address packing on 32-bit, and missing last-fragment sync. Test RX recycling, split pages, XDP_DROP direct recycle, DMA sync paths, highmem VA allocation, unreadable memory providers, and CONFIG_PAGE_POOL off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/page_pool/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/page_pool/memory_provider.h -->
# sources/distributed-fs/ceph-client/include/net/page_pool/memory_provider.h

Purpose: declares the page_pool external memory-provider interface used for netmem/net_iov backed RX buffers, including queue binding and provider lifecycle hooks.

Important APIs and types: `struct memory_provider_ops` supplies provider allocation, release, init/destroy, netlink fill, and uninstall callbacks. Helpers set DMA address and page_pool backpointers on net_iov objects, open/close RX queue memory providers, and place accounted netmem directly into the page_pool allocation cache from provider allocation paths.

Control flow: netdev queue setup binds a memory provider via `netif_mp_open_rxq()`, page_pool calls provider `alloc_netmems()` and `release_netmem()`, netlink can query provider state through `nl_fill()`, and queue teardown invokes close/uninstall/destroy.

State and persistence: provider-private state is referenced by `mp_priv`; page_pool records provider ops/private pointers and net_iov metadata. Configuration persists only as runtime queue binding.

Dependencies and integration points: integrates page_pool, netmem/net_iov, netdev RX queues, netlink extack, and skbuff netlink reporting.

Risks and test signals: risks include placing netmem into a full cache, mismatched page_pool/net_iov backpointers, stale DMA address metadata, queue close races, and drivers reading unreadable netmem. Test provider bind/unbind, allocation/release loops, netlink dumps, unreadable buffer RX paths, DMA address setup, and queue teardown under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/page_pool/memory_provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/page_pool/types.h -->
# sources/distributed-fs/ceph-client/include/net/page_pool/types.h

Purpose: defines page_pool flags, parameters, allocation/recycle stats, memory-provider parameters, the internal `struct page_pool`, and core allocation/destruction prototypes.

Important APIs and types: flags cover DMA mapping, sync-for-device, system pools, and unreadable netmem. `struct page_pool_params` separates hot `fast` fields from slow/control fields such as netdev and queue index. `struct pp_alloc_cache` is the NAPI-side cache. `struct page_pool` stores fast params, CPU/NAPI assumptions, fragment state, delayed release work, stats, XDP memory ID, cache, ptr_ring recycle store, memory provider hooks, DMA xarray, release counters, user refcount, destroy counter, and user-visible ID/list state. Prototypes allocate pages/netmem/frags, create pools, destroy, attach XDP memory, bulk put, and update NUMA node.

Control flow: drivers create one pool per RX queue/NAPI context, allocate from cache/ring/page allocator or provider, recycle through cache/ring/release paths, and destroy after in-flight pages drain.

State and persistence: state is runtime pool memory and DMA mappings; user-facing IDs aid diagnostics but do not persist.

Dependencies and integration points: depends on DMA direction, ptr_ring, xarray, netmem, NAPI, XDP, workqueues, and optional stats.

Risks and test signals: risks include violating single-consumer allocation assumptions, ptr_ring producer/consumer races, lingering in-flight pages during destroy, incorrect flags with unreadable netmem, and stats cacheline contention. Test per-RX-queue pools, high-order pages, NUMA changes, XDP mem disconnect, bulk return, stats, memory-provider pools, and CONFIG_PAGE_POOL disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/page_pool/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pfcp.h -->
# sources/distributed-fs/ceph-client/include/net/pfcp.h

Purpose: defines PFCP-over-UDP header layouts, metadata, headroom constants, and helpers for PFCP virtual netdevices.

Important APIs and types: `struct pfcphdr` contains flags, message type, and length. `struct pfcphdr_node` and `struct pfcphdr_session` model node and session message suffixes, including SEID, sequence number, and message priority. `struct pfcp_metadata` carries tunnel metadata type and SEID. Constants define port 8805, flags, version mask, header sizes, IPv4/IPv6 headroom, and node/session metadata types. Inline helpers locate PFCP headers after `udp_hdr()` and test `netif_is_pfcp()`.

Control flow: UDP tunnel/device code parses the base header, branches on SEID/session flag, accesses node/session suffix, and uses metadata for encapsulation/decapsulation.

State and persistence: no state is stored here; PFCP netdevices and tunnel metadata hold runtime state elsewhere.

Dependencies and integration points: depends on UDP/IP/IPv6/ethernet UAPI headers, dst metadata, netdevice rtnl link ops, and skbuff UDP header positioning.

Risks and test signals: risks include insufficient skb length checks before inline casts, endian/bitfield priority mismatch, wrong headroom for encapsulation, and device-kind string drift. Test node/session packet parsing, IPv4/IPv6 encapsulation headroom, malformed short packets, SEID metadata propagation, and PFCP link creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pfcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phonet/gprs.h -->
# sources/distributed-fs/ceph-client/include/net/phonet/gprs.h

Purpose: declares the GPRS-over-Phonet pipe endpoint hooks used by PEP sockets to expose readable/writable data paths.

Important APIs and types: forward declarations for `sock` and `sk_buff`; functions `pep_writeable()`, `pep_write()`, `pep_read()`, `gprs_attach()`, and `gprs_detach()` form the minimal interface.

Control flow: a Phonet/PEP socket attaches GPRS handling to a socket, checks writability, writes skbs into the pipe endpoint, reads received skbs, and detaches on teardown.

State and persistence: state is maintained in the PEP/GPRS socket implementation, not this header. It is connection-lifetime only.

Dependencies and integration points: integrates Phonet pipe endpoint sockets with GPRS network data handling and skbuff ownership.

Risks and test signals: risks include attach/detach lifetime mismatches, writeability races with pipe flow control, and skb ownership leaks. Test GPRS attach/detach, read/write under credit changes, socket close with queued skbs, and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phonet/gprs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phonet/pep.h -->
# sources/distributed-fs/ceph-client/include/net/phonet/pep.h

Purpose: defines Phonet Pipe End Point socket state, pipe protocol headers, message IDs, error codes, states, subblocks, and flow-control modes.

Important APIs and types: `struct pep_sock` embeds `pn_sock` and stores listener/connected socket state, control request queue, TX/RX credits, interface index, peer type, pipe handle, flow-control selections, auto-enable, and alignment flag. `struct pnpipehdr` models pipe message headers. Constants enumerate pipe create/remove/data, PEP connect/disconnect/reset/enable/control/disable, status indications, invalid handle, common type, flow-control models, and status/error states. `pep_sk()` and `pnp_hdr()` cast from sockets/skbs.

Control flow: Phonet stream operations exchange pipe protocol messages, negotiate flow control, queue control requests, consume/grant credits, and deliver aligned or normal data frames.

State and persistence: per-socket pipe state is runtime only: queues, credits, pipe handle, peer type, listener link, and selected flow-control mode.

Dependencies and integration points: depends on Phonet core socket types and skbuffs; integrates with `phonet_stream_ops`, GPRS helper hooks, and Phonet packet headers.

Risks and test signals: risks include credit underflow/overrun, control queue overflow, invalid pipe handle handling, listener/child lifetime, and aligned data parsing. Test pipe create/connect/enable/data/disable/remove, all flow-control modes, ctrlreq queue limit, peer errors, and socket close while connected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phonet/pep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phonet/phonet.h -->
# sources/distributed-fs/ceph-client/include/net/phonet/phonet.h

Purpose: declares the kernel Phonet socket core: protocol socket base layout, lookup/hash/resource APIs, send helper, address extraction helpers, protocol registration, sysctl/init hooks, and ioctl dispatch.

Important APIs and types: `struct pn_sock` embeds `struct sock` first and stores source/destination Phonet objects plus resource. `struct phonet_protocol` registers socket type, proto, and proto_ops. Helpers cast sockets, access Phonet headers/messages in skbs, populate source/destination `sockaddr_pn`, register/unregister protocols, bind/unbind resources, send skbs, and process resource ioctls.

Control flow: socket creation uses registered Phonet protocols; bind/hash/resource tables locate sockets; receive paths extract source/destination addresses from skb headers; send paths use `pn_skb_send()` to target Phonet addresses.

State and persistence: per-socket object/resource fields and namespace hash/resource bindings are runtime-only. Sysctl values may tune behavior but are not stored here.

Dependencies and integration points: depends on Linux Phonet UAPI, socket core, skbuffs, net namespaces, proc/sysctl, and ISI/PEP protocols.

Risks and test signals: risks include assuming `pn_sock` is first in protocol structs, resource binding collisions, ioctl user-copy errors, skb header offset assumptions, and broadcast delivery fanout. Test datagram/stream sockets, bind/unbind resource, port allocation, broadcasts, ioctl add/delete resource, and protocol register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phonet/phonet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phonet/pn_dev.h -->
# sources/distributed-fs/ceph-client/include/net/phonet/pn_dev.h

Purpose: declares Phonet network-device address and route management structures and functions.

Important APIs and types: `struct phonet_device_list` stores netns device list and lock. `struct phonet_device` links a net_device, 64-address bitmap, and RCU head. APIs initialize/exit device and netlink support, add/delete/get/lookup addresses, notify address changes, add/delete routes, notify route changes, and find route output devices under RCU or refcounted lookup.

Control flow: netdevice/netlink operations add addresses and routes; packet output uses destination address lookup to choose a Phonet device; notifications report RTM-style address/route events.

State and persistence: state is netns-local runtime lists, address bitmaps, and routing mappings. It is not persisted by the header.

Dependencies and integration points: depends on net_device, net namespaces, spinlocks, RCU, seq_file proc operations, and Phonet netlink.

Risks and test signals: risks include address bitmap bounds, RCU use-after-free on devices, route lookup after device removal, and notification mismatches. Test address add/delete/lookup, route add/delete/output, netns teardown, device unregister, and proc seq iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phonet/pn_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phy/realtek_phy.h -->
# sources/distributed-fs/ceph-client/include/net/phy/realtek_phy.h

Purpose: provides a Realtek PHY identifier constant for a dummy SFP PHY.

Important APIs and types: `PHY_ID_RTL_DUMMY_SFP` is defined as `0x001ccbff`. No functions or structs are declared.

Control flow: PHY drivers or SFP matching code include this header to compare device IDs.

State and persistence: no state.

Dependencies and integration points: integrates with PHY/SFP driver ID tables or match logic.

Risks and test signals: risks are limited to ID mismatch or stale constant use. Test compile coverage and PHY/SFP detection paths that reference the dummy ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/phy/realtek_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pie.h -->
# sources/distributed-fs/ceph-client/include/net/pie.h

Purpose: declares Proportional Integral controller Enhanced active queue management parameters, variables, stats, skb private control block, and algorithm entry points for PIE qdiscs.

Important APIs and types: `struct pie_params` stores target delay, update interval, queue limit, alpha/beta controls, ECN, bytemode, and delay-rate estimator flags. `struct pie_vars` stores current/old delay, burst allowance, dequeue timestamp/count, average dequeue rate, backlog, and drop probability. `struct pie_stats` tracks enqueue/drop/mark/limit stats. `struct pie_skb_cb` stores enqueue time and memory usage. Inline initializers set defaults; helpers validate and access qdisc skb private data. Core functions are `pie_drop_early()`, `pie_process_dequeue()`, and `pie_calculate_probability()`.

Control flow: enqueue records timestamp and may drop/mark early based on probability; dequeue updates rate/delay state; periodic update recalculates drop probability from queue delay trends.

State and persistence: qdisc-local runtime variables and stats only.

Dependencies and integration points: depends on qdisc timing, ECN helpers, skbuff control blocks, and packet scheduler core.

Risks and test signals: risks include qdisc CB size conflicts, fixed-point probability overflow, stale dequeue rate, ECN/bytemode interaction, and wrong time unit conversion. Test default parameters, ECN marking, bytemode, burst allowance, delay estimator mode, queue limit drops, and high-rate/idle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ping.h -->
# sources/distributed-fs/ceph-client/include/net/ping.h

Purpose: declares the IPv4/IPv6 ping socket protocol interface, hash sizing, IPv6 module glue, proc iteration, and send/receive helpers.

Important APIs and types: `struct pingv6_ops` supplies IPv6 error/control-message callbacks when IPv6 is modular. `struct ping_iter_state` supports proc sequence iteration. `struct pingfakehdr` carries a fake ICMP header and checksum context for send fragmentation. Functions manage port allocation/hash removal, socket init/close/bind, ICMP errors, send fragments, recvmsg, common sendmsg, receive queueing, packet receive, proc init/exit, and pingv6 init/exit.

Control flow: ping sockets bind to an ICMP identifier, sendmsg builds ICMP payload/checksum, receive path matches packets to sockets, queues skbs, and reports errors/control messages through IPv4 or IPv6 glue.

State and persistence: hash tables and socket state are runtime-only; proc iteration exposes current sockets.

Dependencies and integration points: depends on ICMP, sock/proto core, netns hash, procfs, IPv6 optional hooks, and skb drop reasons.

Risks and test signals: risks include identifier hash collisions, GID permission ranges, IPv6 module glue lifetime, checksum construction, and proc iteration races. Test bind conflicts, send/recv IPv4 and IPv6 echo, ICMP errors, proc dumps, namespace isolation, and IPv6 module unload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pkt_cls.h -->
# sources/distributed-fs/ceph-client/include/net/pkt_cls.h

Purpose: declares traffic-control classifier front-end APIs, filter extension/action plumbing, ematch trees, qevents, classifier offload descriptors, and helper predicates for software/hardware TC.

Important APIs and types: `struct tcf_walker`, `tcf_block_ext_info`, `tcf_qevent`, `tcf_exts`, ematch structs/ops, `tcf_pkt_info`, u32/matchall/BPF offload structs, cookie state, and many qdisc/classifier offload command structs are defined. APIs register classifier/ematch ops, get/put blocks/chains/protos, classify skbs, bind/unbind classes, validate/dump/destroy extensions, execute actions, set up offload callbacks/actions, and manage qevents. Inline helpers validate flags, skip hw/sw, chain 0 offload, indev matching, skb extension allocation, and hardware stats updates.

Control flow: classifier modules validate netlink config into filters/extensions, classification walks blocks/chains/protos, actions execute or offload, qevents trigger blocks, and drivers receive offload command structs through setup callbacks.

State and persistence: runtime TC state lives in blocks, chains, protos, actions, ematch data, cookies, stats, and hardware offload counters; netlink can recreate it but this header stores none.

Dependencies and integration points: integrates qdisc core, act API, flow offload, net namespaces, netdevices, BPF, ematch modules, skb extensions, and netlink extack.

Risks and test signals: risks include class binding on shared blocks, action netns lifetime, skip_hw/skip_sw invalid combos, offload stat double counting, ematch relation logic, and qevent block changes. Test classifier add/delete/replace, shared blocks, action execution, hardware offload flags/stats, ematch AND/OR/invert, BPF/u32/matchall offloads, qevents, and CONFIG_NET_CLS/ACT/EMATCH matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pkt_cls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pkt_sched.h -->
# sources/distributed-fs/ceph-client/include/net/pkt_sched.h

Purpose: declares packet scheduler core helpers, time conversion, qdisc watchdogs, qdisc registration/lookup, default FIFO helpers, and qdisc offload structures for CBS, ETF, mqprio, taprio, and related stats.

Important APIs and types: `qdisc_walker`, `qdisc_priv()`, `psched_time_t` conversion macros, `struct qdisc_watchdog`, FIFO qdisc ops, qdisc registration/default/hash APIs, rate/stab helpers, and `qdisc_run()`. Offload descriptors include `tc_query_caps_base`, CBS/ETF/mqprio/taprio caps and options, taprio schedule entries/stats, and helper functions for taprio refcounting. Other helpers compute MTU, qdisc netns, consume txtime, dump stats, warn non-work-conserving qdiscs, peek length, and init/uninit qdisc locks.

Control flow: qdiscs register ops, enqueue/dequeue under scheduler core, watchdogs schedule future dequeue, qdisc lookup maps handles, and offload structs carry netlink-derived configuration to drivers.

State and persistence: qdisc objects, timers, lock classes, hash membership, rate tables, and driver offload state are runtime-only.

Dependencies and integration points: depends on qdisc core, hrtimers, netdevices, rtnetlink policies, lockdep, VLAN, pkt_sched UAPI, and TC setup callbacks.

Risks and test signals: risks include time unit conversion errors, watchdog cancellation races, lock class leaks, non-work-conserving peek behavior, and flexible taprio offload lifetime. Test qdisc register/unregister, FIFO defaults, watchdog schedule/cancel, qdisc lookup/hash, taprio refcount, txtime timestamp clearing, stats walkers, and lockdep for nested qdiscs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pkt_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pptp.h -->
# sources/distributed-fs/ceph-client/include/net/pptp.h

Purpose: defines PPTP GRE header layout and sequence/window constants used by PPTP tunneling.

Important APIs and types: constants define PPP LCP echo request/reply codes, receive status bit mask, missing window size, sequence wrap detection macro, and header overhead. `struct pptp_gre_header` packs a GRE base header plus payload length, call ID, sequence, and acknowledgment fields.

Control flow: PPTP data paths parse GRE headers, track sequence/ack windows, detect wraparound, and account encapsulation overhead.

State and persistence: no state is stored here; tunnel/session implementations maintain sequence state.

Dependencies and integration points: depends on `net/gre.h` and Linux types; integrates PPTP with GRE and PPP handling.

Risks and test signals: risks include packed header alignment, sequence wrap edge cases, missing-window handling, and overhead miscalculation. Test GRE/PPTP packet parsing, sequence wrap from `0xffffffxx` to zero, LCP echo traffic, and malformed header lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/pptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/proto_memory.h -->
# sources/distributed-fs/ceph-client/include/net/proto_memory.h

Purpose: provides inline helpers for protocol/socket memory pressure and per-CPU fast-path accounting.

Important APIs and types: `SK_MEMORY_PCPU_RESERVE` defines the default per-CPU reserve in pages. Helpers test whether protocols have pressure accounting, read global and cgroup socket memory pressure, read allocated memory, drain per-CPU forward allocation to `proto->memory_allocated`, and add/subtract socket memory usage through per-CPU counters.

Control flow: socket allocation/free paths update per-CPU `per_cpu_fw_alloc`; when thresholds exceed `net_hotdata.sysctl_mem_pcpu_rsv`, the value is drained into the protocol atomic counter. Pressure checks combine memcg, protocol pressure, and socket bypass flag.

State and persistence: updates runtime protocol memory counters and per-CPU accounting only.

Dependencies and integration points: depends on socket/proto internals, memcg socket pressure, per-CPU counters, atomics, and net hotdata sysctls.

Risks and test signals: risks include per-CPU drift if drains are missed, bypass flag misuse, negative accounting, and pressure read races. Test TCP/UDP memory pressure, memcg pressure, per-CPU reserve sysctl changes, allocation/free balance, and protocols without pressure pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/proto_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/protocol.h -->
# sources/distributed-fs/ceph-client/include/net/protocol.h

Purpose: declares IPv4/IPv6 protocol dispatch registration structures, offload registration, and inet socket protocol switch descriptors.

Important APIs and types: `MAX_INET_PROTOS` is 256. `struct net_protocol` supplies IPv4 handler/error handler and policy flags. `struct inet6_protocol` does the same for IPv6 with extension flags. `struct net_offload` stores GSO/offload callbacks and flags. `struct inet_protosw` registers socket type/protocol to proto/proto_ops with reuse/permanent/ICSK flags. Global RCU arrays hold protocol and offload entries. Functions add/delete IPv4/IPv6 protocols and offloads and register/unregister protosw entries.

Control flow: IP receive dispatch indexes protocol arrays by 8-bit protocol, invokes handlers/error handlers, and socket creation scans registered protosw entries for type/protocol matches.

State and persistence: runtime global RCU registration tables/lists only; modules add/remove entries.

Dependencies and integration points: depends on skbuff, netdevice, IPv6 optional headers, offload callbacks, proto/proto_ops, and module registration.

Risks and test signals: risks include duplicate registrations, deleting permanent protocols, RCU lifetime errors, policy flag misuse, and IPv6 module config drift. Test add/delete protocol modules, ICMP/ICMPv6 error dispatch, GSO extension header offload, socket creation by protocol/type, and concurrent receive during unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psample.h -->
# sources/distributed-fs/ceph-client/include/net/psample.h

Purpose: declares packet sampling group state, metadata, reference helpers, and the optional psample packet emission API.

Important APIs and types: `struct psample_group` stores group list node, netns, group number, refcount, sequence, and RCU head. `struct psample_metadata` carries truncation size, ingress/egress ifindexes, output traffic class/occupancy, latency, validity bits, probability-rate flag, and user cookie. APIs get/take/put groups and, when enabled, sample packets to userspace.

Control flow: callers obtain a group, fill metadata, call `psample_sample_packet()`, and release the group. Disabled builds compile sampling to a no-op while group lifecycle functions remain declared.

State and persistence: per-netns group list/refcounts/sequence are runtime only.

Dependencies and integration points: depends on psample UAPI, RCU, net namespaces, skbuffs, and TC/switchdev sampling users.

Risks and test signals: risks include group refcount leaks, sequence wrap assumptions, metadata validity bit mismatch, and disabled-config no-op surprises. Test sampling netlink output, truncation, metadata combinations, user cookie, group get/put, namespace teardown, and CONFIG_PSAMPLE disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psnap.h -->
# sources/distributed-fs/ceph-client/include/net/psnap.h

Purpose: declares SNAP protocol client registration for datalink protocol demultiplexing.

Important APIs and types: `register_snap_client()` registers a SNAP descriptor and receive callback returning a `datalink_proto`; `unregister_snap_client()` removes it. Forward declarations cover skb, packet_type, net_device, and datalink protocol objects.

Control flow: protocol modules register a SNAP OUI/descriptor and receive callback; packet receive dispatch calls the registered function with skb/device/original-device context.

State and persistence: registration tables live in the SNAP implementation, not here, and are runtime only.

Dependencies and integration points: integrates datalink/SNAP handling with packet receive paths and netdevices.

Risks and test signals: risks include unregister while packets are in flight, descriptor collisions, and skb ownership mistakes in callbacks. Test register/unregister, receive dispatch, duplicate clients, module unload, and malformed SNAP frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psnap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psp.h -->
# sources/distributed-fs/ceph-client/include/net/psp.h

Purpose: umbrella include for PSP networking support that pulls in UAPI definitions plus PSP helper functions and core types.

Important APIs and types: this header intentionally declares no standalone APIs; it includes `<uapi/linux/psp.h>`, `net/psp/functions.h`, and `net/psp/types.h`.

Control flow: users include this top-level header when both PSP type definitions and helper functions are needed.

State and persistence: no state is stored here.

Dependencies and integration points: integrates the PSP UAPI with kernel-facing PSP device, association, skb, and socket helpers.

Risks and test signals: risk is mostly include-order or accidental code growth despite the comment directing code to subheaders. Test compile coverage for users including only this aggregate header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psp/functions.h -->
# sources/distributed-fs/ceph-client/include/net/psp/functions.h

Purpose: declares PSP driver-facing APIs plus inline socket/skb policy helpers for Packet Security Protocol associations.

Important APIs and types: driver APIs create/unregister PSP devices, encapsulate packets, receive PSP frames, and release associations. Enabled builds expose key sizing, socket/timewait association lifecycle, decrypted reply marking, association accessors, skb coalesce comparison, RX policy checks, association lookup from decrypted skb, and per-socket overhead. Disabled builds provide no-op/zero-return stubs.

Control flow: drivers register PSP-capable devices and handle encapsulation/receive; TCP sockets attach PSP associations. Receive policy checks compare skb PSP extension fields against socket/timewait association, allow certain pre-upgrade non-data packets, and otherwise return `SKB_DROP_REASON_PSP_INPUT`.

State and persistence: accesses socket/timewait `psp_assoc`, association peer_tx bit, skb decrypted flag, skb extension metadata, and device association refs. Keys/associations are runtime security state.

Dependencies and integration points: depends on skbuff extensions, TCP CB flags/sequence numbers, sockets, timewait sockets, RCU, UDP/TCP headers, and PSP types.

Risks and test signals: risks include RCU/lock misuse around association dereference, allowing wrong plaintext packets during upgrade, coalescing encrypted and plaintext skbs, stale timewait association refs, and disabled-config semantic gaps. Test PSP association attach/free, RX policy match/mismatch, FIN/non-data upgrade exceptions, skb coalescing, timewait receive, encapsulation, and CONFIG_INET_PSP disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psp/functions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psp/types.h -->
# sources/distributed-fs/ceph-client/include/net/psp/types.h

Purpose: defines PSP wire header fields, device configuration/capabilities, device state, skb extension, parsed keys, associations, stats, and driver callback table.

Important APIs and types: `struct psphdr` models PSP encapsulation header. Macros define UDP port, encapsulation length, SPI key/phase bits, header flags/version/crypt offset, and supported no-option header/trailer sizes. `struct psp_dev` stores main netdev, ops/caps/private pointer, lock/refcount, ID/generation/config, active/previous/stale association lists, core stats, and RCU head. `struct psp_assoc` stores device pointer, dev ID, generation, version, peer_tx, upgrade sequence, tx/rx keys, refcount/work/list, and driver data. `struct psp_dev_ops` lets drivers set config, rotate keys, allocate RX SPI/key, add/delete TX keys, and report stats.

Control flow: PSP core configures devices, rotates generations, allocates RX keys, installs/removes TX associations, tracks association lists across key generations, and asks drivers for required stats.

State and persistence: runtime security state includes keys, SPI values, generation, association lists, and counters. Drivers/hardware may persist keys transiently; the header defines no durable storage.

Dependencies and integration points: depends on mutexes, refcounts, netdevices, netlink extack, UDP encapsulation, skbuff extensions, and TCP socket helpers.

Risks and test signals: risks include key lifetime across rotations, association list migration, driver data alignment/size, stats memset prohibition, generation mask handling, and optional header assumptions. Test device create/config/rotate/unregister, rx SPI allocation, tx key add/delete, stats reporting, stale association handling, and malformed PSP headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/psp/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/raw.h -->
# sources/distributed-fs/ceph-client/include/net/raw.h

Purpose: declares IPv4 raw socket protocol state, hash table, receive/error paths, proc iteration, and socket-specific fields.

Important APIs and types: `struct raw_hashinfo` holds a spinlock and 256 hash buckets. `struct raw_sock` embeds `inet_sock` first and adds ICMP filter, multicast routing table, and NUMA drop counters. APIs match sockets, abort, deliver ICMP errors, local-deliver raw packets, receive skbs, hash/unhash sockets, initialize raw support, and expose proc iteration. Helpers compute netns/protocol hash and bound-device matching with L3 master accept behavior.

Control flow: raw sockets are hashed by protocol/netns, incoming IP packets are delivered to matching sockets, ICMP errors are dispatched, and procfs walks buckets.

State and persistence: per-netns/global hash table membership, socket filter/table/drop counters, and proc iterator state are runtime only.

Dependencies and integration points: depends on inet sockets, protocol dispatcher, netns hashing, ICMP, hash functions, procfs, and optional L3 master devices.

Risks and test signals: risks include hash lock contention, incorrect bound-device match, ICMP filter behavior, raw socket teardown races, and proc iteration while unhashing. Test raw socket bind/send/receive, ICMP errors, L3 master sysctl, multicast table field, proc output, and namespace isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rawv6.h -->
# sources/distributed-fs/ceph-client/include/net/rawv6.h

Purpose: declares IPv6 raw socket hash state, match/receive/error delivery functions, and optional Mobile IPv6 header filter registration.

Important APIs and types: `raw_v6_hashinfo` is the IPv6 raw hash table. `raw_v6_match()` matches sockets by netns, protocol, local/remote IPv6 addresses, and ingress device indices. APIs include raw abort, ICMPv6 error delivery, local-deliver predicate, rawv6 receive, and optional mobility-header filter register/unregister.

Control flow: IPv6 receive dispatch asks rawv6 to deliver packets to matching raw sockets; ICMPv6 errors are converted and delivered; Mobile IPv6 filters can intercept mobility header traffic when configured.

State and persistence: runtime socket hash entries and optional filter callback pointer(s); no durable state.

Dependencies and integration points: depends on IPv6 protocol dispatcher and raw socket core, with optional CONFIG_IPV6_MIP6.

Risks and test signals: risks include address/device matching mistakes, shared `raw_abort()` declaration consistency, ICMPv6 inner offset handling, and filter unregister races. Test raw IPv6 sockets, ICMPv6 errors, device-bound sockets, namespace isolation, and MIP6 filter module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rawv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/red.h -->
# sources/distributed-fs/ceph-client/include/net/red.h

Purpose: implements inline Random Early Detection and adaptive RED fixed-point arithmetic, parameters, variables, stats, validation, and action selection helpers for RED/GRED qdiscs.

Important APIs and types: `struct red_parms` stores thresholds, scaling, max probability, reciprocal, adaptive targets, and idle decay table. `struct red_vars` stores qcount, random cache, average queue length, and idle timestamp. `struct red_stats` tracks probability/forced drops/marks and queue-limit drops. Helpers validate parameters/flags, set parameters, reset/restart vars, model idle decay, calculate queue average, choose random thresholds, compare thresholds, decide mark/drop action, and run adaptive probability updates.

Control flow: enqueue paths update `qavg`, call `red_action()` to return no mark/probability mark/hard mark, and optionally adapt `max_P` on timer intervals. Idle periods decay queue average using `Stab`.

State and persistence: qdisc-local RED parameters, variables, and stats only.

Dependencies and integration points: depends on qdisc time helpers, ECN/dsfield helpers, random numbers, reciprocal division, netlink extack, and RED/GRED UAPI flags.

Risks and test signals: risks include fixed-point overflow, invalid threshold/scale values, nodrop without ECN, stale reciprocal after adaptive updates, and idle decay approximation errors. Test parameter validation, ECN/nodrop/harddrop flags, below/between/above thresholds, adaptive RED, idle queue decay, random probability distribution, and GRED multi-DP stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/red.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/regulatory.h -->
# sources/distributed-fs/ceph-client/include/net/regulatory.h

Purpose: defines cfg80211 regulatory request/domain data structures, device regulatory flags, frequency/power/WMM rules, and rule-construction macros.

Important APIs and types: `enum environment_cap` classifies country-IE environment. `struct regulatory_request` records initiator, wiphy index, user hint type, alpha2, DFS region, intersection/processed flags, country-IE environment, list node, and RCU head. `enum ieee80211_regulatory_flags` defines custom/strict/beacon/country-IE/relax/self-managed behavior. `struct ieee80211_reg_rule` composes frequency range, power rule, WMM rule, flags, DFS CAC, PSD, and WMM presence. `struct ieee80211_regdomain` stores alpha2, DFS region, rule count, flexible rule array, and RCU head. `REG_RULE*` macros convert MHz/dBi/dBm inputs.

Control flow: regulatory core queues requests, intersects domains when needed, applies per-wiphy flags, and exposes channel power/DFS/no-IR constraints to wireless drivers.

State and persistence: regulatory requests and regdomains are runtime RCU-managed state; system/user hints may be reapplied but are not persisted here.

Dependencies and integration points: depends on IEEE80211/nl80211 UAPI, cfg80211 wireless core, RCU, DFS handling, country IEs, and driver wiphy registration.

Risks and test signals: risks include incompatible flag combinations, alpha2 special-code semantics, RCU freeing mistakes, WMM rule omission, unit conversion errors, and self-managed device conflicts. Test user/driver/core/country-IE hints, custom/strict/self-managed flags, DFS regions/CAC, WMM regulatory limits, beacon hints, and regulatory domain intersection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/regulatory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/request_sock.h -->
# sources/distributed-fs/ceph-client/include/net/request_sock.h

Purpose: declares generic request socket infrastructure for pending connection requests, SYN-ACK/reset callbacks, accept queues, Fast Open queueing, and skb socket stealing.

Important APIs and types: `struct request_sock_ops` supplies family, size/slab metadata, ACK/reset/destructor callbacks. `struct request_sock` overlays `sock_common` fields, tracks retransmits/timeouts, syncookie status, timestamp, timer, ops, child/listener pointers, saved SYN, security IDs, and timeout. `struct fastopen_queue` tracks TFO pending/RST request lists, lock, qlen/max, and context. `struct request_sock_queue` stores accept FIFO, qlen/young counts, defer-accept flag, flood warning, and TFO queue. Helpers convert between sock/request_sock, steal sockets from skbs, refcount/free requests, remove accept entries, account qlen/young, and clamp SYNACK window.

Control flow: listening protocols allocate request sockets on SYN, retransmit SYNACK by timer, move established children to accept queue, optionally co-own TFO requests with child sockets, and free requests by refcount.

State and persistence: all state is listener/request runtime state; saved SYN is in-memory only.

Dependencies and integration points: depends on sock core, timers, slabs, refcounts, TCP states, SYN cookies, security labels, Fast Open, and reset reason enum.

Risks and test signals: risks include request refcount underflow, stealing prefetched syncookie sockets incorrectly, accept queue races, TFO listener/child lifetime, qlen/young imbalance, and window-scale hardening regressions. Test SYN/SYNACK/ACK, retransmits/timeouts, syncookies, TFO accept/remove/reset, accept queue FIFO, listener close, and skb_steal_sock BPF-prefetched cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/request_sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rose.h -->
# sources/distributed-fs/ceph-client/include/net/rose.h

Purpose: defines the ROSE network address length constant.

Important APIs and types: `ROSE_ADDR_LEN` is set to 5. No functions or structs are declared.

Control flow: ROSE protocol code includes this header when sizing or validating ROSE addresses.

State and persistence: no state.

Dependencies and integration points: integrates with AX.25/ROSE networking code that handles fixed-size ROSE addresses.

Risks and test signals: risk is limited to address-size mismatches. Test compile users and ROSE address parse/format paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rose.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/route.h -->
# sources/distributed-fs/ceph-client/include/net/route.h

Purpose: declares IPv4 routing cache/dst structures, route lookup helpers, PMTU/redirect APIs, address-type helpers, uncached route management, and socket connection route setup helpers.

Important APIs and types: `struct rtable` embeds `dst_entry` first and stores generation, flags/type, input/output bit, gateway use/family/address, ingress ifindex, and PMTU lock/value. Helpers derive route scope/TOS from sockets, access skb rtable, determine input/output route, choose nexthop, initialize flowi4 from sockets, lookup output/input routes, update PMTU/redirect, classify address types, allocate/clone/release routes, map TOS to priority, connect/newports route lookup, get ingress ifindex/hoplimit, and resolve gateway neighbours.

Control flow: output callers build `flowi4`, perform route lookup, optionally redo lookup after port allocation for IPsec/rules, attach dst to skb/socket, and release with `ip_rt_put()`. Input callers run route input under RCU and force dst ref if successful.

State and persistence: route dst entries, uncached lists, per-net generation/cache stats, PMTU metrics, and neighbour references are runtime state.

Dependencies and integration points: depends on dst, FIB, inetpeer, flow, inet sockets, ARP/NDISC, DSCP, LSM flow classification, rtnetlink, XFRM/no-xfrm route flags, and IPv6 gateway neighbours.

Risks and test signals: risks include dst/rtable layout assumptions, RCU/refcount mistakes in input route forcing, incomplete flow keys bypassing rules, IPsec route redo omissions, gateway family handling, and PMTU lock bit packing. Test output/input lookups, policy routing, source routing options, port allocation route redo, PMTU/redirect, blackhole routes, IPv6 gateway nexthop, uncached route cleanup, and namespace/device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/route.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rpl.h -->
# sources/distributed-fs/ceph-client/include/net/rpl.h

Purpose: declares IPv6 RPL lightweight tunnel init/exit hooks and source-routing header compression/decompression helpers.

Important APIs and types: when `CONFIG_IPV6_RPL_LWTUNNEL` is enabled, `rpl_init()` and `rpl_exit()` are external; otherwise init succeeds and exit is a no-op. `ipv6_rpl_srh_decompress()` and `ipv6_rpl_srh_compress()` convert RPL source routing headers relative to destination address and address count.

Control flow: IPv6 tunnel/module init calls RPL init/exit conditionally; packet processing compresses/decompresses SRH fields for RPL routing.

State and persistence: no state in the header; RPL tunnel registration state lives in implementation.

Dependencies and integration points: depends on Linux RPL UAPI and IPv6 lightweight tunnel support.

Risks and test signals: risks include config stubs hiding missing registration, SRH compression length errors, and destination-address reconstruction mistakes. Test enabled/disabled builds, RPL LWT setup, compress/decompress round trips, and malformed SRH lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rps-types.h -->
# sources/distributed-fs/ceph-client/include/net/rps-types.h

Purpose: defines the compact tagged pointer format used for RPS socket flow tables.

Important APIs and types: `typedef unsigned long rps_tag_ptr` stores a table pointer with the low five bits holding `ilog2(size)`. Helpers extract the log, compute the mask, and recover the table pointer by clearing low bits.

Control flow: RPS/RFS code reads a tag from hotdata, derives index mask from flow hash, and accesses the table pointer without storing separate size and pointer fields.

State and persistence: no owned state; it interprets packed runtime pointers.

Dependencies and integration points: used by `rps.h` and net hotdata RPS table storage.

Risks and test signals: risks include pointer alignment assumptions, table sizes beyond 31-bit log encoding, and mask overflow for invalid tags. Test RPS table allocation alignment, varying table sizes, zero tag handling, and 32/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rps-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rps.h -->
# sources/distributed-fs/ceph-client/include/net/rps.h

Purpose: declares Receive Packet Steering/Flow Steering data structures and inline hot-path helpers for recording socket flow CPU hints and queue head/tail counters.

Important APIs and types: enabled builds define static keys `rps_needed`/`rfs_needed`, `struct rps_map`, `struct rps_dev_flow`, and `struct rps_sock_flow_table`. Helpers record flow hash to the current CPU, record/delete flows from sockets, test if RFS is needed, and update `softnet_data` input queue head/tail. Disabled builds compile helpers to no-ops or zero.

Control flow: receive-side socket paths save rxhash; recvmsg or packet processing records the CPU handling a flow; RPS lookup later uses the table to steer packets to that CPU. Device flow entries track selected CPU/filter/tail information.

State and persistence: RPS maps, socket flow table entries, device flow entries, static keys, socket `sk_rxhash`, and softnet queue counters are runtime-only.

Dependencies and integration points: depends on socket core, TCP established state, RCU, static keys, net hotdata, RPS tagged pointer helpers, and softnet data.

Risks and test signals: risks include racing table updates, stale CPU hints after socket close, raw CPU use under preemption, hash zero special-casing, and disabled-config behavior. Test RPS/RFS sysctls, socket flow record/delete, CPU hotplug, table resize, accelerated RFS filters, and CONFIG_RPS disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rsi_91x.h -->
# sources/distributed-fs/ceph-client/include/net/rsi_91x.h

Purpose: declares shared Redpine/RSI 91x coexistence queue IDs, host-interface IDs, and WLAN/BT module operation tables.

Important APIs and types: queue constants identify coexistence, BT, WLAN, Wi-Fi management/data, and BT management/data queues. `enum rsi_coex_queues` classifies common/BT/WLAN coex queues. `enum rsi_host_intf` identifies SDIO or USB transport. `struct rsi_proto_ops` lets protocol modules send packets, query host interface, and set BT context. `struct rsi_mod_ops` defines attach/detach/receive callbacks. `rsi_bt_ops` is the exported Bluetooth module ops table.

Control flow: the core RSI driver attaches a module with protocol ops, module receive paths process messages, and coexistence send paths choose HAL queues.

State and persistence: state is private to the RSI core and modules; this header only defines callbacks and IDs.

Dependencies and integration points: depends on skbuffs and integrates RSI WLAN/BT coexistence modules over SDIO/USB transports.

Risks and test signals: risks include wrong queue selection, attach/detach ordering, BT context lifetime, and host-interface-specific behavior. Test module attach/detach, packet send queue IDs, receive callbacks, SDIO/USB variants, and coexistence traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rsi_91x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rstreason.h -->
# sources/distributed-fs/ceph-client/include/net/rstreason.h

Purpose: defines socket reset reason codes for TCP/MPTCP and maps selected skb drop reasons to reset reasons.

Important APIs and types: `DEFINE_RST_REASON()` macro lists reset reason identifiers. `enum sk_rst_reason` includes drop-derived passive reset reasons, independent TCP reset reasons such as timewait/invalid SYN/abort-on-close/linger/memory/state/keepalive/disconnect-with-data, MPTCP reset reason codes copied from UAPI RFC 8684 values, error, and max sentinel. `sk_rst_convert_drop_reason()` converts known TCP skb drop reasons to matching reset reasons and defaults to not specified.

Control flow: TCP/MPTCP reset send paths pass a reason enum; passive drop paths can convert skb drop reasons; request socket ops use this enum for `send_reset()`.

State and persistence: no state; values are diagnostic/control metadata on reset paths.

Dependencies and integration points: depends on core drop reasons and MPTCP UAPI; integrates with TCP, MPTCP, request sockets, tracepoints/counters, and reset diagnostics.

Risks and test signals: risks include enum order drift against users/trace tooling, incomplete drop reason conversion, MPTCP UAPI mismatch, and using `MAX` as a real reason. Test reset paths for each TCP abort case, passive drop conversion, MPTCP subflow resets, trace/diagnostic output, and compile coverage when MPTCP is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rstreason.h -->
