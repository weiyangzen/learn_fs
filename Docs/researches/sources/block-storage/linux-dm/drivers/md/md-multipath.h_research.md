# File Research: sources/block-storage/linux-dm/drivers/md/md-multipath.h

## Purpose
Defines private structures for the deprecated MD multipath personality.

## Main Interfaces
- `struct multipath_info`: one path entry containing an `md_rdev` pointer.
- `struct mpconf`: MD backpointer, path array, raid disk count, device lock, retry list, and retry-object mempool.
- `struct multipath_bh`: per-I/O retry context containing MD pointer, master bio pointer, embedded cloned bio, selected path, and retry-list node.

## Control Flow
No executable control flow. The structures support request cloning, completion, and retry scheduling in `md-multipath.c`.

## State And Synchronization
`mpconf->device_lock` protects retry-list updates and degraded/path state changes. The path array is read with RCU in the implementation. `multipath_bh` objects are allocated from a mempool to guarantee retry context availability under I/O pressure.

## Integration Points
Included by the multipath personality implementation and tied to MD core `md_rdev`, `mddev`, and block-layer `bio` structures.

## Notable Behaviors
- The embedded bio in `multipath_bh` avoids separate bio allocation for retries after the initial mempool object has been obtained.
- `master_bio` is kept so final completion reports status to the original upper-layer bio.

## Risks And Review Focus
- Structure lifetime is coupled to mempool allocation/free in completion paths; missing completion or double completion would leak or double-free retry contexts.
