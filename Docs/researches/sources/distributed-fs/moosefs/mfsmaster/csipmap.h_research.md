# sources/distributed-fs/moosefs/mfsmaster/csipmap.h

Purpose: declares the small public API for chunkserver IP mapping. This is the low-level mapping layer used by the master multilan subsystem to convert a server IP into a client-specific reachable IP.

Important APIs/types/functions: `csipmap_map(servip, clientip)` returns a mapped destination IP or zero when no map applies. `csipmap_loadmap(fname)` reloads the external mapping file. `csipmap_term()` frees active mapping state. `csipmap_init()` initializes empty state.

Control flow: callers initialize once, load or reload a named mapping file when configuration is read, call `csipmap_map()` during server address serialization, and call `csipmap_term()` on shutdown. A zero return is not an error; it means the caller should keep the original address or fall through to another mapping strategy.

State/persistence: all state is internal to `csipmap.c` and in-memory. The mapping file is external configuration and is not written through this API.

Dependencies/integration: only includes fixed-width integer types. The main integration point is `multilan.c`, which wraps this API and exposes `multilan_map()` to chunkserver-list and chunk-location serialization code.

Risks/test signals: because zero is a valid sentinel rather than a status code, callers must not treat `0.0.0.0` as a usable mapped address. Tests should cover init/load/map/term sequencing, no-map fallback behavior, and reload preserving prior maps after errors.
