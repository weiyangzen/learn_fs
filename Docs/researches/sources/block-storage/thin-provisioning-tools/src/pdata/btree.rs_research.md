# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree.rs

Defines on-disk btree node format: `NodeHeader`, `Node<V>::Internal`, and `Node<V>::Leaf`. Supports packing/unpacking little-endian keys and values using `Pack`/`Unpack`.

Validation checks value size, max-entry capacity against block size, entry count, optional non-fatal invariants such as `max_entries % 3 == 0` and minimum non-root occupancy, sorted keys, checksum type, and block-number match. `calc_max_entries<V>()` computes the kernel-compatible fanout rounded down to a multiple of three.
