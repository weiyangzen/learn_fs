# subset-b-005445 Research

Grouped source research for Thunderbolt KUnit coverage, TMU mode management, tracepoints, and tunnel lifecycle support. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/test.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/test.c

## Purpose

`test.c` is the Thunderbolt driver's KUnit test suite. It builds synthetic host and device router topologies, then validates path walking, path allocation, tunnel allocation, credit accounting, DMA tunnel matching, and Thunderbolt property directory parsing/formatting/copying. The file is test-only but important because it records expected behavior for the shared path and tunnel helpers used by the connection manager.

## Important APIs, Types, and Functions

The fixture layer uses `alloc_switch()`, `alloc_host()`, `alloc_host_usb4()`, `alloc_host_br()`, `alloc_dev_default()`, `alloc_dev_with_dpin()`, `alloc_dev_without_dp()`, and `alloc_dev_usb4()` to allocate `struct tb_switch` instances and `struct tb_port` arrays under KUnit-managed memory. `kunit_ida_init()` wraps `ida_init()` and `ida_destroy()` in KUnit resources so per-port HopID allocators are cleaned up. `struct port_expectation` and `struct hop_expectation` describe expected path walks and hop layouts.

The tests call production APIs from `tb.h` and `tunnel.h`: `tb_next_port_on_path()`, `tb_for_each_port_on_path`, `tb_path_alloc()`, `tb_path_free()`, `tb_tunnel_alloc_pci()`, `tb_tunnel_alloc_dp()`, `tb_tunnel_alloc_usb3()`, `tb_tunnel_alloc_dma()`, `tb_tunnel_match_dma()`, `tb_tunnel_port_on_path()`, `tb_tunnel_put()`, `tb_property_parse_dir()`, `tb_property_find()`, `tb_property_format_dir()`, `tb_property_copy_dir()`, and `tb_property_free_dir()`.

## Control Flow

Test setup constructs host and device routers with explicit port types, HopID ranges, credit limits, dual-link pointers, route values, and `remote` links. Bonded links double lane-0 credit totals and mark lane-1 as bonded with zero usable credits. Individual path tests then walk or allocate routes across single-hop, daisy-chain, tree, complex-tree, maximum-depth, unconnected, unbonded-lane, and mixed bonded/unbonded topologies. Tunnel tests allocate PCIe, DP, USB3, and DMA tunnels and assert source/destination ports, path counts, path lengths, hop direction, and selected HopIDs.

The credit tests switch between legacy fixtures and USB4 credit-allocation fixtures. They verify initial credits and NFC credits for PCIe, DP AUX/main, USB3, and DMA paths, including the case where multiple DMA tunnels consume and release per-port `dma_credits`. The property tests parse a hard-coded root directory block, verify expected values and nested network directory UUID, format it back byte-for-byte, and deep-copy/compare directories recursively.

## State and Persistence Behavior

All state is in-memory and scoped to KUnit test execution. Router, port, path, tunnel, IDA, and property objects are allocated with KUnit or production allocators and released via KUnit cleanup, `tb_path_free()`, `tb_tunnel_put()`, and `tb_property_free_dir()`. No persistent storage is used. The tests intentionally mutate synthetic `struct tb_port` fields such as `remote`, `bonded`, `total_credits`, and `dma_credits` to model hardware/router state.

## Dependencies and Integration Points

The suite depends on the Thunderbolt core headers `tb.h` and `tunnel.h`, KUnit, Linux IDA helpers, production path/tunnel/property implementations, and Thunderbolt constants such as `TB_TYPE_PORT`, `TB_TYPE_PCIE_UP`, `TB_TYPE_DP_HDMI_IN`, `TB_TYPE_USB3_DOWN`, and `TB_TUNNEL_*`. It is registered as the `thunderbolt` KUnit suite through `kunit_test_suite()`, so kernel KUnit infrastructure discovers and runs it.

## Risks and Edge Cases

The synthetic fixtures bypass real config-space reads, hotplug timing, workqueues, ACPI policy, and hardware error returns, so they are strong structural tests but not full integration tests. Many expectations depend on exact port numbering and route literals; legitimate topology helper changes will require synchronized fixture updates. The DP activation path's asynchronous DPRX behavior and TMU behavior are not directly exercised here. Credit expectations are sensitive to constants in `tunnel.c`, ACPI policy helpers, and USB4 credit-allocation rules.

## Test Signals

The file itself is the primary test signal for path and tunnel regressions. Useful follow-up signals are running the `thunderbolt` KUnit suite, compile coverage with Thunderbolt enabled, adding tests for DP bandwidth allocation mode and tunnel activation/deactivation, and hardware or emulation tests that cover real config-space IO, hotplug, DPRX polling, and TMU transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tmu.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/tmu.c

## Purpose

`tmu.c` implements Thunderbolt/USB4 Time Management Unit support. It discovers router and lane-adapter TMU capabilities, records the current TMU mode, configures requested modes, posts grandmaster time to newly attached USB4 routers, enables or disables time synchronization, and rolls hardware back when a mode transition fails.

## Important APIs, Types, and Functions

Public entry points are `tb_switch_tmu_init()`, `tb_switch_tmu_post_time()`, `tb_switch_tmu_disable()`, `tb_switch_tmu_enable()`, and `tb_switch_tmu_configure()`. They operate on `struct tb_switch` and its `sw->tmu` substructure, whose mode enum is declared in `tb.h`. Internal data tables `tmu_rates[]` and `tmu_params[]` map `TB_SWITCH_TMU_MODE_OFF`, `LOWRES`, `HIFI_UNI`, `HIFI_BI`, and `MEDRES_ENHANCED_UNI` to timestamp intervals and averaging/replay parameters.

Important helpers include `tmu_mode_name()`, `tb_switch_tmu_enhanced_is_supported()`, `tb_switch_set_tmu_mode_params()`, `tb_switch_tmu_ucap_is_supported()`, `tb_switch_tmu_rate_read()`, `tb_switch_tmu_rate_write()`, `tb_port_tmu_set_unidirectional()`, `tb_port_tmu_enhanced_enable()`, `tb_port_set_tmu_mode_params()`, `tb_port_tmu_rate_write()`, `tb_port_tmu_time_sync_enable()/disable()`, `tb_switch_tmu_set_time_disruption()`, `tmu_mode_init()`, and rollback helpers `tb_switch_tmu_off()` and `tb_switch_tmu_change_mode_prev()`.

## Control Flow

Initialization skips ICM-managed switches, locates router TMU and lane time capabilities, reads the current timestamp interval, checks unidirectional and enhanced mode flags, and derives `sw->tmu.mode`, `mode_request`, and `has_ucap` without changing hardware. Configuration only validates and stores the requested mode. Enable first marks time disrupted, then either writes only the host router rate or, for device routers, selects an off-to-unidirectional, off-to-bidirectional, off-to-enhanced, or non-off mode-change sequence. Each sequence programs parent/child rates, router parameters, lane-adapter unidirectional or enhanced bits, and time-sync disable bits in a strict order. Failure paths attempt to restore off or previous mode.

`tb_switch_tmu_post_time()` reads the root switch grandmaster local time, converts the register representation to nanoseconds, asserts time disruption on the target, writes Post Local Time and Post Time registers, polls until completion, and clears disruption. Disable turns off the local router rate, disables adapter time sync, clears unidirectional or enhanced state where applicable, and updates `sw->tmu.mode` to off.

## State and Persistence Behavior

Persistent software state is limited to `sw->tmu.cap`, per-port `port->cap_tmu`, `sw->tmu.mode`, `sw->tmu.mode_request`, and `sw->tmu.has_ucap`. Hardware-visible state is stored in TMU router and adapter config registers such as `TMU_RTR_CS_*`, `TMU_ADP_CS_*`, and Titan Ridge VSEC time registers. There is no disk persistence; state is reconstructed by `tb_switch_tmu_init()` and modified during router attach, enable, disable, and mode changes.

## Dependencies and Integration Points

The file depends on `tb.h`, config-space accessors `tb_sw_read/write()` and `tb_port_read/write()`, router helpers such as `tb_route()`, `tb_switch_parent()`, `tb_upstream_port()`, `tb_switch_downstream_port()`, `tb_switch_is_usb4()`, `tb_switch_is_icm()`, `tb_switch_is_titan_ridge()`, and `usb4_switch_version()`. The connection manager in `tb.c` chooses TMU modes, calls configure/enable during discovery, disables TMU on unplug, and initializes low-resolution mode on the root switch.

## Risks and Edge Cases

TMU mode changes touch both sides of a link and can leave partially programmed hardware if a write fails after upstream state was changed. Rollback intentionally ignores some errors, which avoids masking the original failure but may leave stale hardware state after unplug or transient config-space failure. Enhanced mode requires both parent and child support; incorrect version detection can return `-EOPNOTSUPP` or attempt unsupported register writes. Time posting relies on a bounded poll and disruption bit cleanup; timeout or cleanup failure affects synchronization quality. There is no direct KUnit coverage in this file.

## Test Signals

Useful signals include compile coverage, mocked config-space tests for mode validation and rollback ordering, attach/resume tests that confirm `sw->tmu.mode` and hardware rates match, fault injection for read/write failures in each transition step, USB4 v1/v2 and Titan Ridge hardware validation, and tracing/debug logs showing time disruption is cleared on success and failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/trace.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/trace.h

## Purpose

`trace.h` defines Thunderbolt tracepoints for control-channel packets. It formats transmitted packets, received packets, and asynchronous event packets with domain index, package type, route, message-specific header fields, raw dword data, and receive-drop status. The header follows the kernel tracepoint pattern where helper definitions are guarded but `trace/define_trace.h` inclusion remains outside the include guard.

## Important APIs, Types, and Functions

The tracepoint surface consists of event class `tb_raw`, concrete events `tb_tx` and `tb_event`, and `TRACE_EVENT(tb_rx)`. Helper macros `tb_cfg_type_name()` and `show_type_name()` map package type constants such as `TB_CFG_PKG_READ`, `WRITE`, `ERROR`, `EVENT`, `ICM_EVENT`, `ICM_CMD`, and `ICM_RESP` to symbolic names. Inline formatting helpers `show_data_read_write()`, `show_data_error()`, `show_data_event()`, `show_route()`, and `show_data()` interpret raw `u32` payloads as Thunderbolt config packet structures from `tb_msgs.h`.

## Control Flow

At trace runtime, callers pass a domain index, type byte, data pointer, and byte size. `TP_fast_assign` stores the index/type, converts byte size to dword count, and copies the payload into a dynamic trace array. `TP_printk` then prints the symbolic type and delegates raw payload formatting to `show_data()`. That helper emits packet-specific fields for read/write, error, event, and ICM packets, then appends the raw dword array. `tb_rx` follows the same path and adds a `dropped` field to indicate packets not matched to a request.

## State and Persistence Behavior

Tracepoints do not own persistent driver state. They copy packet data into the ftrace ring buffer when enabled. Formatting state is transient in `struct trace_seq`. Trace output persistence is controlled by kernel tracing infrastructure, not this header.

## Dependencies and Integration Points

The header depends on Linux tracepoint APIs, `trace_seq`, `tb_msgs.h` packet layouts, and `tb_cfg_get_route()`. `ctl.c` calls `trace_tb_tx()` when sending, `trace_tb_event()` for event packets, and `trace_tb_rx()` when receiving. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` are set so kernel trace generation can find this header from the Thunderbolt driver directory.

## Risks and Edge Cases

The dynamic array length uses `size / 4`, while `memcpy()` copies `size` bytes. Callers must pass sizes that are valid multiples of four and backed by enough memory for the casted packet structures used by formatting helpers. Unknown package types still call `show_route()`, so malformed short packets could be unsafe if traced from a bad caller. ICM packets force `route=0`, which is an inference based on current message semantics. Trace output is diagnostic only, but wrong formatting can mislead debugging of control-channel failures.

## Test Signals

Compile coverage with tracing enabled is the basic signal. Runtime signals include enabling `thunderbolt:tb_tx`, `thunderbolt:tb_rx`, and `thunderbolt:tb_event` under ftrace, checking READ/WRITE/ERROR/EVENT/ICM formatting against known packets, and fuzz or fault-injection tests in the control layer to ensure dropped/unknown packets do not break tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tunnel.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/tunnel.c

## Purpose

`tunnel.c` implements Thunderbolt tunnel discovery, allocation, activation, deactivation, event notification, credit assignment, and bandwidth management for PCIe, DisplayPort, DMA/XDomain, and USB3 tunnels. It converts pairs of adapter ports into one or more `struct tb_path` objects, programs protocol-specific adapter state, exposes bandwidth hooks to the connection manager, and cleans up incomplete discovered tunnels.

## Important APIs, Types, and Functions

Exported functions are `tb_tunnel_discover_pci()`, `tb_tunnel_alloc_pci()`, `tb_tunnel_reserved_pci()`, `tb_tunnel_discover_dp()`, `tb_tunnel_alloc_dp()`, `tb_tunnel_alloc_dma()`, `tb_tunnel_match_dma()`, `tb_tunnel_discover_usb3()`, `tb_tunnel_alloc_usb3()`, `tb_tunnel_put()`, `tb_tunnel_event()`, `tb_tunnel_is_invalid()`, `tb_tunnel_activate()`, `tb_tunnel_deactivate()`, `tb_tunnel_port_on_path()`, `tb_tunnel_maximum_bandwidth()`, `tb_tunnel_allocated_bandwidth()`, `tb_tunnel_alloc_bandwidth()`, `tb_tunnel_consumed_bandwidth()`, `tb_tunnel_release_unused_bandwidth()`, `tb_tunnel_reclaim_available_bandwidth()`, and `tb_tunnel_type_name()`.

Key internals include `tb_tunnel_alloc()`, kref helpers protected by `tb_tunnel_lock`, PCIe encapsulation and credit helpers, DP capability exchange, bandwidth reduction, bandwidth-allocation-mode support, DPRX delayed work, DMA credit reservation/release, USB3 bandwidth reclaim/release, and generic wrappers that call protocol-specific function pointers stored in `struct tb_tunnel`.

## Control Flow

Allocation creates a flex-array `struct tb_tunnel`, initializes protocol function pointers, stores source/destination ports, allocates paths with protocol HopIDs, and initializes per-hop flow-control, priority, weight, initial credits, and NFC credits. Discovery checks whether a protocol adapter is already enabled, follows existing hardware paths with `tb_path_discover()`, validates endpoint type and completion, and deactivates/cleans up incomplete tunnels.

Activation deactivates any already active paths, sets state to `TB_TUNNEL_ACTIVATING`, runs optional `pre_activate`, activates each `tb_path`, then runs protocol-specific adapter activation. PCIe toggles extended encapsulation on USB4 v2 links and enables downstream/upstream adapters in different order for activate vs deactivate. DP exchanges capabilities, optionally enables bandwidth allocation mode, writes DP HopIDs, enables adapters, and may return `-EINPROGRESS` while delayed DPRX work waits for capabilities read before marking the tunnel active. DMA relies on path activation only and releases reserved credits in its destroy callback. USB3 can pre-allocate isochronous bandwidth and enable both adapters.

Generic bandwidth APIs require active tunnels except `consumed_bandwidth()`, which accepts activating DP tunnels so reserved bandwidth can be reported while DPRX is pending. Bandwidth changes call protocol hooks and emit a changed userspace event.

## State and Persistence Behavior

Software state is in `struct tb_tunnel`: kref, list node, protocol type, state, source/destination ports, path array, bandwidth limits, USB3 allocations, DP bandwidth-mode flag, DPRX work/cancel flags, timeout, and callback. DMA also mutates per-port `dma_credits` and releases them during tunnel destruction. Hardware-visible state is held in path hop registers, protocol adapter enable bits, DP remote/common capability registers, USB4 bandwidth registers, PCIe encapsulation bits, and USB3 bandwidth allocation registers. Module parameters `dprx_timeout`, `dma_credits`, and `bw_alloc_mode` affect behavior at runtime. There is no filesystem persistence.

## Dependencies and Integration Points

The file depends on `tunnel.h`, `tb.h`, path helpers from `path.c`, adapter helpers for PCIe/DP/USB3/USB4, ACPI policy helpers (`tb_acpi_may_tunnel_*`, `tb_acpi_is_xdomain_allowed()`), kernel workqueues, krefs, module parameters, and userspace event delivery through `tb_domain_event()`. It integrates with the domain connection manager, bandwidth allocator, XDomain networking, and KUnit tests in `test.c`.

## Risks and Edge Cases

The highest-risk areas are partial activation rollback, asynchronous DP DPRX lifetime, credit accounting, and bandwidth math. `tb_dp_dprx_start()` takes a reference and delayed work must drop it exactly once on completion or cancellation. Discovery can clean up incomplete hardware paths and disables adapters as a side effect. DMA credit accounting mutates `port->dma_credits`; missing destroy paths or underflow would starve future tunnels. DP bandwidth reduction excludes UHBR values outside bandwidth allocation mode and returns `-ENOSR` when no lower common mode fits. USB3 reclaim subtracts the full new allocation from available bandwidth rather than just the delta, so callers must pass available totals with that contract in mind. Trace/userspace events can be emitted for activation/deactivation and bandwidth changes, so state transitions are externally visible.

## Test Signals

`test.c` covers structural allocation for PCIe, DP, USB3, DMA, port-on-path checks, DMA matching, and many credit-allocation cases. Additional useful signals are activation/deactivation tests with mocked adapter IO, delayed DPRX callback tests, bandwidth allocation mode tests, fault injection for partial path activation and register writes, module-parameter coverage for DMA credits and DPRX timeout, and hardware validation for PCIe extended encapsulation, DP MST/alt-mode, USB3 isochronous bandwidth, and XDomain DMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tunnel.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/tunnel.h

## Purpose

`tunnel.h` is the public internal Thunderbolt tunneling interface. It declares tunnel protocol types, lifecycle states, the central `struct tb_tunnel`, allocation/discovery APIs for PCIe, DP, DMA, and USB3 tunnels, generic lifecycle and bandwidth APIs, tunnel event types, and logging helpers.

## Important APIs, Types, and Functions

`enum tb_tunnel_type` identifies `TB_TUNNEL_PCI`, `TB_TUNNEL_DP`, `TB_TUNNEL_DMA`, and `TB_TUNNEL_USB3`. `enum tb_tunnel_state` distinguishes inactive, activation-started, and fully active tunnels. `struct tb_tunnel` stores references, endpoints, path count and flexible `paths[]` array, protocol callback hooks (`pre_activate`, `activate`, `post_deactivate`, `destroy`, and bandwidth operations), list node, state, bandwidth limits/allocations, DP DPRX state, delayed work, and optional DP activation callback.

The header declares protocol-specific allocators/discoverers, `tb_tunnel_match_dma()`, `tb_tunnel_reserved_pci()`, `tb_tunnel_put()`, `tb_tunnel_activate()`, `tb_tunnel_deactivate()`, active/invalid/path membership checks, maximum/allocated/alloc/consumed/release/reclaim bandwidth functions, type predicate inlines, `tb_tunnel_direction_downstream()`, event emission, and `tb_tunnel_type_name()`.

## Control Flow

The header itself has no executable flow beyond inline predicates. It defines the callback-driven contract used by `tunnel.c`: callers allocate or discover a tunnel, optionally attach it to domain lists, activate it, query or adjust bandwidth while active, deactivate it, and release the reference. DP users may receive a callback when asynchronous DPRX completion changes state from activating to active.

## State and Persistence Behavior

The state model is in-memory. `TB_TUNNEL_INACTIVE` means activation has not been called or has been torn down, `TB_TUNNEL_ACTIVATING` means activation succeeded far enough to reserve/program paths but final completion may still be pending, and `TB_TUNNEL_ACTIVE` means fully active. `struct tb_tunnel` records bandwidth and DP work state across calls; hardware persistence is managed by `tunnel.c` and lower-level path/adapter helpers.

## Dependencies and Integration Points

The header includes `tb.h` for `struct tb`, `struct tb_port`, `struct tb_path`, route helpers, logging helpers, and Thunderbolt topology functions. It is consumed by the connection manager, XDomain code, tests, and any code that tracks or reacts to tunnel events. Logging macros format endpoint route/port pairs and tunnel type through `tb_*` domain logging functions.

## Risks and Edge Cases

The flexible array means allocation must use the correct `npaths` and all users must respect `tunnel->npaths`. Some fields are protocol-specific but live in the shared struct; callers must use the type predicates and exported APIs rather than assuming fields are meaningful for every tunnel. `tb_tunnel_is_active()` deliberately treats DP activating state as not fully active, while `tb_tunnel_consumed_bandwidth()` in the implementation may still report reserved bandwidth for activating DP tunnels. Logging macros assume non-null source and destination ports and are unsafe for incomplete discovered tunnels unless endpoints are validated first.

## Test Signals

Compile coverage and the `test.c` KUnit suite exercise most allocation contracts. Extra checks should cover state transitions, DP callback semantics, bandwidth API return values for inactive tunnels, logging/event behavior with valid endpoints, and misuse resistance for type-specific fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/tunnel.h -->
