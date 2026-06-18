<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/core.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/core.c

Purpose: ISA Plug and Play protocol backend. It isolates ISA PnP cards on legacy ports, parses resource streams into PnP cards/devices/options, and implements get/set/disable callbacks through ISA PnP configuration registers.

Important APIs/types/functions: module parameters `isapnp_disable`, `isapnp_rdp`, `isapnp_reset`, and `isapnp_verbose`. Low-level helpers use `_PIDXR`, `_PNPWRP`, read data port, serial isolation key, wake/device/activate/deactivate commands, and `isapnp_cfg_mutex`. Resource parsers cover small/large tags for logical IDs, compatible IDs, IRQ/DMA/IO/memory options, dependent sets, and names. Protocol callbacks are `isapnp_get_resources()`, `isapnp_set_resources()`, and `isapnp_disable_resources()`. Exported legacy APIs include `isapnp_cfg_begin/end`, `isapnp_read_byte/write_byte`, `isapnp_present`, and `isapnp_protocol`.

Control flow: init reserves PnP write/read ports, registers the protocol, isolates cards if no read data port was supplied, builds card/device lists by waking each CSN and parsing resource maps, prints verbose inventory, and initializes proc entries. Isolation cycles through safe read ports, assigns CSNs by serial bitstream checksum, and stops at no more responders. Device resource maps create `pnp_card` and `pnp_dev` objects and register possible resources. Runtime get reads current config registers into resources; set writes configured resources to port/IRQ/DMA/memory registers and activates; disable deactivates the logical device.

State/persistence: hardware state is ISA PnP config registers and assigned CSNs. Software tracks `isapnp_csn_count`, selected RDP, card/device lists, current resources, and active flag. Reset behavior can deactivate all cards during isolation depending on module parameter.

Dependencies/integration: depends on ISA I/O port access, PnP core/card APIs, proc optional support, resource manager, and legacy `linux/isapnp.h`.

Risks: legacy port probing can hang or conflict with devices; code avoids NE2000 ranges but remains hardware-sensitive. Resource parsing trusts firmware byte streams with length checks but continues after unknown tags. `isapnp_set_resources()` notes 32-bit memory is not handled properly. Init failure paths around protocol registration and port reservation are fragile.

Test signals: ISA PnP hardware/emulation with multiple cards, supplied vs auto RDP, reset/no-reset boot parameters, malformed resource streams, get/set/disable logical device, proc reads, and 32-bit memory resource cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/core.c -->
