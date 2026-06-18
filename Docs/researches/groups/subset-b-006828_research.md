# Research Report: subset-b-006828

Grouped research for Linux networking selftest sources under `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net`. Each section is source-tree aligned and bracketed for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nic_timestamp.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nic_timestamp.py`

## Purpose
Tests hardware timestamping configuration paths on a real NIC, covering both the legacy `SIOCGHWTSTAMP` / `SIOCSHWTSTAMP` ioctl ABI and the ethtool netlink timestamp configuration API. It verifies that advertised TX timestamp types and RX filters can be applied and read back consistently through both interfaces.

## Important APIs, Types, And Functions
- `hwtstamp_config` and `ifreq` are `ctypes.Structure` mirrors of the kernel ABI structs needed by the ioctl path.
- `__get_hwtimestamp_support()` reads `EthtoolFamily.tsinfo_get()` and converts `tx-types` and `rx-filters` bitsets into testable lists.
- `__get_hwtimestamp_config_ioctl()` / `__set_hwtimestamp_config_ioctl()` wrap `fcntl.ioctl()` against `SIOCGHWTSTAMP` and `SIOCSHWTSTAMP`.
- `__get_hwtimestamp_config()` / `__set_hwtimestamp_config()` wrap `cfg.ethnl.tsconfig_get()` and `tsconfig_set()`.
- `__perform_hwtstamp_tx()` and `__perform_hwtstamp_rx()` implement the shared test loops used by `test_hwtstamp_*`.

## Control Flow
`main()` creates `NetDrvEnv(__file__, nsim_test=False)`, attaches an `EthtoolFamily`, and runs four ksft cases: TX via ioctl, TX via netlink, RX via ioctl, and RX via netlink. Each case saves the original timestamp configuration, iterates all supported advertised settings, applies one setting, reads it back through netlink and ioctl, asserts consistency, then restores the original configuration.

## State And Persistence
The file mutates NIC timestamp configuration. Restoration is explicit at the end of `__perform_hwtstamp_tx()` and `__perform_hwtstamp_rx()`, but not protected by `defer()` or `finally`, so a mid-loop assertion or unexpected exception can leave timestamp settings changed. Socket objects in ioctl helpers are closed after successful ioctl but not via a context manager.

## Dependencies And Integration Points
Depends on `lib.py` ksft helpers, `NetDrvEnv`, `EthtoolFamily`, and `NlError`. The test skips `EOPNOTSUPP` from netlink/ioctl as lack of hardware timestamping support. It is intended for hardware devices, not netdevsim.

## Risks
The code assigns `tscfg = orig_tscfg` and mutates nested fields, so the saved original dict can be altered before restoration unless the netlink family returns fresh immutable copies. RX tests allow drivers to broaden PTP filters by accepting returned RX filter indexes greater than requested, which is intentional but could hide overbroad behavior outside the PTP convention.

## Test Signals
Pass signals are ksft equality between netlink bit values and ioctl integer fields for all advertised TX/RX settings. Skip signals are `EOPNOTSUPP` for timestamp info/config support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nic_timestamp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_forward.bpf.c -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_forward.bpf.c`

## Purpose
Provides the tc ingress BPF forwarding program used by `NetDrvContEnv` and netkit queue lease tests. It redirects selected IPv6 traffic from the physical NIC ingress path to the netkit peer with `bpf_redirect_peer()`.

## Important APIs, Types, And Functions
- `SEC("tc/ingress") int tc_redirect_peer(struct __sk_buff *skb)` is the only program.
- Global `.bss` variables `netkit_ifindex` and `ipv6_prefix` are patched by userspace after load.
- `ctx_ptr()` safely casts packet offsets from `__sk_buff`.
- `v6_p64_equal()` compares the first 64 bits of destination IPv6 address with the configured prefix.

## Control Flow
The program exits with `TC_ACT_OK` for non-IPv6 packets, truncated Ethernet headers, truncated IPv6 headers, or IPv6 destinations outside the configured prefix. Matching IPv6 packets are redirected to `netkit_ifindex`.

## State And Persistence
State is only BPF global data in `.bss`, populated by `NetDrvContEnv._attach_bpf()` through `bpftool map update`. The program itself has no maps for counters or persistence beyond the globals.

## Dependencies And Integration Points
Built as `nk_forward.bpf.o` and attached by `tc filter add ... ingress bpf obj ... sec tc/ingress direct-action`. Depends on kernel helpers `bpf_redirect_peer()` and BPF CO-RE style global data availability.

## Risks
Only the upper 64 bits of IPv6 destination are compared, so the userspace prefix must be a /64 as assumed by `NetDrvContEnv`. The program does not inspect L4 protocol or route state, so any IPv6 packet to that prefix is forwarded.

## Test Signals
Validated indirectly by `nk_netns.py` and `nk_qlease.py`: pings or io_uring zero-copy receive traffic must reach the netkit namespace endpoint through the redirected path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_forward.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_netns.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_netns.py`

## Purpose
Selftests `NetDrvContEnv` by verifying IPv6 connectivity between a remote endpoint, the physical NIC, and a netkit-backed namespace created by the environment.

## Important APIs, Types, And Functions
- `test_ping(cfg)` requires IPv6, then runs one ping from the remote host to `cfg.nk_guest_ipv6` and one ping from the test netns to `cfg.remote_addr_v['6']`.
- `main()` creates `NetDrvContEnv(__file__)` and runs `test_ping`.

## Control Flow
Environment creation sets up the netkit pair, namespace routes, and tc BPF forwarding. The test then performs both traffic directions to prove forwarding and route setup work.

## State And Persistence
No local state is created beyond what `NetDrvContEnv` owns. Cleanup is delegated to the context manager, which removes tc filters, netkit links, namespace attachment, and IPv6 sysctl changes.

## Dependencies And Integration Points
Depends on `NetDrvContEnv`, `cmd`, remote command support, IPv6 configuration, and `nk_forward.bpf.o`. It is a small integration smoke test for the larger netkit queue lease setup.

## Risks
The test only sends one packet per direction, so it catches gross connectivity failures but not sustained forwarding, queue selection, or packet loss under load.

## Test Signals
Success is zero exit from both ping commands. `cfg.require_ipver("6")` produces a ksft skip if IPv6 endpoint data is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_netns.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_qlease.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_qlease.py`

## Purpose
Tests netdev queue lease behavior with a netkit namespace and io_uring zero-copy receive (`iou-zcrx`). It validates queue lease metadata, traffic delivery through a leased RX queue, conflicts with XDP multi-buffer attachment, and lease cleanup after netkit device destruction.

## Important APIs, Types, And Functions
- `set_flow_rule(cfg)` installs an ethtool ntuple rule steering TCPv6 traffic on `cfg.port` to `cfg.src_queue`.
- `test_iou_zcrx()` configures TCP data split, RSS indirection, an ntuple rule, then runs `iou-zcrx` in the netns and a remote client.
- `test_attrs()` queries `NetdevFamily.queue_get()` and validates the `lease` object, leased queue ID/type, peer ifindex, and `netns-id`.
- `test_attach_xdp_with_mp()` verifies an active io_uring queue lease rejects XDP attachment with `xdp.frags`.
- `test_destroy()` deletes the netkit host link while `iou-zcrx` holds references, then verifies lease state disappears and direct physical queue receive still works.

## Control Flow
`main()` creates `NetDrvContEnv(__file__, rxqueues=2)`, deploys the `iou-zcrx` binary to the remote, selects the last combined channel as source queue, enters the netkit namespace, and creates a netdev queue lease from the guest RX queue to the physical RX queue. The tests run in order, with `test_destroy()` last because it removes netkit devices.

## State And Persistence
The test mutates ring settings (`tcp-data-split`, `hds-thresh`, `rx`), RSS indirection, ntuple rules, tc filters, and netkit devices. Most changes use `defer()`, while `test_destroy()` explicitly nulls `cfg._nk_host_ifname` and `cfg._nk_guest_ifname` after deleting the link so environment cleanup does not double-delete.

## Dependencies And Integration Points
Depends on `NetDrvContEnv`, `NetNSEnter`, `EthtoolFamily`, `NetdevFamily`, `iou-zcrx`, `nk_forward.bpf.o`, `xdp_dummy.bpf.o`, tc, ethtool ntuple support, netkit, and IPv6. It integrates netdev netlink queue lease API with ethtool ring/RSS state and io_uring.

## Risks
The test assumes at least two combined channels and a driver supporting TCP data split plus queue leases. Cleanup is timing-sensitive: `test_destroy()` uses a timer to terminate `iou-zcrx` while `ip link del` waits on references and later sleeps briefly for asynchronous io_uring cleanup.

## Test Signals
Pass signals include successful `iou-zcrx` transfer, expected queue lease netlink fields, `io-uring` presence while receive is active, XDP attach failure under active memory provider, and `io-uring` absence after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_qlease.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ntuple.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ntuple.py`

## Purpose
Tests ethtool NFC / ntuple flow steering to RX queues for IPv4/IPv6 and TCP/UDP, using different combinations of source/destination IP and L4 port match fields.

## Important APIs, Types, And Functions
- `NtupleField` enumerates source IP, destination IP, source port, and destination port.
- `_require_ntuple()` checks the `ntuple-filters` feature is active.
- `_setup_isolated_queue()` ensures multiple combined channels, sets RSS to queue 0, and selects a nonzero test queue.
- `_ntuple_rule_add()` installs a rule and defers deletion.
- `_send_traffic()` uses local/remote `socat` to generate deterministic flows.
- `queue()` is variant-expanded across IP versions, protocols, and field sets.

## Control Flow
Each `queue()` variant checks IP version and ntuple support, isolates default traffic to queue 0, records queue stats, installs a flow rule to a random nonzero queue, sends 40 packets, then verifies those packets hit the target queue and no unrelated idle queues.

## State And Persistence
Mutates combined channel count, RSS indirection table, and ntuple rules. All expected reversible changes use `defer()` so normal ksft cleanup restores channels, RSS defaults, and rule deletion.

## Dependencies And Integration Points
Depends on `NetDrvEpEnv`, `EthtoolFamily`, `NetdevFamily.qstats_get()`, ethtool `-N`, `-L`, `-X`, remote `socat`, and hardware queue stats. It uses `cfg.wait_hw_stats_settle()` to account for delayed stats updates.

## Risks
It assumes queue stats are accurate enough to identify per-queue packet counts and that background traffic does not hit idle queues. It skips if ntuple is unavailable rather than enabling it.

## Test Signals
At least 40 packets must appear on the selected queue, and the sum on idle queues excluding queue 0 and the test queue must remain zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ntuple.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/pp_alloc_fail.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/pp_alloc_fail.py`

## Purpose
Tests driver resilience and stats reporting when page pool allocation failures are injected through kernel function error injection while traffic is running.

## Important APIs, Types, And Functions
- `_write_fail_config()` writes debugfs fail-function knobs.
- `_enable_pp_allocation_fail()` injects `page_pool_alloc_netmems` failures with interval 511, probability 100, and unlimited times.
- `_disable_pp_allocation_fail()` disables injection and clears the inject target.
- `test_pp_alloc()` checks `rx-alloc-fail` qstats, starts sustained `GenerateTraffic`, enables failures, validates counters and traffic continuity, then tries a ring-size wobble with `ethtool -G`.

## Control Flow
The test first ensures qstats expose `rx-alloc-fail`; if not, it skips. It starts iperf traffic, confirms packets are flowing, enables fail injection, samples counters for three seconds, checks failure growth against packet count, optionally changes RX ring size, and confirms traffic still flows. A `finally` block disables injection, stops traffic, and restores ring size if changed.

## State And Persistence
Mutates `/sys/kernel/debug/fail_function/*` and possibly NIC RX ring size. The critical fail injection state is restored in `finally`, reducing risk of leaving global kernel fault injection enabled.

## Dependencies And Integration Points
Depends on debugfs, `CONFIG_FUNCTION_ERROR_INJECTION`, page pool fail injection support, `NetdevFamily.qstats_get()`, `GenerateTraffic`, iperf3, and ethtool ring configuration.

## Risks
Global fail-function settings can affect unrelated networking during the test. Thresholds are heuristic: failure rate is expected at roughly one per 512 buffers with a 3.1x safety margin, and low failure rates become skips rather than failures.

## Test Signals
Pass requires traffic rate above 4000 RX packets per second before/during injection, increasing `rx-alloc-fail`, expected minimum fail count, and no traffic collapse after optional ring resize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/pp_alloc_fail.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_api.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_api.py`

## Purpose
Exercises ethtool netlink RSS APIs against legacy ioctl/CLI behavior. It validates indirection table setting, hash key setting, flow-hash field configuration, input transforms, context creation/deletion, and notification delivery.

## Important APIs, Types, And Functions
- `_require_2qs()` checks at least two RX queues via sysfs.
- `_ethtool_create()` parses ethtool-created RSS context or rule IDs.
- `_ethtool_get_cfg()` converts `ethtool -n ... rx-flow-hash` text into either ioctl flag letters or netlink names.
- `test_rxfh_nl_set_*`, `test_rxfh_indir*_ntf`, `test_rxfh_fields*`, `test_rss_ctx_*` cover the public cases.

## Control Flow
`main()` creates a hardware `NetDrvEnv`, attaches `EthtoolFamily`, and runs all global `test_` functions. Tests compare netlink reads to CLI/ioctl views, intentionally trigger netlink errors, subscribe to ethtool monitor notifications, and create/delete additional RSS contexts via both netlink and CLI.

## State And Persistence
Mutates RSS indirection tables, RSS keys, flow-hash fields, input transforms, and additional RSS contexts. Most changes are paired with `defer()` resets or delete actions. Some notification tests use `--disable-netlink` CLI calls to force ioctl-originated events.

## Dependencies And Integration Points
Depends on `EthtoolFamily.rss_get()`, `rss_set()`, `rss_create_act()`, `rss_delete_act()`, notification polling, ethtool CLI, and device support for RSS contexts and flow-hash field programming. Error validation inspects `NlError` extack data.

## Risks
The flow-hash parser relies on exact ethtool text labels. Input-transform changes are config-order-sensitive, so tests explicitly restore flow-hash and transform state in a chosen order. Notification timing uses short polling windows, which can be sensitive on slow systems.

## Test Signals
Pass signals include expected netlink errors with no notification, exact RSS table/key readback, consistent netlink vs ioctl flow-hash fields, expected notification names (`rss-ntf`, `rss-create-ntf`, `rss-delete-ntf`), and EBUSY when requesting a duplicate context ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_api.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_ctx.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_ctx.py`

## Purpose
Provides extensive RSS behavior tests for real drivers, focused on RSS key/indirection programming, context isolation, ntuple-to-context steering, context lifetime, queue reconfiguration safety, and persistence across interface down/up.

## Important APIs, Types, And Functions
- `get_rss()`, `ethtool_create()`, `require_ntuple()`, `require_context_cnt()`, `_get_rx_cnts()`, `_send_traffic_check()`, and `_ntuple_rule_check()` are shared helpers.
- `test_rss_key_indir()` checks key and table changes plus traffic distribution.
- `test_rss_queue_reconfigure()` validates table preservation and queue-count rejection for used queues.
- `test_rss_context*()` families create one to many contexts, steer flows with ntuple rules, and validate queue sets.
- `test_rss_context_persist_ifupdown()` is marked `ksft_disruptive` and verifies contexts/filters after link cycling.

## Control Flow
`main()` creates `NetDrvEpEnv`, initializes `EthtoolFamily` and `NetdevFamily`, then runs a fixed case list from basic RSS key/table tests through context creation, overlap, deletion, default context rules, and link-cycle persistence. Traffic checks use iperf-generated packet counts and queue qstats to assert which queues receive traffic.

## State And Persistence
The test frequently changes channel counts, RSS indirection tables, hash keys, ntuple filters, and link state. `defer()` generally restores channel count, RSS defaults, and context/rule deletion. The persistence tests intentionally create contexts before or while the interface is down and expect state to remain through `ip link down/up`.

## Dependencies And Integration Points
Depends on hardware queue stats, ethtool CLI, ethtool netlink, `NetdevFamily.qstats_get()`, ntuple filters, iperf3 via `GenerateTraffic`, and stable remote connectivity. Some cases require many queues and up to 32 RSS contexts.

## Risks
Many assertions are traffic-distribution based and may be noisy on active systems, so helper parameters distinguish target, empty, and noise queues. `cfg.context_cnt` is opportunistically learned when a driver cannot allocate all requested contexts, so test order matters.

## Test Signals
Pass signals include exact queue-hit expectations, nonzero RSS keys, duplicate-free context dumps, EBUSY on deleting in-use contexts, failure for missing contexts or nonexistent target queues, no carrier/error changes for hitless key update, and preserved contexts/ntuple rules after interface up/down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_ctx.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_drv.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_drv.py`

## Purpose
Tests driver-specific RSS indirection table sizing and dynamic resize semantics for the main RSS context and additional contexts.

## Important APIs, Types, And Functions
- `_is_power_of_two()`, `_get_rss()`, `_test_rss_indir_size()`, `_maybe_create_context()`, and `_require_dynamic_indir_size()` are shared helpers.
- `indir_size_4x()` enforces at least four table entries per queue.
- `resize_periodic()` verifies a periodic user table folds and unfolds across channel changes.
- `resize_below_user_size_reject()` validates that channel shrink below netlink user-size is rejected.
- `resize_nonperiodic_reject()` and `resize_nonperiodic_no_corruption()` validate rejection and state preservation for nonperiodic tables.

## Control Flow
Each test is expanded over main and additional context variants. The code reads channel limits, restores original channel counts via `defer()`, optionally creates an RSS context via netlink, then changes channel counts with ethtool while reading the table back through `ethtool -x`.

## State And Persistence
Mutates combined channel count, main RSS table, and additional RSS contexts. Main-context table changes are reset to default where needed; created contexts are deleted via deferred `rss_delete_act()`.

## Dependencies And Integration Points
Depends on `NetDrvEnv`, `EthtoolFamily`, ethtool CLI, ethtool netlink RSS context create/delete, and drivers that dynamically resize indirection tables.

## Risks
The tests intentionally skip devices without dynamic table sizing. Queue-count changes can affect the whole interface, so a failed resize path must leave both channel count and RSS table unchanged.

## Test Signals
Expected pass signals are minimum table length, exact folded/unfolded periodic patterns, `CmdExitFailure` on invalid shrink attempts, unchanged table contents after a failed resize, and unchanged channel count after rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_drv.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_flow_label.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_flow_label.py`

## Purpose
Tests IPv6 Flow Label participation in RSS hashing and verifies that Flow Label configuration does not leak into IPv4 flow types.

## Important APIs, Types, And Functions
- `_check_system()` ensures Python exposes `SO_INCOMING_CPU`, at least two RX queues exist, RPS/RFS is not configured, and the remote has IPv6 auto flow labels enabled.
- `_ethtool_get_cfg()` parses `rx-flow-hash` flags including `IPv6 Flow Label` as `l`.
- `_traffic()` sends either repeated datagrams on one socket or multiple sockets and records incoming CPUs.
- `test_rss_flow_label()` enables/disables UDP6 flow-label hashing and checks CPU spread.
- `test_rss_flow_label_6only()` rejects Flow Label on IPv4 types and scans IPv4 configs.

## Control Flow
The main IPv6 test reads initial UDP6 hash fields, adds `l` if needed, sends one-socket traffic expecting one CPU, sends multi-socket traffic expecting multiple CPUs, then disables `l` and expects multi-socket traffic to collapse to one CPU. The 6-only test attempts invalid `tcp4` configuration and inspects several IPv4 flow types.

## State And Persistence
Mutates UDP6 RSS hash fields through `ethtool -N`; restoration to the initial config is deferred. It reads but does not change RPS/RFS or remote auto-flowlabel sysctl.

## Dependencies And Integration Points
Depends on `NetDrvEpEnv`, `socat` on the remote, Python 3.11 `SO_INCOMING_CPU`, ethtool flow-hash support, and default remote IPv6 `auto_flowlabels=1`.

## Risks
CPU-based validation assumes IRQ/RSS CPU mapping reflects RSS queues and that RPS/RFS is off. It is sensitive to low CPU counts or external RPS configuration.

## Test Signals
Pass signals are exactly one CPU for one-socket flow-label traffic, at least two CPUs for multiple auto-labeled sockets with flow-label hashing enabled, one CPU after removing `l`, and `Invalid argument` for IPv4 flow-label configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_flow_label.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_input_xfrm.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_input_xfrm.py`

## Purpose
Tests symmetric RSS input transforms by sending UDP traffic with swapped source/destination ports and asserting both directions map to the same incoming CPU while still using multiple CPUs across different flows.

## Important APIs, Types, And Functions
- `traffic()` sends one remote `socat` UDP packet and returns the local socket's `SO_INCOMING_CPU`.
- `_rss_input_xfrm_try_enable()` reads current RSS input transforms and tries to enable a symmetric transform from ethtool netlink constants.
- `test_rss_input_xfrm()` runs repeated swapped-port probes for one IP version.
- `test_rss_input_xfrm_ipv4()` and `test_rss_input_xfrm_ipv6()` wrap the common test with IP-version requirements.

## Control Flow
The test skips unless at least two CPUs and Python `SO_INCOMING_CPU` are available. It enables or reuses a symmetric transform, then tries up to 100 random port pairs until 10 successful swapped-port comparisons pass. It finally checks that observed CPUs include at least two values, proving hashing is not trivially pinned.

## State And Persistence
Mutates RSS `input-xfrm` if no symmetric transform is already active. A deferred netlink set restores the original transform set.

## Dependencies And Integration Points
Depends on `NetDrvEpEnv`, `EthtoolFamily`, `socat` on remote, ethtool netlink `input-xfrm` constants, Python socket CPU reporting, and IPv4/IPv6 endpoint configuration.

## Risks
The broad `except` in the loop ignores transient failures and keeps trying, which helps with random port collisions but can hide repeated send/setup issues until the final fail. CPU mapping is an indirect proxy for queue hashing.

## Test Signals
Pass requires matching CPUs for each swapped-port pair, ten successful probes, and at least two distinct CPUs across all successful probes. Lack of symmetric transform support produces a skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_input_xfrm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/toeplitz.c -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/toeplitz.c`

## Purpose
Implements the packet receiver/verifier used by `toeplitz.py`. It validates NIC-provided RX hash values against a userspace Toeplitz calculation and can also validate RSS queue-to-CPU or RPS CPU selection.

## Important APIs, Types, And Functions
- `toeplitz()` computes the Toeplitz hash over IPv4/IPv6 4-tuples using the configured RSS key.
- `verify_rxhash()`, `verify_rss()`, and `verify_rps()` compare kernel packet metadata against software expectations.
- `setup_ring()`, `create_ring()`, `setup_rings()`, `recv_block()`, and `process_rings()` use PF_PACKET, TPACKET_V3, `PACKET_FANOUT_CPU`, and `TP_FT_REQ_FILL_RXHASH`.
- `read_rss_dev_info_ynl()` fetches RSS key and indirection table through ethtool YNL generated bindings.
- `parse_opts()` handles IPv4/IPv6, TCP/UDP, destination port, interface, explicit key, RSS CPU list, RPS bitmap, timeout, sink, and verbose mode.

## Control Flow
`main()` parses options, optionally opens a sink socket, creates one packet ring per CPU in a CPU fanout group, signals ksft readiness, processes rings until enough hash-bearing packets arrive or timeout, cleans up rings, and returns the number of frame verification errors.

## State And Persistence
Global process state stores config options, RSS key/table, RX queue CPU mapping, RPS silo mapping, packet rings, and frame counters. It maps packet rings with `MAP_LOCKED | MAP_POPULATE` and releases them during cleanup.

## Dependencies And Integration Points
Depends on Linux PF_PACKET v3, classic BPF socket filters, PACKET fanout, ethtool YNL generated userspace headers (`ynl.h`, `ethtool-user.h`), kselftest readiness helpers, and the NIC providing `tp_rxhash` metadata.

## Risks
The receiver supports up to 65536 CPU rings for RSS mode and exits if CPU count exceeds `RSS_MAX_CPUS`; memory use can be high on large systems. It assumes RSS key length 40 to 256 bytes and a 4-tuple hash. RPS mode is limited to 16 CPUs.

## Test Signals
The program prints counts for pass/nohash/fail, errors out on too few verifiable frames, and exits nonzero if any computed hash, RSS CPU, or RPS CPU mismatch is found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/toeplitz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/toeplitz.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/toeplitz.py`

## Purpose
Python harness for the Toeplitz RX hash verifier. It configures RSS hash function state, optionally configures RPS, sends TCP/UDP IPv4/IPv6 traffic, and runs the compiled `toeplitz` receiver.

## Important APIs, Types, And Functions
- `_check_rps_and_rfs_not_configured()` prevents external RPS/RFS state from contaminating CPU selection tests.
- `_get_irq_cpus()` maps RX queues to IRQ CPUs through `NetdevFamily.queue_get()` and `napi_get()`.
- `_configure_rps()` writes per-queue `rps_cpus` sysfs masks.
- `_test_variants()` creates rxhash-only, RSS CPU, and RPS CPU variants for TCP/UDP and IPv4/IPv6.
- `test()` builds the receiver command and sends repeated traffic until the receiver exits.

## Control Flow
Each variant requires the IP version, checks `receive-hashing: on`, forces ethtool netlink RSS hash function to Toeplitz with no input transform if necessary, chooses a destination port, builds `toeplitz` command arguments, configures RSS CPU map or RPS mask for grouped tests, starts the receiver with ksft readiness, and repeatedly sends packets from the remote until the receiver finishes.

## State And Persistence
Mutates RSS `hfunc` and `input-xfrm` only if needed and restores via `defer()`. RPS mode writes sysfs `rps_cpus` masks for all RX queues and defers clearing them.

## Dependencies And Integration Points
Depends on `toeplitz` binary in the same directory, `NetDrvEpEnv`, ethtool netlink, `NetdevFamily`, `socat` on remote, IRQ affinity files, and sysfs RPS knobs.

## Risks
RSS CPU tests require IRQs mapped to single CPUs; RPS tests require spare CPUs below the C helper's `RPS_MAX_CPUS`. Existing RPS/RFS configuration causes skips because it would change CPU selection.

## Test Signals
The harness reports receiver stdout/stderr through ksft logs. Success requires the C receiver to see enough packets and exit with no hash/RSS/RPS verification errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/toeplitz.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/tso.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/tso.py`

## Purpose
Runs a TSO/LSO validation suite for direct TCP and tunneled TCP traffic. It verifies that disabling segmentation features suppresses hardware GSO counts, enabling features increases hardware GSO counts, and enabling segmentation does not cause excessive retransmits.

## Important APIs, Types, And Functions
- `sock_wait_drain()` waits for the TCP send queue to drain via `TIOCOUTQ`.
- `tcp_sock_get_retrans()` extracts retransmission count from `TCP_INFO`.
- `run_one_stream()` sends 4 MiB over a TCP socket and compares queue GSO stats before/after.
- `build_tunnel()` creates matching VXLAN/GRE/IP6GRE devices locally and remotely.
- `query_nic_features()` caches hardware/wanted features, partial GSO capability, and qstat support.
- `test_builder()` creates concrete ksft cases for feature/IP/tunnel combinations.

## Control Flow
`main()` creates `NetDrvEpEnv`, queries NIC features and qstats, constructs cases for IPv4/IPv6 TCP, VXLAN, VXLAN checksum, GRE, and IP6GRE combinations, then runs generated tests. Each generated test disables the target feature and verifies low LSO counters, configures GSO partial/mangleid when relevant, enables the target feature, and verifies high LSO counters.

## State And Persistence
Mutates ethtool feature toggles, GSO partial toggles, tunnel links, and local/remote addresses. `defer(restore_wanted_features)` returns NIC features to the original wanted set, and tunnel links are deleted through deferred `ip link del`.

## Dependencies And Integration Points
Depends on `EthtoolFamily.features_get()`, `NetdevFamily.qstats_get()`, ethtool feature toggles, `socat` on remote, tunnel device support, and queue stats `tx-hw-gso-packets` or `tx-hw-gso-wire-packets`.

## Risks
Counters are best effort and system noise can create false negatives. The code tries to enable all hardware features to detect GSO partial behavior, which can fail or affect concurrent traffic. Debug kernels may require receive window clamping to keep traffic stable.

## Test Signals
Pass signals are low retransmits, low GSO stats with feature off, and sufficient super-packet or wire-packet GSO stats with feature on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/tso.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/uso.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/uso.py`

## Purpose
Tests UDP segmentation offload by sending large UDP datagrams with `UDP_SEGMENT` and verifying both remote payload length and local TX packet counter growth.

## Important APIs, Types, And Functions
- `UDP_SEGMENT = 103` is hardcoded because Python lacks the constant.
- `_send_uso()` sets `IPPROTO_UDP/UDP_SEGMENT`, builds a random payload, and sends one large datagram.
- `_get_tx_packets()` reads `ip -s link` TX packet counters.
- `_test_uso()` enables `tx-udp-segmentation`, runs remote `socat`, sends traffic, and checks segment count.
- `test_uso()` is variant-expanded over IPv4/IPv6 and exact/partial final segment sizes.

## Control Flow
Each variant requires IP version and remote `socat`, enables USO if supported, chooses a UDP port, records TX packets, starts a remote UDP listener, sends one segmented datagram, checks received byte count, waits for stats to settle, then verifies TX packet delta is at least the expected segment count.

## State And Persistence
Mutates `tx-udp-segmentation` feature only if it was initially off; a deferred ethtool call restores it to off. It otherwise uses transient sockets and remote `socat`.

## Dependencies And Integration Points
Depends on `NetDrvEpEnv`, ethtool feature reporting/toggle support, Python UDP socket options, remote `socat`, and accurate TX packet stats.

## Risks
TX packet counter deltas can include unrelated traffic and therefore only assert a lower bound. A device that offloads but reports stats unusually may still pass due to generic packet counters rather than dedicated USO stats.

## Test Signals
Pass requires the remote stdout length to match total payload and TX packet delta to be greater than or equal to computed segment count for both exact and partial datagram sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/uso.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/xdp_metadata.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/xdp_metadata.py`

## Purpose
Tests device-bound XDP metadata kfunc support, specifically `bpf_xdp_metadata_rx_hash()`, by loading a BPF object, sending traffic, and reading BPF maps populated by the program.

## Important APIs, Types, And Functions
- `_load_xdp_metadata_prog()` loads all programs from `xdp_metadata.bpf.o` with `bpftool prog loadall ... xdpmeta_dev`, pins them, attaches one with `ip link set ... xdpdrv pinned`, and returns program/map IDs.
- `_send_probe()` uses `socat` to send a TCP or UDP probe.
- `test_xdp_rss_hash()` is variant-expanded over TCP and UDP and inspects `map_rss`.

## Control Flow
For each protocol, the test reads netdev info and skips unless `xdp-rx-metadata-features` contains `hash`. It loads and attaches `xdp_rss_hash`, writes the selected port into `map_xdp_setup`, sends a remote probe, dumps the RSS map, and asserts packet count, zero errors, nonzero hash value, and L4 hash type bit.

## State And Persistence
Creates and deletes `/sys/fs/bpf/xdp_metadata_test` pins and attaches XDP driver mode to the tested NIC. Deferred cleanup removes the pin directory and turns XDP off.

## Dependencies And Integration Points
Depends on compiled `xdp_metadata.bpf.o`, `xdp_dummy`-style net lib BPF helpers, `bpftool`, `bpf_map_set`, `bpf_map_dump`, `bpf_prog_map_ids`, `NetdevFamily.dev_get()`, remote `socat`, and driver support for XDP RX hash metadata.

## Risks
The test assumes BPF map names (`map_xdp_setup`, `map_rss`) and key constants match the C BPF object. Attaching XDP driver mode can disrupt existing XDP state and is restored by a broad `xdpdrv off`.

## Test Signals
Pass requires at least one packet observed by the BPF program, zero error count, nonzero RSS hash, and hash type containing the L4 bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/xdp_metadata.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/xsk_reconfig.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/xsk_reconfig.py`

## Purpose
Reproduces AF_XDP/virtio-net reconfiguration races by binding a zero-copy XDP socket without filling the fill ring, then toggling XDP program attachment and RX ring size.

## Important APIs, Types, And Functions
- `_get_rx_ring_entries()` reads current RX ring size via `ethtool -g`.
- `setup_xsk()` probes and starts `xdp_helper <ifindex> <queue> -z` in background, skipping if AF_XDP or zero-copy bind is unsupported.
- `check_xdp_bind()` attaches and detaches `xdp_dummy.bpf.o` while XSK is bound.
- `check_rx_resize()` halves and restores RX ring size while XSK is bound.

## Control Flow
`main()` creates `NetDrvEnv(__file__, nsim_test=False)` and runs the two checks. Each check enters a `with setup_xsk(cfg)` block so the helper is alive while the potentially racy reconfiguration occurs.

## State And Persistence
Mutates XDP attachment and RX ring size. The XDP program is explicitly turned off; ring size is restored to the original value in the same test body.

## Dependencies And Integration Points
Intended for a virtio-net guest interface with zero-copy AF_XDP support. Depends on `xdp_helper`, `xdp_dummy.bpf.o`, ethtool ring configuration, and XDP attach support.

## Risks
The helper is deliberately started without fill ring setup to trigger delayed refill work, so failures can be hangs or deadlocks on buggy kernels. The format string in `setup_xsk()` is split such that `{xdp_queue_id}` is literal in the second string, which may be intentional shell text only if the helper accepts it; otherwise it is a likely bug because it will not substitute the queue ID.

## Test Signals
Success is completion of XDP attach/off and RX ring resize/restore while the zero-copy XSK helper is bound. Unsupported AF_XDP or failed zero-copy bind becomes a skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/xsk_reconfig.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/__init__.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/__init__.py`

## Purpose
Acts as the driver-networking selftest Python package facade. It adjusts `sys.path` to import the common `tools/testing/selftests/net/lib/py` library, re-exports its command, ksft, and netlink helpers, and adds driver-specific environment, traffic, and remote abstractions.

## Important APIs, Types, And Functions
- `KSFT_DIR` resolves the kernel selftests root and is appended to `sys.path`.
- Re-exports include `NetNS`, `NetdevSimDev`, netlink families (`EthtoolFamily`, `NetdevFamily`, `DevlinkFamily`, etc.), command wrappers (`cmd`, `ip`, `ethtool`, `bpftool`), ksft assertions, and BPF map helpers.
- Imports and re-exports `NetDrvEnv`, `NetDrvEpEnv`, `NetDrvContEnv`, `GenerateTraffic`, `Iperf3Runner`, and `Remote`.

## Control Flow
Import-time code attempts all imports in one `try` block. If the common `net` library is not importable, it prints a diagnostic and exits with code 4.

## State And Persistence
Import-time state is limited to `sys.path` mutation and the module `__all__` list. There is no runtime cleanup.

## Dependencies And Integration Points
Every Python file in this subset imports from `lib.py`; this facade provides the stable local import path and hides the cross-directory common library structure.

## Risks
Import failure exits the interpreter rather than raising an import error, which is appropriate for selftests but can surprise static tooling. `__all__` includes `ksft_not_none` twice.

## Test Signals
No direct tests. Its signal is successful import by all Python selftests; failure exits with a clear message about missing `net` library imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/env.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/env.py`

## Purpose
Defines reusable test environments for driver networking selftests: single local NIC, local NIC plus remote endpoint, and a specialized netkit container/namespace topology.

## Important APIs, Types, And Functions
- `NetDrvEnvBase` loads `net.config` or environment via `ksft_setup()`, resolves `test_dir` and `net_lib_dir`, and brings the device up on context entry.
- `NetDrvEnv` selects either `NETIF` hardware or a `NetdevSimDev` local device.
- `NetDrvEpEnv` creates or consumes a local/remote endpoint pair, resolves addresses and remote interface name, supports command requirements, IP-version requirements, netdevsim requirements, and hardware stats settling.
- `NetDrvContEnv` extends endpoint topology with a netkit pair, namespace, IPv6 forwarding sysctls, tc ingress BPF forwarding, and queue-lease-friendly addresses.

## Control Flow
Construction loads config, selects hardware vs netdevsim based on `NETIF` and `nsim_test`, creates local netdevsim peer namespaces when needed, creates `Remote(kind, args, src_path)`, resolves interface metadata, and initializes helper state. `NetDrvContEnv` then validates IPv6 and `LOCAL_PREFIX_V6`, creates a netkit pair with rtnetlink, sets namespace routes/sysctls, attaches `nk_forward.bpf.o`, and patches its `.bss` map.

## State And Persistence
The classes create and destroy netdevsim devices, network namespaces, netkit devices, tc qdiscs/filters, BPF programs, routes, addresses, and sysctl values. Cleanup is in `__del__()` and context-manager exit, with internal flags preventing double deletion.

## Dependencies And Integration Points
Depends on common net selftest classes (`NetNS`, `NetdevSimDev`), `ip`, `tc`, ethtool, `RtnlFamily`, `Netlink`, `bpftool`, remote backends, and compiled `nk_forward.bpf.o`. Most hardware tests in this subset rely on `NetDrvEnv` or `NetDrvEpEnv`; netkit tests rely on `NetDrvContEnv`.

## Risks
Destructor-based cleanup depends on object lifetime and can be skipped by hard exits. `NetDrvContEnv` modifies global IPv6 forwarding and accept_ra sysctls, then restores saved values. BPF attachment lookup assumes the tc filter BPF name starts with `nk_forward.bpf`.

## Test Signals
Environment failures become ksft skips/xfails for unsupported netdevsim/hardware combinations or missing config. `wait_hw_stats_settle()` uses ethtool coalesce stats period to improve qstat-based test reliability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/env.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/load.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/load.py`

## Purpose
Provides traffic generation helpers for driver tests, wrapping iperf3 server/client setup and a long-running packet generator.

## Important APIs, Types, And Functions
- `Iperf3Runner` builds server/client commands, starts one-shot servers, starts clients, and computes stable average bandwidth from JSON output.
- `GenerateTraffic` starts a one-shot server and a long-running 16-stream background client, waits for traffic ramp-up, and exposes `wait_pkts_and_stop()`.

## Control Flow
`Iperf3Runner` requires local and remote `iperf3`, picks or accepts a port, and uses the test environment's local address unless server/client bind IPs are provided. `GenerateTraffic` starts server then client, waits for at least 1000 pps, and raises if traffic does not ramp.

## State And Persistence
Maintains background process handles for iperf3 client and server. `stop()` terminates both, optionally logs stdout/stderr, and waits for the remote TCP connection to disappear from `/proc/net/tcp*`.

## Dependencies And Integration Points
Depends on `cmd`, `ip`, `wait_port_listen`, `rand_port`, remote command support, and interface RX packet stats. Used by page-pool failure, RSS, TSO, and other traffic-sensitive tests.

## Risks
`Iperf3Runner.start_server()` waits for the port locally because the server runs on the local host by default; client runs on `env.remote`. `GenerateTraffic._wait_pkts()` watches local RX packets, so it assumes reverse direction from remote client to local server.

## Test Signals
Traffic helpers raise if iperf3 fails, JSON is malformed, too few bandwidth samples are present, traffic does not ramp, or client shutdown does not complete within timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/load.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote.py`

## Purpose
Factory for remote endpoint backends used by `NetDrvEpEnv`.

## Important APIs, Types, And Functions
- Module cache `_modules` stores imported backend modules.
- `Remote(kind, args, src_path)` imports `..remote_<kind>` relative to this package, resolves the source directory, and constructs that backend's `Remote` class.

## Control Flow
On first use for a backend kind, the module is imported dynamically with `importlib.import_module()`. Subsequent calls reuse the cached module. The returned object supplies at least `cmd()` and `deploy()` methods.

## State And Persistence
Only the module cache persists. Backend instances own their own remote state.

## Dependencies And Integration Points
Integrated by `NetDrvEpEnv`, which passes `REMOTE_TYPE` and `REMOTE_ARGS` from config or uses `netns` for local netdevsim tests.

## Risks
Backend kind strings directly drive module import, so bad config becomes an import error. There is no validation beyond constructing the class.

## Test Signals
No direct tests; failures surface when environment creation cannot import or instantiate the requested remote backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote_netns.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote_netns.py`

## Purpose
Implements a remote backend that executes commands inside a Linux network namespace on the same host.

## Important APIs, Types, And Functions
- `Remote.__init__(name, dir_path)` stores namespace name and source directory.
- `cmd(comm)` returns a `subprocess.Popen` running `ip netns exec <name> bash -c <comm>`.
- `deploy(what)` resolves relative paths against `dir_path` and otherwise returns absolute paths unchanged.

## Control Flow
Commands are not run through the common `cmd()` wrapper directly; they return `Popen` for the wrapper to manage. Deployment is a no-copy path resolution because the namespace shares the same filesystem.

## State And Persistence
No mutable remote resources are created. It assumes the namespace already exists and remains valid.

## Dependencies And Integration Points
Used by local netdevsim endpoint tests through `NetDrvEpEnv.create_local()`. Depends on `ip netns exec` and shared filesystem visibility.

## Risks
Because deployment does not copy files, it only works for namespaces on the same host. The imported `cmd` symbol is unused.

## Test Signals
Command failures are surfaced by the higher-level command wrapper consuming the returned process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote_netns.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote_ssh.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote_ssh.py`

## Purpose
Implements a remote backend that executes commands over SSH and copies test binaries to a temporary remote directory as needed.

## Important APIs, Types, And Functions
- `Remote.cmd(comm)` returns `subprocess.Popen(["ssh", "-q", self.name, comm])`.
- `_mktmp()` creates random lowercase path fragments.
- `deploy(what)` lazily creates a remote `/tmp/<random>` directory, copies the file by `scp`, and returns the remote path.
- `__del__()` removes the remote temporary directory via remote command.

## Control Flow
First deployment creates a remote temp directory. Each deployed file gets another random prefix plus the local basename. Commands are raw SSH command strings.

## State And Persistence
Owns `_tmpdir` on the remote host and deletes it during object destruction. If the process exits abruptly, the temp directory may remain.

## Dependencies And Integration Points
Used when `REMOTE_TYPE=ssh` in `net.config` or environment. Depends on passwordless/noninteractive SSH and SCP.

## Risks
Random names are only eight lowercase characters and no collision retry is implemented. Command strings and paths are not shell-quoted, so unusual filenames or hostnames can break deployment.

## Test Signals
Failure to create the directory, copy files, or run remote commands surfaces through the common command wrapper when it observes process exit status/stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote_ssh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/sh/lib_netcons.sh -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/sh/lib_netcons.sh`

## Purpose
Shared shell library for netconsole selftests. It creates netdevsim-backed source/destination interfaces, configures netconsole dynamic targets, starts listeners, validates received console messages and userdata, and cleans up namespaces/devices.

## Important APIs, Types, And Functions
- Top-level variables define default IPv4/IPv6 addresses, UDP port, message text, configfs paths, namespace, and random netdevsim IDs.
- `set_network()`, `create_ifaces()`, `link_ifaces()`, and `configure_ip()` build a two-interface netdevsim topology with the destination in a namespace.
- `_create_dynamic_target()`, `create_dynamic_target()`, `create_cmdline_str()`, and `disable_release_append()` configure netconsole targets.
- `listen_port_and_save_to()`, `validate_msg()`, and `validate_result()` capture and validate netconsole output.
- `check_for_dependencies()`, `check_netconsole_module()`, `wait_target_state()`, `wait_for_port()`, and cleanup helpers provide test scaffolding.

## Control Flow
Tests source this file, call dependency checks, set up networking, create a configfs target or command-line target, start `socat` listeners inside the namespace, trigger console messages, validate output, then call cleanup through traps.

## State And Persistence
Creates netdevsim devices, network namespaces, configfs netconsole targets, user data directories, printk configuration changes, optional bonding netdevsim devices, and listener processes. Cleanup removes configfs entries, netdevsim devices, namespaces, and restores printk values.

## Dependencies And Integration Points
Depends on `net/lib.sh`, root privileges, `socat`, `ip`, `udevadm`, IPv6 support, netdevsim sysfs, and `NETCONSOLE_DYNAMIC` configfs. It also integrates with ksft exit status variables from the common shell library.

## Risks
Uses global variable state heavily and random netdevsim IDs. Several cleanup paths intentionally ignore failures to handle partial setup. Configfs target deletion must disable the target and remove userdata before `rmdir`.

## Test Signals
Validation checks that a listener output file is created, contains the expected message, and for extended format contains configured userdata. Dependency failures produce ksft skip exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/sh/lib_netcons.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/macsec.py -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/macsec.py`

## Purpose
Tests MACsec hardware offload API behavior, netdevsim limits, offload state/feature reflection, and VLAN-over-MACsec data path behavior with local offload and remote software MACsec.

## Important APIs, Types, And Functions
- `_require_ip_macsec()`, `_require_ip_macsec_offload()`, and `_require_macsec_offload()` gate iproute2 and device feature support.
- `_setup_macsec_sa()`, `_setup_macsec_devs()`, `_setup_vlans()`, and `_setup_vlan_ips()` build matching local/remote MACsec and VLAN topology.
- `test_offload_api()` creates SecYs, adds SAs/SCs, and toggles offload through rtnetlink and genetlink.
- `test_max_secy()` and `test_max_sc()` are nsim-only limit tests.
- `test_offload_state()`, `test_vlan()`, and `test_vlan_toggle()` verify state, feature snapshots, VLAN propagation, and ping behavior.

## Control Flow
`main()` creates `NetDrvEpEnv` and runs the MACsec cases. Tests use a PID-derived interface-name prefix to avoid collisions. Offload tests create devices, defer deletion, perform ip/macsec operations, and assert expected command failures or feature states.

## State And Persistence
Creates MACsec interfaces, TX/RX secure associations, VLAN interfaces, addresses, and remote software MACsec peers. Deferred `ip link del` calls clean up both local and remote devices.

## Dependencies And Integration Points
Depends on `ip macsec`, iproute2 offload syntax, `macsec-hw-offload` ethtool feature, `NetDrvEpEnv`, remote endpoint commands, and optionally netdevsim debugfs VLAN state.

## Risks
The fixed MACsec key and port/SCI values are test-only. Offloaded netdevsim lacks datapath handling, so ping checks are skipped for offloaded nsim cases. Feature dictionary equality assumes stable ethtool JSON ordering/content.

## Test Signals
Pass signals include rejected offload disable while SAs exist, expected max SecY/SC failures on nsim, matching offload state strings and feature snapshots, VLAN debugfs presence matching offload state, and successful ping when datapath is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/macsec.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/microchip/ksz9477_qos.sh -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/microchip/ksz9477_qos.sh`

## Purpose
Tests QoS classification behavior on Microchip KSZ switch ports, covering port default priority, apptrust ordering between PCP and DSCP, and the global DSCP priority map.

## Important APIs, Types, And Functions
- Topology helpers `h1_create()`, `h2_create()`, `switch_create()`, `setup_prepare()`, and `cleanup()` build a two-host bridge through switch ports.
- `set_apptrust_order()`, `port_default_prio_get()`, `port_get_default_apptrust()`, DSCP map helpers, and `restore_priorities()` manipulate DCB app/apptrust state.
- `run_test()` is the core packet/counter validator, deriving expected internal priority and high-priority counter behavior.
- `test_port_default()`, `test_port_apptrust()`, and `test_global_dscp_map()` are the exported test cases.

## Control Flow
After setup, tests manipulate DCB default priority, apptrust order, and DSCP maps, then call `run_test()` for IPv4 and IPv6 traffic. `run_test()` primes the MAC table, samples port packet/byte and `rx_hi`/`tx_hi` ethtool stats, sends crafted mausezahn packets with DSCP and optional VLAN PCP, waits for counters, then compares high-priority byte counters against expected classification.

## State And Persistence
Mutates bridge membership, link state, IPv6 disable sysctls, DCB apptrust/default-prio/DSCP maps, and switch counters indirectly. Cleanup restores sysctls, bridge, VRFs, and DCB state using saved originals.

## Dependencies And Integration Points
Depends on forwarding test libraries, `dcb`, `jq`, `mausezahn`, ethtool stats helpers, stable MAC addresses, and Microchip KSZ `rx_hi`/`tx_hi` counters.

## Risks
The test encodes switch-specific thresholds: ingress high priority for internal priority > 0, egress high priority for > 1. Counter comparison adjusts for Ethernet FCS length and waits six seconds for hardware stats to update, which is device-specific.

## Test Signals
Pass signals are expected packet counts on ingress/egress ports, exact high-priority byte counter behavior, successful DCB apptrust/default-prio readback, and restoration of original DSCP/apptrust/default settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/microchip/ksz9477_qos.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/blackhole_routes.sh -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/blackhole_routes.sh`

## Purpose
Tests that mlxsw blackhole routes are offloaded and that packets matching them are dropped by the ASIC rather than trapped/dropped by the kernel.

## Important APIs, Types, And Functions
- `h1_create()`, `h2_create()`, and `router_create()` build a routed two-host topology with IPv4/IPv6 addresses and default routes.
- `ping_ipv4()` and `ping_ipv6()` are baseline connectivity checks.
- `blackhole_ipv4()` and `blackhole_ipv6()` add blackhole routes, install skip-hw tc filters to detect kernel-trapped packets, and verify offload/drop behavior.

## Control Flow
Setup enables forwarding and VRFs, brings router ports up, and assigns addresses. Baseline ping tests run first. Blackhole tests add a route, wait until it is marked offloaded, send ping expected to fail, then assert the skip-hw tc filter saw zero packets.

## State And Persistence
Mutates routes, tc clsact/qdisc/filter state, interface addresses, link state, forwarding, and VRFs. Cleanup deletes filters/routes within each test and tears down router/host configuration via trap.

## Dependencies And Integration Points
Depends on forwarding shell libraries, `tc_common.sh`, mlxsw-capable hardware, `wait_for_offload`, tc flower counters, and ping helpers.

## Risks
If the route is not offloaded in time, the test fails before traffic validation. The zero-packet tc check assumes the skip-hw filter would see packets if they reached software.

## Test Signals
Pass requires route offload marking, failed pings to blackholed destinations, and zero matching packets on the software tc filter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/blackhole_routes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_linecard.sh -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_linecard.sh`

## Purpose
Tests mlxsw devlink line card provisioning, unprovisioning, port instantiation, nested devlink information, and activation for a `16x100G` line card type.

## Important APIs, Types, And Functions
- State helpers `lc_state_get()`, `lc_wait_until_state_changes()`, `lc_wait_until_state_becomes()`, `lc_port_count_get()`, and `lc_nested_devlink_dev_get()` query devlink JSON through `jq`.
- `unprovision_one()` and `provision_one()` drive devlink line card state transitions.
- `supported_types_check()`, `ports_check()`, `lc_dev_info_provisioned_check()`, and `lc_dev_info_active_check()` validate metadata.
- Tests are `unprovision_test()`, `provision_test()`, and `activation_16x100G_test()`.

## Control Flow
`setup_prepare()` requires line card support and explicit `LC_SLOT`, then avoids creating netifs until activation. Tests unprovision/provision the selected slot, wait for expected states and port counts, read nested devlink device info, and for activation bring interfaces up before validating active firmware info.

## State And Persistence
Mutates physical line card provisioning state. Cleanup only brings test interfaces down if they were raised; it does not restore the previous line card type/state beyond what individual tests do.

## Dependencies And Integration Points
Depends on `devlink`, `jq`, forwarding `lib.sh`, `devlink_lib.sh`, an mlxsw platform with line card support, and `LC_SLOT` environment variable.

## Risks
This is disruptive to line card state and can take seconds to instantiate ports. It skips if `LC_SLOT` is absent, and `activation_16x100G_test()` is tied to a specific supported type.

## Test Signals
Pass requires successful devlink state transitions, expected provisioned type, exactly 16 ports for `16x100G`, nonempty nested devlink handle, and readable fixed/running firmware metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_linecard.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap.sh -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap.sh`

## Purpose
Tests generic mlxsw devlink trap behavior during device reload/delete while trapped packets are arriving.

## Important APIs, Types, And Functions
- Standard topology helpers create two simple host interfaces connected through a bridge on two switch ports.
- `dev_del_test()` sends continuous multicast-source packets that trigger `source_mac_is_multicast`, sets the trap action to `trap`, repeatedly reloads the devlink device, and rebuilds topology.

## Control Flow
Setup creates VRFs and bridge topology. `dev_del_test()` starts mausezahn in the background, loops five times setting trap action, sleeping, reloading the device, waiting for netdevices to be recreated, then calling cleanup/setup again. It logs one ksft test at the end and kills the traffic generator.

## State And Persistence
Mutates bridge topology, trap action, and triggers devlink reloads. Cleanup tears down bridge/VRF state; reload recreates netdevices and requires topology reconstruction.

## Dependencies And Integration Points
Depends on forwarding libraries, `devlink_lib.sh`, mausezahn, mlxsw devlink reload support, and `source_mac_is_multicast` trap support.

## Risks
The test is disruptive and timing-heavy, with a fixed 20 second wait after reload. It validates robustness primarily by absence of crash/failure during repeated reload under trapped traffic.

## Test Signals
Pass is successful completion of five reload iterations while traffic is trapped, with no command failures in setup/cleanup/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_acl_drops.sh -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_acl_drops.sh`

## Purpose
Tests mlxsw devlink trap accounting for packets dropped by ingress and egress tc flower ACL actions.

## Important APIs, Types, And Functions
- Topology helpers create a bridge with two switch ports and clsact on both ports.
- `ingress_flow_action_drop_test()` installs ingress drop on `swp1` and egress pass counter on `swp2`.
- `egress_flow_action_drop_test()` installs egress drop and a separate egress pass counter on `swp2`.
- Both use `devlink_trap_drop_test()` and `devlink_trap_drop_cleanup()` from the devlink library.

## Control Flow
For each test, tc filters are installed, continuous mausezahn IP traffic is started from h1 to h2, devlink trap drop counters are validated against the pass counter, the specific drop filter is removed, and cleanup kills traffic and removes pass filter state.

## State And Persistence
Mutates bridge topology, clsact qdiscs, tc flower filters, and background traffic. Trap-level cleanup is delegated to the library helper.

## Dependencies And Integration Points
Depends on forwarding libs, `tc_common.sh`, `devlink_lib.sh`, mausezahn, tc flower offload/drop actions, and mlxsw devlink trap drop groups.

## Risks
Correctness depends on the pass filter counter being placed where it observes packets that would otherwise be dropped and on devlink trap accounting being synchronized enough for the helper.

## Test Signals
Pass requires `devlink_trap_drop_test` to observe the expected ingress or egress flow action drop trap while the corresponding tc counter confirms test traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_acl_drops.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_control.sh -->
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_control.sh`

## Purpose
Tests mlxsw devlink control-plane trap coverage for many protocol packets and control events. It sends crafted packets matching each registered control trap and verifies devlink trap stats increment under the right conditions.

## Important APIs, Types, And Functions
- Topology helpers create a routed two-host VRF setup through two router ports.
- `ALL_TESTS` enumerates traps for STP, LACP, LLDP, IGMP, MLD, DHCP, ARP, IPv6 neighbor discovery, BFD, OSPF, BGP, VRRP, PIM, route exceptions, router-alert options, IPv6 all-nodes/all-routers, PTP, tc sample/trap, and EAPOL.
- Payload builders such as `lacp_payload_get()`, `lldp_payload_get()`, `mld_payload_get()`, `icmpv6_header_get()`, router-alert helpers, and `eapol_payload_get()` produce raw mausezahn payload fragments.
- Most tests call `devlink_trap_stats_test <name> <trap> $MZ ...`.

## Control Flow
Setup enables forwarding, creates VRFs, addresses, and default routes. Each trap test crafts a packet with appropriate L2/L3/L4 headers and invokes the shared devlink stats checker. Some tests install temporary neighbors, dummy devices/routes, or tc clsact filters to trigger route exception, sample, or trap behavior.

## State And Persistence
Mutates router addresses/routes, neighbors, dummy links, tc clsact filters, and forwarding state. Temporary state is generally removed in the same test; global topology cleanup runs through trap.

## Dependencies And Integration Points
Depends on forwarding `lib.sh`, `devlink_lib.sh`, `mlxsw_lib.sh`, mausezahn, tc, devlink trap stats, and mlxsw Spectrum behavior. PTP tests call `mlxsw_only_on_spectrum 1`.

## Risks
The suite is broad and packet encodings are hand-crafted, so protocol format changes or mausezahn differences can break individual trap cases. Some local/external route tests include `sp=12345` where `dp` may have been intended, but the goal is trap triggering rather than payload delivery.

## Test Signals
Pass requires `devlink_trap_stats_test` to observe the expected trap stat delta for each crafted control packet or tc action case. Failures identify trap name and packet scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_control.sh -->
