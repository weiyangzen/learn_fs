# Research: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/privhelper.c.in

Purpose: implements the root privileged XPC helper for the macOS preference pane and backgrounder.

Important APIs and control flow: `main` creates a Mach service listener for `org.openafs.privhelper`, installs code-signing requirements, and dispatches incoming connections. `XPCEventHandler` rejects unauthorized connections, rejects missing/invalid external authorization, extracts `task`, calls `ProcessRequest`, and replies with integer `status`. `IsConnAuthorized` uses `xpc_connection_set_peer_code_signing_requirement` on newer SDKs or `SecCodeCreateWithXPCMessage`/`SecCodeCheckValidity` on older SDKs. `IsEventAuthorized` deserializes `AuthorizationExternalForm` and verifies `kAuthorizationRightExecute`. `ProcessRequest` implements `startup_enable`, `startup_disable`, `startup_check`, `afsd_start`, `afsd_stop`, `backup`, and `write`.

State and persistence: persistent effects include `launchctl load/unload -w /Library/LaunchDaemons/org.openafs.filesystems.afs.plist`, running `/Library/OpenAFS/Tools/root.client/usr/vice/etc/afs.rc start|stop`, copying config backups, and writing allowlisted files under `/var/db/openafs`. `WriteFile` writes a temp file, chowns root:wheel, then atomically moves it into place.

Dependencies and integration: receives messages from `TaskUtil.m`. Code requirements include Apple System Preferences legacy loaders and signed OpenAFS identifiers. Uses XPC, Security.framework, CoreFoundation, syslog, `posix_spawn`, and `waitpid`.

Risks: the allowlist must stay synchronized with UI write targets. `RunCommand` passes at most four argv entries and uses inherited environment. `WriteFile` writes string data, so embedded NUL bytes are unsupported. Code-signing requirement changes across macOS versions are complex. Unknown tasks return `-1`, but callers often only log or ignore status.

Test signals: authorized and unauthorized client connections, invalid external auth data, each fixed task path, allowlist rejection, backup no-clobber semantics, write temp/chown/move failure, launchctl status interpretation, older SDK code-signing fallback, and helper response format.
