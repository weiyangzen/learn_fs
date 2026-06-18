# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_mntent.c

## Scope

Private util-linux-derived mount-table parser/writer for legacy helpers.

## APIs And Behavior

- `mangle()` escapes spaces, tabs, newlines, and backslashes as octal sequences for mtab/fstab output.
- `unmangle()` decodes octal escapes while parsing fields.
- `my_setmntent()` opens a mount table with restrictive umask and initializes parser state.
- `my_endmntent()` closes the file and frees parser state.
- `my_addmntent()` appends a formatted, escaped mount entry.
- `my_getmntent()` reads nonblank noncomment lines, parses fsname, dir, type, opts, freq, and passno, tolerates missing final newline, and skips up to `ERR_MAX` malformed lines before stopping.

## State And Dependencies

Uses a static input buffer and static `struct my_mntent` for returned records; strings inside records are freshly allocated. Depends on `xmalloc`, `xstrdup`, and NLS messages.

## Risks And Invariants

The returned `struct my_mntent` is overwritten by the next call, but the allocated strings are transferred to callers such as `read_mntentchn()`. Long lines are treated as corruption. Classic mtab/fstab limitations around whitespace are handled only through this escape convention.
