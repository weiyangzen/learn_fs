<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thunderbolt.h -->
# sources/distributed-fs/ceph-client/include/linux/thunderbolt.h

## Purpose
declares the Thunderbolt/USB4 service API, domain and XDomain structures, property-directory helpers, service-driver binding, NHI/ring DMA structures, and ring enqueue/poll interfaces.

## Important APIs, Types, and Functions
The file is 699 lines and exports these visible symbol families: types/enums `fwnode_handle`, `device`, `tb_cfg_pkg_type`, `tb_security_level`, `tb`, `tb_property_dir`, `tb_property_type`, `tb_property`, `tb_link_width`, `tb_xdomain`, `tb_protocol_handler`, `tb_service`, `tb_service_driver`, `tb_nhi`, and 3 more; macros/constants `THUNDERBOLT_H_`, `TB_LINKS_PER_PHY_PORT`, `TB_PROPERTY_KEY_SIZE`, `RING_FLAG_NO_SUSPEND`, `RING_FLAG_FRAME`, `RING_FLAG_E2E`, `TB_FRAME_SIZE`; function-like macros `tb_property_for_each`, `TB_SERVICE`; inline helpers `tb_phy_port_from_link`, `tb_xdomain_disable_all_paths`, `tb_xdomain_find_by_uuid_locked`, `tb_xdomain_find_by_route_locked`, `tb_xdomain_put`, `tb_is_xdomain`, `tb_service_put`, `tb_is_service`, `tb_service_set_drvdata`, `tb_ring_rx`, `tb_ring_tx`, `usb4_usb3_port_match`; external prototypes `tb_property_format_dir`, `tb_property_free_dir`, `tb_property_add_immediate`, `tb_property_add_data`, `tb_property_add_text`, `tb_property_add_dir`, `tb_property_remove`, `tb_register_property_dir`, `tb_unregister_property_dir`, `tb_xdomain_lane_bonding_enable`, `tb_xdomain_lane_bonding_disable`, `tb_xdomain_alloc_in_hopid`, `tb_xdomain_release_in_hopid`, `tb_xdomain_alloc_out_hopid`, and 22 more.

## Control Flow
A Thunderbolt domain owns a root switch, control channel, workqueue, security level, and connection-manager ops. XDomain discovery exchanges property blocks, allocates hop IDs, enables paths, and creates service devices. Service drivers match with `TB_SERVICE`. NHI ring users allocate TX/RX rings, start them, enqueue `ring_frame` DMA buffers, receive callbacks or poll completions, then stop/free rings.

## State and Persistence Behavior
`tb`, `tb_xdomain`, `tb_service`, `tb_nhi`, and `tb_ring` carry substantial runtime state: devices, locks, work items, property generations, ID allocators, path/ring queues, DMA descriptors, interrupt vectors, link width/speed, unplug state, and debugfs pointers.

## Dependencies and Integration Points
It depends on the device model, IDA/IDR, list/mutex/workqueue, PCI, UUID, module device tables, DMA mapping, and CONFIG_USB4. The only always-available helper is USB4/USB3 port matching, stubbed to false without USB4. Direct includes are `linux/types.h`, `linux/device.h`, `linux/idr.h`, `linux/list.h`, `linux/mutex.h`, `linux/mod_devicetable.h`, `linux/pci.h`, `linux/uuid.h`, `linux/workqueue.h`.

## Risks and Edge Cases
External hotplug, DMA rings, and security levels make lifetime and authorization critical. Service properties can change asynchronously, ring buffers require correct DMA mapping and stop cancellation, and lock ordering between NHI and ring locks is documented in the structs.

## Test Signals
Build CONFIG_USB4 on/off, run Thunderbolt/USB4 hotplug and authorization tests, validate XDomain property parsing/formatting, service driver probe/remove, lane bonding and path allocation, ring TX/RX cancellation, polling, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thunderbolt.h -->
