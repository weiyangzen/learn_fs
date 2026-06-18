<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.c

Purpose: implements CIFS debug/procfs reporting and runtime toggles for `/proc/fs/cifs`, plus low-level dump helpers used by error paths.

Important APIs: exported or externally used functions include `cifs_dump_mem()`, `cifs_dump_mids()`, `cifs_proc_init()`, and `cifs_proc_clean()`. Proc show/write handlers cover `DebugData`, `open_files`, `open_dirs`, `Stats`, `cifsFYI`, `traceSMB`, `LinuxExtensionsEnabled`, `SecurityFlags`, `LookupCacheEnabled`, `mount_params`, optional DFS cache, and SMB Direct tunables.

Control flow: proc initialization creates entries under `fs/cifs`. Show handlers use `seq_file` to walk global server/session/tcon lists under `cifs_tcp_ses_lock` and finer-grained locks. DebugData prints feature flags, server/channel/session/share/interface/MID state, compression/encryption status, and witness registrations. Stats write resets counters when a boolean is accepted. SecurityFlags write parses booleans or numeric flags, validates against `CIFSSEC_MASK`, normalizes MUST flags, and updates `global_secflags`.

State and persistence: proc writes mutate global module state (`cifsFYI`, `traceSMB`, `linuxExtEnabled`, `lookupCacheEnabled`, `global_secflags`) and reset counters on servers/tcons. Proc output reflects live in-memory connection/session/open-file/cache state; no persistent storage exists.

Dependencies and integration: depends on procfs, `seq_file`, CIFS global lists and locks, SMB Direct, DFS cache, witness dump, cached directory invalidation, security flag definitions, and mount parameter descriptors.

Risks: diagnostic paths traverse complex live state while holding global locks, so output changes can introduce lock ordering or sleep-under-spinlock issues. SecurityFlags parsing is user-facing ABI. DebugData may disclose sensitive topology and, with debug key options elsewhere, can support secret exposure workflows. `open_dirs` write invalidates caches across all mounts.

Test signals: read all proc files with no sessions and active multichannel sessions, reset Stats, toggle cifsFYI/traceSMB/linux extensions/lookup cache, reject invalid security flags, verify MUST flag normalization, drop open_dirs cache, enable SMB Direct tunables, and run lockdep while sessions reconnect during DebugData reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.c -->
