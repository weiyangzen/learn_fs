# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_hw.c

Purpose: Implements the main firmware command ABI for Prestera switch functionality and event parsing. It is the central hardware abstraction used by switch setup, ports, VLAN/FDB, bridge, ACL/vTCAM, counters, SPAN, router, LAG, policer, RX/TX, flood-domain, and MDB code.

Important APIs/types/functions: Command enum `prestera_cmd_type_t`, many packed firmware request/response structs, `prestera_hw_build_tests()` ABI size assertions, command wrappers `prestera_cmd_ret[_wait]()`/`prestera_cmd()`, event parsers and handler registry, plus exported `prestera_hw_*` functions declared in `prestera_hw.h`.

Control flow: Public helpers fill little-endian firmware messages, call `prestera_cmd*()` through `sw->dev->send_req`, validate ACK/status in `__prestera_cmd_ret()`, and decode response fields. Switch init initializes the event handler list, performs firmware switch init, installs RX message callbacks, and stores switch capabilities. Firmware event receive decodes event type/id, parses port/FDB payloads, finds a registered handler under RCU, and invokes it.

State and persistence: Maintains runtime firmware-facing switch attributes (`port_count`, MTU limits, switch id, LAG limits, nexthop table size), event handler list, and hardware object IDs returned by firmware (bridges, vTCAMs, rules, counters, SPAN IDs, RIFs, VRs, nexthop groups, flood domains). No durable persistence beyond firmware state and in-memory driver structures.

Dependencies/integration: Depends on `prestera_device->send_req` supplied by PCI transport, central Prestera structs, ACL action definitions, router HW types, counter stats, netdev/LAG helpers, and Linux endian/ethernet helpers. It is called by nearly every higher-level Prestera module.

Risks: This file is firmware ABI-sensitive: struct sizes, endian conversions, command IDs, and response lengths must match firmware. `prestera_hw_nhgrp_blk_get()` uses a static response buffer, which is not reentrant. Dynamic message sizing for vTCAM rules/counters/flood ports must match firmware expectations. Event handler lookup supports one handler per event type and uses RCU copying semantics. Several helpers return generic `-EINVAL` for firmware failure, limiting diagnostics.

Test signals: Build-time `BUILD_BUG_ON` layout checks, full probe/switch init, firmware command timeout/failure injection, port config/stat operations, VLAN/FDB/bridge operations, ACL rule add/delete with multiple actions, counter block read/trigger/clear, router LPM/NH/RIF/VR operations, SPAN/mirror, LAG membership and FDB, flood-domain/MDB programming, and port/FDB event delivery.
