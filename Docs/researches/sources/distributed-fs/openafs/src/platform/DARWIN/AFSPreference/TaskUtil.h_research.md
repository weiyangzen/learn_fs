# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/TaskUtil.h

Purpose: declares shell-command and privileged-helper utilities used by preference pane controllers and configuration managers.

Important APIs and constants: `PRIVHELPER_ID` is `org.openafs.privhelper`. Methods search executable paths, run commands via `NSTask`, send generic privileged tasks, and send backup/write privileged tasks with filenames/data.

Control flow and persistence: unprivileged commands return captured stdout as strings. Privileged commands are sent to the XPC Mach service implemented by `PrivilegedHelper/privhelper.c.in`; persistent effects depend on the requested helper task.

Dependencies and integration: imports Cocoa and Security Authorization headers. `AFSPropertyManager`, `AFSCommanderPref`, and `PListManager` use it heavily.

Risks: filename/data are exposed as `char *` in the generic API even though wrapper methods pass UTF-8 strings. Callers must use exact task names recognized by the helper.

Test signals: command path lookup, stdout trimming, nonzero exit behavior, helper unavailable, denied authorization, backup/write allowed paths, and start/stop/startup task names.
