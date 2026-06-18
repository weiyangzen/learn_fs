# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/snapshot.h

Public snapshot API. It declares bkey ops for snapshot and snapshot-tree keys, lookup/create/validate/text functions, trigger entry points, tree reporting, deletion checks, and fsck/reconstruction passes.

Inline helpers access the RCU snapshot table, compare tree IDs, get parents/root/depth/state, test live/deleted/existing snapshots, identify leaves/internal nodes, find live descendants through `NO_KEYS` nodes, and manage snapshot ID lists. It also defines iteration macros over snapshot trees and wrappers for overwrite and key-snapshot validation fast paths.
