# File Research: sources/block-storage/util-linux/sys-utils/lscpu-riscv.c

`lscpu-riscv.c` provides RISC-V ISA identification and formatting for `lscpu`.

Key behavior:
- `is_riscv()` checks whether the CPU type ISA begins with `rv32`, `rv64`, or `rv128`, case-insensitively.
- `lscpu_format_isa_riscv()` splits the ISA string on underscores, sorts multi-letter extensions alphabetically, and rewrites underscores as spaces.
- Keeps the base ISA and single-letter extension segment first.

Important dependencies:
- util-linux string-vector helpers `ul_strv_split()`, `ul_strv_length()`, and `ul_strv_free()`.
- Shared `struct lscpu_cputype`.

Risk notes:
- `lscpu_format_isa_riscv()` assumes `ct->isa` is writable and large enough for the reformatted string; the comment notes the length stays the same.
- It does not guard against `ct->isa == NULL`; callers check `ct->isa` before invoking.
