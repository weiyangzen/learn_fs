# sources/cloud-native/ostree/src/libostree/ostree-ref.c

## Purpose
This file implements `OstreeCollectionRef`, a boxed value representing `(collection_id, ref_name)`. It gives OSTree a globally unique ref identity for peer-to-peer and collection-aware operations, while allowing `NULL` collection IDs for legacy plain refs.

## Important APIs and Control Flow
`ostree_collection_ref_new()` validates a non-NULL ref name and optional collection ID, then deep-copies both strings. `ostree_collection_ref_dup()` uses the constructor to copy. `ostree_collection_ref_free()` releases strings and the struct. `ostree_collection_ref_hash()` XORs collection and ref hashes when a collection exists, otherwise hashes only the ref name. `ostree_collection_ref_equal()` compares both fields with `g_strcmp0()`. `dupv()` and `freev()` deep-copy and free NULL-terminated arrays; `dupv()` uses `g_strv_length()` as a pointer-array length hack.

## State, Dependencies, Integration, Risks, and Tests
State is the allocated pair of strings. Dependencies include validation helpers from `ostree-core`, GLib boxed types, and libglnx headers. Integration points include ref maps, summary/pull code, and APIs that accept collection-ref vectors. Risks are hash collisions from XOR being acceptable but simple, `dupv()` assuming a NULL-terminated pointer array compatible with string-vector length scanning, and constructor validation returning NULL rather than setting `GError`. Tests should cover NULL collection IDs, invalid collection/ref names, equality/hash table behavior, and vector ownership.
