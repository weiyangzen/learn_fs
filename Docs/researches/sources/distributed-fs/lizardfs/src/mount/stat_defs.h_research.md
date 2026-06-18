## sources/distributed-fs/lizardfs/src/mount/stat_defs.h

Purpose: provides cross-platform Unix stat/statvfs definitions for mount code, especially Windows builds.

Important content: on `_WIN32`, defines a `statvfs` struct and Unix mode bit constants/macros (`S_IF*`, `S_IS*`, permissions, suid/sgid/sticky). On non-Windows, includes system `<sys/stat.h>` and `<sys/statvfs.h>`.

Integration: included last by `polonaise/main.cc` with an explicit warning, because it may redefine mode macros on Windows.

Risks: Windows definitions must match expectations of LizardFS and Polonaise conversions. Redefining standard-like macros can conflict if included in the wrong order.

Test signals: compile on Windows and non-Windows, verify mode conversions for every file type and permission bit, and statfs field mapping.
