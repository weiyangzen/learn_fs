# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/PListManager.m

Purpose: implements plist and launchd management for Kerberos-at-login, backgrounder activation, and legacy AFS startup plist handling.

Important APIs and control flow: `krb5TiketAtLoginTime:helper:` reads Active Directory prefs and skips changes when AD auth authority generation is enabled, reads `/etc/authorization`, locates `system.login.console` mechanisms, replaces the OS-version-specific mechanism with `builtin:krb5authnoverify,privileged` or restores it, serializes to `/tmp/authorization`, backs up `/etc/authorization`, chowns temp file to root:wheel, and moves it into `/etc`. `installBackgrounderLaunchdFile:` creates a per-user LaunchAgent plist for `AFSBackgrounder.app` or removes it. `launchctlCommand:` builds a user/system Library LaunchAgents path and runs `/bin/launchctl`. `launchdJobState:` runs `launchctl list jobName`.

State and persistence: mutates `/etc/authorization`, `/etc/authorization_bk`, `~/Library/LaunchAgents/it.infn.lnf.network.AFSBackgrounder.plist`, and launchd job state.

Dependencies and integration: `AFSCommanderPref` calls these methods for UI toggles. `FileUtil` performs privileged `/etc/authorization` updates; `TaskUtil` runs unprivileged launchctl/mv/rm calls.

Risks: `indexOfObject:` returning `NSNotFound` is not checked before `replaceObjectAtIndex:`. Editing `/etc/authorization` is fragile and obsolete on modern macOS. Some temp moves use unprivileged `mv`. The `helper` argument is unused in the visible implementation. `launchctlCommand` always constructs `LaunchAgents`, even for non-user domains.

Test signals: OS 10.4/10.5/10.6 mechanism replacement, missing target mechanism, malformed plist, AD skip condition, LaunchAgents directory missing, backgrounder path correctness, launchctl load/unload arguments, and job-state false positives.
