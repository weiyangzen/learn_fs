<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.h

Purpose: defines CIFS debug logging macros, severity/category bits, and declarations for memory, SMB packet, and MID dump helpers.

Important APIs and symbols: declares `cifs_dump_mem()`, `cifs_dump_mids()`, `dump_smb()`, `traceSMB`, and `cifsFYI`. Logging bits include `CIFS_INFO`, `CIFS_RC`, `CIFS_TIMER`, category constants `VFS`, `FYI`, `NOISY`, and `ONCE`. Macros include `cifs_info()`, `cifs_dbg()`, `cifs_server_dbg()`, and `cifs_tcon_dbg()`.

Control flow: when `CONFIG_CIFS_DEBUG` is enabled, macros route VFS messages to ratelimited `pr_err`, FYI messages to `pr_debug` only when `cifsFYI & CIFS_INFO`, and optional noisy messages under `CONFIG_CIFS_DEBUG2`. Server macros lock `server->srv_lock` around hostname access. Tcon macros prefix tree names when available. When debug is disabled, macros compile references in dead `if (0)` blocks to preserve type checking but emit nothing except `cifs_info()`.

State and persistence: reads global debug controls but owns no storage.

Dependencies and integration: depends on Linux printk/pr_debug variants, CIFS server/tcon structures at macro expansion sites, and procfs controls implemented in `cifs_debug.c`.

Risks: macros evaluate parameters in contexts that may hold locks; adding expensive expressions can still matter in enabled builds. `cifs_server_dbg()` assumes a variable named `server` is in scope, and `cifs_tcon_dbg()` assumes `tcon`, making call-site naming part of the API.

Test signals: compile with `CONFIG_CIFS_DEBUG` off/on and `CONFIG_CIFS_DEBUG2`; verify no unused-variable fallout; toggle `cifsFYI`; check ONCE/rate-limited behavior; and run lockdep around server debug logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.h -->
