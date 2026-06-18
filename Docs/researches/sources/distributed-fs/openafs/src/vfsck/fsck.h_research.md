<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/fsck.h -->
# sources/distributed-fs/openafs/src/vfsck/fsck.h

## Purpose
Central shared header for the OpenAFS UFS/HFS fsck implementation. It defines inode state values, traversal descriptors, buffer-cache structures, duplicate-block and zero-link lists, repair flags, global process state, and platform-specific filesystem compatibility macros.

## Important APIs, Types, And Functions
Important types are `struct bufarea`, `struct inodesc`, `struct dups`, and `struct zlncnt`. Key constants include inode states `USTATE`, `FSTATE`, `DSTATE`, `DFOUND`, `DCLEAR`, `FCLEAR`, OpenAFS `VSTATE`, HP-UX ACL states `CSTATE` and `CRSTATE`, descriptor types `DATA`/`ADDR`, callback return bits `STOP`, `SKIP`, `KEEPON`, `ALTERED`, and `FOUND`, plus `MAXDUP`, `MAXBAD`, and `MAXBUFSPACE`. It declares shared functions such as `getdatablk`, `getblk`, `ginode`, `allocino`, `findino`, `setup`, `bread`, and `bwrite`.

## Control Flow
The header does not execute control flow itself, but it defines the callback contract used throughout the fsck passes. `ckinode` walks an inode and invokes an `inodesc.id_func`; callbacks return bitmasks to stop, continue, skip, or mark data altered. Macros such as `dirty`, `sbdirty`, `cgdirty`, and `zapino` centralize how files mark buffered filesystem structures for later flush.

## State And Persistence
Most global state is declared here: device names, file descriptors, flags (`preen`, `nflag`, `yflag`, `debug`, `cvtflag`, `fflag`, `mflag`), superblock/cylinder group buffers, block and inode maps, link count table, path buffers, lost+found inode, file/block counters, AFS Vice file counters, Sun clean-state tracking, and HP-UX continuation inode counters. These globals drive all persistent disk modifications made by the passes.

## Dependencies And Integration Points
Every `vfsck` C file includes this header after platform filesystem headers. It bridges OpenAFS Vice inode recognition (`VICEINODE`, `OLDVICEINODE`) with host UFS/HFS structures and exposes platform-specific compatibility shims for Sun and HP-UX.

## Risks And Test Signals
Risks are broad global mutable state, platform macro drift, duplicate global definitions across translation units, K&R-era declarations that hide type mismatches, and subtle differences in `zapino` behavior for Vice versus non-Vice builds. Compile coverage across supported platforms and full fsck pass tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/fsck.h -->
