# sources/distributed-fs/ceph-client/drivers/thunderbolt/tb.h

## Purpose
`tb.h` is the central private interface for the Thunderbolt/USB4 driver. It defines the kernel-side object model for domains, routers, adapters, USB4 port devices, retimers, NVM images, paths, bandwidth groups, and connection-manager callbacks. It also declares most cross-file helper APIs used by the software connection manager, ICM firmware manager, switch/port code, USB4 router operations, retimer/NVM code, XDomain support, ACPI integration, and debugfs.

In USB4 terminology, `struct tb_switch` represents a router and `struct tb_port` represents an adapter or lane adapter. The header preserves Thunderbolt naming for existing driver code while documenting the USB4 mapping.

## Important APIs, Types, and Functions
- Quirk bits `QUIRK_FORCE_POWER_LINK_CONTROLLER`, `QUIRK_NO_CLX`, and `QUIRK_KEEP_POWER_IN_DP_REDRIVE` describe router-specific behavior needed by power, CLx, and redrive handling.
- `struct tb_nvm` and `enum tb_nvm_write_ops` model active/non-active NVM partitions, buffered writes, authentication state, and vendor operations.
- `enum tb_switch_tmu_mode` and `struct tb_switch_tmu` describe router Time Management Unit modes and requested/current state.
- `struct tb_switch` stores device identity, configuration-space header, ports, DMA/NVM/TMU/CLx state, topology fields, authorization/security state, runtime-PM fields, link parameters, credit preferences, quirks, and debugfs state.
- `struct tb_bandwidth_group` stores a group ID, member DP IN ports, temporary reserved bandwidth, and delayed release work.
- `struct tb_port` stores cached port registers, owning switch, remote router link, XDomain link, capability offsets, USB4 port device, lane-bonding data, HopID allocators, list nodes, credit state, DP bandwidth group state, maximum bandwidth, and redrive state.
- `struct usb4_port` and `struct tb_retimer` define child devices for USB4 lane adapters and retimers.
- `struct tb_path_hop`, `enum tb_path_port`, and `struct tb_path` define hop programming and unidirectional path state for protocol tunnels.
- `struct tb_cm_ops` is the connection-manager vtable used by the domain core to abstract software CM and firmware ICM behavior.
- Inline helpers such as `tb_priv()`, `tb_upstream_port()`, `tb_is_upstream_port()`, `tb_route()`, `tb_port_at()`, `tb_width_name()`, `tb_port_has_remote()`, type predicates, `tb_sw_read()`, `tb_sw_write()`, `tb_port_read()`, `tb_port_write()`, `tb_switch_parent()`, `tb_switch_downstream_port()`, `tb_route_length()`, and `tb_downstream_route()` centralize common topology and config-space operations.
- Iteration macros `tb_switch_for_each_port()`, `tb_for_each_port_on_path()`, `tb_for_each_upstream_port_on_path()`, and `tb_path_for_each_hop()` encode traversal contracts.

## Control Flow
`tb.h` itself has no runtime control flow, but it defines the contracts used by every runtime path. Domain allocation installs a `struct tb_cm_ops`; the domain core then calls connection-manager callbacks for start/stop, suspend/resume, runtime PM, events, authorization, PCIe disapproval, XDomain path approval, and USB4 router operation proxying. The software CM in `tb.c` fills this table with `tb_start()`, `tb_stop()`, `tb_handle_event()`, tunnel approval functions, and power hooks.

Topology traversal relies on route encoding. `tb_route()` combines `route_hi` and `route_lo` from the cached switch header. `tb_port_at()` extracts the port number for a switch depth from a route and returns the corresponding `struct tb_port`. `tb_downstream_route()` appends a downstream port number at the current switch depth. These helpers are used during scanning, event routing, XDomain setup, and path construction.

Config-space access is wrapped by `tb_sw_read()`, `tb_sw_write()`, `tb_port_read()`, and `tb_port_write()`. These helpers check `sw->is_unplugged` before issuing control-channel reads/writes, reducing the chance that removal paths continue touching gone hardware.

Path and tunnel code uses `struct tb_path` and `struct tb_path_hop` to program hop entries from ingress adapters to egress adapters. Higher-level tunnel constructors in `tunnel.h` build protocol-specific collections of paths using the port and path helper APIs declared here.

## State and Persistence Behavior
Most persistent in-memory Thunderbolt state is represented by structures in this header. `struct tb_switch` persists router identity, topology, link state, authorization, NVM pointers, runtime-PM support, and capability offsets for as long as the device is registered. `struct tb_port` persists adapter state and is embedded in the owning switch's `ports` array. `struct tb_path` persists programmed tunnel path state until deactivated and freed. `struct tb_nvm` persists buffered firmware update state until NVM cleanup.

The header also encodes state ownership expectations. `struct tb_nvm` documentation states that users must serialize concurrent access. Switch add/remove operations require the domain lock when modifying other switches. HopID allocators belong to ports. DP bandwidth group membership is stored on DP IN ports and in group lists. Runtime-PM completions and ICM connection identifiers are stored in `struct tb_switch` for firmware-managed domains.

No disk persistence is implemented here. NVM operations declared here write to device flash through other source files; this header defines the in-memory buffers, sizes, authentication flags, and APIs.

## Dependencies and Integration Points
The header includes Linux debugfs, nvmem, PCI, Thunderbolt UAPI, UUID, bitfield, and local `tb_regs.h`, `ctl.h`, and `dma_port.h`. It exposes a broad internal API surface to many driver compilation units: domain lifecycle, switch/port config, path programming, DROM, link controller, USB4 router operations, USB4 sideband/margining, retimer NVM, USB3/DP bandwidth, PCIe encapsulation, ACPI policy, debugfs, and quirks.

`tb_regs.h` supplies the packed register/config-space structures used inside `struct tb_switch`, `struct tb_port`, and register helper prototypes. `tb_msgs.h` is indirectly related through `ctl.h` and the control-channel event and config-space packet APIs.

## Risks
- Many packed register structures and bitfields are exposed through cached config headers. ABI drift with hardware specs can silently break topology parsing.
- `tb_port_at()` warns and returns NULL if the encoded port exceeds `max_port_number`; callers must handle NULL in hotplug/XDomain paths.
- Inline config-space helpers only guard `is_unplugged`; they do not serialize access. Callers must use domain locks and runtime-PM references appropriately.
- Several structures expose raw pointers and embedded list nodes. Ownership is implicit and cross-file, making double removal, stale pointers, or list corruption possible if contracts are violated.
- The broad prototype surface makes layering loose. Changes to router, port, USB4, XDomain, retimer, NVM, or tunnel behavior can affect `tb.c` without compiler-visible semantic checks.
- ACPI and debugfs fallback inline stubs change behavior depending on Kconfig, so tests need coverage with and without `CONFIG_ACPI` and `CONFIG_DEBUG_FS`.

## Test Signals
Compile coverage is a major signal because this header is included across the Thunderbolt driver. Runtime tests should validate route encoding/decoding, port type predicates, parent/downstream-port helpers, config-space read/write rejection after unplug, switch generation/vendor predicates, TMU and CLx state helpers, path iteration over multi-hop topologies, USB4 version detection, and ACPI/debugfs stub behavior under different configurations.

For integration, hotplug, suspend/resume, NVM update, retimer scan, USB4 sideband access, DP bandwidth allocation, PCIe tunneling, USB3 bandwidth allocation, XDomain DMA paths, and debugfs registration all exercise contracts declared here.
