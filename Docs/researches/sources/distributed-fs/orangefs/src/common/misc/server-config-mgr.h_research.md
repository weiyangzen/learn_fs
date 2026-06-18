# sources/distributed-fs/orangefs/src/common/misc/server-config-mgr.h

Purpose: Declares the server-configuration manager API and maps config access differently for client and server builds.

Important APIs and definitions: Declares manager lifecycle, reload, add/remove, locked get/put, and minimum handle-recycle-time query functions. For `__PVFS2_CLIENT__`, `PINT_server_config_mgr_get_config` and `put_config` map to the manager implementations. For `__PVFS2_SERVER__`, get maps to `PINT_get_server_config()`, put is an inline no-op, and `PINT_server_config_mgr_set_config` maps to `PINT_set_server_config`.

Control flow: Header control flow is preprocessor selection by build role. Client code gets mutex-protected fsid lookup; server code bypasses fsid lookup and uses the process server config.

State and persistence: No state is stored here. It defines ownership and synchronization contracts for implementation-held or server-global config state.

Dependencies and integration points: Includes `pvfs2-internal.h` and `server-config.h`; server builds include `config-utils.h`. This header is the abstraction boundary for modules that need configuration without hard-coding client vs server storage.

Risks: If neither `__PVFS2_CLIENT__` nor `__PVFS2_SERVER__` is defined, callers see only the underscored functions and may miss the generic macros. The server put inline ignores its parameter and returns from a void function expression, which is harmless but stylistically odd. Client callers must understand that get may hold a mutex until put.

Test signals: Compile in client, server, and neutral build configurations; verify macro expansion in callers; test client get/put pairing and server get/set behavior; ensure modules do not mix underscored and macro APIs inconsistently.
