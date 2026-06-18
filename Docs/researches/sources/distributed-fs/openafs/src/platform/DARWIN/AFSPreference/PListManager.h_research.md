# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/PListManager.h

Purpose: declares static utilities for modifying macOS authorization and launchd plist configuration used by OpenAFS login/startup/backgrounder features.

Important APIs and constants: constants define login mechanism strings for 10.4 and 10.5+, `/etc/authorization` paths, temp/backup files, backgrounder LaunchAgent labels/paths, and AFS startup LaunchDaemon paths. Methods include `krb5TiketAtLoginTime:helper:`, `checkKrb5AtLoginTimeLaunchdEnable`, `installBackgrounderLaunchdFile:resourcePath:`, `checkLoginTimeLaunchdBackgrounder`, `manageAfsStartupLaunchdFile:afsStartupScript:afsBasePath:afsdPath:`, `launchctlCommand:userDomain:option:plistName:`, and `launchdJobState:`.

State and persistence: persistent effects are edits to `/etc/authorization`, user LaunchAgents under `~/Library/LaunchAgents`, and LaunchDaemon-style startup plists.

Dependencies and integration: implemented with `FileUtil`, `TaskUtil`, Cocoa plist serialization, and `launchctl`. Called by `AFSCommanderPref`.

Risks: system authorization database formats changed across macOS releases. Header still exposes legacy startup-plist management that overlaps with the newer privileged helper approach.

Test signals: enabling/disabling Kerberos login mechanism by OS version, backgrounder LaunchAgent creation/removal, `launchctl list` parsing, missing LaunchAgents directory, and authorization file backup behavior.
