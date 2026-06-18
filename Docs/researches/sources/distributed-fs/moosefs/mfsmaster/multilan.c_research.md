## sources/distributed-fs/moosefs/mfsmaster/multilan.c

Purpose: maps chunkserver addresses to client-appropriate LAN addresses in multi-homed deployments. It supports explicit source/client mappings through `csipmap` and class-based address rewriting through `MULTILAN_BITS`/`MULTILAN_CLASSES`.

Important APIs and types: global config state includes `MultiLanMask`, number of classes, and `MultiLanClassTab`. `multilan_map(servip, clientip)` first tries `csipmap_map`, then rewrites the network bits of `servip` to match `clientip` if both belong to configured classes. `multilan_match(servip, iptab, iptablen)` chooses a matching alternate IP from a server IP table. `multilan_parse_netlist` parses class lists. `multilan_reload` loads config and the optional IP map file. `multilan_init` initializes `csipmap` and registers reload/destruct.

Control flow: reload enables class rewriting only if both `MULTILAN_BITS` and `MULTILAN_CLASSES` are defined and valid. Parse errors log warnings and preserve/clear state according to the branch. If class config is absent, class mapping is disabled. The explicit IP map file is loaded on every reload from `MULTILAN_IPMAP_FILENAME` or default path.

State and persistence behavior: all state is in memory and derived from config files. No metadata is written. `multilan_term` frees class state and terminates `csipmap`.

Dependencies and integration points: depends on `cfg`, `main`, `mfslog`, `massert`, `csipmap`, and `MFSCommunication` defaults. `matocsserv_get_csdata` calls `multilan_map` before returning chunkserver addresses to clients.

Risks: address parsing is permissive about shortened classes but rejects garbage bits outside the common mask. Class-based rewrite can create unreachable addresses if LANs are not symmetric. `multilan_match` returns the original address when more than one candidate matches, treating ambiguity as an error case.

Test signals: test explicit map precedence, no-client-ip fallback, absent config, invalid bit counts/classes, class rewrite when both networks are known, no rewrite when either side is unknown, ambiguous `multilan_match`, and reload/destruct memory behavior.
