# sources/distributed-fs/orangefs/src/common/misc/pint-cached-config.h

Purpose: Declares the cached configuration API for mapping OrangeFS filesystem configuration data into fast lookup services. It is the public interface for server arrays, handle routing, server typing, filesystem root metadata, and layout-aware datafile selection.

Important APIs and constants: `PINT_SERVER_TYPE_IO`, `PINT_SERVER_TYPE_META`, and `PINT_SERVER_TYPE_ALL` mirror management server flags. The API exposes lifecycle, load/reinitialize, alias/address mapping, role-specific server counts and arrays, handle-to-server mapping, datafile count calculation, root handle and handle timeout retrieval, server name/list retrieval, and IO server name listing.

Control flow and integration: Callers initialize the cache, load each parsed `filesystem_configuration_s` together with the owning `server_configuration_s`, then use lookup methods during request routing, datafile creation, management queries, and client system-interface setup. Several functions return borrowed pointers to cached or configuration-owned arrays; callers must not free or retain them beyond config cache lifetime unless explicitly documented.

State and persistence behavior: The header describes an in-memory cache only. It depends on stable parsed server configuration and BMI address mappings. Reinitialization refreshes all cached entries from a server configuration object.

Dependencies and risks: Includes PVFS internal/storage/management types, BMI, TROVE, and server config types. The API mixes borrowed-output semantics, caller-owned arrays, and allocated string-list outputs, so misuse can produce leaks or dangling pointers. Test signals include compile coverage of all users and lifecycle tests that validate no stale pointers remain after reinitialize/finalize.
