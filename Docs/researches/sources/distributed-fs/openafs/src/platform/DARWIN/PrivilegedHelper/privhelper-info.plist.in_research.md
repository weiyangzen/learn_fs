# Research: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/privhelper-info.plist.in

Purpose: Info.plist template embedded in the privileged helper executable.

Important keys: `CFBundleIdentifier` is `org.openafs.privhelper`, version metadata is static, and `SMAuthorizedClients` restricts clients to the signed preference pane identifier `it.infn.lnf.network.openafs` with Apple generic/Developer ID certificate constraints and `@MACOS_TEAM_ID@`.

State and persistence: build-time metadata used by ServiceManagement and launchd when blessing or validating the helper.

Dependencies and integration: must align with `TaskUtil`'s service name, `AFSPreference/Info.plist.in` `SMPrivilegedExecutables`, and the runtime code-signing checks inside `privhelper.c.in`.

Risks: Team ID substitution or bundle identifier mismatch prevents helper installation or client authorization. The runtime helper also allows backgrounder/menu identifiers, so plist authorized clients and runtime code requirements must be reviewed together.

Test signals: validate substituted plist, code-signing requirement syntax, SMJobBless acceptance, and client connection from the signed preference pane.
