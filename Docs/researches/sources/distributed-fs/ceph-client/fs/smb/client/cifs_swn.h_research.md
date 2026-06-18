<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.h

Purpose: declares Witness Service APIs and provides no-op stubs when `CONFIG_CIFS_SWN_UPCALL` is disabled.

Important APIs: enabled builds expose `cifs_swn_register()`, `cifs_swn_unregister()`, `cifs_swn_notify()`, `cifs_swn_dump()`, `cifs_swn_check()`, `cifs_swn_set_server_dstaddr()`, and `cifs_swn_reset_server_dstaddr()`. Disabled builds inline success/no-op/false stubs.

Control flow: callers can unconditionally invoke SWN hooks. `cifs_swn_set_server_dstaddr()` copies the witness-provided destination address into `server->dstaddr` when `use_swn_dstaddr` is set; reset clears the flag.

State and persistence: header inline helpers read/write `TCP_Server_Info` address fields but own no independent state.

Dependencies and integration: depends on `cifsglob.h`, tcon/server types, generic netlink forward declarations, and optional SWN implementation.

Risks: no-op stubs mean callers must not assume witness functionality is active unless config and runtime registration succeed. Address override helpers directly mutate server destination state and must be used in reconnect code only.

Test signals: compile with SWN enabled and disabled, verify unconditional call sites link, exercise reconnect address override/reset, and confirm DebugData omits witness registrations in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.h -->
