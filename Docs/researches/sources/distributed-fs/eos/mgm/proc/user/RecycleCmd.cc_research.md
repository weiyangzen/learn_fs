# sources/distributed-fs/eos/mgm/proc/user/RecycleCmd.cc

Purpose: implements protobuf-backed recycle-bin commands for listing, purging, restoring, configuring recycle policies, and setting recycle project IDs.

Important APIs and types: dispatches on `RecycleProto::SubcmdCase`, calls `Recycle::Print`, `Purge`, `Restore`, `Config`, `RecycleIdSetup`, uses `Quota::SetQuotaTypeForId` for recycle-bin quota limits, reads `gOFS->mRecycler->Dump()`, and fills `ReplyProto`.

Control flow: `ls` maps enum type to `uid`, `all`, or `rid` and calls `Recycle::Print`. `purge` and `restore` translate options into recycle subsystem calls and route output to stdout or stderr based on return code. `config` requires root and handles add/remove bin, lifetime, ratio, size, inode, collection/remove interval, dry-run, enforce, enable, and dump operations. `project` is intended to require root before calling `RecycleIdSetup`.

State and persistence: purge, restore, config, project setup, and recycle quota changes mutate recycle subsystem state, namespace state, or quota state. Listing is read-only.

Dependencies and integration: integrates recycle command protobufs with MGM recycle services and quota enforcement for the global recycle prefix/project ID.

Risks: in the `project` branch, after setting EPERM for non-root, the code does not return before calling `RecycleIdSetup`, so unauthorized callers may still trigger setup depending on downstream checks. Config size and inode both use `config.size()`. Tests should cover every config op, non-root config and project denial, `ls` vector-output overload, purge/restore success and failure routing, type enum mapping, quota failures, and recycler dump output.
