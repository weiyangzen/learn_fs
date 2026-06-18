# sources/distributed-fs/ceph-client/fs/hfs/trans.c

Purpose: converts names between Linux-visible byte strings and classic HFS Mac-encoded Pascal strings, including the HFS path separator rule.

Important APIs and control flow: `hfs_mac2asc()` converts an on-disk `struct hfs_name` to a Linux filename buffer, capping source length at `HFS_NAMELEN`, using optional disk and I/O NLS tables when configured, replacing on-disk `/` with Linux-visible `:`, and returning the produced byte length. `hfs_asc2mac()` converts a Linux `qstr` into an on-disk HFS name, optionally translating through NLS tables, replacing Linux-visible `:` with on-disk `/`, truncating to `HFS_NAMELEN`, storing the Pascal length, and zero-filling the remaining name bytes.

State and persistence: the conversion itself is pure with respect to global filesystem state, but its output is persisted in catalog keys and thread records. NLS table choices from mount options determine the byte representation on disk.

Dependencies and integration: used by catalog key/thread construction and directory iteration. Depends on `HFS_SB(sb)->nls_disk` and `nls_io`, and Linux NLS conversion callbacks.

Risks and test signals: conversion failures substitute `?` except for name-too-long termination paths, so distinct Unicode names can collide. Separator mapping is compatibility-sensitive. Tests should include NLS-enabled mounts, invalid byte sequences, names containing `:` and `/`, max-length truncation, and round-trip uniqueness assumptions.
