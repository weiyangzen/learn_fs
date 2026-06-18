# File Research: sources/block-storage/lvm2/lib/misc/last-path-component.h

This header provides one inline path helper.

API:
- `last_path_component(const char *name)` returns the substring after the last `/`.
- If there is no slash, it returns `name`.
- If the path ends with `/`, it returns the empty string after the slash.

Dependencies:
- `<string.h>` for `strrchr`.

Role:
- Lightweight basename-like helper without allocation and without libc `basename()` mutation/portability issues.
