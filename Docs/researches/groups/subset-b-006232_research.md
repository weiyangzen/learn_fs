# subset-b-006232 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/tpe.c -->
# sources/distributed-fs/ceph-client/net/mac80211/tests/tpe.c

## Purpose
This file is a KUnit suite for mac80211 transmit power envelope (TPE) helper behavior. It validates the 6 GHz channel-subchannel offset logic and PSD reordering logic that are implemented in `mlme.c` and exported only for KUnit with `EXPORT_SYMBOL_IF_MAC80211_KUNIT`.

## Important APIs, types, and functions
- `struct subchan_test_case` describes one channel definition, a target partial subchannel count, and the expected offset returned by `ieee80211_calc_chandef_subchan_offset()`.
- `struct psd_reorder_test_case` describes AP and actually-used channel definitions plus an input/output `struct ieee80211_parsed_tpe_psd`.
- `subchan_offset()` asserts that the provided chandef is valid and compares the computed offset with the expected result.
- `psd_reorder()` copies the input PSD, calls `ieee80211_rearrange_tpe_psd()`, and compares the whole parsed PSD structure with `KUNIT_EXPECT_MEMEQ()`.
- `tpe_test_cases` registers two parameterized test families, and `kunit_test_suite(tpe)` exposes the suite as `mac80211-tpe`.

## Control flow
The suite defines static 6 GHz channels for control frequencies 5955, 6115, and 6255 MHz. Parameter generation comes from `KUNIT_ARRAY_PARAM_DESC()` for both case arrays. Each test first validates the constructed `cfg80211_chan_def`; this catches test-fixture errors before testing mac80211 helper logic. The offset cases cover equal-width channels, 320 MHz subdivision, 80+80 MHz primary/secondary ordering, and narrowing to 20/40/160 MHz. The PSD cases cover unchanged 320 MHz data, N=0 default behavior, and 320 MHz AP cases where HE subchannels and used EHT subchannels are lower, upper, or split.

## State and persistence
The tests use only static channel fixtures and stack-local copies of input structs. They do not allocate resources, mutate global state, or persist any state after a KUnit invocation. The PSD test intentionally copies `params->psd` before mutation because `ieee80211_rearrange_tpe_psd()` operates in place.

## Dependencies and integration points
The file includes `../ieee80211_i.h` for internal mac80211 declarations and imports the `EXPORTED_FOR_KUNIT_TESTING` namespace so it can link against KUnit-only exported helpers. It depends on cfg80211 channel validation and nl80211 channel-width constants. The covered production path is `ieee80211_rearrange_tpe()` in `mlme.c`, which rearranges parsed TPE values before station association/channel-use decisions consume them.

## Risks and edge cases
The test data encodes expected channel arithmetic directly; future changes to `ieee80211_chandef_downgrade()` or 320 MHz/80+80 semantics can require fixture updates. `KUNIT_EXPECT_MEMEQ()` compares the entire PSD structure, so padding or unrelated field changes in `struct ieee80211_parsed_tpe_psd` could make the test fragile if the structure layout changes. The tests focus on selected 6 GHz cases and do not exhaustively cover invalid chandefs, puncturing interactions, or every possible primary-channel offset.

## Test signals
Passing `mac80211-tpe` gives a direct signal that TPE PSD rearrangement still handles 320 MHz and 80+80 MHz offset calculations used by association logic. Failures identify either invalid fixture chandefs, wrong subchannel offset calculation, or in-place PSD mutation that no longer matches expected count/N/power ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/tpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/util.c -->
# sources/distributed-fs/ceph-client/net/mac80211/tests/util.c

## Purpose
This file provides reusable KUnit fixture construction for mac80211 tests. It builds a minimal but capability-rich `ieee80211_sub_if_data`, `wiphy`, and supported-band environment so unit tests can exercise internal mac80211 code without a real driver or registered wireless device.

## Important APIs, types, and functions
- `channels_2ghz` and `channels_5ghz` are static channel tables with nl80211 bands, center frequencies, and hardware values.
- `bitrates` provides legacy 2.4/5 GHz rates, including short-preamble flags where relevant.
- `sband_capa_5ghz` defines HE and EHT interface-type capabilities for station and P2P-client modes. It models a small hwsim-like capability set with up to four spatial streams.
- `t_sdata_init()` is the KUnit resource initializer. It allocates `struct t_sdata`, `struct ieee80211_sub_if_data`, and `struct wiphy`, wires the local/sdata/wiphy relationships, and allocates per-band channels/rates.
- `t_sdata_exit()` frees allocated channel/rate arrays plus the fake `sdata`, `wiphy`, and wrapper object.

## Control flow
Initialization allocates the wrapper first, then `sdata`, then `wiphy`, setting the KUnit resource name to `sdata`. It assigns a station-mode default interface, initializes the default link back-pointer and link ID, attaches 2 GHz and 5 GHz supported-band structs to `wiphy->bands`, and loops from `NL80211_BAND_2GHZ` through `NL80211_BAND_5GHZ`. For each band, it assigns band identity, duplicates the shared bitrate table, duplicates the correct channel table, and fills HT capabilities. The 5 GHz path additionally sets VHT capabilities and MCS maps. After the loop, `ieee80211_set_sband_iftype_data()` attaches HE/EHT station/P2P capability data to the 5 GHz band.

## State and persistence
All state is per KUnit resource and freed by `t_sdata_exit()`. The fixture stores pointers into its own `struct t_sdata` for bands while dynamically allocating channel and bitrate arrays. There is no persistence beyond the test resource lifetime. The helper leaves `t_sdata->ctx` available for tests that need to associate caller-specific context, but `t_sdata_init()` itself does not consume the `ctx` argument.

## Dependencies and integration points
The fixture depends on internal mac80211 structures from `ieee80211_i.h` via `util.h`, public wireless structures from `<net/mac80211.h>`, cfg80211/nl80211 capability constants, KUnit resource APIs, and kernel allocation helpers such as `kzalloc_obj()` and `kmemdup()`. It is consumed through the `T_SDATA(test)` macro in `util.h`; one visible user in this tree is `tests/chan-mode.c`.

## Risks and edge cases
Allocation failures after earlier allocations rely on KUnit assertions to abort; the exit hook is the cleanup path for successfully created resources. The code duplicates `bitrates` before the switch and again in each supported case, which makes the first duplicate unreachable for 2 GHz/5 GHz and is a small fixture leak if not optimized away by test abort semantics. The fixture currently only models 2 GHz and 5 GHz bands, so tests needing 6 GHz, S1G, or richer per-interface capabilities must extend it. Since it uses partial internal structs, tests can accidentally depend on fields left zeroed here but initialized differently in real mac80211 devices.

## Test signals
A test that obtains `T_SDATA(test)` and reaches its assertions verifies that basic fake mac80211 object wiring, band tables, and HE/EHT capability setup are sufficient for the unit under test. Failures during resource allocation or cleanup point to fixture setup errors rather than production wireless behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/util.h -->
# sources/distributed-fs/ceph-client/net/mac80211/tests/util.h

## Purpose
This header declares the shared mac80211 KUnit fixture API implemented by `tests/util.c`. It gives test files a compact way to allocate a fake `ieee80211_sub_if_data` environment as a KUnit-managed resource.

## Important APIs, types, and functions
- `struct t_sdata` is the fixture wrapper. It contains pointers to fake `ieee80211_sub_if_data` and `wiphy`, an embedded `ieee80211_local`, optional `ctx`, and embedded 2 GHz/5 GHz supported-band structs.
- `T_SDATA(test)` allocates the fixture using `kunit_alloc_resource(test, t_sdata_init, t_sdata_exit, GFP_KERNEL, NULL)`, asserts success, and returns the wrapper.
- `t_sdata_init()` and `t_sdata_exit()` are declared for the KUnit resource lifecycle.

## Control flow
Consumers include this header, call `T_SDATA(test)` inside a KUnit test, and receive a fully initialized wrapper or fail the test through `KUNIT_ASSERT_NOT_NULL()`. KUnit owns the resource and invokes `t_sdata_exit()` during cleanup.

## State and persistence
The header defines the shape of per-test state but no global state. The returned wrapper persists for the lifetime of the KUnit resource. The embedded `ieee80211_local` is stable by address and is referenced by the fake `sdata->local` pointer.

## Dependencies and integration points
The header includes `../ieee80211_i.h`, which exposes internal mac80211 structures unavailable through the public API. It is intended only for in-tree mac80211 tests. The macro wraps KUnit resource management and therefore assumes the caller runs in a KUnit test context.

## Risks and edge cases
Because the macro contains an assertion and returns an expression, it is convenient but not suitable for non-KUnit or setup paths that need ordinary error propagation. The fixture intentionally exposes internal mutable structures; tests can modify them freely, so cross-test isolation depends on each test allocating its own resource. The header currently names only 2 GHz and 5 GHz bands in `struct t_sdata`, matching the implementation.

## Test signals
The header itself has no standalone tests. Its signal comes from dependent KUnit suites: successful use demonstrates that the fixture ABI and implementation still agree with current mac80211 internal structure layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tests/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tkip.c -->
# sources/distributed-fs/ceph-client/net/mac80211/tkip.c

## Purpose
This file implements TKIP key mixing, IV construction, payload encryption, and payload decryption for mac80211 software crypto and hardware-assist paths. It bridges 802.11 TKIP packet fields, per-key TKIP phase state, WEP/RC4 payload encryption helpers, replay detection, and optional driver upload of phase-1 keys.

## Important APIs, types, and functions
- `tkip_sbox[]` and `tkipS()` implement the TKIP S-box operation used in key mixing.
- `write_tkip_iv()` writes the three byte TKIP IV prefix from IV16.
- `tkip_mixing_phase1()` computes P1K from temporal key, transmitter address, and IV32, then records `TKIP_STATE_PHASE1_DONE` and `p1k_iv32` in `struct tkip_ctx`.
- `tkip_mixing_phase2()` derives the 16-byte per-packet RC4 key from cached P1K and IV16.
- `ieee80211_tkip_add_iv()` is exported GPL and writes TKIP IV/Ext IV/key index fields for a packet number.
- `ieee80211_get_tkip_p1k_iv()`, `ieee80211_get_tkip_rx_p1k()`, and `ieee80211_get_tkip_p2k()` are exported helper APIs used by drivers or hardware crypto paths to obtain phase keys.
- `ieee80211_tkip_encrypt_data()` derives the per-packet key and calls `ieee80211_wep_encrypt_data()`.
- `ieee80211_tkip_decrypt_data()` validates IV/key index/replay, optionally updates hardware phase-1 state through `drv_update_tkip_key()`, decrypts through `ieee80211_wep_decrypt_data()`, and returns TKIP-specific status codes.

## Control flow
TX starts when `wpa.c` pushes IV space, increments `key->conf.tx_pn`, calls `ieee80211_tkip_add_iv()`, and, for software crypto, calls `ieee80211_tkip_encrypt_data()`. Encryption reads the packet IV from the skb, computes or reuses P1K under `key->u.tkip.txlock`, runs phase 2, and encrypts the payload/ICV area with RC4 through WEP helpers.

RX starts when `wpa.c` calls `ieee80211_tkip_decrypt_data()` with the 802.11 payload. The function checks minimum length, parses IV16/keyid/IV32, requires Ext IV, verifies the key index, and rejects replays against the selected receive queue context. In hardware-decrypted `only_iv` mode it marks the receive context as hardware-uploaded and skips RC4. Otherwise it computes phase 1 if state is uninitialized or IV32 changed, optionally calls the driver's `update_tkip_key` callback when hardware needs P1K, computes phase 2, decrypts bytes after the 8-byte TKIP IV, and on success reports IV32/IV16 back to the caller for later replay-counter commit after MIC verification.

## State and persistence
Transmit state lives in `key->u.tkip.tx`: cached P1K, `p1k_iv32`, state enum, and `txlock`. Receive state is per queue in `key->u.tkip.rx[queue]`, tracking IV32/IV16 and a phase context. This state persists for the lifetime of the key and is not stored outside kernel memory. The code deliberately does not advance RX replay state directly on decrypt success; it returns the observed IV so the caller can commit it only after Michael MIC verification.

## Dependencies and integration points
The implementation depends on `key.h` for internal key layout, `driver-ops.h` for hardware key updates, `wep.h` for RC4 encryption/decryption, unaligned little-endian access helpers, and public `<net/mac80211.h>` definitions. `wpa.c` is the main software path caller. Driver-visible helpers are exported for devices that need TKIP phase keys. Hardware integration occurs when `KEY_FLAG_UPLOADED_TO_HARDWARE` and `local->ops->update_tkip_key` are set.

## Risks and edge cases
TKIP is legacy crypto; correctness is mostly about compatibility and safe replay handling rather than modern security. Queue index validity is assumed by the caller. The RX replay exception allows the first TSC 0 frame only when the context is completely uninitialized, matching 802.11 compatibility rules but requiring careful state management. P1K caching can recompute often for out-of-order access categories, and locking must remain correct because TX phase state is shared. The `ra` parameter in decrypt is currently unused, so changes expecting receiver-address-specific behavior need scrutiny.

## Test signals
No direct KUnit tests are in this item. Useful signals are mac80211 crypto RX/TX tests, interoperability with TKIP APs, hardware crypto tests that exercise `update_tkip_key`, replay rejection tests, and static checks for exported symbol users. Tracepoint `drv_update_tkip_key` can confirm hardware phase-1 upload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tkip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tkip.h -->
# sources/distributed-fs/ceph-client/net/mac80211/tkip.h

## Purpose
This header declares the internal mac80211 TKIP software crypto entry points and decrypt result codes used by the WPA/TKIP receive and transmit paths.

## Important APIs, types, and functions
- `ieee80211_tkip_encrypt_data()` encrypts a TKIP payload using an ARC4 context, internal key, skb-derived IV fields, and payload pointer/length.
- `TKIP_DECRYPT_OK`, `TKIP_DECRYPT_NO_EXT_IV`, `TKIP_DECRYPT_INVALID_KEYIDX`, and `TKIP_DECRYPT_REPLAY` define status codes returned by the decrypt helper.
- `ieee80211_tkip_decrypt_data()` validates and decrypts a TKIP payload and reports IV32/IV16 to the caller on success.

## Control flow
The header is included by TKIP implementation and WPA crypto code. Callers pass an already selected `struct ieee80211_key`, packet buffer information, transmitter/receiver address context, hardware-decrypt mode, security queue index, and output IV pointers. The return code determines whether the RX path continues or drops the frame as a TKIP failure.

## State and persistence
The header declares APIs that mutate per-key TKIP state in `struct ieee80211_key`, but it defines no storage itself. Output IV parameters are transient handoff state used by the caller before committing replay counters after MIC validation.

## Dependencies and integration points
It includes kernel type definitions, crypto declarations for `struct arc4_ctx`, and `key.h` for the internal mac80211 key type. This is not a public driver API header; driver-facing phase-key helpers are exported from `tkip.c` through other declarations in public/internal headers.

## Risks and edge cases
The decrypt status enum uses negative values that overlap ordinary error-style returns, while success is zero. Callers must not collapse all negative values if they need diagnostics. Since function parameters include raw payload pointers and lengths, callers must ensure skb linearization and minimum length checks match the implementation's expectations.

## Test signals
Compilation of `wpa.c` and `tkip.c` verifies declaration compatibility. Runtime signals come from TKIP encrypted TX/RX, replay rejection, and hardware-decrypted `only_iv` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/tkip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/trace.c -->
# sources/distributed-fs/ceph-client/net/mac80211/trace.c

## Purpose
This file instantiates mac80211 tracepoints and, when message tracing is enabled, provides formatted logging wrappers that mirror mac80211 debug/info/error messages into trace events.

## Important APIs, types, and functions
- `CREATE_TRACE_POINTS` before including `trace.h` and `trace_msg.h` causes the Linux tracepoint definitions declared in those headers to be emitted in this translation unit.
- `__sdata_info()`, `__sdata_dbg()`, `__sdata_err()`, and `__wiphy_dbg()` are compiled under `CONFIG_MAC80211_MESSAGE_TRACING`.
- Each message wrapper builds a `struct va_format`, optionally prints through `pr_info`, `pr_debug`, `pr_err`, or `wiphy_dbg`, and always emits the matching `trace_mac80211_*` event.

## Control flow
The file is excluded from sparse checker processing through `#ifndef __CHECKER__`, because tracepoint macros are intentionally macro-heavy. During normal builds it includes cfg80211, driver ops, debug declarations, then defines and includes the trace headers. Message wrapper calls originate from macros in `debug.h`; they collect variadic arguments, set `vaf.va`, perform optional printk-style logging, emit a trace event, and then end the varargs scope.

## State and persistence
There is no durable state. Tracepoints are static kernel instrumentation objects generated at build time, and message wrapper state is stack-local `va_list`/`va_format` data. Emitted trace records persist only in the kernel tracing buffers configured by the runtime tracing subsystem.

## Dependencies and integration points
The file depends on Linux module and tracepoint infrastructure, cfg80211/mac80211 types, `driver-ops.h`, `debug.h`, `trace.h`, and `trace_msg.h`. It is the central instantiation point for trace events consumed by ftrace/perf/BPF-style tracing. The message wrappers integrate with `sdata_info`, `sdata_dbg`, `sdata_err`, and `wiphy_dbg` macros in `debug.h`.

## Risks and edge cases
Varargs must remain valid through both printk and trace assignment. Message tracing changes logging cost when enabled because strings are formatted into trace buffers even if ordinary debug printing is suppressed. The sparse exclusion means static-analysis coverage is weaker for this file. Tracepoint header include order and `CREATE_TRACE_POINTS` placement are fragile and must follow kernel tracepoint conventions.

## Test signals
Build success with tracing enabled verifies tracepoint instantiation. Runtime signals include visible events under the `mac80211` and `mac80211_msg` trace systems and correct duplication of debug messages into trace buffers when `CONFIG_MAC80211_MESSAGE_TRACING` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/trace.h -->
# sources/distributed-fs/ceph-client/net/mac80211/trace.h

## Purpose
This header declares the main mac80211 tracepoint system. It instruments driver callbacks, driver return values, driver-called mac80211 APIs, queue stop/wake internals, multi-link operation changes, channel context management, power-save/TWT/NAN/TDLS operations, and other high-value control paths.

## Important APIs, types, and functions
- Common field macros such as `LOCAL_ENTRY`, `STA_ENTRY`, `VIF_ENTRY`, `CHANDEF_ENTRY`, `CHANCTX_ENTRY`, `KEY_ENTRY`, and `AMPDU_ACTION_ENTRY` centralize trace record layout and print formatting.
- Event classes such as `local_only_evt`, `local_sdata_addr_evt`, `local_u32_evt`, `local_sdata_evt`, `sta_event`, `chanswitch_evt`, `release_evt`, `mgd_prepare_complete_tx_evt`, `local_chanctx`, `local_sdata_chanctx`, and `sta_flag_evt` reduce duplication across related events.
- Driver callback tracepoints include lifecycle/configuration (`drv_start`, `drv_stop`, `drv_config`, `drv_add_interface`, `drv_change_interface`, `drv_remove_interface`), keying (`drv_set_key`, `drv_update_tkip_key`, `drv_get_key_seq`, `drv_set_rekey_data`), scanning, station operations, AMPDU, channel switching, chanctx assignment/switching, AP/IBSS/NAN/PMSR/TDLS/TWT, netdev offload, traffic-control, and MLO/EML/TTLM operations.
- API tracepoints include `api_start_tx_ba_session`, BA callbacks, restart/beacon/connection loss, CQM notifications, scan completion, channel switch completion, GTK rekey notification, EOSP/buffered-station operations, radar detection, SMPS, and OMI bandwidth preparation/finalization.
- Internal queue tracepoints `wake_queue` and `stop_queue` record queue, reason, and refcount.

## Control flow
This header follows the Linux tracepoint pattern: guarded declarations are included normally by users, while `trace.c` defines `CREATE_TRACE_POINTS` and includes the header once to instantiate tracepoints. Call sites invoke generated functions such as `trace_drv_config()` and `trace_api_scan_completed()`. Most driver callback wrappers in `driver-ops.h` trace before invoking a driver op and then trace a typed return event. Other direct call sites in `mlme.c`, `scan.c`, `sta_info.c`, `ht.c`, `he.c`, `main.c`, `offchannel.c`, `util.c`, and aggregation code emit API or internal events.

## State and persistence
The header defines trace record schemas, not mac80211 state. At runtime each enabled event snapshots selected fields from live objects into trace buffers: wiphy names, vif names/types, station addresses, chandefs, key metadata, changed bitmasks, link IDs, queue reasons, and selected payload arrays. Dynamic arrays are used for variable-length data such as SSIDs, ARP address lists, and vif channel-context switch arrays. Trace records persist according to kernel tracing buffer configuration, not in mac80211 objects.

## Dependencies and integration points
It depends on `<linux/tracepoint.h>`, `<net/mac80211.h>`, `ieee80211_i.h`, and many cfg80211/mac80211 internal types referenced in trace prototypes. The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` block is required by the kernel trace generator. The trace names form a user-visible ABI for tracing scripts under systems that consume ftrace/perf events, so renames and field layout changes can affect observability tooling.

## Risks and edge cases
Trace macros dereference many pointers supplied by call sites; call sites must ensure objects remain valid for the duration of trace evaluation. Some events snapshot sensitive material-adjacent metadata such as key indices, replay counters, rekey material arrays, BSSIDs, and SSIDs, so tracing configuration matters in production. Dynamic array lengths depend on live fields and must remain bounded; for example ARP addresses are capped to `IEEE80211_BSS_ARP_ADDR_LIST_LEN`. The `drv_switch_vif_chanctx` helper structs are packed and manually populated, so changes to `struct ieee80211_vif_chanctx_switch` require matching trace updates.

## Test signals
Primary signals are build-time tracepoint generation and runtime availability of `/sys/kernel/tracing/events/mac80211/*` events. Functional signals are trace consistency around driver op wrappers: a driver operation should produce an entry event and an appropriate return event. BPF/ftrace scripts that decode event fields are useful regression detectors for field names and formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/trace_msg.h -->
# sources/distributed-fs/ceph-client/net/mac80211/trace_msg.h

## Purpose
This header declares the optional `mac80211_msg` tracepoint system used to capture formatted mac80211 debug/info/error messages as trace events when `CONFIG_MAC80211_MESSAGE_TRACING` is enabled.

## Important APIs, types, and functions
- `DECLARE_EVENT_CLASS(mac80211_msg_event)` defines a single `struct va_format *` based event class with a dynamic formatted string field.
- `mac80211_info`, `mac80211_dbg`, and `mac80211_err` are concrete events derived from the class.
- `__vstring()` and `__assign_vstr()` store the formatted message in the trace record.

## Control flow
When message tracing is configured, the header defines trace declarations under `TRACE_SYSTEM mac80211_msg`. `trace.c` includes it with `CREATE_TRACE_POINTS` to instantiate events. The wrappers in `trace.c` call `trace_mac80211_info()`, `trace_mac80211_dbg()`, or `trace_mac80211_err()` after preparing a `va_format`.

## State and persistence
The header defines event schema only. Each event snapshots one formatted message string into the tracing ring buffer. No mac80211 state is changed, and no message history is persisted outside the tracing subsystem.

## Dependencies and integration points
It depends on Linux tracepoint infrastructure, public mac80211 types, and `ieee80211_i.h`. It integrates with `debug.h` message macros through the wrapper functions implemented in `trace.c`. The final `TRACE_INCLUDE_FILE trace_msg` block is required so the trace generator can find this header when building trace definitions.

## Risks and edge cases
The trace event formats variadic strings, so invalid format strings or mismatched arguments in callers affect both printk and tracing paths. Enabling message tracing increases overhead and can expose operational messages in trace buffers. Because the whole header is under `CONFIG_MAC80211_MESSAGE_TRACING`, callers must be guarded by the corresponding debug wrapper definitions.

## Test signals
Build success with `CONFIG_MAC80211_MESSAGE_TRACING=y` verifies trace declaration and instantiation. Runtime signal is the presence of `mac80211_msg/mac80211_info`, `mac80211_msg/mac80211_dbg`, and `mac80211_msg/mac80211_err` events and matching formatted messages when mac80211 debug wrappers run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/trace_msg.h -->
