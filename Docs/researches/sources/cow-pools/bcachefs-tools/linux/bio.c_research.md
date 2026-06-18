# File Research: sources/cow-pools/bcachefs-tools/linux/bio.c

Implements Linux bio helpers for userspace block I/O. It maps block statuses to errno/strings, copies and zero-fills bio data, clones/splits bios, advances iterators, manages bio refcounts/freeing, adds virtual segments, chains endio callbacks, resets/allocates bios, and initializes/exits biosets.

`fs_bio_set` is created by constructor and destroyed by destructor using mempools for bio and bvec allocation.
