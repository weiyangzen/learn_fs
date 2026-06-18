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
