# sources/distributed-fs/eos/mgm/proc/user/Map.cc

Purpose: implements legacy path map administration through `ProcCommand::Map()`. It lists, adds, and removes namespace path mappings.

Important APIs and types: uses `mSubCmd`, `pOpaque` keys `mgm.map.src` and `mgm.map.dest`, `gOFS->PathMap`, `PathMapMutex`, and `mConfigEngine` `SetConfigValue`/`DeleteConfigValue`.

Control flow: `ls` takes a read lock and formats all mapping pairs. `link` checks root/admin identity, validates source and destination syntax, rejects duplicate sources, adds the map entry, and persists it to config. `unlink` checks root/admin identity, takes a write lock, validates existence, removes the map entry, and deletes the config value.

State and persistence: mutates in-memory `PathMap` and persistent config namespace `map`. Listing is read-only.

Dependencies and integration: path mapping feeds the broader proc namespace mapping macros used by many handlers in this folder.

Risks: `link` writes `PathMap` without taking `PathMapMutex`, while `ls` and `unlink` lock, so concurrent mutation may race. Validation is string-based and intentionally strict about slashes, spaces, backslashes, and dot segments. Tests should cover admin authorization, invalid path forms, duplicate link, unlink missing path, persistence calls, and concurrent link/list behavior.
