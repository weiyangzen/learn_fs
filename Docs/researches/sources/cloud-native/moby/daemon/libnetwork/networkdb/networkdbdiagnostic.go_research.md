## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdbdiagnostic.go

Purpose: HTTP diagnostic/control surface for NetworkDB, wiring debug endpoints that join clusters, inspect peers, mutate entries, query tables, join/leave networks, and report per-network stats.

Important APIs/types/functions: `Mux` abstracts `HandleFunc`; `RegisterDiagnosticHandlers` registers `/join`, `/networkpeers`, `/clusterpeers`, `/joinnetwork`, `/leavenetwork`, `/createentry`, `/updateentry`, `/deleteentry`, `/getentry`, `/gettable`, and `/networkstats`. Handler methods call core NetworkDB APIs and return `diagnostic` response objects.

Control flow: each handler parses form parameters, logs an audit entry with remote address, caller method, and URL, validates required parameters, performs a NetworkDB operation, and replies through `diagnostic.HTTPReply`. Create/update/get/table handlers optionally base64-decode or encode values unless unsafe mode is requested by diagnostic options.

State and persistence behavior: handlers mutate live NetworkDB state through `Join`, `JoinNetwork`, `LeaveNetwork`, `CreateEntry`, `UpdateEntry`, and `DeleteEntry`. They do not persist data themselves; changes propagate through normal NetworkDB gossip and table state. Stats read `thisNodeNetworks` under read lock and report entry count plus table broadcast queue length.

Dependencies and integration points: integrates `net/http`, `containerd/log`, `daemon/libnetwork/diagnostic`, and `internal/caller`. This file is likely mounted into Docker's debug diagnostics server, so it bridges operator commands into cluster control paths.

Risks: diagnostic endpoints can mutate cluster state, so exposure must be tightly controlled by the surrounding diagnostic server. Unsafe mode may return or accept raw string values; default base64 mode is safer for arbitrary bytes. Input validation only checks presence, not semantic correctness beyond downstream NetworkDB errors.

Test signals: no direct tests in this subset. Coverage is indirect through core NetworkDB API tests, but HTTP parameter parsing, base64 behavior, and diagnostic response formatting would benefit from focused handler tests.
