# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TaskUtil.m

Purpose: implements command execution and XPC privileged-helper RPC.

Important APIs and control flow: `executeTaskSearchingPath:args:` resolves a command with `/usr/bin/which` and executes it. `executeTask:arguments:` launches an `NSTask`, sets a custom PATH, captures stdout, trims the final byte, and returns nil on nonzero status. `executePrivTask:filename:data:` obtains authorization through `AuthUtil`, serializes `AuthorizationExternalForm`, creates a privileged Mach service XPC connection to `org.openafs.privhelper`, sends `task`, `auth`, optional `filename`, and optional `data`, waits synchronously, and extracts integer `status`. Wrapper methods implement no-arg tasks, backup, and write.

State and persistence: no local persistent state. Privileged helper requests affect launchd state, AFS service state, or config files under `/var/db/openafs`.

Dependencies and integration: depends on ServiceManagement, Security, XPC, and `AuthUtil`. Called from the preference pane and property manager.

Risks: synchronous XPC calls can block the UI. `executeTask:` trims one byte from all nonempty stdout, which can corrupt output that lacks a trailing newline. The PATH string includes literal `$PATH`, not expansion. It does not capture stderr. Helper errors are returned but many callers ignore nonzero statuses.

Test signals: stdout with and without trailing newline, stderr-only failures, nonexistent commands, PATH lookup for OpenAFS tools, helper not installed, invalid reply type, denied authorization, and each helper task status.
