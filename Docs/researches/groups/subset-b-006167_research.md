# Research Group subset-b-006167

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/smp.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/smp.c

Purpose: implements the Linux Bluetooth Security Manager Protocol (SMP) fixed-channel logic for LE pairing, LE Secure Connections, key derivation, key distribution, security upgrade requests, resolvable private address helpers, Secure Connections OOB generation, optional SMP-over-BR/EDR key derivation, and SMP crypto self-tests.

Important APIs, types, and functions: private state is split between per-device `struct smp_dev` on the listening L2CAP SMP channel and per-pairing `struct smp_chan` on the connection channel. `smp_register`, `smp_unregister`, and `smp_force_bredr` manage root fixed channels. `smp_conn_security`, `smp_sufficient_security`, `smp_user_confirm_reply`, and `smp_cancel_and_remove_pairing` are the main external security hooks. `smp_irk_matches`, `smp_generate_rpa`, and `smp_generate_oob` serve address privacy and OOB consumers. The cryptographic core implements Bluetooth-specified `aes_cmac`, `smp_f4`, `smp_f5`, `smp_f6`, `smp_g2`, `smp_h6`, `smp_h7`, legacy `smp_e`, `smp_c1`, `smp_s1`, and `smp_ah`.

Control flow: `smp_add_cid` creates root listening channels for LE SMP and optionally BR/EDR SMP. `smp_new_conn_cb` creates per-connection L2CAP channels, `smp_ready_cb` publishes them through `conn->smp`, and `smp_recv_cb` dispatches inbound PDUs through `smp_sig_channel`. The dispatcher validates opcode ordering with `smp->allow_cmd`, calls command handlers, sends Pairing Failed on protocol errors, and destroys the session on failure. Pairing starts from `smp_conn_security`, `smp_cmd_security_req`, or `smp_cmd_pairing_req`; request/response negotiation fills raw `preq` and `prsp` byte arrays because those exact PDUs feed confirm and Secure Connections calculations. Legacy pairing selects Just Works, passkey, or OOB through `tk_request`, exchanges confirm/random PDUs, verifies `c1`, derives STK with `s1`, and starts encryption or stores responder STK. Secure Connections exchanges public keys, computes ECDH DHKey, selects OOB/passkey/numeric-comparison flow, derives MacKey and LTK through `f5`, verifies DHKey checks through `f6`, then starts encryption and distributes eligible keys. Key distribution sends local LTK, IRK, CSRK, or BR/EDR link keys and waits for remote keys in strict order.

State and persistence: transient secrets, randoms, key material pointers, method, passkey round, and flags live in `struct smp_chan` and are freed with `kfree_sensitive`. `security_timer` disconnects after 30 seconds of inactivity. Long-lived keys are persisted through HCI lists using `hci_add_ltk`, `hci_add_irk`, `hci_add_link_key`, and reported to management with `mgmt_new_*` only after `SMP_FLAG_COMPLETE`. Failed sessions remove partially added LTK and IRK RCU list entries; debug keys are deleted unless explicitly kept. Identity-address updates can retarget the connection and schedule `id_addr_timer`.

Dependencies and integration points: depends on Bluetooth HCI/L2CAP/mgmt, kernel crypto `cmac(aes)` and `ecdh-nist-p256`, AES helpers, debugfs for self-test reporting, HCI key stores, device feature flags, and L2CAP fixed-channel callbacks. It integrates with userspace through management user confirmation/passkey requests, key notifications, and authentication failure events.

Risks: this file is security critical. Errors in byte order, confirm inputs, allowed-command transitions, key-size enforcement, or debug-key cleanup can cause interoperability failures or weaken pairing. RCU key deletion during cancellation is delicate, and user-reply races are guarded by the L2CAP channel lock. OOB and SC false-positive fallback paths are compatibility-sensitive. The dispatcher drops unexpected commands silently except selected key rejection cases, so trace/debug coverage matters when diagnosing peers.

Test signals: `CONFIG_BT_SELFTEST_SMP` runs spec-vector tests for debug public key generation, `ah`, `c1`, `s1`, `f4`, `f5`, `f6`, `g2`, and `h6`, publishing PASS/FAIL under debugfs. Runtime test signals include Bluetooth mgmt pairing tests, LE privacy/RPA tests, SMP interoperability, BR/EDR cross-transport pairing, debug-key handling, and negative tests for blocked keys, invalid key size, out-of-order PDUs, and user rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/smp.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/smp.h

Purpose: declares Bluetooth SMP wire-format structures, opcodes, error reasons, key-distribution/authentication constants, internal LTK type helpers, and the SMP entry points used by the rest of the Bluetooth stack.

Important APIs, types, and functions: packed command structs mirror the SMP PDUs: `smp_command_hdr`, `smp_cmd_pairing`, confirm/random/fail PDUs, encryption information, identity information, signing information, security request, Secure Connections public key, DHKey check, and keypress notification. Constants define command codes through `SMP_CMD_MAX`, IO capabilities, OOB flags, distribution bits, auth bits including Secure Connections and CT2, failure reasons, and min/max encryption key sizes. Inline helpers `smp_ltk_is_sc` and `smp_ltk_sec_level` map stored `struct smp_ltk` metadata to security levels. `enum smp_key_pref` lets callers distinguish "STK is acceptable" from "prefer an LTK".

Control flow: the header does not implement protocol flow, but it defines the contract used by `smp.c` and other Bluetooth modules. Callers use `smp_conn_security` to request a security level, `smp_sufficient_security` to decide whether the current link already satisfies policy, `smp_user_confirm_reply` to feed mgmt user decisions back into the SMP state machine, and `smp_cancel_and_remove_pairing` to abort pairing while removing stored keys. Device lifecycle code calls `smp_register`, `smp_unregister`, and `smp_force_bredr`.

State and persistence: no storage is allocated here. The LTK type enum records whether stored keys are legacy STK/LTK, responder keys, P-256 Secure Connections keys, or debug P-256 keys. Those values influence persistence and security-level decisions in `smp.c`.

Dependencies and integration points: relies on Bluetooth address and HCI key types from surrounding headers included before or with it. The public prototypes connect HCI core, L2CAP, mgmt, and privacy code to SMP implementation details while keeping the PDU layout centralized.

Risks: because the structs are packed wire contracts, field order and sizes must stay exactly aligned with the Bluetooth specification. Changing enum values or auth/distribution bit masks would corrupt negotiation and stored-key semantics. The fallback inline `bt_selftest_smp` returns success when selftests are disabled, so build configurations must be explicit when crypto vector testing is required.

Test signals: compile-time users validate the API surface. Runtime signals come through SMP selftests when enabled, Bluetooth pairing/security tests, and any code that checks security-level mapping for authenticated, unauthenticated, Secure Connections, and debug LTKs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/Makefile -->
# sources/distributed-fs/ceph-client/net/bpf/Makefile

Purpose: builds the kernel networking BPF test-run support objects when BPF syscall support is enabled.

Important APIs, types, and functions: this Makefile has no runtime APIs. It assigns `test_run.o` to `obj-$(CONFIG_BPF_SYSCALL)` and adds `bpf_dummy_struct_ops.o` only when `CONFIG_BPF_JIT=y`.

Control flow: Kbuild includes `test_run.c` whenever the BPF syscall is compiled so `BPF_PROG_TEST_RUN` support and related test kfunc registrations are present. The dummy struct-ops provider is JIT-gated because struct-ops test execution prepares BPF trampolines and executable images.

State and persistence: none directly. The selected objects register late-init callbacks and BTF/kfunc metadata at runtime.

Dependencies and integration points: depends on Kbuild symbols `CONFIG_BPF_SYSCALL` and `CONFIG_BPF_JIT`. It integrates with the networking tree by placing BPF test-run code under `net/bpf`.

Risks: an incorrect config gate would either omit required syscall test support or compile trampoline-dependent dummy struct ops where JIT infrastructure is unavailable. Since the file uses `:=` for the first assignment, additional unconditional objects would need care not to overwrite `test_run.o`.

Test signals: build matrix coverage for BPF enabled/disabled and BPF JIT enabled/disabled. BPF selftests that use `BPF_PROG_TEST_RUN`, fentry/fexit, modify-return, and struct-ops dummy programs signal whether this object selection is correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/bpf_dummy_struct_ops.c -->
# sources/distributed-fs/ceph-client/net/bpf/bpf_dummy_struct_ops.c

Purpose: provides a dummy BPF struct-ops target used by BPF selftests to validate struct-ops verifier behavior, trampoline preparation, nullable pointer handling, sleepable restrictions, and test-run invocation.

Important APIs, types, and functions: exports `bpf_struct_ops_test_run` for test execution against `bpf_dummy_ops`. `struct bpf_dummy_ops_test_args` holds up to `MAX_BPF_FUNC_ARGS` raw user arguments plus a copied `bpf_dummy_ops_state`. `dummy_ops_init_args`, `dummy_ops_copy_args`, and `dummy_ops_call_op` marshal user state into a generated trampoline call. `check_test_run_args` inspects the attached function prototype and verifier context arg metadata to reject NULL for non-nullable pointer arguments. `bpf_dummy_ops_btf_struct_access` permits verifier writes only to `bpf_dummy_ops_state`. `bpf_dummy_ops_check_member` limits sleepable programs to the `test_sleepable` member.

Control flow: late init registers `bpf_bpf_dummy_ops`. A test run first verifies the program is attached to the dummy ops BTF type, copies exactly the number of u64 arguments implied by the attach function prototype, checks nullable pointer rules, creates a temporary `bpf_tramp_link`, increments the program reference, asks `bpf_struct_ops_prepare_trampoline` for an executable image, protects it, calls the selected op through the trampoline, copies the possibly modified state back to userspace, and writes the return value. Cleanup frees args, trampoline image, link, and tlink array on all paths.

State and persistence: global `bpf_dummy_ops_btf` caches the BTF pointer passed by struct-ops registration. Runtime test state is per-call and temporary. Registration state persists for the module lifetime through `register_bpf_struct_ops`.

Dependencies and integration points: depends on BPF verifier internals, BTF type lookup, BPF link and trampoline APIs, CFI offset handling, and the generated CFI stub instance `__bpf_bpf_dummy_ops`. It is built only with BPF syscall and JIT support.

Risks: argument marshalling is ABI-sensitive because it calls a variadic function pointer through a trampoline. Nullable pointer enforcement depends on correct BTF arg offsets and verifier `ctx_arg_info`. Missing cleanup would leak BPF program refs or executable trampoline memory. Sleepable acceptance must stay aligned with struct-ops verifier expectations.

Test signals: BPF selftests for dummy struct ops, nullable and non-nullable context arguments, writes to `bpf_dummy_ops_state`, sleepable member acceptance/rejection, and test-run return/state copyback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/bpf_dummy_struct_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/test_run.c -->
# sources/distributed-fs/ceph-client/net/bpf/test_run.c

Purpose: implements kernel-side execution paths for `BPF_PROG_TEST_RUN` across tracing, raw tracepoint, SKB, XDP, flow dissector, socket lookup, syscall, and netfilter program types, plus test-only kfunc/fentry/modify-return hooks used by BPF selftests.

Important APIs, types, and functions: exported test-run functions include `bpf_prog_test_run_tracing`, `bpf_prog_test_run_raw_tp`, `bpf_prog_test_run_skb`, `bpf_prog_test_run_xdp`, `bpf_prog_test_run_flow_dissector`, `bpf_prog_test_run_sk_lookup`, `bpf_prog_test_run_syscall`, and `bpf_prog_test_run_nf`. Shared helpers include `bpf_test_timer_*`, `bpf_test_run`, `bpf_test_finish`, `bpf_ctx_init`, and `bpf_ctx_finish`. XDP live-frame mode uses `struct xdp_page_head`, `struct xdp_test_data`, `xdp_test_run_setup`, `xdp_test_run_batch`, and `bpf_test_run_xdp_live`. Test kfuncs include `bpf_fentry_test*`, `bpf_modify_return_test*`, and release/dtor kfuncs for referenced test structs.

Control flow: most entry points validate unsupported flags, CPU, repeat, batch, and buffer combinations; copy user data and context; build a synthetic kernel context; run the BPF program in a timed loop; and copy retval, duration, data, and context back. `bpf_test_run` wraps program execution in RCU and BPF run context setup, with cgroup storage allocation. SKB mode builds a dummy socket and skb, supports linear and fragmented packet input, converts selected `__sk_buff` fields, optionally verifies checksum-complete behavior, and returns packet bytes. XDP mode prepares an `xdp_buff` with optional metadata and frags; live mode allocates page-pool backed frames, runs actions in batches, converts PASS frames into skb receive lists, and flushes redirects. Raw tracepoint mode can run on a requested CPU. Flow dissector, sk_lookup, syscall, and netfilter paths each construct the relevant kernel context and enforce tight field validation.

State and persistence: per-call allocations include packet buffers, pages, skbs, sockets, context copies, page pools, cgroup storage, and temporary BPF run contexts. Late init registers fmodret IDs, kfunc ID sets, and destructor kfuncs that persist for the module lifetime. The timer accumulates average nanoseconds per iteration and handles reschedule and signal interruption.

Dependencies and integration points: integrates with BPF core, verifier-visible BTF/kfunc registration, trace events, page pool, XDP redirect machinery, netdevice RX queues, skb allocation, cgroup storage, flow dissector, sk lookup, netfilter hooks, and current network namespace loopback devices.

Risks: user-controlled sizes and contexts make validation critical. Nonlinear SKB/XDP copyback must avoid overrun and correctly report `-ENOSPC`. XDP live frames run side effects through redirect and receive paths, so device refs, page-pool lifetime, and bottom-half/RCU state must be balanced. Repeat loops need to remain interruptible and scheduler-friendly. Adding context fields without updating zero-tail validation can expose uninitialized or unsupported state.

Test signals: upstream BPF selftests heavily exercise this file: `prog_test_run` for SKB/XDP data and ctx copyback, tracing fentry/fexit/modify-return return encodings, raw tracepoint CPU selection, flow dissector output, sk_lookup selected socket cookies, syscall program context mutation, netfilter verdict contexts, XDP live-frame redirect/pass/drop behavior, kfunc release/dtor registration, and checksum-complete validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/test_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/Kconfig -->
# sources/distributed-fs/ceph-client/net/bridge/Kconfig

Purpose: defines configuration symbols for the Linux Ethernet bridge module and optional bridge features.

Important APIs, types, and functions: no C APIs are defined. Symbols include `BRIDGE`, `BRIDGE_IGMP_SNOOPING`, `BRIDGE_VLAN_FILTERING`, `BRIDGE_MRP`, and `BRIDGE_CFM`. `BRIDGE` is tristate and selects `LLC` and `STP`; the others are boolean feature gates depending on `BRIDGE` and, for VLAN filtering, `VLAN_8021Q`.

Control flow: Kconfig choices determine which bridge source files are compiled by the bridge Makefile and which code paths appear behind `IS_ENABLED(CONFIG_...)` in bridge implementation files. Defaults enable IGMP/MLD snooping but leave VLAN filtering, MRP, and CFM off unless selected.

State and persistence: the file controls build-time state only. User choices persist in kernel `.config` and affect module contents and runtime feature availability.

Dependencies and integration points: integrates with the networking Kconfig tree, LLC/STP protocol support, inet multicast support for snooping, VLAN support, MRP, and CFM code. Help text also documents the user-visible bridge module name and firewall implications.

Risks: changing defaults or dependencies changes kernel footprint and feature availability. Enabling bridge netfilter behavior has operational consequences because bridged IP/ARP traffic can appear in firewall paths. Optional feature gates must match Makefile object lists and source `#if` guards.

Test signals: configuration build tests for built-in, module, and disabled bridge states; feature combinations for snooping, VLAN filtering, MRP, CFM, bridge netfilter, IPv6, and switchdev; runtime smoke tests that verify requested features expose netlink options only when compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/Makefile -->
# sources/distributed-fs/ceph-client/net/bridge/Makefile

Purpose: maps bridge Kconfig symbols to the bridge module and its optional object files.

Important APIs, types, and functions: no runtime APIs are declared. `obj-$(CONFIG_BRIDGE) += bridge.o` builds the core bridge module. `bridge-y` includes core forwarding, FDB, STP, netlink, ioctl, device, input, and ARP/ND proxy objects. Feature-specific lines append sysfs, netfilter core, multicast/MDB/EHT, VLAN/MST, switchdev, MRP, and CFM objects. `br_netfilter.o` is a separate object selected by `CONFIG_BRIDGE_NETFILTER`.

Control flow: Kbuild composes `bridge.o` from `bridge-y` plus `bridge-$(CONFIG_...)` fragments. `subst m,y` is used for bridge netfilter and IPv6-related object inclusion so module/built-in combinations include compatible support objects.

State and persistence: none directly. The object composition determines which module init code and global registrations exist at runtime.

Dependencies and integration points: integrates the bridge directory with netfilter subdirectory builds, sysfs, multicast, VLAN, switchdev, MRP, and CFM subsystems. It must stay consistent with Kconfig feature gates and source-level `IS_ENABLED` guards.

Risks: missing an object silently removes feature handlers or leaves unresolved symbols. Incorrect `m` versus `y` handling can break mixed built-in/module bridge netfilter builds. Core object ordering is usually not semantically important but all required init/exit providers must be linked.

Test signals: build coverage for combinations of `CONFIG_BRIDGE`, `CONFIG_SYSFS`, `CONFIG_BRIDGE_NETFILTER`, `CONFIG_IPV6`, `CONFIG_BRIDGE_IGMP_SNOOPING`, `CONFIG_BRIDGE_VLAN_FILTERING`, `CONFIG_NET_SWITCHDEV`, `CONFIG_BRIDGE_MRP`, and `CONFIG_BRIDGE_CFM`, plus module load/unload smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br.c -->
# sources/distributed-fs/ceph-client/net/bridge/br.c

Purpose: provides generic bridge module lifecycle, netdevice and switchdev notifiers, per-net cleanup, STP protocol registration, boolean option routing, and bridge module init/exit.

Important APIs, types, and functions: notifier callbacks are `br_device_event`, `br_switchdev_event`, and `br_switchdev_blocking_event`. User-facing option helpers are `br_boolopt_toggle`, `br_boolopt_get`, `br_boolopt_multi_toggle`, and `br_boolopt_multi_get`; internal options are updated by `br_opt_toggle`. Module lifecycle is handled by `br_init` and `br_deinit`, and per-net namespace cleanup by `br_net_exit_rtnl`.

Control flow: netdevice events for bridge masters and ports update VLAN state, sysfs, FDB entries, STP bridge IDs, carrier state, MTU, features, and port deletion. Switchdev events add, delete, flush, and mark externally learned or offloaded FDB entries; blocking switchdev events handle port offload, unoffload, and replay. Boolean options dispatch to feature-specific code for multicast VLAN snooping, MST, MDB offload failure notification, local VLAN 0 FDB behavior, and no-link-local learning. `br_init` registers STP, FDB, pernet ops, netfilter core, netdevice notifier, switchdev notifiers, netlink, and ioctl hooks with reverse-order cleanup on failure.

State and persistence: maintains module-level notifier registrations and per-net bridge devices. Bridge option bits live in `br->options`. FDB, VLAN, STP, and switchdev changes persist in each `struct net_bridge` until device deletion or namespace teardown.

Dependencies and integration points: depends on LLC/STP, netdevice notifier API, switchdev, bridge netlink/ioctl/sysfs, FDB, VLAN, multicast, MST, and netfilter core. `MODULE_ALIAS_RTNL_LINK("bridge")` links rtnetlink bridge creation to the module.

Risks: notifier ordering and locking matter. `br_device_event` mixes RTNL, spinlock, and VLAN/FDB/STP side effects; missed notifications can leave stale FDB entries or wrong bridge MAC. Option multi-toggle can partially apply options before an error. Init error paths must unwind exactly. Switchdev offload replay has hardware integration risk.

Test signals: bridge module load/unload, creating/deleting bridges in namespaces, adding/removing ports, changing port MAC/MTU/name/carrier, VLAN events, switchdev FDB offload tests, boolean option netlink tests, and failure-injection tests around init registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_arp_nd_proxy.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_arp_nd_proxy.c

Purpose: implements bridge ARP proxy, IPv6 Neighbor Discovery suppression/proxy behavior, and helper logic for per-port or per-VLAN neighbor suppression.

Important APIs, types, and functions: `br_recalculate_neigh_suppress_enabled` updates the bridge-level optimization bit. IPv4 helpers include `br_do_proxy_suppress_arp`, `br_arp_send`, and local-address checks. IPv6 helpers include `br_is_nd_neigh_msg`, `br_do_suppress_nd`, `br_nd_send`, and local IPv6 address checks. `br_is_neigh_suppress_enabled` is the exported predicate for port and VLAN suppress state.

Control flow: ingress ARP or ND processing starts from bridge input/transmit paths when `BROPT_NEIGH_SUPPRESS_ENABLED` is set. ARP handling validates header lengths and address types, skips loopback/multicast targets, suppresses floods for gratuitous/duplicate cases, checks local bridge or VLAN IP ownership, then looks up a neighbor entry and matching FDB entry. If the destination port is proxy/suppress eligible, it crafts an ARP reply and either transmits through the port path or injects locally for bridge-originated traffic. ND handling validates ICMPv6 neighbor solicitation/advertisement, suppresses unsolicited advertisements and invalid source cases, checks local IPv6 ownership, then replies with a Neighbor Advertisement based on neighbor and FDB state.

State and persistence: no persistent tables are owned here. It reads bridge port flags, VLAN private flags, neighbor tables, FDB entries, bridge options, and writes `BR_INPUT_SKB_CB(skb)->proxyarp_replied` to guide later flooding decisions.

Dependencies and integration points: integrates with ARP, IPv6 addrconf, neighbor tables, VLAN devices, bridge FDB/VLAN helpers, SKB control block state, and bridge forwarding paths. IPv4 code is gated by `CONFIG_INET`; IPv6 ND code is gated by `CONFIG_IPV6`.

Risks: packet parsing and skb linearization must be conservative. Incorrect suppression can blackhole neighbor discovery or leak broadcasts to suppressed ports. VLAN PVID/tag handling affects whether replies are tagged correctly. Local-address detection walks upper devices, so RCU context and device references matter. ND option parsing must avoid malformed option loops.

Test signals: ARP/ND proxy and suppression selftests with per-port and per-VLAN settings, VLAN-tagged requests, local bridge IP targets, gratuitous ARP, unsolicited NA, invalid ND options, neighbor table validity changes, and FDB-known versus unknown destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_arp_nd_proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_cfm.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_cfm.c

Purpose: implements bridge Connectivity Fault Management (CFM) MEP and peer-MEP state, Continuity Check Message (CCM) transmit/receive processing, defect detection timers, and CFM frame interception for the bridge.

Important APIs, types, and functions: MEP lookup helpers `br_mep_find`, `br_mep_find_ifindex`, `br_peer_mep_find`, and `br_mep_get_port` drive object resolution. Public configuration APIs include `br_cfm_mep_create`, `br_cfm_mep_delete`, `br_cfm_mep_config_set`, `br_cfm_cc_config_set`, `br_cfm_cc_peer_mep_add`, `br_cfm_cc_peer_mep_remove`, `br_cfm_cc_rdi_set`, `br_cfm_cc_ccm_tx`, `br_cfm_mep_count`, `br_cfm_peer_mep_count`, `br_cfm_created`, and `br_cfm_port_del`. Runtime frame/timer helpers include `ccm_frame_build`, `ccm_tx_work_expired`, `ccm_rx_work_expired`, `ccm_tlv_extract`, and `br_cfm_frame_rx`.

Control flow: creating the first MEP registers an `ETH_P_CFM` bridge frame handler; deleting the last removes it. MEP creation validates port-domain/down-MEP constraints and enforces one port MEP per port. CC configuration enables or disables peer timers and resets sequence counters. Peer MEP add starts receive defect monitoring if CC is enabled. RX handling consumes CFM frames at or below the local MD level, validates version, opcode, MAID, peer MEP ID, and interval, updates peer status flags and sequence tracking, clears defects on valid reception, parses up to four TLVs, and notifies netlink listeners on defect changes. TX scheduling builds CCM frames with sequence number, local MEP ID, MAID, optional port/interface TLVs, and sends them until a configured period expires.

State and persistence: CFM state lives under `br->mep_list` as RCU hlist entries. Each MEP stores creation/configuration, RDI, CC config, TX info, status flags, sequence numbers, a port RCU pointer, peer list, and delayed TX work. Each peer stores status, miss count, and delayed RX work. State persists until netlink deletion, port deletion, or bridge teardown.

Dependencies and integration points: depends on `br_private_cfm.h`, UAPI CFM bridge attributes, bridge frame-type registration, RCU, RTNL, delayed work on `system_percpu_wq`, netlink notifications through `br_info_notify`, and bridge port lifecycle.

Risks: delayed work and RCU deletion must be synchronized to avoid use-after-free. The 3.25 interval defect logic depends on timer cadence and jiffies conversion. Sequence numbers are tracked per MEP, not per peer, which is important for interpreting multiple peer behavior. Partial TLV parsing intentionally handles status TLVs only. CFM frame consumption rules can affect forwarding at different maintenance-domain levels.

Test signals: bridge CFM netlink create/config/delete tests, peer add/remove, CCM TX period start/stop/update, RX of valid CCMs, wrong MAID/interval/opcode/version/MD level, TLV extraction, defect notification after missed intervals, port deletion cleanup, and RCU/workqueue debug testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_cfm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_cfm_netlink.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_cfm_netlink.c

Purpose: parses bridge CFM nested netlink attributes into CFM core operations and serializes CFM configuration/status back into bridge netlink responses.

Important APIs, types, and functions: policy arrays define accepted attributes for MEP create/delete/config, CC config, peer MEP add/remove, RDI, and CCM TX. `br_cfm_parse` is the main setter entry point. Parser helpers call into `br_cfm_mep_create`, `br_cfm_mep_delete`, `br_cfm_mep_config_set`, `br_cfm_cc_config_set`, `br_cfm_cc_peer_mep_add`, `br_cfm_cc_peer_mep_remove`, `br_cfm_cc_rdi_set`, and `br_cfm_cc_ccm_tx`. Dump functions are `br_cfm_config_fill_info` and `br_cfm_status_fill_info`.

Control flow: `br_cfm_parse` adjusts a port-scoped call to the owning bridge, parses the top-level nested CFM attribute, then applies any present nested operations in a fixed order: create, delete, MEP config, CC config, peer add, peer remove, RDI, and CCM TX. Each parser verifies required attributes, copies binary MAC/MAID fields, decodes scalar values, and delegates semantic validation to `br_cfm.c`. Config dumping iterates all MEPs and peers, emitting nested create/config/CC/RDI/TX/peer-info records. Status dumping emits MEP and peer status, and on GETLINK clears edge-triggered "seen" flags after reporting them.

State and persistence: this file owns no long-lived state. It mutates CFM state indirectly through core APIs and clears selected status flags during status reporting when `getlink` is true.

Dependencies and integration points: depends on rtnetlink/genetlink attribute helpers, CFM UAPI attribute IDs and constants, bridge private structures, CFM core implementation, and RCU iteration over MEP/peer lists while filling skb responses.

Risks: required-attribute checks are strict, so userspace must send complete nested records. Applying multiple operations from one netlink message can partially mutate state before a later operation fails. Status dumping has read-and-clear semantics for several flags, which can surprise pollers. `-EMSGSIZE` paths must cancel only the active nest.

Test signals: rtnetlink tests for every CFM operation, missing attribute rejection, policy max enforcement for mdlevel and MEP ID, nested dump layout compatibility with `ip link`/bridge tools, status read-and-clear behavior, and multi-operation error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_cfm_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_device.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_device.c

Purpose: implements the bridge net_device operations, transmit path from the bridge device, device initialization/uninitialization, open/stop behavior, ethtool reporting, netpoll support, slave add/delete hooks, forward-path reporting, and bridge private structure setup.

Important APIs, types, and functions: `br_dev_xmit` is the bridge master transmit routine. Lifecycle helpers are `br_dev_init`, `br_dev_uninit`, `br_dev_open`, `br_dev_stop`, `br_change_mtu`, `br_set_mac_address`, and `br_dev_setup`. Netpoll helpers include `br_netpoll_enable` and `br_netpoll_disable` when configured. `br_add_slave` and `br_del_slave` call port attach/detach code. `br_fill_forward_path` describes hardware/software forwarding paths for upper stack consumers. `nf_br_ops` is an exported RCU pointer for bridge netfilter hooks.

Control flow: transmit validates Ethernet header, clears bridge skb control state, lets bridge netfilter intercept, accounts TX stats, strips the Ethernet header, validates VLAN ingress, optionally performs ARP/ND proxy suppression, then classifies destination as broadcast, multicast, known unicast, or unknown unicast. Broadcast and unknown unicast flood, multicast consults snooping/MDB/querier state, and known unicast forwards to the FDB destination port. Device init builds FDB/MDB/VLAN/multicast stats state with unwind on errors. Open starts the queue, enables STP and multicast; stop disables them and stops the queue. Setup initializes netdev ops, features, flags, bridge lists, locks, STP defaults, netfilter fake route, timers, multicast, and FDB garbage collection work.

State and persistence: persistent bridge state is allocated in `netdev_priv(dev)` as `struct net_bridge`. It owns port, FDB, frame type, MRP, CFM, and hash lists; locks; options; timers; multicast/VLAN/FDB/MDB data; STP bridge IDs and timers; and per-CPU stats. MTU changes set `BROPT_MTU_SET_BY_USER`. Netpoll state attaches to ports while enabled.

Dependencies and integration points: integrates with net_device ops, bridge FDB/MDB/VLAN/multicast/STP/netlink/ioctl code, bridge netfilter, netpoll, ethtool, switchdev forwarding path API, neighbor suppression helpers, and optional CFM/MRP list initialization.

Risks: `br_dev_xmit` runs with BH disabled and relies on RCU-protected bridge data. Incorrect skb header movement or VLAN ingress handling can corrupt forwarding. Multicast logic must free or forward skb exactly once. Init/uninit unwind must mirror allocations. `br_fill_forward_path` mutates VLAN stack context and can underflow if caller state is inconsistent.

Test signals: bridge forwarding tests for broadcast/multicast/known/unknown unicast, VLAN ingress filtering, neighbor suppression on locally originated packets, multicast snooping/MDB paths, MTU and MAC changes, open/stop STP transitions, netpoll setup/cleanup, add/delete slave operations, ethtool link settings, and device teardown leak/UAF checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_device.c -->
