## sources/distributed-fs/moosefs/mfsmaster/matomlserv.h

Purpose: declares the externally visible master-to-metalogger/supervisor service functions. It hides all connection internals and exposes only list, changelog, lifecycle, port, and initialization hooks needed by adjacent master modules.

Important APIs: `matomlserv_mloglist_size` and `matomlserv_mloglist_data` serialize connected metalogger versions/IPs for status clients. `matomlserv_get_min_version` feeds changelog retention. `matomlserv_broadcast_logstring` and `matomlserv_broadcast_logrotate` push live metadata changes and log rotation markers. Lifecycle APIs include `matomlserv_no_more_pending_jobs`, `matomlserv_disconnect_all`, `matomlserv_close_lsock`, and `matomlserv_init`; port helpers return the current control port.

Control flow and integration: `changelog.c` broadcasts through this header, `matoclserv`/status code can list metaloggers, and `metadata.c` uses close/drain helpers during forked store and shutdown. `main` calls the registered callbacks set up by `matomlserv_init`, not declared here directly.

State and persistence behavior: the header owns no state but provides access to runtime connection state and changelog retention requirements. Persistence is indirect: broadcasts mirror changelog content, and supervisor calls can trigger metadata storage in the implementation.

Dependencies: only fixed-width integer types are exposed; protocol structures remain private.

Risks: callers depend on `matomlserv_get_min_version` to avoid deleting changelog history still needed by delayed metaloggers. Misusing broadcast calls before initialization or after disconnect-all would silently drop mirror updates.

Test signals: compile and integration tests should verify changelog broadcasts reach registered metaloggers, delayed metaloggers influence minimum version, and shutdown drains pending output before process exit.
