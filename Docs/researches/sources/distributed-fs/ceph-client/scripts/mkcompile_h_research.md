<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mkcompile_h -->
# sources/distributed-fs/ceph-client/scripts/mkcompile_h

## Purpose

`mkcompile_h` generates compile identity macros for kernel build metadata: target machine, build user, build host, and compiler/linker string.

## Important APIs, Types, and Functions

It accepts `UTS_MACHINE`, `CC_VERSION`, and `LD` as positional arguments. It honors `KBUILD_BUILD_USER` and `KBUILD_BUILD_HOST`; otherwise it derives them from `whoami` and `uname -n`. Linker identity comes from `$LD -v`.

## Control Flow

The script chooses user/host strings, escapes backslashes in the user, normalizes the first linker version line by removing compatibility parentheticals/trailing whitespace, and prints a small C header fragment with four `#define`s.

## State and Persistence Behavior

It writes only to stdout. Kbuild decides whether generated output replaces a header.

## Dependencies and Integration Points

It depends on shell, `whoami`, `uname`, `head`, `sed`, and a linker executable. It integrates with generated kernel compile metadata included in version reporting.

## Risks and Edge Cases

User/host strings can contain quotes or other characters not escaped here. Linker version formatting is tool-dependent. Reproducible builds must set `KBUILD_BUILD_USER` and `KBUILD_BUILD_HOST` to stable values.

## Test Signals

Run with explicit build user/host, unset environment, linker strings with compatibility text, and unusual usernames. Verify produced C string literals compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mkcompile_h -->
