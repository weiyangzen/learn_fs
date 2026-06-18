# Research: sources/distributed-fs/openafs/src/platform/DARWIN/PrivilegedHelper/Makefile.in

Purpose: builds and stages the `org.openafs.privhelper` privileged XPC helper embedded in the preference pane bundle.

Important targets and control flow: `all` builds `org.openafs.privhelper` from generated `privhelper.c`, using `AFS_LDRULE`, minimum macOS 10.6, embedded `__info_plist` from `privhelper-info.plist`, embedded `__launchd_plist` from `privhelper-launchd.plist`, and Security/CoreFoundation frameworks. `dest` installs the helper under `OpenAFS.prefPane/Contents/Library/LaunchServices`.

State and persistence: build output is the helper executable. Staging path is inside the preference pane so ServiceManagement can bless/install it.

Dependencies and integration: includes OpenAFS config and version makefiles. Must match `Info.plist.in` `SMPrivilegedExecutables` and `TaskUtil` service id.

Risks: embedded plist section paths must exist at link time. Code signing/blessing fails if the helper is not staged exactly where ServiceManagement expects. `install` target is empty; packaging relies on `dest`.

Test signals: helper links with embedded plist sections, staged bundle path correctness, code signing requirements, and ServiceManagement installation from the preference pane.
