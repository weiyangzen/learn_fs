# sources/distributed-fs/ceph-client/drivers/firewire/core-topology.c

### Purpose
`core-topology.c` turns self-ID packets from each bus reset into an in-memory FireWire node tree, compares new and old topologies, reports node lifecycle events, updates bus-manager inputs, and maintains the local topology map CSR payload.

### Important APIs, Types, And Functions
Exports are `fw_core_handle_bus_reset()` and `fw_destroy_nodes()`. Important helpers include `fw_node_create()`, `update_hop_count()`, `build_tree()`, `for_each_fw_node()`, `report_lost_node()`, `report_found_node()`, `move_tree()`, `update_tree()`, and `update_topology_map()`. The file operates on `struct fw_node` from `core.h` and card fields such as `local_node`, `root_node`, `irm_node`, `gap_count`, `beta_repeaters_present`, `color`, and `topology_map`.

### Control Flow, State, And Persistence
On bus reset, `fw_core_handle_bus_reset()` verifies generation continuity, destroys old nodes if needed, updates card generation/node/reset/bus-manager fields, then calls `build_tree()` under `card->lock`. `build_tree()` enumerates self-ID sequences, validates PHY IDs, parent/child counts, extended self-ID consistency, constructs nodes bottom-up from a stack, identifies local/root/IRM nodes, detects beta repeaters and gap-count mismatch, and computes max depth/hops. For first topology, `for_each_fw_node()` reports every node as created. For subsequent compatible topologies, `update_tree()` walks old and new trees in parallel, emits updated/link on/link off/initiated reset events, moves newly found subtrees into the persistent tree, and reports lost subtrees. After releasing the card lock, bus-manager work is scheduled and the topology map buffer is regenerated under its own lock.

### Dependencies, Integration Points, Risks, And Test Signals
The topology layer depends on PHY/self-ID decoding helpers, `fw_node_event()` from `core-device.c`, bus-manager work from `core-card.c`, transaction CSR topology map reads, krefs, and tracepoints. Risks include malformed self-ID sequences causing NULL topology, stack underflow, parent-count inconsistencies, color reuse bugs during graph traversal, generation discontinuity requiring full destruction, and `card->root_node` assumptions after a failed build. Test signals include self-ID sequence helper KUnit coverage, bus reset traces, create/update/destroy event ordering, link-on/link-off transitions, root and IRM detection, gap mismatch forcing bus-manager reset logic, beta repeater detection, and topology map CRC/generation changes.
