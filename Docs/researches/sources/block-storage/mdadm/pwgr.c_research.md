# File Research: sources/block-storage/mdadm/pwgr.c

Purpose: static-linking stub for passwd/group lookup.

Behavior:
- Defines `getpwnam()` and `getgrnam()` to always return `NULL`.
- The file comment says static binaries cannot link passwd/group support, so mdadm builds can omit that functionality.

Dependencies:
- Includes `<stdlib.h>`, `<pwd.h>`, and `<grp.h>` only for matching declarations/types.

Impact:
- Any caller must tolerate lookup failure.
- This file intentionally changes feature behavior for static builds rather than emulating NSS.
