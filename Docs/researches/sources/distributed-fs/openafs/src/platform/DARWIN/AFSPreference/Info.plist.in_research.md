# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Info.plist.in

Purpose: plist template for the `OpenAFS.prefPane` bundle.

Important keys: identifies the bundle as `it.infn.lnf.network.openafs`, package type `BNDL`, principal class `AFSCommanderPref`, main nib `OpenAFSPreference`, icon `AFSCommanderIcon`, and displayed preference pane label `OpenAFS`. `SMPrivilegedExecutables` declares the embedded helper `org.openafs.privhelper` and the code-signing requirement for helper installation.

State and persistence: this file becomes bundle metadata at build/install time. The `@MACOS_TEAM_ID@` substitution controls the Team ID requirement for helper authorization.

Dependencies and integration: consumed by Xcode/build tooling and ServiceManagement. It must match `TaskUtil`'s `PRIVHELPER_ID` and `PrivilegedHelper/privhelper-info.plist.in`'s client requirements.

Risks: bundle identifier mismatch breaks CFPreferences domains and distributed notifications. Incorrect Team ID substitution prevents SMJobBless/helper authorization. Legacy version strings are static.

Test signals: built bundle has expected identifiers, `NSPrincipalClass` loads, nib exists, helper requirement matches the signed helper, and ServiceManagement accepts the `SMPrivilegedExecutables` entry.
