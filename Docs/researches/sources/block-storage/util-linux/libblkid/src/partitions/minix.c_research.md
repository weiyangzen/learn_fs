# File Research: sources/block-storage/util-linux/libblkid/src/partitions/minix.c

## Purpose
Parses Minix subpartition tables stored inside an MBR Minix partition.

## Main Components
- Reads sector 0 using DOS/MBR partition entry layout.
- Requires a parent partition from the current partition list.
- Requires the parent MBR type to be `MBR_MINIX_PARTITION`.
- Creates a `minix` partition table at `MBR_PT_OFFSET`.
- Iterates `MINIX_MAXPARTITIONS`, adding entries whose `sys_ind` is Minix and whose dimensions fit inside the parent.
- Sets numeric type and flags from MBR entry fields.
- `minix_pt_idinfo` uses the same `55 AA` MBR magic as DOS.

## Dependencies and Interactions
Usually invoked as a DOS nested subprobe for Minix MBR partition types. Uses `minix.h`, MBR helpers, and nested-dimension validation from `partitions.c`.

## Research Notes
The parser assumes DOS-like partition entries and distinguishes Minix only by the parent partition type.
