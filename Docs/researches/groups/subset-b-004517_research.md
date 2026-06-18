# subset-b-004517 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_reg.h

## Purpose

`rvu_reg.h` is the RVU Admin Function register map for OcteonTX2/CN10K/CN20K networking blocks. It gives symbolic offsets and offset-generating macros for RVU AF/PF/VF mailboxes, NPA, NIX, SSO/SSOW, TIM, CPT, NPC, NDC, LBK, and APR register spaces. It is included by AF and NIC-side code that needs to read or program hardware through `rvu_read64()`, `rvu_write64()`, `otx2_read64()`, and mailbox-driven register configuration.

## Important APIs, Types, And Functions

- RVU AF/PF/VF mailbox and interrupt offsets: `RVU_AF_AFPFX_MBOXX()`, `RVU_PF_VFX_PFVF_MBOXX()`, `RVU_PF_PFAF_MBOXX()`, FLR/ME/GEN/MBX interrupt status and enable registers.
- Privileged function mapping registers: `RVU_PRIV_PFX_*`, `RVU_PRIV_HWVFX_*`, and block type revision discovery macros.
- NPA AF and LF configuration offsets for LF reset, admin queues, aura/pool allocation, qints, RAS, poison, and error paths.
- NIX AF offsets for LF allocation, RX/TX queue contexts, scheduler hierarchy, stats, RSS, LSO, VLAN, IPsec, multicast, mirror, timestamp, and backpressure programming.
- CPT offsets for engine, LF, fault, RAS, context cache, inline IPsec, BAR2 alias, and LF queue programming.
- NPC offsets for parser/KPU, key-extract configuration, MCAM, exact-match, debug, and match-stat registers.
- Dynamic NPC MCAM macros such as `NPC_AF_MCAMEX_BANKX_CAMX_W0()` switch register layout when `rvu->hw->npc_ext_set` is set.
- LBK and APR masks define loopback channel/link configuration and LMTST throttle/map fields used by AF/NIC code.

## Control Flow

The header has no runtime control flow, but it shapes most register-level control flow in the AF driver. Callers calculate offsets with these macros, then issue MMIO reads/writes or encode offsets into mailbox register-write requests. Most simple macros are pure arithmetic over block, LF, entry, bank, queue, scheduler, or channel indexes. The NPC MCAM and match-stat macros are GNU statement expressions that inspect the caller-visible `rvu` pointer to choose legacy versus extended NPC address layouts.

## State And Persistence

The file stores no state. Its constants identify volatile hardware state: mailbox doorbells, interrupt enables, LF contexts, NPA pools/auras, NIX queues, scheduler registers, NPC MCAM entries, CPT LF queues, and context caches. Incorrect values persist indirectly by programming hardware into the wrong state until reset or explicit reconfiguration.

## Dependencies And Integration Points

The macros depend on Linux bit helpers such as `BIT_ULL()` and `GENMASK_ULL()` from included users. `rvu_switch.c`, `rvu_rep.c`, AF mailbox handlers, NPA/NIX/CPT/NPC code, and NIC files such as `otx2_common.c`, `cn10k_ipsec.c`, and `cn20k.c` use these offsets. The register map must remain aligned with `rvu_struct.h` context layouts and mailbox ABI structures in `mbox.h`/`npc.h`.

## Risks

- A wrong offset or mask can corrupt unrelated hardware state because all consumers perform raw MMIO or AF-mediated writes.
- The NPC extended-set macros rely on an in-scope variable named `rvu`; they are convenient but fragile if reused in a different naming context.
- Some macros use uncast shifts while others explicitly cast to `u64`; high index values require careful review for overflow and precedence.
- Duplicate names such as `NPC_AF_BLK_RST` appear in adjacent sections and must match the hardware specification.
- New silicon revisions require updating both register offsets and context structures; partial updates are likely to fail only on hardware.

## Test Signals

Validation signals are hardware boot/probe success, mailbox interrupt traffic, resource attach/detach, NPA/NIX AQ operations, MCAM rule programming, CPT/IPsec bring-up, and loopback switch operation. Static review should compare every offset and mask against the hardware reference manual, especially NPC extended-set branches and CN20K mailbox register definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_rep.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_rep.c

## Purpose

`rvu_rep.c` implements AF-side support for RVU representor mode. It forwards PF/VF state and MAC events to the representor PF, reports NIX LF stats, builds VLAN-based MCAM steering rules between represented functions and the representor, and handles mailbox requests for e-switch mode and representor count/map discovery.

## Important APIs, Types, And Functions

- `MBOX_UP_REP_MESSAGES` expands allocation helpers for AF-to-PF representor up messages.
- `rvu_rep_up_notify()` sends `rep_event` messages to the representor PF and updates AF cached MAC state on MAC-change events.
- `rvu_rep_wq_handler()` drains `rvu->rep_evtq_head` and serializes up-notification through `rvu->mbox_lock`.
- `rvu_mbox_handler_rep_event_notify()` queues PF/VF-originated representor events from mailbox context.
- `rvu_rep_notify_pfvf_state()` notifies the representor PF when a CGX-mapped PF/VF is enabled or disabled.
- `rvu_mbox_handler_nix_lf_stats()` reads NIX LF RX/TX stats or delegates reset to `rvu_mbox_handler_nix_stats_rst()`.
- VLAN helpers `rvu_rep_tx_vlan_cfg()`, `rvu_rep_rx_vlan_cfg()`, and `rvu_rep_get_vlan_id()` allocate/derive per-representee tags.
- `rvu_rep_install_rx_rule()` and `rvu_rep_install_tx_rule()` install MCAM rules for representor-to-representee and representee-to-representor paths.
- `rvu_rep_install_mcam_rules()`, `rvu_rep_update_rules()`, and `rvu_rep_pf_init()` drive representor mode setup and per-function rule enablement.
- `rvu_mbox_handler_esw_cfg()` and `rvu_mbox_handler_get_rep_cnt()` expose representor mode control and mapping discovery.

## Control Flow

Representor discovery starts when the representor PF sends `get_rep_cnt`; the handler records `rvu->rep_pcifunc`, allocates `rep2pfvf_map`, counts CGX-mapped PFs/VFs, and returns the map. When e-switch setup later enables `rvu->rep_mode`, `rvu_switch_enable()` calls `rvu_rep_pf_init()` and `rvu_rep_install_mcam_rules()`. The installer walks each CGX-mapped PF and its VFs, sets the NIX block address, skips VFs without attached NIX LFs, and installs four MCAM entries per represented function: RX/TX rules for representor traffic and RX/TX rules for represented-function traffic.

RX rules match LBK-channel VLAN tags. Representor-bound rules use the representor pcifunc and unicast action index derived from the representor id; return traffic rules target the represented pcifunc and default RX action. TX rules configure VLAN insertion for the source function, then steer packets to `RVU_SWITCH_LBK_CHAN` on the correct LBK id derived from NIX0/NIX1.

Event flow is asynchronous. PF/VF mailbox events allocate a `rep_evtq_ent` with `GFP_ATOMIC`, append it under `rep_evtq_lock`, and queue `rep_evt_work`. The worker removes one entry at a time, calls `rvu_rep_up_notify()`, and frees it. Up-notification holds `mbox_lock`, allocates an up message for the representor PF, waits for any previous up mailbox message to clear, sends, waits for response, and unlocks.

## State And Persistence

State lives in `struct rvu`: `rep_pcifunc`, `rep_mode`, `rep_cnt`, `rep2pfvf_map`, the representor workqueue/list/spinlock, and `rvu->rswitch` MCAM entry metadata. The AF also updates `struct rvu_pfvf::mac_addr`, `sdp_info`, flags, and NIX interface fields through helper calls. Hardware persistence is in NIX VLAN config, NPC MCAM entries/counters, LBK link scheduler state, and NIX LF stats. No disk persistence exists.

## Dependencies And Integration Points

The file depends on AF helpers in `rvu.h`, register definitions in `rvu_reg.h`, NIX/NPC mailbox handlers, `is_pf_cgxmapped()`, `nix_get_nixlf()`, `rvu_get_pf_numvfs()`, `rvu_get_nix_blkaddr()`, and `rvu_switch_enable_lbk_link()`. It integrates with the NIC representor driver through mailbox up events and with `rvu_switch.c` for shared MCAM allocation and update hooks.

## Risks

- `rvu_mbox_handler_get_rep_cnt()` reallocates `rep2pfvf_map` without guarding repeated calls; repeated discovery can leak devm memory or change mappings while rules exist.
- Rule count assumptions must match `rvu_switch_enable()` allocation (`rep_cnt * 4` in representor mode); missed VFs or skipped NIX LFs can leave unused entries in the allocated range.
- Event queue allocation in atomic context can fail and drop events.
- Up-notification waits under a global mailbox lock; stuck representor mailbox response can delay unrelated AF mailbox paths.
- VLAN id is derived from representor index and uses bit 8 to distinguish direction; growth beyond the expected bit width could collide with protocol semantics.

## Test Signals

Useful tests include representor count/map discovery, e-switch enable/disable, PF/VF state notification, MAC address change propagation, bidirectional representor traffic over LBK, VLAN insertion/strip behavior, NIX LF stat reads and resets, NIX0/NIX1 represented functions, VFs without NIX LF attached, and mailbox allocation/response timeout fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_rep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_sdp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_sdp.c

## Purpose

`rvu_sdp.c` identifies SDP PF/VF functions and manages SDP channel information in the RVU AF. It supports both firmware-provided channel data and PCI discovery of SDP PF devices, then serves mailbox requests that set or retrieve SDP channel ranges used by NIX/SDP traffic paths.

## Important APIs, Types, And Functions

- `PCI_DEVID_OTX2_SDP_PF`, `RVU_SDP_VF_DEVID`, `MAX_SDP`, and static `sdp_pf_num[]` define recognized SDP devices.
- `is_sdp_pfvf()` checks whether a pcifunc belongs to a discovered SDP PF.
- `is_sdp_pf()` distinguishes the PF function from its VFs.
- `is_sdp_vf()` handles both RVU VF-device-id based SDP VFs and VFs under discovered SDP PFs.
- `rvu_sdp_init()` discovers SDP PFs or consumes firmware channel data and attaches `sdp_node_info` storage to `struct rvu_pfvf`.
- `rvu_mbox_handler_set_sdp_chan_info()` copies PF-provided SDP channel metadata into the AF-side PF/VF state.
- `rvu_mbox_handler_get_sdp_chan_info()` returns fixed legacy SDP channel ranges or programmable channel data from hardware.

## Control Flow

Initialization first checks `rvu->fwdata->channel_data.valid`. If valid, PF 0 is treated as SDP, and its `sdp_info` pointer aliases firmware channel info. Otherwise it scans PCI devices with Cavium vendor id and the SDP PF device id, derives the RVU PF number from `pdev->bus->number - 1`, allocates `struct sdp_node_info` for each discovered PF, stores the PF number in `sdp_pf_num[]`, and releases the final PCI reference.

Mailbox set-channel-info simply finds the requester PF/VF state and copies the supplied `sdp_node_info`. Mailbox get-channel-info checks `hw->cap.programmable_chans`: legacy hardware returns `NIX_CHAN_SDP_CH_START` and `NIX_CHAN_SDP_NUM_CHANS`; programmable hardware reads the first NIX block `NIX_AF_CONST1` low 12 bits for channel count and uses `hw->sdp_chan_base`.

## State And Persistence

State is process-local/static in `sdp_pf_num[]` and per-RVU in `rvu->pf[pf].sdp_info`. The firmware-data path points directly at firmware channel data; the PCI-discovery path allocates devm-managed memory. Channel info is not persisted outside AF memory, and hardware channel counts come from NIX registers.

## Dependencies And Integration Points

The file depends on PCI core discovery, RVU pcifunc helpers, firmware data in `rvu->fwdata`, `struct sdp_node_info`, and NIX constants/register reads. NIC and AF paths use `is_sdp_*()` to special-case SDP representor or SDP function behavior, including scheduler/channel setup in `otx2_common.c`.

## Risks

- The PF-number derivation from PCI bus number is platform-specific and can break if bus numbering changes.
- `sdp_pf_num[]` is static module-global; multiple RVU devices would share discovery state.
- Firmware path assumes PF 0 is SDP and does not allocate a private copy of channel info.
- `set_sdp_chan_info()` assumes `pfvf->sdp_info` is non-null; malformed ordering of mailbox calls could dereference a null pointer.

## Test Signals

Probe on firmware-channel-data and PCI-discovery platforms, `is_sdp_pf()`/`is_sdp_vf()` pcifunc tests, SDP mailbox set/get, programmable versus fixed channel hardware, and SDP representor datapath setup are the most useful signals. Fault injection should cover missing allocation and absent SDP PCI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_sdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_struct.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_struct.h

## Purpose

`rvu_struct.h` defines hardware-visible RVU, NPA, NIX, and queue-context structures for the AF driver. It maps block addresses/types, interrupt vector numbers, admin queue operation encodings, NPA aura/pool contexts, NIX RQ/SQ/CQ/RSS/MCE/bandwidth-profile contexts, LSO and flow-key formats, VLAN tag controls, and per-LF statistic enums.

## Important APIs, Types, And Functions

- Block enums `rvu_block_addr_e` and `rvu_block_type_e` encode hardware block addresses and abstract block types used during discovery and resource assignment.
- Interrupt vector enums describe AF, PF, NPA, NIX, and CPT interrupt layout.
- `npa_aq_inst_s`, `npa_aq_res_s`, `nix_aq_inst_s`, and `nix_aq_res_s` define admin queue instruction/result words.
- `npa_aura_s` and `npa_pool_s` define buffer-pool state, flow control, thresholds, counters, and memory-stack metadata.
- `nix_cq_ctx_s`, `nix_rq_ctx_s`, `nix_sq_ctx_s`, `nix_cn10k_rq_ctx_s`, and `nix_cn10k_sq_ctx_s` are 128-byte queue contexts programmed by AQ.
- `nix_rsse_s`, `nix_rx_mce_s`, and `nix_bandprof_s` cover RSS entries, multicast/mirror entries, and ingress policer bandwidth profiles.
- `nix_lso_format` and `nix_rx_flowkey_alg` describe hardware LSO and RSS/parser extraction algorithms.
- VLAN enums and `VTAG_STRIP`/`VTAG_CAPTURE` define NIX VTAG behavior.
- `nix_stat_lf_tx` and `nix_stat_lf_rx` define per-LF stats indexes used by AF and NIC stats code.
- `static_assert(sizeof(...) == NIX_MAX_CTX_SIZE)` protects context sizes.

## Control Flow

The header has no executable control flow. Runtime code populates these packed bitfield structures in mailbox AQ requests and the AF writes them to hardware contexts. The same definitions are used to decode/read contexts in debug or stats paths. CN10K/CN20K-specific code chooses CN10K/CN20K request types but shares many field names, so the structure layout is part of the hardware ABI.

## State And Persistence

The structures represent persistent hardware context while an LF is configured: NPA aura/pool counters and flow-control state, NIX queue enable bits, buffer auras, scheduler mapping, stats counters, RSS entries, multicast chains, policer rates/actions, and VLAN/LSO/parser formats. In memory, they appear as transient mailbox request payloads or debug copies; in hardware, they remain until AQ write/disable/reset.

## Dependencies And Integration Points

Consumers include AF NPA/NIX resource handlers, NIC queue setup in `otx2_common.c`, CN10K/CN20K SQ/RQ/aura/pool setup, representor stat reads, RSS/LSO programming, TC/policer offload, and debugfs context dumping. The file depends on the compiler's kernel bitfield layout conventions for the target architecture and on exact alignment/size expectations from hardware.

## Risks

- Bitfield ordering and width errors directly corrupt queue or buffer-pool hardware context.
- CN10K and older NIX queue context differences are subtle; using the wrong request/context type can set unrelated bits.
- Several fields encode counter widths and split high/low ids; masks in callers must match these definitions.
- `static_assert` only validates total size, not bit position correctness.
- Hardware revisions with extended fields require coordinated changes across this header, mailbox structs, and setup code.

## Test Signals

Compile-time `static_assert` coverage, successful NPA/NIX LF allocation, RX/TX queue bring-up, RSS distribution, MCAM multicast/mirror operation, ingress policer behavior, VLAN tag insertion/strip, LSO offload, and debug context dumps matching expected hardware values are strong signals. Hardware smoke tests should include CN10K/CN20K and older OTX2 silicon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_switch.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_switch.c

## Purpose

`rvu_switch.c` implements AF-side LBK/NPC based switching among CGX-mapped PFs/VFs and delegates to representor-mode logic when enabled. It allocates MCAM entries, installs RX/TX steering rules, rewrites default RX channel masks, enables/disables LBK scheduler links, and updates rules when a function's NIX LF becomes available.

## Important APIs, Types, And Functions

- `rvu_switch_enable_lbk_link()` toggles NIX TL2 scheduler/LBK link configuration for a pcifunc.
- `rvu_switch_install_rx_rule()` installs or updates a default unicast DMAC RX rule with a configurable channel mask.
- `rvu_switch_install_tx_rule()` installs a TX MCAM rule matching destination MAC and steering to `RVU_SWITCH_LBK_CHAN`.
- `rvu_switch_install_rules()` walks CGX-mapped PFs/VFs and installs non-representor switch rules.
- `rvu_switch_enable()` allocates contiguous MCAM entries, creates `entry2pcifunc`, and invokes normal or representor rule installation.
- `rvu_switch_disable()` restores RX channel masks, disables LBK links, deletes MCAM rules, frees entries, and releases mapping memory.
- `rvu_switch_update_rules()` updates a single pcifunc's rules or delegates to `rvu_rep_update_rules()` in representor mode.

## Control Flow

Enable allocates a contiguous MCAM range sized to `cgx_mapped_pfs + cgx_mapped_vfs`, or four times that in representor mode. On success it records `used_entries` and `start_entry`. In normal mode, `rvu_switch_install_rules()` scans PFs from 1 upward, skips non-CGX-mapped PFs, initializes NIX block/interface metadata before NIX LF attach, installs an RX rule with channel mask zero so traffic from either LBK or wire can match, then installs a TX LBK rule and records the pcifunc at the current entry. It repeats this for each VF.

Disable skips normal RX rollback in representor mode, otherwise it reinstalls RX rules with channel mask `0xFFF`, disables LBK links for every represented pcifunc, then deletes the allocated MCAM range and frees all MCAM entries. Update searches `entry2pcifunc` for the target pcifunc and reinstalls its TX/RX rules once the LF has been initialized.

## State And Persistence

Runtime state lives in `rvu->rswitch`: `start_entry`, `used_entries`, and `entry2pcifunc`. Per-function state such as MAC address, NIX block address, RX/TX interfaces, and `NIXLF_INITIALIZED` flags lives in `struct rvu_pfvf`. Hardware state persists in NPC MCAM entries/counters and NIX scheduler/LBK link configuration until disabled, deleted, or reset.

## Dependencies And Integration Points

The file depends on RVU helpers, NIX scheduler helper `rvu_nix_tx_tl2_cfg()`, NPC mailbox flow install/delete/free handlers, `rvu_get_pf_numvfs()`, `is_pf_cgxmapped()`, and representor functions from `rvu_rep.c`. It is called by AF e-switch lifecycle paths and by NIX attach/update paths that need to refresh rules after a PF/VF becomes initialized.

## Risks

- MCAM allocation/free uses broad `free_all` requests on failure/disable, so coordination with other AF MCAM users must be correct.
- RX rule installation is skipped if `NIXLF_INITIALIZED` is false; update paths must fire reliably after attach.
- Rule count and `entry2pcifunc` indexing must stay aligned across PF/VF enumeration and representor sizing.
- Disabling representor mode skips normal RX rollback and depends on representor cleanup to avoid stale policy.
- MAC address changes require rule refresh elsewhere; stale DMAC entries can blackhole switched traffic.

## Test Signals

Test enable/disable cycles, PF/VF attach after switch enable, MAC-change rule refresh, NIX0/NIX1 LBK id selection, traffic between PFs/VFs and wire, MCAM allocation failure cleanup, representor mode delegation, and repeated e-switch toggles. Hardware counters and NPC MCAM dumps are useful observability points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_trace.c

## Purpose

`rvu_trace.c` instantiates and exports RVU tracepoints declared in `rvu_trace.h`. It defines `CREATE_TRACE_POINTS`, includes the trace header once as the tracepoint definition site, and exports selected tracepoint symbols for modules.

## Important APIs, Types, And Functions

- `CREATE_TRACE_POINTS` makes the `TRACE_EVENT()` definitions in `rvu_trace.h` allocate tracepoint storage.
- Exported symbols include `otx2_msg_alloc`, `otx2_msg_interrupt`, `otx2_msg_process`, `otx2_msg_status`, and `otx2_parse_dump`.

## Control Flow

There is no runtime control flow in this file. It participates in build/link flow: exactly one translation unit must define `CREATE_TRACE_POINTS` before including the trace header. Other files include `rvu_trace.h` without this macro and call `trace_otx2_*()` helpers generated by the trace subsystem.

## State And Persistence

Tracepoint registration metadata is kernel runtime state. Events are emitted only when tracepoints are enabled and are not persisted by the driver itself. User tooling such as ftrace/perf can record them externally.

## Dependencies And Integration Points

The file depends on Linux tracepoint infrastructure and on `rvu_trace.h`. AF and NIC mailbox paths call the generated trace helpers. Exported tracepoints allow other OcteonTX2 modules to use the trace events.

## Risks

- Exporting only a subset of declared tracepoints may surprise out-of-tree users that expect every event symbol exported.
- Duplicate `CREATE_TRACE_POINTS` definitions elsewhere would cause link errors.
- Removing or renaming trace events is ABI-visible to tracing scripts.

## Test Signals

Build/link success, enabled ftrace events under `/sys/kernel/tracing/events/rvu/`, and observing mailbox events during PF/VF probe or AF mailbox traffic validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_trace.h

## Purpose

`rvu_trace.h` declares tracepoints for RVU/OTX2 mailbox and parse-debug observability. It defines event payloads and print formats for message allocation, sends, response checking, interrupts, processing, wait timeouts, status reports, and NIX parse dumps.

## Important APIs, Types, And Functions

- `TRACE_SYSTEM rvu` places events under the RVU tracing subsystem.
- `otx2_msg_alloc` records PCI device, mailbox id/name, message size, and pcifunc.
- `otx2_msg_send` records number of messages, payload size, id, and pcifunc.
- `otx2_msg_check` records request/response ids and response code.
- `otx2_msg_interrupt` records the device, mailbox interrupt description, and interrupt bits.
- `otx2_msg_process` records mailbox processing result per id and pcifunc.
- `otx2_msg_wait_rsp` records response wait timeouts.
- `otx2_msg_status` records status strings and message counts.
- `otx2_parse_dump` records six 64-bit words from a NIX parse dump.

## Control Flow

The header follows the Linux trace event pattern. The guarded `TRACE_EVENT()` declarations are read once by normal includes and a second time through `trace/define_trace.h` when `CREATE_TRACE_POINTS` is set by `rvu_trace.c`. Call sites execute generated `trace_otx2_*()` functions, which are low overhead when disabled and copy event fields into trace buffers when enabled.

## State And Persistence

The header defines trace event metadata but no driver state. Event records contain copies of message ids, strings, device names, response codes, interrupt masks, and parse words at emission time. Persistence depends on external tracing buffers and tools.

## Dependencies And Integration Points

It includes Linux tracepoint and PCI headers plus `mbox.h` for mailbox id-to-name conversion. It is included by AF and NIC code that emits mailbox trace events, notably mailbox interrupt handlers and message allocation/processing paths.

## Risks

- `otx2_parse_dump` dereferences six words from the passed pointer without length checking; callers must provide a valid six-word buffer.
- `TP_printk` calls `otx2_mbox_id2name()` at formatting time, so mailbox id tables must remain available and stable.
- Trace strings expose mailbox flow details; that is useful for debug but can increase trace volume under heavy mailbox traffic.
- `TRACE_INCLUDE_PATH .` assumes the build include path resolves the trace header correctly.

## Test Signals

Enable each event through ftrace/perf while exercising PF/AF and PF/VF mailbox traffic. Confirm event fields show correct PCI names, mailbox message names, pcifunc values, response errors, and parse dump words. Build tests should include modular and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/Makefile

## Purpose

The NIC `Makefile` defines how Marvell RVU Ethernet PF, VF, and representor drivers are built and which optional objects are included for DCB, MACsec, and XFRM/IPsec offload support.

## Important APIs, Types, And Functions

- `obj-$(CONFIG_OCTEONTX2_PF)` builds `rvu_nicpf.o` and `otx2_ptp.o`.
- `obj-$(CONFIG_OCTEONTX2_VF)` builds `rvu_nicvf.o` and `otx2_ptp.o`.
- `obj-$(CONFIG_RVU_ESWITCH)` builds `rvu_rep.o`.
- `rvu_nicpf-y` includes PF core, common, tx/rx, ethtool, flows, TC, CN10K/CN20K, DMAC filters, devlink, QoS, and AF_XDP objects.
- `rvu_nicvf-y` includes `otx2_vf.o`.
- `rvu_rep-y` includes NIC-side `rep.o`.
- Conditional additions include `otx2_dcbnl.o`, `cn10k_macsec.o`, and `cn10k_ipsec.o`.
- `ccflags-y` adds the AF directory include path so NIC code can include AF ABI headers such as `rvu.h`, `rvu_trace.h`, `mbox.h`, and `npc.h`.

## Control Flow

Build control is driven by Kconfig symbols. Enabling the PF driver pulls common hardware support and both CN10K/CN20K specialization objects into the PF module. Enabling optional features links additional implementation files into the PF object so runtime capability checks can expose hardware features only when kernel frameworks are available.

## State And Persistence

The file has no runtime state. It determines which symbols exist in the resulting kernel/module. Feature absence changes runtime behavior through missing objects and inline stubs in headers such as `cn10k_ipsec.h`.

## Dependencies And Integration Points

It integrates the NIC directory with the AF header directory. It depends on Kconfig symbols `CONFIG_OCTEONTX2_PF`, `CONFIG_OCTEONTX2_VF`, `CONFIG_RVU_ESWITCH`, `CONFIG_DCB`, `CONFIG_MACSEC`, and `CONFIG_XFRM_OFFLOAD`. The object list must align with exported symbols used by PF/VF/representor source files.

## Risks

- `otx2_ptp.o` is listed for both PF and VF objects; build-system behavior must avoid duplicate or unintended linkage depending on how objects are combined.
- Optional code paths must have correct stubs when objects are not built.
- Adding source files without updating this list silently omits functionality.
- Include path dependence on the AF directory means header ABI churn can break NIC builds.

## Test Signals

Build matrix coverage for PF-only, VF-only, PF+VF, representor, DCB, MACsec, and XFRM offload configurations is the primary signal. Module load/probe tests should confirm optional feature symbols are present only when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k.c

## Purpose

`cn10k.c` provides CN10K-specific NIC hardware operations for LMTST send/refill paths, SQ context initialization, dynamic LMT line setup, and ingress policer allocation/programming. It also selects between older OTX2 hardware ops and CN10K ops at runtime.

## Important APIs, Types, And Functions

- `otx2_hw_ops` and `cn10k_hw_ops` populate `struct dev_hw_ops` function tables.
- `otx2_init_hw_ops()` selects CN10K ops when `CN10K_LMTST` capability is set.
- `cn10k_lmtst_init()` allocates per-CPU LMT metadata and a dynamic LMT qmem region, then asks AF to configure the LMTST table.
- `cn10k_sq_aq_init()` initializes CN10K NIX SQ contexts through `nix_cn10k_aq_enq`.
- `cn10k_refill_pool_ptrs()` batch-refills NPA auras with up to 16 pointers.
- `cn10k_sqe_flush()` copies an SQE into the per-CPU LMT line and flushes it with `cn10k_lmt_flush()`.
- Ingress policer functions allocate/free leaf profiles, map/unmap RQ policers, calculate mantissa/exponent/rdiv values, and program matchall policer rate/actions.

## Control Flow

Initialization calls `otx2_init_hw_ops()` before queue setup so later common code dispatches through the right ops. If CN10K LMTST is present, `cn10k_lmtst_init()` requests local LMT-region use from AF, allocates qmem sized as `num_online_cpus() * LMT_BURST_SIZE`, and initializes each possible CPU's `otx2_lmt_info` with an address and LMT id.

Transmit flush uses the current CPU's LMT info, copies the prepared SQE into the LMT line, builds the target address with SQ IO address and SQE size, issues a DMA write barrier, flushes, then advances the SQ head. RX refill batches buffer addresses and calls `__cn10k_aura_freeptr()` when the batch reaches 16 or refill completes.

Policer configuration allocates a leaf bandwidth profile through mailbox, calculates token bucket fields from requested burst/rate, writes `nix_cn10k_aq_enq` band-profile fields, then maps the profile to every RQ for matchall policing. Free reverses all RQ mappings and frees the leaf profile.

## State And Persistence

State lives in `pfvf->hw_ops`, `pfvf->hw.lmt_info`, `pfvf->hw.lmt_base`, `pfvf->dync_lmt`, `pfvf->tot_lmt_lines`, and `pfvf->hw.matchall_ipolicer`. Hardware state persists in LMTST table setup, NIX SQ contexts, NPA aura contents, and NIX bandwidth profile/RQ policer mappings.

## Dependencies And Integration Points

The file depends on `otx2_common.h`, `otx2_reg.h`, `otx2_struct.h`, `cn10k_lmt_flush()`, mailbox allocators, qmem allocation, NIX/NPA context definitions, and common queue setup. It is called by PF probe/setup paths and by TC or ethtool code that configures ingress policing.

## Risks

- `alloc_percpu()` result is not checked before use in `cn10k_lmtst_init()`.
- Error after `qmem_alloc()` in LMT setup does not free already allocated percpu/qmem state in this function.
- Batch refill uses `num_ptrs` initialized to 1, leaving index 0 intentionally unused for the hardware helper; this convention is easy to break.
- Rate/burst calculations use integer approximations; low rates and very large bursts need boundary tests.
- Matchall policer setup can partially map RQs if a later map fails.

## Test Signals

CN10K probe with LMTST enabled, TX traffic through LMT flush, RX refill under pressure, per-CPU transmit on many CPUs, ingress policer rate/pps behavior, allocation-failure injection, and common OTX2 fallback when `CN10K_LMTST` is absent are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k.h

## Purpose

`cn10k.h` exposes CN10K NIC helper prototypes and an inline DWRR weight helper to the common NIC driver. It is the public header for CN10K LMTST, SQ, refill, and ingress policer operations implemented in `cn10k.c`.

## Important APIs, Types, And Functions

- `mtu_to_dwrr_weight()` computes scheduler DWRR weight as `ceil(mtu / hw.dwrr_mtu)`.
- Prototypes cover `cn10k_refill_pool_ptrs()`, `cn10k_sqe_flush()`, `cn10k_sq_aq_init()`, `cn10k_lmtst_init()`, policer allocation/free/rate/map helpers, and `otx2_init_hw_ops()`.

## Control Flow

The header provides inline arithmetic only. Runtime dispatch happens through `otx2_init_hw_ops()` and `struct dev_hw_ops`, then common code calls the selected functions indirectly for SQ setup, SQE flush, pool refill, aura/pool init, and mailbox interrupts.

## State And Persistence

No state is stored here. The inline helper reads `pfvf->hw.dwrr_mtu`, and the declared functions mutate NIC runtime state and hardware contexts in their implementation files.

## Dependencies And Integration Points

It includes `otx2_common.h`, so it inherits NIC core type definitions and also creates a circular-looking include dependency that is tolerated by include guards. `otx2_common.c`, `cn20k.c`, and feature/offload code use these declarations.

## Risks

- `mtu_to_dwrr_weight()` assumes `hw.dwrr_mtu` is nonzero; `otx2_get_max_mtu()` later normalizes zero to one, so call ordering matters.
- Header inclusion pulls in the large common header; changes can affect many translation units.
- Prototype drift from `cn10k.c` breaks builds across optional configurations.

## Test Signals

Compile coverage across OTX2, CN10K, and CN20K objects, plus runtime checks that DWRR weight changes when AF reports different DWRR MTUs, validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_ipsec.c

## Purpose

`cn10k_ipsec.c` implements CN10K outbound ESP crypto offload through XFRM device offload and the CPT engine. It attaches/configures a CPT LF, allocates its instruction queue, validates XFRM states, writes outbound SA context into hardware, adds CPT/NIX scatter-gather descriptors for offloaded packets, and transmits packets by flushing CPT instructions through LMTST.

## Important APIs, Types, And Functions

- `DEFINE_STATIC_KEY_FALSE(cn10k_ipsec_sa_enabled)` is declared in the header and controlled when SAs exist.
- CPT LF lifecycle helpers attach/detach resources, allocate/free/configure CPT LF, allocate/init/free IQ memory, enable/disable IQ, and clean the CPT path.
- `cn10k_cpt_device_set_inuse()/available()/unavailable()` serialize direct CPT operations through an atomic state machine.
- `cn10k_outb_write_sa()` issues a CPT write-SA instruction and flushes the CPT context cache.
- `cn10k_outb_prepare_sa()` converts an XFRM AES-GCM state into `struct cn10k_tx_sa_s`.
- `cn10k_ipsec_validate_state()` accepts only outbound ESP AES-GCM-ICV16, transport/tunnel, IPv4/IPv6, crypto-mode, seqiv, no ESN, no encap, no TFC.
- XFRM ops `cn10k_ipsec_add_state()` and `cn10k_ipsec_del_state()` manage SA qmem and `x->xso.offload_handle`.
- `cn10k_ipsec_ethtool_init()` toggles CPT offload setup/cleanup.
- `cn10k_ipsec_init()` installs `xfrmdev_ops` and HW ESP feature bits.
- `otx2_sqe_add_sg_ipsec()` prepares paired CPT SG and NIX SG subdescriptors and DMA mappings.
- `cn10k_ipsec_transmit()` builds and flushes an outbound IPsec CPT instruction for a packet.

## Control Flow

Feature initialization checks the PCI device, computes 128-byte-aligned SA size, creates a workqueue, installs XFRM ops, advertises `NETIF_F_HW_ESP`, and marks CPT unavailable. Enabling through ethtool/probe attaches CPT resources, allocates a CPT LF, allocates/initializes IQ memory, configures inline outbound IPsec for the PF pcifunc, stores the CPT enqueue IO address, sets the IPsec-enabled flag, and marks CPT available. Disabling refuses while SAs exist, then disables IQ, clears queue registers, frees IQ, frees/detaches the CPT LF, and marks unavailable.

Adding an outbound state validates XFRM attributes, allocates qmem for the SA, writes a prepared SA into memory, sends a CPT write-SA instruction, stores the qmem pointer in `offload_handle`, enables the static key for the first SA, and increments `outb_sa_count`. Deletion writes a disabled SA context back to CPT, frees qmem, decrements the count, and queues work to disable the static key and update netdev features when the last SA disappears.

Transmit first verifies offload is enabled, finds the XFRM state from the skb security path, checks mode and SA handle, calculates payload/auth/IV offsets, points the CPT result to per-SQ response memory, encodes major opcode `OUTB_IPSEC`, dptr/rptr as the SG gather list before the NIX SQE, cptr as the SA IOVA, and NIXTX location/size in word 0. It reports bytes to the netdev queue, advances SQ head, and flushes the CPT instruction through LMTST.

## State And Persistence

Per-PF IPsec state is `pf->ipsec`: CPT IO address, atomic CPT state, IQ DMA memory, SA size, outbound SA count, static-key work, and workqueue. Each offloaded XFRM state owns qmem containing the hardware SA context, referenced through `x->xso.offload_handle`. Per-SQ state includes doubled SQE/CPT-SG ring and CPT response qmem from `otx2_common.c`. Hardware state persists in CPT LF registers, IQ DMA memory, CPT context cache/SA memory, and NIX/CPT inline configuration until cleanup or reset.

## Dependencies And Integration Points

The file depends on Linux XFRM offload, crypto AEAD/GCM metadata, the OTX2 mailbox/resource API, qmem, LMTST, NIX SQE structures, CPT register definitions, and common DMA mapping helpers. It integrates with `otx2_common.c` for SQ memory layout and DMA directions, with transmit code through `otx2_sqe_add_sg_ipsec()` and `cn10k_ipsec_transmit()`, and with ethtool feature control.

## Risks

- In `cn10k_outb_cptlf_iq_disable()`, `nq_ptr` and `dq_ptr` are both extracted with `CPT_LF_Q_GRP_PTR_DQ_PTR`; this looks suspicious because `NQ_PTR` has a separate mask.
- `cn10k_cpt_device_set_inuse()` busy-waits with `mdelay(1)` and no timeout while the state is `IN_USE`.
- `skb_unshare()` in `otx2_dma_map_skb_frag()` can replace a local skb pointer but does not update the caller's skb ownership, which deserves scrutiny on IPsec DMA error paths.
- Only inbound add returns unsupported; feature advertising must not imply inbound offload.
- SA count/static key updates are not obviously protected by a lock.
- Deleting a state writes a disabled SA and frees qmem even if CPT write fails.
- Transmit drop frees the skb; callers must not also free it.

## Test Signals

XFRM selftests for outbound ESP AES-GCM IPv4/IPv6 tunnel and transport, negative validation for unsupported algorithms/modes/ESN/encap/inbound, ethtool offload enable/disable with active SAs, CPT response timeout injection, SA add/delete loops, high-rate offloaded TX, DMA mapping failure tests, and reset/unload cleanup are essential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_ipsec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_ipsec.h

## Purpose

`cn10k_ipsec.h` defines the CN10K IPsec offload ABI used by the NIC driver: CPT instruction queue sizes, CPT LF register offsets, hardware state structures, outbound SA layout, CPT instruction/result/scatter-gather formats, register bit masks, and build-time stubs when XFRM offload is disabled.

## Important APIs, Types, And Functions

- Queue sizing macros define CPT instruction count, bytes, group queue bytes, extra required entries, and flow-control size.
- CPT LF register macros encode RVU function block address plus CPT LF offsets.
- Opcode macros identify write-SA and outbound IPsec operations.
- `enum cn10k_cpt_comp_e` lists CPT completion codes and mask.
- `struct cn10k_cpt_inst_queue` tracks real/aligned CPU and DMA pointers.
- `enum cn10k_cpt_hw_state_e` backs the atomic CPT availability state.
- `struct cn10k_ipsec` is embedded in `struct otx2_nic`.
- `struct cn10k_tx_sa_s` is the hardware outbound SA context, including cipher key, salt, and hardware context words.
- `struct cpt_inst_s`, `struct cpt_res_s`, and `struct cpt_sg_s` define CPT work queue ABI.
- Conditional prototypes/stubs expose `cn10k_ipsec_init()`, cleanup, ethtool toggle, SG setup, and transmit.

## Control Flow

This header has no runtime control flow except inline stubs. With `CONFIG_XFRM_OFFLOAD`, callers bind to real implementations. Without it, initialization and cleanup are no-ops, ethtool init returns success, and transmit/SG helpers return true, allowing the rest of the NIC code to compile without feature logic.

## State And Persistence

The header defines in-memory and DMA-visible state. `struct cn10k_ipsec` persists for the NIC lifetime. SA contexts and CPT instructions persist in coherent memory while offload is active. Hardware consumes the bitfield layouts exactly as written.

## Dependencies And Integration Points

It depends on Linux types and, through users, RVU block address shifts and CPT register semantics. It is included by `otx2_common.h` and transmit code. Its stubs are the integration boundary for kernels built without XFRM offload.

## Risks

- Bitfield layout must match CPT hardware exactly; compiler/endianness assumptions are critical.
- Stub `cn10k_ipsec_ethtool_init()` returning 0 when XFRM offload is absent can make callers treat unavailable offload as a successful no-op unless feature bits are also absent.
- Queue size constants must maintain hardware-required alignment and extra-entry constraints.
- SA key/salt fields are sensitive material and must be zeroed or freed carefully by implementations.

## Test Signals

Build with `CONFIG_XFRM_OFFLOAD=y` and disabled, verify object linkage/stubs, validate struct sizes/offsets against hardware specs, and run XFRM outbound offload tests that exercise CPT instruction/result/SG layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_ipsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_macsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_macsec.c

## Purpose

`cn10k_macsec.c` implements CN10K MACsec hardware offload through the Linux `macsec_ops` interface. It allocates MCS hardware resources, programs TX/RX SecY policies, flow-id TCAM entries, SC CAM entries, SA keys and PN tables, tracks software-to-hardware mappings, reports MACsec stats, handles packet-number wrap events, and exposes `NETIF_F_HW_MACSEC`.

## Important APIs, Types, And Functions

- Policy and TCAM macros define MCS register fields for MAC DA/SA, EtherType, RX/TX SecY policy, cipher selectors, and SecTAG TCI bits.
- `cn10k_ecb_aes_encrypt()` derives the MACsec hash subkey from SAK using AES ECB over zeroes.
- Mapping helpers find `cn10k_mcs_txsc` and `cn10k_mcs_rxsc` entries in `pfvf->macsec_cfg` lists.
- Resource helpers allocate/free MCS FLOWID, SC, SECY, and SA ids through mailbox.
- Write helpers program RX/TX SecY policies, flow-id entries, SC CAM, SA policies, SA-to-SC maps, and PN tables.
- Stats helpers query/optionally clear SA/SC/SecY stats and accumulate software counters where hardware counters are shared.
- Create/delete helpers manage TXSC/RXSC resource lifetimes and all child SAs.
- `cn10k_mcs_ops` implements the Linux MACsec callbacks for open/stop, add/update/delete SecY, RXSC, RXSA, TXSA, and stats.
- `cn10k_handle_mcs_event()` reports TX PN wrap through `macsec_pn_wrapped()`.
- `cn10k_mcs_init()` and `cn10k_mcs_free()` install/uninstall MACsec offload support.

## Control Flow

Initialization checks `CN10K_HW_MACSEC`, allocates `cn10k_mcs_cfg`, initializes TX/RX SC lists, sets `NETIF_F_HW_MACSEC`, attaches `macsec_ops`, and asks AF to enable MCS TX PN wrap interrupts. Adding a SecY allocates TX flow id, TX SecY, RX SecY, and TX SC resources, caches software SecY and VLAN state, and immediately programs TX policy if the netdev is running. Opening a MACsec device programs the active TX SA, TX SecY, TX flow id, RX SecY, and active RXSC/RXSA resources.

TX SA add allocates a hardware SA, stores key/salt/SSCI in the driver, writes SA policy, writes PN, and links it to the TX SC if it is the encoding SA. RX SC add allocates RX flow id and SC; RX SA add allocates SA, stores key/salt/SSCI, writes policy/map, and writes PN. Updates change PNs, active bits, encoding SA linkage, flow enablement, and SecY policy. Delete paths disable flow ids, free SA/SC/SecY resources, unlink lists, and free memory.

Stats callbacks query hardware through mailbox. Some RX SecY/SC counters are cleared on read and accumulated in software because hardware counters are shared or policy-dependent. `cn10k_mcs_sync_stats()` snapshots affected counters before changing validation or replay-protect policy.

## State And Persistence

State lives in `pfvf->macsec_cfg`, with `txsc_list` and `rxsc_list` entries storing software pointers, hardware ids, key material, salt, SSCI, SA bitmaps, encoding SA, VLAN mode, last policy values, and accumulated stats. Hardware state persists in MCS resource allocation, TCAM entries, SecY policy tables, SC CAM, SA policy tables, SA maps, PN tables, counters, and interrupt configuration.

## Dependencies And Integration Points

The file depends on Linux MACsec, rtnl/RCU access conventions, AES helper routines, OTX2 mailbox APIs, MCS mailbox message types, and hardware capability discovery from `otx2_set_hw_capabilities()`. It integrates with `otx2_common.c` capability setup and mailbox up handlers for MCS events.

## Risks

- Several add paths allocate hardware resources and then return on later programming errors without fully unwinding the newly allocated/listed resources.
- Key material is stored in driver structures and not explicitly zeroed before `kfree()`.
- List operations do not show a local lock; MACsec core/rtnl serialization must be relied upon.
- Stats callbacks clear hardware counters and accumulate in software, so missed calls around policy changes can skew reported counters.
- `cn10k_mcs_init()` returns 0 even when PN wrap interrupt configuration fails, leaving offload enabled with reduced event reporting.
- Event handling walks TXSC/SA mappings without breaking after a match; duplicate or stale ids could produce wrong reporting.

## Test Signals

MACsec selftests with HW offload for AES-GCM-128/256 and XPN variants, VLAN device SecTAG offset, SecY open/stop/update/delete, TX/RX SC/SA add/update/delete, PN update and wrap events, replay protection, validate-frame modes, stats read/clear behavior, resource exhaustion, and unload cleanup are critical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_macsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn20k.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn20k.c

## Purpose

`cn20k.c` supplies CN20K-specific NIC operations. It implements new mailbox interrupt handling for AF/PF/VF and PF/VF channels, CN20K TC flower MCAM priority management, CN20K NPA aura/pool AQ initialization, CN20K SQ context initialization, and registers a CN20K `dev_hw_ops` table.

## Important APIs, Types, And Functions

- `cn20k_pfaf_mbox_intr_handler()` handles AF-to-PF up messages and AF replies.
- `cn20k_vfaf_mbox_intr_handler()` handles PF-to-VF notifications and replies.
- `cn20k_enable_pfvf_mbox_intr()`, `cn20k_disable_pfvf_mbox_intr()`, `cn20k_pfvf_mbox_intr_handler()`, and `cn20k_register_pfvf_mbox_intr()` manage four PF/VF mailbox interrupt vectors covering two mailbox banks and up to 96 VFs.
- TC helpers allocate/free MCAM entries, maintain priority ordering, and shift entries when possible.
- `cn20k_aura_aq_init()` and `cn20k_pool_aq_init()` program CN20K NPA AQ requests, including backpressure and page_pool setup.
- `cn20k_sq_aq_init()` programs CN20K NIX SQ contexts.
- `cn20k_hw_ops` selects CN20K mailbox, SQ, LMTST, refill, aura, and pool operations.
- `cn20k_init()` installs the ops table.

## Control Flow

PF/AF and VF/AF interrupt handlers read trigger bits, clear status, sync mailbox bounce buffers, inspect mailbox headers, queue the correct work item, and trace the interrupt. PF/VF registration allocates four `pf_irq_data` records, fills status register/start/mdev ranges by vector, names IRQs, requests IRQs with the selected hardware handler, and then enables interrupt masks.

TC allocation assigns hardware priority: rules with priority <=125 use that as hardware priority, otherwise PF/VF defaults 127/126. It allocates an MCAM entry relative to the current first TC entry unless using hardware priority. On add, the new node is inserted in priority order; if all entries up to the insertion point share the same key-width type, existing entries are shifted to preserve priority while saving MCAM space. Delete performs the inverse shift or frees the node's entry directly when mixed X2/X4 widths prevent shifting.

CN20K queue setup mirrors common/CN10K setup but uses CN20K mailbox request structures. Aura setup allocates a flow-control qmem cache line, configures count/limit/backpressure bpid, and uses a single `bpid` field rather than older split fields. Pool setup allocates stack qmem and creates a page_pool for RQ pools. `cn20k_init()` is a simple ops-table switch.

## State And Persistence

State includes `hw->pfvf_irq_devid[]`, dynamically allocated `pf_irq_data`, TC flow list entries and MCAM ids, NPA pool stack/fc/page_pool objects, and NIX SQ contexts. Hardware state persists in interrupt enable/status registers, NPC MCAM entries/counters, NPA aura/pool contexts, and NIX SQ contexts.

## Dependencies And Integration Points

The file depends on common NIC types, mailbox and trace helpers, CN10K LMT/refill helpers, TC flow-list helpers from `otx2_tc.c`, NPC install/free mailbox messages, DCB PFC mapping when enabled, page_pool, and CN20K register definitions from `otx2_reg.h`. PF/VF probe selects these ops for CN20K silicon.

## Risks

- PF/VF IRQ registration can leak already requested IRQs if a later vector request fails.
- Interrupt ranges use `mdevs = 96` for the second bank, so queue-work helpers must interpret start/count consistently.
- TC shifting only works when all affected entries have the same key-width type; mixed X2/X4 flows can reject insertion after resources were allocated.
- Delete shifting depends on list order and `list_next_entry()` before reaching the deleted node; edge cases need coverage.
- CN20K pool init returns page_pool errors without freeing previously allocated stack qmem.

## Test Signals

CN20K PF/VF probe with AF/PF and PF/VF mailbox traffic, >64 VF interrupt coverage, TC flower add/delete with priority shifts and mixed X2/X4 entries, MCAM allocation/free failure injection, RX/TX queue bring-up, DCB/PFC backpressure, page_pool allocation failure, and TX/RX traffic under CN20K ops are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn20k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn20k.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn20k.h

## Purpose

`cn20k.h` declares CN20K-specific NIC entry points used by common PF/VF and TC code. It is a narrow header for hardware-op installation, PF/VF mailbox interrupt management, and TC MCAM priority helpers.

## Important APIs, Types, And Functions

- Forward declarations for `struct otx2_flow_config` and `struct otx2_tc_flow`.
- `cn20k_init()` installs CN20K `dev_hw_ops`.
- `cn20k_register_pfvf_mbox_intr()`, `cn20k_disable_pfvf_mbox_intr()`, and `cn20k_enable_pfvf_mbox_intr()` manage PF/VF mailbox interrupts.
- `cn20k_tc_update_mcam_table_del_req()`, `cn20k_tc_update_mcam_table_add_req()`, `cn20k_tc_alloc_entry()`, and `cn20k_tc_free_mcam_entry()` manage CN20K TC MCAM entries.

## Control Flow

There is no executable control flow in this header. Callers use these prototypes to dispatch CN20K-specific setup from probe and to call CN20K TC helpers when installing/removing flower rules.

## State And Persistence

No state is stored here. Implementations mutate NIC runtime state, IRQ registrations, TC flow lists, and hardware MCAM contexts.

## Dependencies And Integration Points

It includes `otx2_common.h`, so it shares core NIC types and also relies on include guards to avoid recursive header issues. It is included by common NIC and TC code that needs CN20K specialization.

## Risks

- Prototype drift breaks cross-file builds.
- The `cn20k_tc_alloc_entry()` parameter name `dummy` hides that callers pass an install-flow request; mismatched expectations can obscure review.
- Including `otx2_common.h` from a silicon-specific header increases rebuild/blast radius for common header changes.

## Test Signals

Build coverage with CN20K support enabled and disabled, plus probe and TC offload tests that call every declared function, validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn20k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_common.c

## Purpose

`otx2_common.c` is the central shared implementation for OcteonTX2/RVU NIC PF/VF resource setup, queue configuration, stats, RSS, MAC/MTU/pause programming, TX scheduler configuration, NPA/NIX attach/detach, buffer/aura/pool management, interrupt affinity, feature gating, mailbox response handlers, and DMA mapping helpers used by the transmit path.

## Important APIs, Types, And Functions

- Stats APIs update RQ/SQ op stats, LMAC/FEC stats, device stats, and `ndo_get_stats64`.
- Netdev programming APIs set/get MAC address, MTU, pause frames, RSS key/table/flowkey, UDP GSO LSO formats, IRQ coalescing, and max MTU.
- Buffer helpers allocate RX buffers from AF_XDP, page_pool, or napi fragments and refill pools.
- Scheduler helpers allocate/configure/free/flush NIX TX scheduler queues and SQBs.
- Queue setup functions initialize RQ, SQ, CQ, NIX LF, NPA LF, SQ/RQ aura pools, refill work, and CQ interrupt affinity.
- Resource APIs attach/detach NPA/NIX LFs, disable NPA/NIX contexts, and configure backpressure.
- Mailbox handlers cache AF responses for CGX stats, FEC stats, NPA/NIX LF allocation, MSIX offsets, and backpressure ids.
- Feature helpers validate NTUPLE/TC feature interactions and query MACsec capability.
- Weak `otx2_mbox_up_handler_*` stubs provide default no-op handling for CGX/MCS up messages.
- DMA helpers map/unmap skb fragments, switching to bidirectional DMA for XFRM offload.

## Control Flow

Probe/open setup attaches NPA/NIX resources, reads MSIX offsets, configures NPA LF, allocates aura/pool software state, initializes RQ and SQ aura/pool contexts, allocates buffer pointers and frees them to hardware auras, configures NIX LF with queue counts and RSS settings, initializes RQ/SQ/CQ contexts, sets up scheduler hierarchy, RSS, LSO, IRQ coalescing, and refill work. Much of this code batches AQ mailbox messages and flushes when the shared mailbox buffer is full.

Queue initialization is layered. `otx2_rq_init()` programs RQ drop/pass thresholds and large-packet aura. `otx2_sq_init()` allocates SQE, doubled SQE/CPT-SG ring, CPT response memory, TSO headers, SG tracking, optional timestamp memory, SQB metadata, and then calls the silicon-selected `sq_aq_init`. `otx2_cq_init()` selects RX/TX/XDP/QoS type, allocates CQE memory, configures XDP memory model when needed, links the receive buffer pool, and programs CQ context.

Cleanup frees SQBs back to pools, drains/free buffer pointers, destroys page_pools and AF_XDP state, frees scheduler queues, disables contexts, and detaches resources through mailbox. Feature toggles ensure TC and ntuple rules do not conflict. Stats paths read hardware atomic op registers or send mailbox requests to refresh CGX counters.

## State And Persistence

The file manages most of `struct otx2_nic` runtime state: `hw` queue counts, channel bases, scheduler lists, RSS config, stats, bpid values, capability flags, `qset` queues/pools/CQs, refill work, flow config, AF_XDP bitmaps, and mailbox-derived resource metadata. Hardware state persists in NPA LF/aura/pool contexts, NIX LF/RQ/SQ/CQ/RSS/LSO contexts, scheduler hierarchy, backpressure, MAC/MTU/pause settings, interrupt coalescing registers, and flow/capability state until reset or detach.

## Dependencies And Integration Points

It depends on Linux PCI/interrupt/page_pool/XDP/DCB/XFRM APIs, OTX2 register and context headers, `cn10k.h` silicon ops, AF mailbox ABI, QoS/TC/flow helpers, devlink/ethtool call sites, and transmit/receive datapaths. Many functions are exported for PF, VF, representor, ethtool, TC, and XDP modules.

## Risks

- Error unwinding is complex; many setup functions allocate multiple qmem/page_pool/software structures before returning, so partial failures can leak or leave mailbox messages queued.
- `otx2_sq_init()` has repeated comment text and several allocations where later failures do not free earlier qmem allocations locally.
- `otx2_dma_map_skb_frag()` calls `skb_unshare()` for XFRM offload but assigns only to a local variable, which needs careful validation against caller expectations.
- Feature interaction rules for NTUPLE and TC are strict; stale flow counts can block feature changes.
- Shared mailbox batching requires callers to reset or flush correctly on allocation failures.
- Scheduler and backpressure configuration has many silicon/SDP/DCB branches; wrong channel/link type can break traffic shaping or pause behavior.

## Test Signals

Probe/open/close/reset cycles, RX/TX traffic, RSS indirection/hash tests, UDP GSO offload, XDP and AF_XDP zero-copy, page_pool and napi-frag paths, PTP timestamp SQ allocation, MAC/MTU/pause changes, DCB/PFC backpressure, TC/ntuple feature toggles, NPA/NIX attach/detach failure injection, IRQ affinity/coalescing, stats correctness, and IPsec DMA mapping/unmapping tests provide broad coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_common.c -->
