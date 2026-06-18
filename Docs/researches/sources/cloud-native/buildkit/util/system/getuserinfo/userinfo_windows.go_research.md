<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/getuserinfo/userinfo_windows.go -->
# sources/cloud-native/buildkit/util/system/getuserinfo/userinfo_windows.go

Purpose: Windows reexec helper that resolves a username or group to a SID and prints it as JSON.

Important APIs and types: `getUserInfoCmd`, `init`, and `userInfoMain`.

Control flow: `init` registers the `get-user-info` command with `moby/sys/reexec`. `userInfoMain` validates a single argument, calls `windows.LookupSID`, marshals `{SID: ...}` to JSON, writes stdout, and exits with distinct nonzero codes on usage, lookup, or marshal errors.

State and persistence: no persistent state; process exits directly after command handling.

Dependencies and integration: Windows-only file using `x/sys/windows` and BuildKit/Moby reexec. Used when Windows-specific user/group SID lookup is needed from a helper process.

Risks: prints errors to stdout rather than stderr. Hard exits make it unsuitable for direct library use outside reexec.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/getuserinfo/userinfo_windows.go -->
