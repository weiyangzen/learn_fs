# Research: sources/distributed-fs/openafs/src/platform/DARWIN/afssettings.m

Purpose: command-line tool that reads OpenAFS Darwin settings from a plist and applies them to the AFS kernel filesystem via sysctl.

Important APIs and control flow: `mygetvfsbyname` discovers the VFS type number for `afs` and seeds the sysctl OID. `recurse` walks a tree of `Setting` descriptors and plist dictionaries; leaf numeric values are written with `sysctl`, and leaf strings are written as UTF-8 bytes. Static setting trees map `All/RealModes`, `All/FSEvents`, `All/Bulkstat`, and Darwin-version nodes to `AFS_SC_*` selectors. `main` loads `/var/db/openafs/etc/config/settings.plist`, parses it as a property list, and recurses into the sysctl tree.

State and persistence: input is persistent plist configuration; output mutates live kernel/sysctl state for the AFS filesystem. It does not write the plist.

Dependencies and integration: includes `<afs/sysctl.h>`, Foundation/CoreFoundation, BSD `sysctl`, and mount/VFS structures. Built and installed by `DARWIN/Makefile.in`.

Risks: setting descriptors with `Node` and no children are skipped, so Darwin-version-specific empty nodes are placeholders. Invalid plist value types can be sent to numeric/string sysctl leaves. Errors are printed to stderr but processing continues. Requires AFS VFS to be present.

Test signals: missing AFS filesystem, missing/malformed settings plist, numeric and string sysctl success/failure, unknown keys ignored, nested `All/Darwin` settings, and errno reporting.
