# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-peer-utils.h

Purpose: Declares the public peer utility surface used by glusterd management code. It exposes peer lookup, lifecycle, address-list management, serialization, and peer-count helpers while keeping implementation details in `glusterd-peer-utils.c`.

Important APIs and types: The header forward-depends on `glusterd.h` for `glusterd_peerinfo_t`, `glusterd_peer_hostname_t`, `glusterd_volinfo_t`, and friend-state types. It declares cleanup/creation APIs, hostname and uuid lookups, peer-state predicates, address helpers, dict add/update/from-dict helpers, `gd_add_peer_detail_to_dict()`, generation lookup, and `glusterd_get_peers_count()`.

Control flow: There is no executable code in the header. It defines the callable interface by which peer FSM code, CLI handlers, brick validation, and management operations locate peers, check their connection state, and marshal peer metadata into dictionaries.

State and persistence: The header owns no state. It exposes functions that operate on the RCU-protected peer list in `glusterd_conf_t` and on persisted peer-store entries indirectly through cleanup/deserialization helpers.

Dependencies and integration points: Included by source files that need peer metadata access, including replace/reset brick validation and peer CLI/status paths. The dictionary helpers provide the data contract for peer exchange across management RPCs and CLI responses.

Risks: Callers must understand the RCU lifetime expectations of returned `glusterd_peerinfo_t *` pointers. The declared functions mix ownership styles: some return duplicated strings that callers must free, while lookup helpers return internal peer pointers.

Test signals: Build coverage of prototypes, peer add/remove/status operations, dictionary round-trips, and remote brick validation paths validate this header contract.
