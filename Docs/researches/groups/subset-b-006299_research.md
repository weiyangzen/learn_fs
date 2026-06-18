# subset-b-006299 Research

Grouped code research for cfg80211 wireless scan, SME, sysfs, trace, and KUnit test files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/scan.c -->
# sources/distributed-fs/ceph-client/net/wireless/scan.c

## Purpose
`scan.c` implements cfg80211 scan result handling. It owns the per-wiphy BSS cache, scan and scheduled-scan completion plumbing, 6 GHz split-scan and colocated-AP discovery, multi-BSSID and MLO-derived BSS creation, information-element inheritance/fragmentation helpers, BSS lookup/reference APIs, and wireless-extension scan compatibility output.

## Important APIs, Types, And Functions
Driver-facing exports include `cfg80211_scan_done()`, `cfg80211_sched_scan_results()`, `cfg80211_sched_scan_stopped()`, `cfg80211_bss_flush()`, `__cfg80211_get_bss()`, `cfg80211_inform_bss_data()`, `cfg80211_inform_bss_frame_data()`, `cfg80211_ref_bss()`, `cfg80211_put_bss()`, `cfg80211_unlink_bss()`, `cfg80211_bss_iter()`, `cfg80211_find_elem_match()`, `cfg80211_find_vendor_elem()`, `cfg80211_get_ies_channel_number()`, `cfg80211_merge_profile()`, and `cfg80211_defragment_element()`. Internal structures and helpers center on `cfg80211_internal_bss`, `cfg80211_bss_ies`, `cfg80211_colocated_ap`, `cfg80211_scan_request_int`, `cfg80211_inform_single_bss_data`, `cfg80211_mle`, and RB-tree/list manipulation helpers.

## Control Flow
Scanning starts through `cfg80211_scan()`. If the wiphy does not request split 6 GHz scanning, the original request goes directly to `rdev_scan()`. With `WIPHY_FLAG_SPLIT_SCAN_6GHZ`, the first request scans non-6 GHz channels and later `___cfg80211_scan_done()` triggers `cfg80211_scan_6ghz()` for the second phase. The 6 GHz path builds a derived scan request from cached RNR colocated AP data, PSC requirements, SSID/BSSID filters, and per-channel `scan_6ghz_params`, then submits it to the driver. Completion sends scan-done netlink or stores a deferred message, notifies wireless extensions, wakes SME scan handling, optionally flushes pre-scan BSS entries, releases the held netdev, and frees both original and internal split requests.

BSS insertion flows through `cfg80211_inform_bss_data()` or `cfg80211_inform_bss_frame_data()`, which normalize frame metadata, choose or correct channels from IEs, validate 6 GHz power-type usability, allocate `cfg80211_bss_ies`, and call `__cfg80211_bss_update()` under `bss_lock`. Updates either refresh an existing RB-tree match or allocate a new cache entry, link it into hidden-SSID and transmitted/nontransmitted BSSID relationships, enforce `bss_entries_limit`, increment generation counters, and return a referenced public BSS. Multi-BSSID parsing expands nontransmitted profiles with `cfg80211_gen_new_ie()`, while MLO parsing defragments Basic Multi-Link elements and per-STA profiles to synthesize link BSS entries.

## State And Persistence
Runtime state persists in `rdev->bss_list`, `rdev->bss_tree`, `rdev->bss_entries`, `rdev->bss_generation`, `rdev->scan_req`, `rdev->int_scan_req`, `rdev->scan_msg`, and `rdev->sched_scan_req_list`. Each BSS carries timestamp, channel, signal, capability, `use_for` restrictions, `cannot_use_reasons`, source type, RCU-protected beacon/probe-response IE pointers, hidden-SSID links, nontransmitted BSSID links, optional transmitted-BSS reference, and a refcount that also propagates to hidden beacon and transmitted-BSS dependencies. Scan entries expire after `IEEE80211_SCAN_RESULT_EXPIRE`, can be aged across suspend, and can be flushed explicitly.

## Dependencies And Integration Points
The file integrates cfg80211 core state from `core.h`, nl80211 event generation, WEXT compatibility, driver ops via `rdev_scan()` and scheduled-scan stop, regulatory hints from beacon/country/channel discovery, 802.11 IE parsers from cfg80211/mac80211 headers, MLO and 6 GHz helpers, RCU and spinlock lifetime rules, and KUnit-only symbol visibility. SME code receives scan completion callbacks here, and connection/roam code depends on the BSS reference APIs and current-BSS hold semantics.

## Risks And Edge Cases
The highest-risk areas are BSS lifetime and IE synthesis. `bss_lock`, RCU, propagated reference counts, hidden-SSID grouping, transmitted/nontransmitted BSS references, and held current-BSS references must remain balanced or scan-cache teardown can leak or free live data. Multi-BSSID and MLO parsing operate on attacker-controlled beacon/probe-response IEs, so every length, fragmentation, continuation, BSSID-index, MLD-ID, channel, and buffer-size check matters. Split 6 GHz scans must preserve first-phase TSF metadata, not double-free internal requests, and must avoid scanning disallowed channels. WEXT scan formatting walks IE streams while holding RCU and can fail with `-E2BIG` when userspace buffers are too small.

## Test Signals
The local KUnit suite exercises `cfg80211_gen_new_ie()`, malformed IE handling, element fragmentation, direct BSS inform/lookup, MLO STA-profile BSS generation including fragmented MLE/profile data, NSTR nonprimary usability restrictions, and RNR colocated AP parsing. Additional valuable signals are scan start/done races, split 6 GHz first/second phase behavior, scheduled scan stop/results ordering, BSS cache limit eviction, hidden SSID beacon/probe response pairing, MBSSID nontransmitted profile generation, RCU/lockdep checks for `cfg80211_ref_bss()`/`cfg80211_put_bss()`, and WEXT scan result buffer truncation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/sme.c -->
# sources/distributed-fs/ceph-client/net/wireless/sme.c

## Purpose
`sme.c` implements cfg80211 station connection management. It provides the software SME used when drivers expose auth/assoc rather than connect/disconnect, handles driver SME connection/roam/disconnect events, manages current BSS references for single-link and MLO clients, reports nl80211 and WEXT events, uploads cached connect keys, and cleans up connections when owning userspace sockets disappear.

## Important APIs, Types, And Functions
The central private type is `struct cfg80211_conn`, which stores copied connect parameters and a software-SME substate such as scanning, authenticating, associating, connected, deauth, or abandon. Important functions include `cfg80211_conn_scan()`, `cfg80211_conn_do_work()`, `cfg80211_conn_work()`, `cfg80211_sme_scan_done()`, `cfg80211_sme_rx_auth()`, `cfg80211_sme_rx_assoc_resp()`, timeout/disassoc/abandon handlers, `cfg80211_sme_connect()`, `cfg80211_sme_disconnect()`, `__cfg80211_connect_result()`, `cfg80211_connect_done()`, `__cfg80211_roamed()`, `cfg80211_roamed()`, `__cfg80211_port_authorized()`, `cfg80211_port_authorized()`, `__cfg80211_disconnected()`, `cfg80211_disconnected()`, `cfg80211_connect()`, `cfg80211_disconnect()`, and `cfg80211_autodisconnect_wk()`.

## Control Flow
`cfg80211_connect()` validates duplicate connection attempts, reassociation `prev_bssid`, cached WEP keys, capability masks, and requested BSS type. It stores the SSID and connect keys on `wdev`, then either calls driver `connect` or starts the software SME. The software SME first looks for an existing BSS; if none exists it issues a scan. Scan completion calls `cfg80211_sme_scan_done()`, which either advances to authentication or reschedules work to fail. Auth success schedules association, auth algorithm rejection may rotate automatic auth type, association failure may retry without reassoc, and terminal failures emit `__cfg80211_connect_result()` with failure status.

Driver SME events are queued as `cfg80211_event` objects by `cfg80211_connect_done()`, `cfg80211_roamed()`, `cfg80211_port_authorized()`, and `cfg80211_disconnected()` for serialized processing on cfg80211 workqueues. Immediate internal handlers update `wdev->connected`, `wdev->valid_links`, per-link `current_bss`, connected address, cached SSID, key state, QoS map, critical-protocol state, regulatory country hints, WEXT notifications, and nl80211 messages. Disconnect paths choose software SME deauth, `rdev_disconnect()`, or MLME down depending on the driver API and current connection state.

## State And Persistence
Connection-attempt state lives in `wdev->conn`, including copied IEs and BSSID/previous-BSSID buffers. Established state lives in `wdev->connected`, `wdev->valid_links`, `wdev->links[link].client.current_bss`, per-link client addresses for MLO, `wdev->u.client.connected_addr`, `wdev->u.client.ssid`, `wdev->connect_keys`, `wdev->conn_owner_nlportid`, WEXT previous BSSID state, and the per-wdev event list. Current BSS entries are held with `cfg80211_hold_bss()` and released with `cfg80211_unhold_bss()` plus `cfg80211_put_bss()`.

## Dependencies And Integration Points
The file depends on scan/BSS APIs from `scan.c`, MLME auth/assoc/deauth helpers, nl80211 event construction, regulatory disconnect and country-IE hints, rtnetlink and wiphy locking, cfg80211 workqueues, WEXT compatibility, driver ops (`connect`, `disconnect`, `auth`, `assoc`, `deauth`, `del_key`, `crit_proto_stop`), and interface-type-specific leave/stop helpers for autodisconnect. It is the main bridge between userspace connection requests, driver callbacks, and cfg80211-maintained client state.

## Risks And Edge Cases
Ownership of BSS references is subtle because connect/roam APIs intentionally consume BSS objects one way or another. MLO events require valid `ap_mld_addr`, per-link BSSID/address fields, and success filtering for individual links. Software SME retry and timeout transitions must avoid duplicate userspace notifications. Connect-key memory is sensitive and must be freed on failure/disconnect. Disconnect and regulatory idle checks span all registered devices, so lock ordering with RTNL and wiphy mutex matters. Queued events must copy variable data before driver-owned buffers disappear.

## Test Signals
Useful tests include software SME scan/auth/assoc success and each timeout/failure transition, automatic auth fallback with and without WEP keys, reassociation fallback from reassoc to assoc, driver-SME connect/roam/disconnect queued event ordering, MLO connect/roam per-link BSS reference balancing, failure cleanup of connect keys and SSID state, WEXT event emission for legacy clients, port-authorized validation, autodisconnect for station/AP/mesh/IBSS owners, and lockdep/KASAN coverage for event-list processing and BSS release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/sme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/sysfs.c -->
# sources/distributed-fs/ceph-client/net/wireless/sysfs.c

## Purpose
`sysfs.c` registers the `/sys/class/ieee80211/<wiphy>/` class and default attributes for cfg80211 wireless PHY devices. It also provides wiphy device release, network-namespace attribution, and suspend/resume behavior for cfg80211 devices.

## Important APIs, Types, And Functions
The file defines `ieee80211_class`, attribute show handlers for `index`, `macaddress`, `address_mask`, `addresses`, and `name`, `wiphy_dev_release()`, optional PM callbacks `wiphy_suspend()` and `wiphy_resume()`, and module-level `wiphy_sysfs_init()`/`wiphy_sysfs_exit()`. `dev_to_rdev()` converts the embedded device back to `struct cfg80211_registered_device`.

## Control Flow
Class registration installs the sysfs class with its attribute group and release function. Attribute reads format values from the owning rdev/wiphy, with `addresses_show()` returning either the permanent address or every advertised address. On suspend, cfg80211 records suspend time, tries WoWLAN suspend if configured, otherwise leaves all interfaces and calls driver suspend without WoWLAN after processing pending cfg80211 work. On resume, scan results are aged by suspend duration, driver resume is called if registered, cfg80211 work is queued, and failed resume shuts down all interfaces.

## State And Persistence
Sysfs state is the global `ieee80211_class` registration plus each wiphy's embedded device and attributes. Suspend state uses `rdev->suspend_at` and `rdev->suspended`; it also affects scan-cache timestamps via `cfg80211_bss_age()`. Device release transfers final cleanup to `cfg80211_dev_free()`.

## Dependencies And Integration Points
The file integrates with the Linux driver core, sysfs class infrastructure, network namespace operations, PM sleep hooks, rtnetlink, cfg80211 leave/shutdown helpers, work processing, BSS aging from `scan.c`, and driver suspend/resume operations from `rdev-ops.h`.

## Risks And Edge Cases
Suspend has two different paths depending on whether WoWLAN can be configured; driver return value `1` is treated as refusal and falls back to disconnecting/leaving interfaces. Lock ordering uses RTNL around wiphy work and driver PM operations. Resume failure forces interface shutdown, so callers must expect connection loss. Attribute formatting uses `sprintf()` into sysfs buffers and assumes address arrays remain stable for registered wiphys.

## Test Signals
Signals include class register/unregister success, sysfs attribute contents for single and multiple MAC addresses, namespace visibility, suspend with successful WoWLAN, suspend fallback after WoWLAN refusal, resume BSS aging, resume failure interface shutdown, and register/unregister loops under PM, lockdep, and KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/sysfs.h -->
# sources/distributed-fs/ceph-client/net/wireless/sysfs.h

## Purpose
`sysfs.h` is the small internal declaration header for cfg80211 wiphy sysfs support.

## Important APIs, Types, And Functions
It declares `wiphy_sysfs_init()`, `wiphy_sysfs_exit()`, and the global `struct class ieee80211_class` defined in `sysfs.c`.

## Control Flow
The header has no runtime control flow. It lets cfg80211 initialization call class registration and teardown call class unregistration while allowing other code to reference the class object.

## State And Persistence
The persistent object exposed by the header is `ieee80211_class`, which exists while cfg80211 sysfs support is registered.

## Dependencies And Integration Points
The header is included by cfg80211 core/sysfs code that needs to initialize, exit, or attach devices to the ieee80211 class.

## Risks And Edge Cases
Because the header exposes a global class, initialization order must ensure users do not register wiphy devices before `wiphy_sysfs_init()` succeeds or after `wiphy_sysfs_exit()` starts.

## Test Signals
Compile coverage and cfg80211 module load/unload are the main signals; runtime class registration tests in `sysfs.c` validate the declarations indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/Makefile -->
# sources/distributed-fs/ceph-client/net/wireless/tests/Makefile

## Purpose
This Makefile wires cfg80211 KUnit test objects into the kernel build when `CONFIG_CFG80211_KUNIT_TEST` is enabled.

## Important APIs, Types, And Functions
It defines `cfg80211-tests-y` as `module.o fragmentation.o scan.o util.o chan.o` and adds `cfg80211-tests.o` to `obj-$(CONFIG_CFG80211_KUNIT_TEST)`.

## Control Flow
There is no executable runtime control flow. Kbuild combines the listed objects into one test module/object according to the config symbol.

## State And Persistence
No runtime state is maintained. The file persists the build membership contract for the cfg80211 KUnit suite.

## Dependencies And Integration Points
The Makefile integrates with Linux Kbuild, KUnit, and the corresponding C test files in this directory. `module.o` supplies module metadata, while the other objects register suites with `kunit_test_suite()`.

## Risks And Edge Cases
Forgetting to list a new test object silently excludes its suite. Renaming or removing a C file without updating this list breaks Kbuild for `CONFIG_CFG80211_KUNIT_TEST`.

## Test Signals
The direct signal is a successful kernel build with `CONFIG_CFG80211_KUNIT_TEST=y` or `m`, followed by KUnit discovering the channel, fragmentation, scan/IE-generation, inform-BSS, and 6 GHz scan suites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/chan.c -->
# sources/distributed-fs/ceph-client/net/wireless/tests/chan.c

## Purpose
`chan.c` contains KUnit coverage for cfg80211 channel-definition compatibility, especially 6 GHz channel widths up to 320 MHz and puncturing behavior.

## Important APIs, Types, And Functions
The file defines static 6 GHz channel fixtures, parameter table `chandef_compat_cases`, `test_chandef_compat()`, suite `chandef_compat`, and imports the KUnit-only symbol namespace. The tested production APIs are `cfg80211_chandef_valid()` and `cfg80211_chandef_compatible()`.

## Control Flow
Each parameterized case builds two `cfg80211_chan_def` values, substitutes `c2` for `c1` for identical-channel cases, asserts both chandefs are valid, then checks compatibility in both argument orders. Expected return is either the wider/compatible chandef pointer or `NULL`; identical cases also verify that reversing arguments returns the other identical object.

## State And Persistence
The tests use only static channel fixtures and parameter data. No state persists outside the KUnit invocation.

## Dependencies And Integration Points
The suite depends on cfg80211 channel helpers, KUnit parameter generation via `KUNIT_ARRAY_PARAM_DESC`, and the KUnit-exported production symbols. It is built into `cfg80211-tests.o` by the local Makefile.

## Risks And Edge Cases
The cases target compatibility regressions around primary-channel mismatch, bandwidth containment, 160 MHz inside 320 MHz, and punctured secondary segments. Pointer identity is part of the expected contract, so helper changes that return equivalent copies instead of original inputs would break this suite.

## Test Signals
Passing cases demonstrate that identical 20/no-HT/40/80/160/320 MHz definitions are compatible, 20 MHz can be compatible within 320 MHz, mismatched primary 20 or 320 MHz definitions are rejected, and puncturing masks are interpreted correctly for compatible and incompatible 160-in-320 scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/fragmentation.c -->
# sources/distributed-fs/ceph-client/net/wireless/tests/fragmentation.c

## Purpose
`fragmentation.c` tests `cfg80211_defragment_element()` for normal and fragmented 802.11 elements, with emphasis on EHT Multi-Link extension elements and trailing fragment handling.

## Important APIs, Types, And Functions
The suite defines `defragment_0()`, `defragment_1()`, `defragment_2()`, and `defragment_at_end()`, registered as KUnit suite `cfg80211-element-defragmentation`. The production API under test is `cfg80211_defragment_element()` from `scan.c`.

## Control Flow
Each test builds a static IE byte stream, optionally counts elements with `for_each_element()`, first calls the helper with `data == NULL` to get the required output length, then calls again with an allocated buffer and validates copied payload bytes. The cases cover no fragmentation, one used fragment with a later unused fragment, two used fragments with a later unused fragment, and a used fragment at the end of the stream.

## State And Persistence
The suite has no persistent state; KUnit allocates temporary output buffers per test.

## Dependencies And Integration Points
The tests depend on Linux 802.11 element constants, cfg80211's exported defragment helper, KUnit allocation/assertion APIs, and normal IE iteration macros.

## Risks And Edge Cases
Fragment handling is security-sensitive because malformed management frames are untrusted. The tests assert that an extension element skips the extension ID byte, that only 255-byte elements continue into fragments, that short fragments terminate defragmentation, and that later fragment elements are ignored once the current fragmented element is complete.

## Test Signals
Passing tests show correct length calculation and byte-for-byte reconstruction for unfragmented, singly fragmented, multiply fragmented, and end-of-buffer fragmented elements, including correct refusal to consume unrelated later fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/fragmentation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/module.c -->
# sources/distributed-fs/ceph-client/net/wireless/tests/module.c

## Purpose
`module.c` supplies minimal module metadata for the cfg80211 KUnit test aggregate.

## Important APIs, Types, And Functions
It includes `<linux/module.h>` and declares `MODULE_LICENSE("GPL")` plus `MODULE_DESCRIPTION("tests for cfg80211")`.

## Control Flow
There is no executable test logic or init/exit code in this file.

## State And Persistence
No runtime state is maintained.

## Dependencies And Integration Points
The file is compiled with the other cfg80211 test objects into `cfg80211-tests.o`, giving the aggregate test object valid module metadata when built as a module.

## Risks And Edge Cases
The main risk is metadata omission: without a GPL-compatible license declaration, KUnit-only exported symbols or GPL-only symbols used by the tests could be unavailable or taint behavior could change.

## Test Signals
A successful `CONFIG_CFG80211_KUNIT_TEST=m` build and module load confirms this boilerplate is sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/scan.c -->
# sources/distributed-fs/ceph-client/net/wireless/tests/scan.c

## Purpose
`tests/scan.c` provides KUnit coverage for cfg80211 scan-related helpers: multi-BSSID IE generation, malformed IE handling, BSS inform/lookup behavior, MLO STA-profile BSS synthesis, and 6 GHz colocated AP parsing from Reduced Neighbor Report elements.

## Important APIs, Types, And Functions
The file defines `struct test_elem`, parameter tables for `gen_new_ie`, `inform_bss_ml_sta`, and `cfg80211_parse_colocated_ap`, and tests `test_gen_new_ie()`, `test_gen_new_ie_malformed()`, `test_inform_bss_ssid_only()`, `test_inform_bss_ml_sta()`, and `test_cfg80211_parse_colocated_ap()`. It registers suites `cfg80211-ie-generation`, `cfg80211-inform-bss`, and `cfg80211-scan-6ghz`. Production APIs under test include `cfg80211_gen_new_ie()`, `cfg80211_inform_bss_data()`, `cfg80211_get_bss()`, `__cfg80211_get_bss()`, `cfg80211_put_bss()`, `cfg80211_parse_colocated_ap()`, and `cfg80211_free_coloc_ap_list()`.

## Control Flow
IE-generation tests build parent, child, and expected SKBs from table entries, run `cfg80211_gen_new_ie()` with ample, exact, and insufficient output sizes, and compare output lengths/data. The malformed test checks that truncated elements are ignored rather than overread. The SSID-only inform test creates a KUnit wiphy, installs an `inform_bss` callback, submits a BSS, validates returned metadata and IE contents, then verifies lookup by SSID and BSSID. The MLO test constructs a probe response containing SSID, optional operating class, RNR, fragmented Basic Multi-Link element, fragmented STA profile, and vendor elements; it then expects both reporting and link BSS entries and validates link metadata, generated IE length, NSTR restrictions, and BSS lookup visibility. The colocated-AP tests build RNR elements and verify valid/invalid parsing outcomes.

## State And Persistence
All state is per-test and allocated through KUnit helpers. `T_WIPHY()` creates a disposable wiphy with a 2.4 GHz band. Test callbacks count inform-BSS notifications through `struct inform_bss`. BSS cache entries created by production code are released with `cfg80211_put_bss()`.

## Dependencies And Integration Points
The suite depends on KUnit SKB helpers, cfg80211 core internals, the local `util.h` wiphy fixture, mac80211 IE fragmentation helper `ieee80211_fragment_element()`, KUnit-exported cfg80211 symbols, and 802.11 constants for RNR/MLE/MBSSID fields.

## Risks And Edge Cases
The tests target untrusted-management-frame parsing risks: fragmented elements, invalid extension elements, non-inheritance rules, MLE common/profile length validation, duplicate link handling, RNR channel derivation, unsupported NSTR nonprimary links, invalid BSSID and disabled MLD links, and precise IE buffer sizing. Because expected generated IE lengths are explicit, benign production changes in generated metadata may require coordinated test updates.

## Test Signals
Passing suites show that IE inheritance preserves or overrides elements correctly, malformed IEs do not corrupt output, BSS inform callbacks receive the expected `ies` pointer and driver data, BSS lookup works by SSID/BSSID, MLO STA-profile parsing creates a link BSS with expected channel/TSF/capability/use restrictions, and RNR colocated AP parsing accepts only valid 6 GHz TBTT records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/util.c -->
# sources/distributed-fs/ceph-client/net/wireless/tests/util.c

## Purpose
`util.c` implements the shared KUnit wiphy fixture used by cfg80211 wireless tests.

## Important APIs, Types, And Functions
It defines `t_wiphy_init()` and `t_wiphy_exit()`. Initialization allocates `cfg80211_ops`, creates a named wiphy via `wiphy_new_nm()`, stores test context and ops in `struct t_wiphy_priv`, and installs a copied 2.4 GHz channel table. Exit frees the wiphy and the allocated ops.

## Control Flow
KUnit calls `t_wiphy_init()` through `kunit_alloc_resource()` from the `T_WIPHY()` macro. The init path asserts allocations, initializes the private fixture data, and returns the wiphy as resource data. KUnit later calls `t_wiphy_exit()` to recover the private data, free the wiphy, and release ops memory.

## State And Persistence
Fixture state persists only for the lifetime of a KUnit resource. It includes the caller context pointer, allocated cfg80211 ops, a supported-band object, and a mutable copy of the shared 2.4 GHz channels.

## Dependencies And Integration Points
The file depends on KUnit resource APIs, cfg80211 wiphy allocation/free APIs, `channels_2ghz` and `struct t_wiphy_priv` from `util.h`, and tests that need a lightweight wiphy without registering real hardware.

## Risks And Edge Cases
The fixture intentionally does not fully register the wiphy, so tests must use only APIs that work on an unregistered test wiphy. If future tests need more bands, rates, regulatory flags, or driver ops, they must extend this fixture without breaking existing assumptions. The TODO-style comment notes that teardown does not currently assert absence of outstanding state.

## Test Signals
Successful use by `tests/scan.c` confirms that channels can be looked up and inform-BSS callbacks can be installed. KASAN/KUnit resource cleanup can detect leaks in wiphy or ops allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/util.h -->
# sources/distributed-fs/ceph-client/net/wireless/tests/util.h

## Purpose
`util.h` declares shared fixtures and helpers for cfg80211 KUnit tests.

## Important APIs, Types, And Functions
It defines the `CHAN2G()` initializer macro, static `channels_2ghz` table for channels 1 through 14, `struct t_wiphy_priv`, `T_WIPHY(test, ctx)`, `t_wiphy_ctx(wiphy)`, prototypes for `t_wiphy_init()`/`t_wiphy_exit()`, and `t_skb_remove_member()` for packed SKB structure manipulation.

## Control Flow
The `T_WIPHY()` macro allocates a KUnit resource backed by `t_wiphy_init()` and asserts success. `t_skb_remove_member()` performs an in-place `memmove()` and `skb_trim()` to remove a structure member from the tail-packed SKB data used in tests.

## State And Persistence
The header provides static channel fixture data and defines the private state layout used by `util.c`: test pointer, ops pointer, caller context, supported-band object, and mutable channel array.

## Dependencies And Integration Points
It depends on cfg80211 and KUnit types being available to including tests. `tests/scan.c` uses `T_WIPHY()`, `t_wiphy_ctx()`, channel fixtures, and `t_skb_remove_member()` when building synthetic MLO frames.

## Risks And Edge Cases
`channels_2ghz` is a header-local static array, so each translation unit gets its own copy. The SKB member-removal macro assumes the member being removed is in the final packed structure currently at the end of the SKB; misuse can corrupt test frames. Fixture channel data has no rates or advanced band capabilities unless tests add them.

## Test Signals
Compile coverage from all cfg80211 KUnit tests validates macro/type consistency. Runtime use by scan tests validates channel lookup and context recovery through `t_wiphy_ctx()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/tests/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/trace.c -->
# sources/distributed-fs/ceph-client/net/wireless/trace.c

## Purpose
`trace.c` instantiates cfg80211 tracepoints by defining `CREATE_TRACE_POINTS` and including `trace.h`.

## Important APIs, Types, And Functions
The file has no functions of its own. Its important symbol effect is generating tracepoint definitions declared in `trace.h` when not being parsed by sparse (`__CHECKER__`).

## Control Flow
There is no runtime control flow beyond normal tracepoint registration emitted by the kernel tracepoint machinery for included definitions.

## State And Persistence
Tracepoint state is generated by the included trace definitions and persists with the cfg80211 module/core lifetime.

## Dependencies And Integration Points
The file depends on `<linux/module.h>` and local `trace.h`. Other cfg80211 files call trace helpers such as scan, BSS, scheduled-scan, connect, and roam tracepoints whose storage is instantiated here.

## Risks And Edge Cases
Only one C file may define `CREATE_TRACE_POINTS` for a trace header; duplicate definitions would cause link errors, while omission would leave tracepoints undefined. The `__CHECKER__` guard avoids sparse-specific issues while preserving normal builds.

## Test Signals
Build/link success is the primary signal. Runtime ftrace/perf tracepoint discovery for cfg80211 events confirms that the trace definitions are instantiated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/trace.c -->
