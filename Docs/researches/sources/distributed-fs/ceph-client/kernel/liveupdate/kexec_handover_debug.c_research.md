# sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_debug.c

## Purpose
`kexec_handover_debug.c` provides optional KHO debug validation helpers, currently focused on detecting attempts to preserve memory that overlaps KHO scratch areas.

## Important APIs, Types, and Functions
The exported/internal function is `kho_scratch_overlap(phys_addr_t phys, size_t size)`. It scans global `kho_scratch` descriptors and `kho_scratch_cnt`.

## Control Flow
For each scratch region, the function computes `[scratch_start, scratch_end)` and tests interval overlap with `[phys, phys + size)`. It returns true on the first overlap, otherwise false.

## State and Persistence Behavior
The file does not persist state; it reads scratch descriptors prepared by KHO boot memory setup.

## Dependencies and Integration Points
It includes `kexec_handover_internal.h`. `kho_preserve_folio()` and `kho_preserve_pages()` call this helper under `CONFIG_KEXEC_HANDOVER_DEBUG` and reject overlapping preservations.

## Risks and Test Signals
The overlap check assumes non-overflowing `phys + size`; very large ranges should be scrutinized. Tests should preserve ranges before, inside, spanning, and after scratch areas and verify non-debug builds compile to the inline false helper.
