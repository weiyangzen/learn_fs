# subset-b-005862

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i3c/master.h -->
# sources/distributed-fs/ceph-client/include/linux/i3c/master.h

## Purpose
Defines the internal Linux I3C master-controller interface, including mixed I3C/I2C bus modeling, board information, device descriptors, IBI handling, address-slot state, master operations, DMA helpers, bus notification, and registration APIs. It is a framework contract consumed by I3C controller drivers and the I3C core, not a standalone implementation.

## Important APIs, Types, And Functions
Core types are `i3c_master_controller`, `i3c_master_controller_ops`, `i3c_bus`, `i3c_dev_desc`, `i2c_dev_desc`, `i3c_device`, `i3c_device_ibi_info`, `i3c_ibi_slot`, and `i3c_dma`. Important operations include `bus_init`, `do_daa`, `send_ccc_cmd`, `i3c_xfers`, `i2c_xfers`, IBI request/enable/disable/recycle hooks, hotjoin hooks, open-drain speed configuration, and NACK retry configuration. Exported helpers cover CCCs, DAA, address allocation, dynamic device add, DMA map/unmap, master registration, hotjoin, IBI pooling, notifier registration, and private per-device master data.

## Control Flow
Typical controller flow is registration through `i3c_master_register()`, controller `bus_init`, master information setup, static/boardinfo device attachment, optional SETDASA/DAA through `do_daa`, and steady-state I3C/I2C transfers through ops callbacks. IBI flow is preallocation, hardware receives an interrupt payload into an `i3c_ibi_slot`, the controller queues it with `i3c_master_queue_ibi()`, the workqueue invokes the device handler, then the master recycles the slot.

## State And Persistence
Bus state is in address-slot bitmaps, current master, I2C/I3C device lists, SCL rates, and the bus `rw_semaphore`. Device state is in descriptors, dynamic/static addresses, boardinfo pointers, controller-private data, and IBI counters/completions. State is runtime kernel state only; persistence comes from firmware/DT boardinfo and rediscovery during bus initialization.

## Dependencies And Integration Points
Depends on I2C core, I3C CCC/device headers, Linux device model, workqueues, completions, mutexes, spinlocks, rwsems, DMA mapping, notifiers, and firmware nodes. Ceph has no direct dependency, but this header is part of the imported kernel client tree and may be compiled with other kernel subsystems in integrated builds.

## Risks
High-risk areas are bus-lock ordering, address-slot corruption during DAA/reattach, incorrect mixed-bus timing, IBI lifetime races, missing IBI disable/drain before free, DMA bounce/mapping mistakes, and optional operation hooks being treated as mandatory. Multi-master state makes `cur_master` and bus ownership assumptions especially sensitive.

## Test Signals
Useful tests include controller registration/unregistration, pure and mixed I2C/I3C enumeration, DAA and RSTDAA/ENTDAA paths, address collision handling, I2C fallback transfers, I3C SDR/HDR transfers, IBI request/enable/disable/drain, hotjoin detection, runtime PM interactions, DMA mapping error paths, and lockdep/KASAN/KCSAN runs around concurrent transfers and bus maintenance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i3c/master.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i8042.h -->
# sources/distributed-fs/ceph-client/include/linux/i8042.h

## Purpose
Defines the public kernel interface for the legacy i8042 keyboard/aux controller used by serio input drivers and platform quirks. It supplies command encodings, status/control bits, a filter callback type, and config-gated helper APIs.

## Important APIs, Types, And Functions
Command macros cover controller read/write/test, keyboard enable/disable/test/loopback, auxiliary port enable/disable/test/send/loopback, and mux prefix/send. Status bits include parity, timeout, aux data, keylock, command/data, mux error, input-buffer-full, and output-buffer-full. Control bits enable keyboard/aux interrupts, ignore keylock, disable ports, and translation. Runtime APIs are `i8042_lock_chip()`, `i8042_unlock_chip()`, `i8042_command()`, `i8042_install_filter()`, and `i8042_remove_filter()`.

## Control Flow
When `CONFIG_SERIO_I8042` is enabled, callers can serialize controller access, issue encoded commands, and install interrupt-context filters that decide whether incoming bytes are consumed before normal serio handling. Without the config, inline stubs return `-ENODEV` for functional operations and no-op for locking.

## State And Persistence
The header stores no state. Real state lives in the i8042 driver: controller registers, serio ports, installed filter/context, and locking. Platform firmware and controller hardware persist across boots, but this API only exposes runtime access.

## Dependencies And Integration Points
Includes errno/types and forward-declares `struct serio`. Integrates with the serio/input stack, architecture platform setup, ACPI/DMI quirks, and low-level interrupt handling.

## Risks
Filters run in interrupt context and must not sleep. Incorrect command encoding or locking can wedge legacy keyboard/mouse input. Callers must handle `-ENODEV` because the API compiles on systems without an i8042 driver.

## Test Signals
Test enabled and disabled configs, command return paths, filter install/remove ordering, interrupt-context filtering, parity/timeout status handling, and suspend/resume or hotplug paths on systems with PS/2 keyboard or touchpad hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i8042.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i8253.h -->
# sources/distributed-fs/ceph-client/include/linux/i8253.h

## Purpose
Exposes common definitions for the legacy i8253/i8254 PIT timer path: I/O port constants, latch calculation, global PIT lock, clockevent device, and setup/init helpers.

## Important APIs, Types, And Functions
Defines `PIT_MODE`, `PIT_CH0`, `PIT_CH2`, and `PIT_LATCH`, where `PIT_LATCH` derives the reload count from `PIT_TICK_RATE` and `HZ`. Externs are `i8253_lock`, `i8253_clockevent`, `clockevent_i8253_init(bool oneshot)`, `clockevent_i8253_disable()`, and `setup_pit_timer()`.

## Control Flow
Architecture timer setup calls `setup_pit_timer()` or initializes `i8253_clockevent`; low-level code programs PIT mode/channel ports under `i8253_lock`; clockevent mode selection may enable oneshot or periodic behavior; disable tears down PIT clockevent use.

## State And Persistence
Runtime state lives in the hardware PIT registers, `i8253_clockevent`, and the raw spinlock. There is no persistent software state beyond boot-time timer selection and hardware programming.

## Dependencies And Integration Points
Depends on kernel `HZ`, PIT tick rate from timex, raw spinlocks, and clockevents. Integrates with architecture timekeeping, legacy x86/PC-compatible timer setup, and speaker/CH2 users where applicable.

## Risks
PIT programming is low-level and timing-sensitive; incorrect locking or reload values can break scheduler ticks, timekeeping fallback, or oneshot behavior. Raw spinlock use indicates IRQ/early-boot constraints.

## Test Signals
Boot on PIT-backed or PIT-fallback platforms, verify clockevent registration, periodic and oneshot tick delivery, suspend/resume or clocksource fallback behavior, and lockdep coverage around concurrent PIT users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i8253.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i8254.h -->
# sources/distributed-fs/ceph-client/include/linux/i8254.h

## Purpose
Provides the small generic device-managed registration API for i8254-compatible counter/timer devices exposed through a `regmap`.

## Important APIs, Types, And Functions
Defines `struct i8254_regmap_config` with a parent `struct device *` and `struct regmap *`, plus `devm_i8254_regmap_register()`. The API lets a parent driver register an i8254 function without manually managing teardown.

## Control Flow
A parent device creates or obtains a regmap, fills `i8254_regmap_config`, and calls the devm registration helper. Device-managed lifetime ties cleanup to the parent device, so remove/error paths should not free the registered child manually.

## State And Persistence
This header stores no state. Runtime state is in the regmap-backed i8254 driver instance and devres records associated with the parent device.

## Dependencies And Integration Points
Forward-declares device and regmap, integrating with the driver core, devres, and regmap-backed counter/timer hardware. It is distinct from the legacy port-I/O PIT header.

## Risks
Bad regmap configuration or parent lifetime mistakes can produce invalid register access. Because the helper is devm-managed, double cleanup is a risk if callers also attempt explicit unregister paths.

## Test Signals
Probe/remove tests for parent drivers, devm cleanup on probe failure, regmap read/write validation, and counter/timer functional tests on hardware or regmap mocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/i8254.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/icmp.h -->
# sources/distributed-fs/ceph-client/include/linux/icmp.h

## Purpose
Defines in-kernel IPv4 ICMP helpers and RFC 4884/RFC 5837 extension constants. It bridges `sk_buff` transport-header access, UAPI ICMP definitions, and error-queue extension parsing.

## Important APIs, Types, And Functions
`icmp_hdr()` returns the ICMP header at `skb_transport_header()`. `icmp_is_err()` classifies destination unreachable, source quench, redirect, time exceeded, and parameter problem as ICMP error messages. `ip_icmp_error_rfc4884()` parses extended ICMP error data into `sock_ee_data_rfc4884`. Constants and `icmp_ext_iio_name_subobj` describe RFC 4884 extension versions and RFC 5837 interface information objects.

## Control Flow
Networking receive/error paths set the skb transport header, use `icmp_hdr()` to inspect the ICMP header, classify error types with `icmp_is_err()`, and optionally parse extension data for socket error queues or sysctl-enabled ICMP error extensions.

## State And Persistence
No persistent state is defined. State is packet-local in `sk_buff`, ICMP headers, and error queue metadata generated elsewhere.

## Dependencies And Integration Points
Includes `linux/skbuff.h`, UAPI ICMP constants, and UAPI error queue definitions. Integrates with IPv4 input, routing, socket error queues, PMTU/error reporting, and sysctls controlling ICMP error extensions.

## Risks
Callers must ensure transport headers and packet lengths are valid before dereferencing. Error classification influences whether packets are treated as network errors; incorrect classification can break error propagation or filtering. Extension parsing must defend against malformed lengths.

## Test Signals
IPv4 ICMP receive tests, error queue tests with RFC 4884 extensions, PMTU and redirect behavior, malformed/truncated ICMP packets, and sysctl-controlled interface-information extension reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/icmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/icmpv6.h -->
# sources/distributed-fs/ceph-client/include/linux/icmpv6.h

## Purpose
Defines in-kernel IPv6 ICMP helper entry points, config-gated send wrappers, error conversion, parameter-problem reporting, flow initialization, and ICMPv6 error classification.

## Important APIs, Types, And Functions
`icmp6_hdr()` accesses the ICMPv6 header from an skb. With IPv6 enabled, `icmp6_send()`, `icmpv6_send()`, `icmpv6_ndo_send()`, and `ip6_err_gen_icmpv6_unreach()` generate ICMPv6 errors; without IPv6, wrappers compile to no-ops. Other externs include `icmpv6_init()`, `icmpv6_cleanup()`, `icmpv6_err_convert()`, `icmpv6_param_prob_reason()`, and `icmpv6_flow_init()`. `icmpv6_is_err()` classifies destination unreachable, packet-too-big, time exceeded, and parameter problem.

## Control Flow
Protocol paths call `icmpv6_send()` with type/code/info, which forwards to `icmp6_send()` using IPv6 skb control block state. NAT-enabled builds can use a specialized ndo send path; otherwise a zeroed `inet6_skb_parm` is supplied. Parameter-problem helpers add a drop reason before emitting the ICMPv6 response.

## State And Persistence
No state is owned by the header. Runtime state is in skb control blocks, IPv6 routing/flow structures, per-net ICMPv6 implementation state, sockets, and module init/cleanup.

## Dependencies And Integration Points
Depends on skb, IPv6, netdevice, UAPI ICMPv6, netfilter NAT config, flowi6, sockets, and drop reasons. Integrates with IPv6 input/output, routing, neighbor discovery, socket errors, netfilter, and network-device transmit error paths.

## Risks
Disabled IPv6 builds silently drop send calls via no-op stubs, so callers must not depend on side effects. ICMPv6 generation is sensitive to skb ownership, control-block initialization, rate limiting, source address selection, and avoiding ICMP errors in response to invalid packets.

## Test Signals
IPv6 enabled/disabled builds, ICMPv6 error generation, packet-too-big and PMTU behavior, NAT ndo send paths, parameter-problem drop reasons, error conversion to errno, and malformed skb/control-block tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/icmpv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/idle_inject.h -->
# sources/distributed-fs/ceph-client/include/linux/idle_inject.h

## Purpose
Declares the idle injection framework used by thermal/power code to force selected CPUs into idle for controlled durations.

## Important APIs, Types, And Functions
The opaque `idle_inject_device` is registered with `idle_inject_register()` or `idle_inject_register_full()`, the latter accepting an update callback. Control APIs are `idle_inject_unregister()`, `idle_inject_start()`, `idle_inject_stop()`, `idle_inject_set_duration()`, `idle_inject_get_duration()`, and `idle_inject_set_latency()`.

## Control Flow
A governor or cooling driver registers a cpumask, sets run/idle durations and optional latency, starts injection, and later stops/unregisters it. The implementation schedules periodic CPU idle forcing outside this header; the optional update callback lets the owner revise policy during operation.

## State And Persistence
State is runtime-only in the opaque device: target CPUs, active/inactive status, run and idle durations, latency constraints, timers/work, and optional callback. There is no persistent policy storage here.

## Dependencies And Integration Points
Uses `struct cpumask` and integrates with CPU idle, scheduler, thermal cooling, power management, and CPU hotplug behavior.

## Risks
Incorrect durations or latency can damage performance or thermal response. CPU hotplug and cpumask lifetime must be handled carefully. Callers need to stop injection before unregister and avoid sleeping/expensive work in update paths if implementation context is constrained.

## Test Signals
Thermal throttling tests, start/stop idempotence, duration get/set validation, latency behavior, CPU hotplug under active injection, cpumask edge cases, and tracing that confirms requested idle/run duty cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/idle_inject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/idr.h -->
# sources/distributed-fs/ceph-client/include/linux/idr.h

## Purpose
Provides the legacy IDR and IDA allocation APIs: ID-to-pointer mapping via radix tree and plain integer ID allocation via xarray. It is widely used by kernel subsystems that need compact numeric handles without fixed-size tables.

## Important APIs, Types, And Functions
`struct idr` wraps a radix-tree root plus base and cyclic cursor. Initialization macros include `IDR_INIT_BASE`, `IDR_INIT`, and `DEFINE_IDR`; helpers include cursor get/set, lock wrappers, `idr_preload()`, allocation (`idr_alloc`, `idr_alloc_u32`, `idr_alloc_cyclic`), lookup, removal, replace, destroy, and iteration macros. `DEFINE_CLASS(idr_alloc, ...)` supplies cleanup integration that removes an allocated ID unless ownership is taken. `struct ida` wraps an xarray for ID-only allocation with `IDA_INIT`, `DEFINE_IDA`, `ida_alloc_range`, `ida_alloc`, min/max variants, `ida_free`, `ida_destroy`, and existence/find helpers.

## Control Flow
IDR users initialize, optionally preload memory, lock around modifications, allocate IDs for pointers, look up entries possibly under RCU, iterate or replace, then remove and destroy. IDA users allocate/free integer IDs without an external lock because the implementation handles locking internally. Cyclic allocation uses `idr_next` as a cursor and can be read/written with `READ_ONCE`/`WRITE_ONCE`.

## State And Persistence
State lives in radix tree/xarray nodes, free-space tags, `idr_base`, `idr_next`, and stored pointers or allocated bits. It is in-memory only; callers own object lifetimes and any RCU grace period after deletion.

## Dependencies And Integration Points
Depends on radix tree, xarray locking, GFP flags, percpu preload storage, cleanup helpers, and RCU synchronization conventions. Integrates with device minors, namespace IDs, request IDs, filesystem handles, and many driver subsystems.

## Risks
IDR lookups may be lockless only if callers manage object lifetime correctly. Forgetting `idr_preload_end()`, using the wrong allocation bounds/base, freeing objects before RCU readers are done, or mixing IDR lock wrappers with external locks incorrectly can cause leaks, UAF, or deadlocks. IDA differs from IDR in locking semantics, so porting between them is error-prone.

## Test Signals
Allocation/removal under concurrency, cyclic cursor wraparound, base-offset allocation, `idr_alloc_u32()` bounds, replace failure modes, iteration correctness during sparse IDs, RCU lookup lifetime tests, cleanup-class ownership transfer, and IDA range exhaustion/free/reuse tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/idr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-eht.h -->
# sources/distributed-fs/ceph-client/include/linux/ieee80211-eht.h

## Purpose
Defines IEEE 802.11be EHT data structures, capability/operation bit fields, multi-link element layouts, protected EHT action codes, TID-to-link mapping, and inline validators/parsers used by cfg80211/mac80211 and drivers.

## Important APIs, Types, And Functions
Important packed types include EHT capability and operation elements, MCS/NSS maps, EHT operation info, bandwidth indication, multi-link element/common-info variants, per-STA profiles, and TTLM elements. Inline helpers compute MCS/NSS and PPE sizes, validate EHT capability/operation/bandwidth indication/MLE/STA-profile/TTLM lengths, extract MLE common fields, derive EMLSR delays/timeouts, and iterate MLE subelements.

## Control Flow
Management-frame parsers first validate element size (`ieee80211_eht_capa_size_ok`, `ieee80211_eht_oper_size_ok`, `ieee80211_mle_size_ok`, `ieee80211_mle_type_ok`) and then consume optional fields based on presence bits. Accessor helpers advance through optional common-info fields in spec order and return defaults when a field is absent.

## State And Persistence
No mutable state is stored. The header describes on-wire state from association, beacon, probe, action, and multi-link frames. Parsed capabilities persist in higher-level station/BSS data structures outside this file.

## Dependencies And Integration Points
Depends on Linux types, Ethernet length, bitfield helpers, unaligned little-endian access, element iteration, and HE definitions for EHT capability sizing. It integrates with Wi-Fi 7/EHT negotiation, MLO link management, station profiles, action frame handling, and rate/control capability selection.

## Risks
Most risk is parser correctness: optional fields are variable length and many accessors assume prior validation. Missing `from_ap` handling changes MCS/NSS length. Multi-link common fields require exact offset progression; malformed presence bits can otherwise cause out-of-bounds reads. Draft/standard evolution also risks bit drift.

## Test Signals
Fuzz EHT elements and MLE subelements, validate boundary lengths for PPE/MCS/NSS/disabled-subchannel fields, test AP vs non-AP capabilities, multi-link profiles with every presence-bit combination, TTLM map sizes, EMLSR delay encodings, and interop association with EHT APs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-eht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-he.h -->
# sources/distributed-fs/ceph-client/include/linux/ieee80211-he.h

## Purpose
Defines IEEE 802.11ax HE structures, MAC/PHY capability bits, TWT, MCS/NSS, HE operation, spatial reuse, MU EDCA, 6 GHz operation/capability, transmit power envelope, and inline size validators.

## Important APIs, Types, And Functions
Key types are `ieee80211_twt_params`, `ieee80211_twt_setup`, `ieee80211_he_cap_elem`, `ieee80211_he_mcs_nss_supp`, `ieee80211_he_operation`, `ieee80211_he_spr`, `ieee80211_mu_edca_param_set`, `ieee80211_he_6ghz_oper`, `ieee80211_tx_pwr_env`, and `ieee80211_he_6ghz_capa`. Helpers compute HE MCS/NSS and PPE sizes, validate HE capability and TPE elements, compute HE operation and spatial reuse element sizes, and locate the 6 GHz operation field.

## Control Flow
Parsers inspect fixed fields, use channel-width and presence bits to add optional lengths, and only then expose optional structures. HE operation size is derived from VHT operation info, co-hosted BSS, and 6 GHz operation bits. TPE validation branches by category and interpretation, with different count rules for EIRP and PSD formats.

## State And Persistence
No state is owned here. It represents on-wire management-frame capabilities that are cached by wireless stack station/BSS state elsewhere after parsing.

## Dependencies And Integration Points
Depends on Linux types, Ethernet constants, bit operations, unaligned/LE helpers, and related HT/VHT constants referenced by 6 GHz capability definitions. Integrates with cfg80211/mac80211 association, scan parsing, regulatory power handling, rate control, TWT negotiation, and 6 GHz operation.

## Risks
Variable-length elements can be truncated or malformed. TPE extension counts, PPE sizing, and 6 GHz optional offsets need exact validation before access. Some capability bits have AP vs non-AP semantics, so callers must interpret in context.

## Test Signals
HE capability fuzzing, MCS/NSS size tests for 80/160/80+80, PPE boundary tests, HE operation optional-field tests, TPE validation for EIRP/PSD and extension fields, 6 GHz operation extraction, and Wi-Fi 6 association/regulatory interop tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-he.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-ht.h -->
# sources/distributed-fs/ceph-client/include/linux/ieee80211-ht.h

## Purpose
Defines IEEE 802.11n HT frame structures, capability/operation bit masks, MCS layout, aggregation parameters, spatial multiplexing power-save values, and HT/BACK action codes.

## Important APIs, Types, And Functions
Key structures are `ieee80211_bar`, `ieee80211_mcs_info`, `ieee80211_ht_cap`, and `ieee80211_ht_operation`. Macros describe MPDU sizes, HT control length, BAR control fields, MCS masks and stream calculation, capability bits, extended capability bits, A-MPDU parameters, operation-mode fields, block-ack parameters, and max A-MPDU buffer sizes for HT/HE/EHT.

## Control Flow
This is mostly declarative. Management-frame and action-frame parsers cast validated bytes to packed structures, inspect capability/operation masks, and use action-code enums to dispatch HT and block-ack actions. `IEEE80211_HT_MCS_CHAINS()` derives chain count from an MCS index.

## State And Persistence
No mutable state is stored. HT capability, MCS, operation, and block-ack negotiation results are cached by wireless stack station/session state outside the header.

## Dependencies And Integration Points
Depends on Linux types and Ethernet address size. Integrates with mac80211/cfg80211 HT association, rate control, aggregation setup/teardown, block-ack handling, channel-width negotiation, and later HE/EHT code that references HT aggregation and SMPS constants.

## Risks
Endian conversion is required for packed little-endian fields. Incorrect MCS or A-MPDU interpretation affects rate selection and aggregation limits. Block-ack masks are protocol-sensitive; wrong shifts can corrupt TID or buffer-size negotiation.

## Test Signals
HT capability parsing, MCS mask/rate derivation, 20/40 MHz operation handling, SMPS mode handling, ADDBA/DELBA frame parsing, A-MPDU limit enforcement, and interop with 802.11n APs and clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-ht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-mesh.h -->
# sources/distributed-fs/ceph-client/include/linux/ieee80211-mesh.h

## Purpose
Defines IEEE 802.11s mesh header layouts, mesh configuration and channel-switch elements, HWMP/RANN fields, mesh action codes, and mesh path/sync/root mode identifiers.

## Important APIs, Types, And Functions
Key packed structures are `ieee80211s_hdr`, `ieee80211_mesh_chansw_params_ie`, `ieee80211_meshconf_ie`, and `ieee80211_rann_ie`. Constants cover mesh ID length, address-extension flags, power-save flag, PREQ flags, channel-switch flags, mesh capability flags, RANN gate flag, action codes, sync methods, path protocols, path metrics, and root modes.

## Control Flow
Mesh data paths parse `ieee80211s_hdr` to determine TTL, sequence, address extension, and optional extended addresses. Management paths parse mesh configuration, channel switch, PREQ/RANN, and action-code fields to drive peering, HWMP path selection, root announcements, and channel changes.

## State And Persistence
No state is stored here. Mesh peering, path tables, sequence numbers, root mode, and beacon/configuration state live in mac80211 mesh code and driver state.

## Dependencies And Integration Points
Depends on Linux types and Ethernet constants. Integrates with mac80211 mesh networking, HWMP routing, mesh power save, channel switch announcements, beacon/probe parsing, and mesh action-frame handling.

## Risks
Packed/aligned mesh headers require careful length checks before accessing optional addresses. TTL/sequence and path metric interpretation affects loop prevention and routing. Capability mismatches can break peering or forwarding.

## Test Signals
Mesh peering and forwarding tests, HWMP PREQ/PREP/RANN behavior, address-extension frame parsing, mesh channel-switch handling, root mode transitions, power-save flags, and malformed mesh element fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-mesh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-nan.h -->
# sources/distributed-fs/ceph-client/include/linux/ieee80211-nan.h

## Purpose
Defines Wi-Fi Aware NAN operation-mode and device-capability bits, NAN attribute headers, master indication, anchor master information, and an attribute iteration macro.

## Important APIs, Types, And Functions
Constants describe VHT/HE PHY modes, 80+80/160 MHz support, PNDL support, TX/RX antenna count masks, device capability flags, and NAN attribute IDs. Packed types are `ieee80211_nan_attr`, `ieee80211_nan_master_indication`, and `ieee80211_nan_anchor_master_info`. `for_each_nan_attr()` safely walks variable-length NAN attributes using the 16-bit little-endian length field.

## Control Flow
NAN frame parsers iterate attributes from a data pointer and total length. The iterator checks that both the attribute header and declared payload fit before advancing to the next attribute.

## State And Persistence
No mutable state is owned here. NAN cluster/master election, discovery state, and parsed attributes are maintained by cfg80211/mac80211 or driver NAN logic.

## Dependencies And Integration Points
Uses Linux types, endian annotations, packed layout, and Ethernet address length. Integrates with Wi-Fi Aware discovery, NAN cluster information parsing, and vendor/driver management-frame handling.

## Risks
Attribute iteration depends on correct total length and little-endian conversion. Misspelled `NAN_OP_MODE_PNDL_SUPPRTED` is API surface and should not be casually renamed. Callers must still validate attribute-specific payload sizes after iteration.

## Test Signals
NAN attribute fuzzing, zero-length and truncated attributes, master indication parsing, anchor master rank/address union interpretation, antenna mask extraction, and operation-mode capability parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-nan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-p2p.h -->
# sources/distributed-fs/ceph-client/include/linux/ieee80211-p2p.h

## Purpose
Defines Wi-Fi Direct/P2P information-element attribute IDs and Notice of Absence structures used by wireless management-frame parsing.

## Important APIs, Types, And Functions
`enum ieee80211_p2p_attr_id` enumerates standard P2P attributes from status through invite flags and vendor-specific ID 221. `IEEE80211_P2P_NOA_DESC_MAX` limits typical stored NoA descriptors to four. Packed structures `ieee80211_p2p_noa_desc` and `ieee80211_p2p_noa_attr` describe absence schedules. Macros expose opportunistic power-save enable and CTWindow masks.

## Control Flow
P2P parsers dispatch attributes by ID, parse NoA attributes into index, OPPPS/CTWindow, and up to four descriptors, then drivers or mac80211 use the schedule to avoid transmissions during GO absence windows.

## State And Persistence
No state is stored here. P2P group ownership, client state, NoA schedules, and parsed attributes are retained by cfg80211/mac80211 or device firmware/driver code.

## Dependencies And Integration Points
Depends on Linux types and packed little-endian fields. Integrates with P2P action/probe/beacon IE parsing, power-save scheduling, group-owner behavior, and vendor-specific P2P extensions.

## Risks
The fixed four-descriptor array is a storage convention, not a full parser guarantee; callers must validate actual attribute length before indexing. Endian conversion is required for descriptor times. Attribute ID drift can affect interop.

## Test Signals
P2P IE parsing, NoA schedule length boundaries, OPPPS/CTWindow extraction, vendor-specific attributes, group-owner absence behavior, and malformed/truncated P2P attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-p2p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-s1g.h -->
# sources/distributed-fs/ceph-client/include/linux/ieee80211-s1g.h

## Purpose
Defines IEEE 802.11ah/S1G frame, operation, capability, beacon, TIM/PVB parsing, channel-width, and action-code helpers for sub-1 GHz Wi-Fi.

## Important APIs, Types, And Functions
Key APIs include `ieee80211_is_s1g_beacon()`, optional-field predicates, `ieee80211_s1g_optional_len()`, `ieee80211_is_s1g_short_beacon()`, TIM encoded-block length helpers, `ieee80211_s1g_find_target_block()`, parse helpers for bitmap/single/OLB modes, and `ieee80211_s1g_check_tim()`. Structures include S1G beacon compatibility, operation, AID response, S1G capability, `s1g_tim_aid`, and `s1g_tim_enc_block`.

## Control Flow
Beacon parsing checks frame-control type/subtype, derives optional fixed-field length from S1G beacon flags, and determines short-beacon status from the first variable element. TIM checking maps an AID into block/subblock/bit coordinates, scans encoded PVB blocks until the target block is found, validates block length, and evaluates the correct encoding mode with inversion support.

## State And Persistence
No persistent state is held. The header operates on frame-control fields, beacon variable data, TIM elements, and parsed capability/operation fields supplied by callers.

## Dependencies And Integration Points
Depends on 802.11 frame-control constants, WLAN element IDs, TIM IE layout, bitfield helpers, endian helpers, and errno values from surrounding kernel headers. Integrates with S1G scan/beacon parsing, power-save buffered-traffic checks, channel setup, and action-frame handling.

## Risks
TIM parsing is boundary-sensitive and must avoid off-by-one reads in variable encoded blocks. Short-beacon detection assumes element ordering required by the standard. AID mapping and inverted encodings are easy to misinterpret and directly affect whether clients wake for buffered traffic.

## Test Signals
S1G beacon and short-beacon parsing, optional fixed-field length combinations, TIM/PVB fuzzing for bitmap/single/OLB and inverted modes, AID boundary values, malformed length rejection, and interop with S1G AP beacon/TIM schedules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-s1g.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-uhr.h -->
# sources/distributed-fs/ceph-client/include/linux/ieee80211-uhr.h

## Purpose
Defines draft IEEE 802.11bn UHR operation and capability element layouts, UHR MAC/PHY capability bits, DPS/NPCA/P-EDCA/DBE parameter structures, SMD information, and inline validators/accessors.

## Important APIs, Types, And Functions
Important structures include `ieee80211_uhr_operation`, `ieee80211_uhr_npca_info`, `ieee80211_uhr_dps_info`, `ieee80211_uhr_dbe_info`, `ieee80211_uhr_p_edca_info`, `ieee80211_uhr_cap`, `ieee80211_uhr_cap_phy`, and `ieee80211_smd_info`. Helpers are `ieee80211_uhr_oper_size_ok()`, `ieee80211_uhr_npca_info()`, `ieee80211_uhr_npca_dis_subch_bitmap()`, `ieee80211_uhr_capa_size_ok()`, and `ieee80211_uhr_phy_cap()`.

## Control Flow
UHR operation validation starts with fixed operation fields, returns immediately for beacons, and otherwise walks optional DPS, NPCA, P-EDCA, and DBE fields in bit-order, adding disabled-subchannel bitmap lengths when presence bits are set. Capability validation accounts for AP-only DBE capability parameters before locating PHY capabilities.

## State And Persistence
No mutable state is stored. UHR operation/capability data is on-wire management-frame state cached elsewhere after validation.

## Dependencies And Integration Points
Depends on Linux types, Ethernet length, packed little-endian fields, and bit operations. Integrates with emerging Wi-Fi UHR/cfg80211/mac80211 parsing, DBE bandwidth negotiation, NPCA/P-EDCA operation, DPS mode handling, and SMD information exchange.

## Risks
This tracks draft 802.11bn fields, so spec churn is a major compatibility risk. Accessors assume `ieee80211_uhr_oper_size_ok(..., false)` or capability validation has already succeeded. AP vs non-AP capability size differences and optional bitmap offsets are likely bug sources.

## Test Signals
Operation-size tests for every optional-field combination, beacon vs non-beacon behavior, NPCA/DBE bitmap presence, AP and non-AP capability parsing, DBE MCS map length combinations, malformed/truncated UHR elements, and interop against updated draft vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-uhr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-vht.h -->
# sources/distributed-fs/ceph-client/include/linux/ieee80211-vht.h

## Purpose
Defines IEEE 802.11ac VHT capability, operation, MCS, operating-mode notification, A-MPDU, channel-width, and action-code interfaces.

## Important APIs, Types, And Functions
Key types are `ieee80211_vht_mcs_info`, `ieee80211_vht_cap`, `ieee80211_vht_operation`, `ieee80211_vht_opmode_bits`, `ieee80211_vht_max_ampdu_length_exp`, `ieee80211_vht_mcs_support`, and `ieee80211_vht_chanwidth`. The exported `ieee80211_get_vht_max_nss()` computes maximum usable spatial streams for a bandwidth/MCS combination, considering extended NSS bandwidth capability and operating-mode notification.

## Control Flow
Parsers cast validated VHT capability/operation elements, decode capability masks, MCS maps, channel width, center frequencies, and operation-mode notification bits. Rate-control or association code calls `ieee80211_get_vht_max_nss()` to reconcile advertised MCS/NSS capability with bandwidth and local extended-NSS support.

## State And Persistence
No state is owned here. Parsed VHT capability, operation, and opmode values persist in station/BSS state maintained by the wireless stack.

## Dependencies And Integration Points
Depends on Linux types and Ethernet constants. Integrates with cfg80211/mac80211 VHT association, channel definition, rate control, beamforming capability, aggregation limits, and HE 6 GHz capability definitions that reuse VHT MPDU/A-MPDU encodings.

## Risks
Packed little-endian fields must be converted before bit operations. Extended NSS bandwidth support is subtle and can overstate supported streams if local capability is ignored. Incorrect channel-width or MCS-map parsing can cause failed association or invalid rates.

## Test Signals
VHT capability/operation parsing, MCS map extraction, maximum NSS calculation for 80/160/80+80 and extended-NSS cases, opmode notification handling, A-MPDU exponent limits, and interop with 802.11ac APs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ieee80211-vht.h -->
