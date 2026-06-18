# sources/distributed-fs/ceph-client/drivers/thunderbolt/lc.c

## Purpose

`lc.c` implements Thunderbolt link-controller register helpers. It reads LC UUID/fuse data, locates per-port LC register blocks, resets downstream ports, marks ports or XDomain links configured, starts lane initialization after sleep, manages CLx/wake/sleep bits, connects internal xHCI on Thunderbolt 3 routers, arbitrates DisplayPort sink allocation, checks lane bonding, and forces LC power.

## Important APIs, Types, and Functions

Public functions include `tb_lc_read_uuid()`, `tb_lc_reset_port()`, `tb_lc_configure_port()`, `tb_lc_unconfigure_port()`, `tb_lc_configure_xdomain()`, `tb_lc_unconfigure_xdomain()`, `tb_lc_start_lane_initialization()`, `tb_lc_is_clx_supported()`, `tb_lc_is_usb_plugged()`, `tb_lc_is_xhci_connected()`, `tb_lc_xhci_connect()`, `tb_lc_xhci_disconnect()`, `tb_lc_set_wake()`, `tb_lc_set_sleep()`, `tb_lc_lane_bonding_possible()`, `tb_lc_dp_sink_query()`, `tb_lc_dp_sink_alloc()`, `tb_lc_dp_sink_dealloc()`, and `tb_lc_force_power()`.

Internal helpers `read_lc_desc()` and `find_port_lc_cap()` decode the LC descriptor to compute the base offset for a physical port. `tb_lc_set_port_configured()`, `tb_lc_set_xdomain_configured()`, `__tb_lc_xhci_connect()`, `tb_lc_set_wake_one()`, `tb_lc_dp_sink_from_port()`, and `tb_lc_dp_sink_available()` implement shared register updates.

## Control Flow

Most operations first reject unsupported generations or missing LC capability, then compute a per-port LC offset from `TB_LC_DESC`. The code maps logical lane adapter numbers to physical port numbers with `tb_phy_port_from_link()` and selects lane-specific bits based on odd/even port number.

Port reset sets the downstream port reset bit, sleeps for 10 ms, rereads mode, clears the bit, and writes it back. Port/XDomain configuration toggles lane configured bits and upstream bit where appropriate. Lane initialization sets the SLI bit for non-root generation 2+ switches after resume.

Wake/sleep operations iterate over all link-controller instances described by the LC descriptor and update `TB_LC_SX_CTRL` bits. Wake flags map to connect, USB4, PCIe, and DP wake bits. Sleep sets the sleep bit for every LC.

DisplayPort sink functions map the first DP IN port to sink 0 and the second to sink 1. They query allocation state, require availability or CM ownership, set allocation to CM on alloc, and clear it on dealloc for generation 3+ hardware.

## State and Persistence Behavior

The file stores no long-lived kernel state. It mutates LC hardware registers that affect link power management, reset state, wake behavior, lane initialization, internal xHCI routing, DP sink ownership, and forced power. These settings persist in hardware until changed, reset, or power-managed by firmware/hardware.

Functions that return booleans generally collapse read errors and unsupported hardware to `false`, which makes callers treat unavailable LC state as unsupported or not connected.

## Dependencies and Integration Points

The file depends on `tb_sw_read/write()`, switch/port helpers from `tb.h`, LC register definitions, generation checks, route checks, DP/USB/PCIe port type helpers, and wake flag definitions. It is used by switch setup, tunnel management, DisplayPort allocation, power management, USB3/xHCI handling, and NVM authentication force-power flows.

## Risks and Edge Cases

LC descriptor fields are trusted when computing per-port offsets. Corrupt or unexpected descriptors can point reads/writes at wrong config offsets. Several void functions ignore failures from their internal setters, so cleanup paths may silently leave LC state configured.

`tb_lc_dp_sink_query()` returns `!tb_lc_dp_sink_available()`: because availability returns `0` when available and negative otherwise, this maps any error to `false`, but also makes the logic easy to misread.

DP sink ownership treats allocation values `0` and CM-owned as available. If firmware or BIOS uses other ownership values, allocation correctly returns `-EBUSY`, but deallocation also requires the same availability check and may refuse to clear a sink not considered CM-owned.

Generation gating is conservative. Some operations return success without doing anything on older generations, so callers must not interpret success as proof that hardware state changed.

## Test Signals

Tests should cover LC descriptor parsing, per-port offset calculation for odd/even lanes, generation gating, downstream port reset sequencing, configured/unconfigured port bits, XDomain bits, lane initialization on resumed devices, CLx support reads, USB plugged/xHCI connected checks, xHCI connect/disconnect, wake flag combinations, sleep over multiple LCs, lane bonding checks, DP sink query/alloc/dealloc ownership values, force power, and read/write error propagation versus boolean collapse.
