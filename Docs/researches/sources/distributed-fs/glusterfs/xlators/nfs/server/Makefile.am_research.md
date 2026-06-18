# sources/distributed-fs/glusterfs/xlators/nfs/server/Makefile.am

## Purpose
Intermediate automake entry for the GlusterFS NFS server translator.

## APIs, Types, and Functions
The file defines `SUBDIRS = src` and an empty `CLEANFILES`.

## Control Flow, State, and Persistence
Build traversal descends into `xlators/nfs/server/src`, where the loadable translator module is defined. There is no runtime state.

## Dependencies and Integration
Depends on automake recursive make. It integrates the server source directory into the NFS subtree build.

## Risks and Test Signals
Risk is limited to build-system wiring. Test signals are recursive make logs entering `xlators/nfs/server/src` and package generation including the server source artifacts.
