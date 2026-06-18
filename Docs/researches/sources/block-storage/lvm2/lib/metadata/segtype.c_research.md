# File Research: sources/block-storage/lvm2/lib/metadata/segtype.c

This file provides lookup helpers for LVM segment types registered in `cmd_context->segtypes`.

Functions:
- `get_segtype_from_string(cmd, str)` searches registered segment types by name. If no match exists, it creates an unknown segment type with `init_unknown_segtype()`, appends it to the command context list, warns about the unrecognized type, and returns it.
- `get_segtype_from_flag(cmd, flag)` iterates registered segment types backwards and returns the first type whose flags match the supplied bit. Backward iteration supports aliases, for example returning `raid5` instead of `raid5_ls` where registration order makes that preferable.

Behavioral notes:
- Unknown on-disk segment type names can still be represented rather than immediately rejected.
- Flag lookup logs an internal error and returns `NULL` if no registered type matches.
- The file is small but central: conversion and metadata code use these helpers to map user-visible names and internal flags to `struct segment_type` objects.
