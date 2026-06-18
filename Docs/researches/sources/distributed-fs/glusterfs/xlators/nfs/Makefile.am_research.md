# sources/distributed-fs/glusterfs/xlators/nfs/Makefile.am

## Purpose
Top-level automake entry for the GlusterFS NFS translator subtree.

## APIs, Types, and Functions
The file defines `SUBDIRS = server` and an empty `CLEANFILES`.

## Control Flow, State, and Persistence
Build traversal descends into `xlators/nfs/server`. There is no runtime state.

## Dependencies and Integration
Depends on automake's recursive make behavior. It integrates the NFS server translator subtree into the broader `xlators` build.

## Risks and Test Signals
Risk is limited to build coverage: omitting `server` would silently exclude the NFS translator subtree. Test signals are recursive make logs entering `xlators/nfs/server`, generated distribution files including the subtree, and configured builds reaching `server/src`.
