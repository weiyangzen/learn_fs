# File Research: sources/block-storage/util-linux/libblkid/src/partitions/solaris_x86.c

## Purpose
Parses Solaris x86 VTOC slice tables, usually nested inside a primary DOS Solaris partition.

## Main Components
- Defines Solaris VTOC and slice structures.
- Constants locate VTOC at sector 1 and magic/sanity offset.
- `probe_solaris_pt()` reads sector 1, requires VTOC version 1, returns early for type-only probing, creates a `solaris` table, bounds `v_nparts` to 16, and iterates slices.
- Skips whole-disk slices and zero-size slices.
- If nested, adds the parent start to slice starts and validates containment.
- Sets slice tag as partition type and slice flags as partition flags.
- `solaris_x86_pt_idinfo` detects little-endian sanity magic `EE DE 0D 60`.

## Dependencies and Interactions
Normally called from DOS nested subprobes for Solaris MBR partition type. Uses generic parent/nested validation from `partitions.c`.

## Research Notes
The loop starts with `i = 1` while pointing at `v_slice[0]`, which matches the file’s existing behavior but means the reported/iterated index logic is not a simple zero-based slice walk.
