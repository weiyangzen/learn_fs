<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/intel_pmc_mux.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/intel_pmc_mux.c

## Purpose

`intel_pmc_mux.c` exposes Intel PMC firmware-controlled USB Type-C routing as Type-C switch, mux, and USB role-switch devices. It sends PMC USBC IPC commands for connect, disconnect, safe mode, DisplayPort, Thunderbolt, USB4, and DP HPD routing and reads IOM port status through ACPI-discovered MMIO.

## Important APIs, Types, and Functions

State is in `struct pmc_usb` and per-port `struct pmc_usb_port`. Key functions include `pmc_usb_send_command()`, `pmc_usb_command()`, `update_port_status()`, `pmc_usb_connect()`, `pmc_usb_disconnect()`, `pmc_usb_mux_safe_state()`, `pmc_usb_mux_dp()`, `pmc_usb_mux_dp_hpd()`, `pmc_usb_mux_tbt()`, `pmc_usb_mux_usb4()`, `pmc_usb_mux_set()`, `pmc_usb_set_orientation()`, `pmc_usb_set_role()`, `pmc_usb_register_port()`, `pmc_usb_probe_iom()`, and debugfs status support.

## Control Flow

Probe counts child ACPI/fwnode port nodes, limits to four ports, obtains Intel SCU IPC, discovers an IOM ACPI device and maps its port-status MMIO, creates debugfs, and registers switch/mux/role-switch devices for each child using `usb2-port-number`, `usb3-port-number`, and optional orientation overrides. Role-switch calls connect or disconnect. Mux calls refresh IOM status, skip work if orientation/role is absent, send safe/USB/DP/TBT/USB4 commands according to mode and altmode SVID, and handle DP HPD updates when already in DP mode. Commands retry PMC busy responses up to three times.

## State and Persistence Behavior

The driver caches per-port orientation, role, port numbers, optional SBU/HSL orientation overrides, and last IOM status. The authoritative routing state lives in PMC firmware/IOM and is queried through MMIO. Debugfs exposes current `iom_status`. No state is persisted by the driver.

## Dependencies and Integration Points

Dependencies include ACPI, Intel SCU IPC, USB role-switch, Type-C mux/switch, DP/TBT/USB4 data structures, debugfs, USB debug root, and IOM ACPI IDs for several Intel platforms. It integrates firmware-controlled routing with generic Type-C class consumers.

## Risks and Test Signals

Risks include subtle platform-specific bit packing, incorrect active/retimer cable flags for TBT/USB4, an apparent `||`/`&&` logic hazard in USB4 retimer-cable ACPI ID checks, role stored after command even if connect/disconnect failed, unregister loops that may touch unregistered devices on partial probe failure, and stale status if IOM layout data is wrong. Test signals include ACPI child parsing, Tiger/Alder/Meteor/Lunar IOM offsets, role swaps causing disconnect/reconnect, safe-state no-op conditions, DP HPD level/IRQ sequencing, TBT and USB4 cable-type permutations, PMC busy retry behavior, and debugfs `iom_status`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/intel_pmc_mux.c -->
