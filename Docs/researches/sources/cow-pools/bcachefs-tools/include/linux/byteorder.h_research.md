# File Research: sources/cow-pools/bcachefs-tools/include/linux/byteorder.h

Purpose: maps Linux byte-order helper names onto asm byte-order shim names and adds small helpers.

Key contents:
- Defines `swab*`, `cpu_to_*`, `*_to_cpu`, pointer, and in-place conversion aliases.
- Provides `le16_add_cpu()`, `le32_add_cpu()`, and `le64_add_cpu()`.
- Provides `le32_to_cpu_array()` for in-place array conversion.

Important interactions:
- Used by on-disk format parsing and serialization code.
- Depends on `<asm/byteorder.h>` and kernel-style type definitions.
