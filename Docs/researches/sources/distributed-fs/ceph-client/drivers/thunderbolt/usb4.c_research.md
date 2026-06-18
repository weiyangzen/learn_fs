# sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4.c` implements the core USB4-specific Thunderbolt router and adapter helper layer. It wraps USB4 router operations, DROM/NVM access, wake and sleep programming, buffer credit discovery, DisplayPort resource arbitration, USB4 port configuration, sideband access, retimer management, lane margining, USB3 bandwidth allocation, DP bandwidth allocation mode, and PCIe extended encapsulation. The source was read as a complete 3147-line file for this report.

## Important APIs, Types, and Functions

Major router helpers include `usb4_switch_setup`, `usb4_switch_configuration_valid`, `usb4_switch_read_uid`, `usb4_switch_drom_read`, `usb4_switch_set_wake`, `usb4_switch_set_sleep`, `usb4_switch_credits_init`, `usb4_switch_query_dp_resource`, `usb4_switch_alloc_dp_resource`, `usb4_switch_dealloc_dp_resource`, and the router NVM functions `usb4_switch_nvm_sector_size`, `usb4_switch_nvm_read`, `usb4_switch_nvm_write`, `usb4_switch_nvm_authenticate`, and `usb4_switch_nvm_authenticate_status`.

Port-facing APIs include `usb4_switch_add_ports`, `usb4_switch_remove_ports`, `usb4_port_unlock`, `usb4_port_hotplug_enable`, `usb4_port_reset`, `usb4_port_configure`, `usb4_port_unconfigure`, `usb4_port_configure_xdomain`, `usb4_port_unconfigure_xdomain`, `usb4_port_sb_read`, `usb4_port_sb_write`, `usb4_port_router_offline`, `usb4_port_router_online`, `usb4_port_enumerate_retimers`, `usb4_port_clx_supported`, `usb4_port_asym_supported`, `usb4_port_asym_set_link_width`, and `usb4_port_asym_start`.

Retimer and diagnostics APIs are built on sideband transactions: `usb4_port_margining_caps`, `usb4_port_hw_margin`, `usb4_port_sw_margin`, `usb4_port_sw_margin_errors`, `usb4_port_retimer_set_inbound_sbtx`, `usb4_port_retimer_unset_inbound_sbtx`, `usb4_port_retimer_is_last`, `usb4_port_retimer_is_cable`, `usb4_port_retimer_nvm_*`. Adapter bandwidth and protocol helpers include `usb4_usb3_port_max_link_rate`, `usb4_usb3_port_allocated_bandwidth`, `usb4_usb3_port_allocate_bandwidth`, `usb4_usb3_port_release_bandwidth`, `usb4_dp_port_*`, and `usb4_pci_port_set_ext_encapsulation`. Key local machinery is `usb4_native_switch_op`, `__usb4_switch_op`, `usb4_port_wait_for_bit`, `usb4_port_sb_op`, `usb3_bw_to_mbps`, and `mbps_to_usb3_bw`.

## Control Flow

Router operations flow through `__usb4_switch_op`: validate that TX/RX data is at most `USB4_DATA_DWORDS`, optionally proxy through `tb_cm_ops->usb4_switch_op`, then fall back to native config-space operation. The native path writes metadata and TX data to router registers, asserts the operation-valid bit, waits for completion, checks operation-not-supported and status fields, and reads metadata/RX data back.

Router setup starts with capability/config reads, detects whether the upstream link is USB4 or Thunderbolt 3, enables USB3 and PCIe tunneling according to ACPI policy and parent adapter availability, optionally leaves internal xHCI enabled, then `usb4_switch_configuration_valid` sets the configuration-valid bit and waits for completion. Wake and sleep paths program router and port registers and feed wake status into PM core.

NVM and DROM reads use `tb_nvm_read_data` callbacks that translate byte offsets into USB4 operation metadata. NVM writes set the write offset, stream blocks through `tb_nvm_write_data`, and authenticate with special handling for expected disconnect/timeouts during router power cycling. Retimer NVM mirrors this through sideband target operations.

Sideband register access writes command metadata into USB4 port config space, waits for `PND` to clear, maps no-response/response-code bits to Linux errno values, and optionally reads/writes up to 16 data dwords. Higher-level retimer, router-offline, lane-margining, and CLx/asymmetric-link helpers all layer on top of this sideband primitive.

USB3 bandwidth allocation obtains CM ownership with the CMR/HCA handshake, reads consumed and allocated bandwidth registers, converts between scaled USB3 register units and Mb/s, clamps allocations so consumed bandwidth is not removed, and releases to at least 900 Mb/s. DP bandwidth allocation validates USB4 DP-IN support, programs CM ID, group ID, non-reduced link parameters, granularity, estimated/allocated bandwidth, acknowledges DPCD requests, and waits for the DP request bit to clear.

## State and Persistence Behavior

The file persists state through `struct tb_switch` and `struct tb_port` fields such as `link_usb4`, `credit_allocation`, credit limits, `port->usb4`, XDomain link type, `port->bonded`, and adapter-specific maximum bandwidth. Hardware state is persisted in USB4 router, adapter, sideband, retimer, NVM, DP, USB3, and PCIe registers. NVM write/authentication paths modify firmware storage and may power cycle routers or retimers. There is no filesystem persistence.

## Dependencies and Integration Points

The implementation depends on Thunderbolt core types and helpers in `tb.h`, sideband register definitions in `sb_regs.h`, config-space accessors (`tb_sw_read`, `tb_sw_write`, `tb_port_read`, `tb_port_write`), NVM streaming helpers (`tb_nvm_read_data`, `tb_nvm_write_data`), ACPI policy helpers, PM wake APIs, retimer scanning, topology helpers, and DisplayPort/USB3/PCIe adapter register definitions. It is consumed by the Thunderbolt connection manager, tunnel creation logic, retimer/NVM sysfs flows, bandwidth management, XDomain setup, and USB4 port device registration.

## Risks and Edge Cases

The operation wrappers are tightly coupled to register bit layouts and operation completion timing. Incorrect metadata length/offset packing can corrupt NVM or read wrong data. Authentication intentionally treats several transport errors as success because hardware disappears during power cycling; callers must read authentication status before any other router operation. Sideband calls can time out or return `-ENODEV` for missing retimers, and the first inbound SBTX command has a special retry allowance. Bandwidth conversion uses scale selection and rounding; bad values can over- or under-allocate isochronous capacity. Many helpers silently return unsupported for non-USB4 or non-DP-IN ports, so callers need explicit capability checks.

## Test Signals

Useful signals include USB4 router enumeration with USB3/PCIe/DP tunneling enabled and disabled by ACPI policy; suspend/resume wake tests for connect, disconnect, USB4, USB3, PCIe, and DP wake bits; router and retimer NVM read/write/authentication with power-cycle status checks; sideband timeout and missing-retimer coverage; retimer enumeration and offline/online transitions; USB3 bandwidth allocation/release with active isochronous load; DP bandwidth allocation mode request/ack tests; lane bonding/asymmetric width transitions; and kernel build coverage for Thunderbolt with USB4 enabled.
