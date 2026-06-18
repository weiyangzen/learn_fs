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
