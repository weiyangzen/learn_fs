# sources/distributed-fs/eos/namespace/utils/Mode.hh

## Purpose
Implements POSIX mode rendering helpers for EOS namespace metadata. It maps `mode_t` file-type and permission bits to the ten-character listing string used by Unix-style directory listings, with EOS-specific xattr indication.

## Important APIs, types, and functions
`S_XATTR` is an EOS marker bit used to display extended ACL/xattr presence. `modeToFileTypeChar(mode_t)` maps `S_IFIFO`, `S_IFCHR`, `S_IFDIR`, `S_IFBLK`, `S_IFREG`, `S_IFLNK`, and `S_IFSOCK` to `p`, `c`, `d`, `b`, `-`, `l`, and `s`. `modeToBuffer(mode_t, char*)` fills a caller-provided buffer with a mode string like `drwxr-xr-x`.

## Control flow
`modeToBuffer()` initializes the buffer to `"----------"`, sets the file type, applies user/group/other permission bits, then overlays sticky-bit, xattr, setuid, and setgid indicators. Unknown file types are logged critically and rendered as regular files.

## State and persistence
No state is retained. The output buffer must be large enough for ten characters plus null terminator. Display semantics are user-visible and affect command output compatibility.

## Dependencies and integration points
Depends on `<sys/stat.h>` and EOS static logging. It is used by namespace stat/listing helpers and metadata-to-text conversions.

## Risks and test signals
Setuid/setgid handling always writes `s` and does not distinguish no-execute uppercase `S`, while sticky/xattr compete for the last character. Tests should cover every file type, all permission classes, xattr-only, sticky-plus-xattr, setuid/setgid without execute, unknown types, and buffer sizing at callers.
