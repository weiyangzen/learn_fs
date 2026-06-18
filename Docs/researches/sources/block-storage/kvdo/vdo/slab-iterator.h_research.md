# File Research: sources/block-storage/kvdo/vdo/slab-iterator.h

Defines an inline reverse iterator for arrays of `struct vdo_slab *`.

Type:
- `struct slab_iterator` stores the slab array, next slab pointer, end slab number, and stride.

Functions:
- `vdo_iterate_slabs()` initializes iteration from `start` down to `end` by `stride`. If the array is `NULL` or `start < end`, iteration is empty.
- `vdo_has_next_slab()` reports whether another slab is available.
- `vdo_next_slab()` returns the current slab and advances to `slab_number - stride`, stopping once it would pass the end.

Used by depot code to walk slabs from higher to lower numbers, for example when allocating refcount objects.
