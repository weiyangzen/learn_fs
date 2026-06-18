# sources/distributed-fs/coda/coda-src/venus/venusstats.h

## Purpose
This header defines Venus statistics structures for VFS operations, filesystem objects, volumes, communication components, RPC operations, and RPC/SFTP packet counters.

## Important APIs, Types, and Functions
`VFSStat` stores operation name, success/retry/timeout/failure counts, and timing sums; `VFSStatistics` contains `NVFSOPS` entries. Placeholder structs exist for FSO, volume, connection, mgrp, server, and VSG stats. `RPCOpStat` stores per-RPC success/failure/timing and retry counts for unicast and multicast operations. `RPCPktStatistics` mirrors RPC2 and SFTP sent/received packet stats. `CommStatistics` and `VenusStatistics` aggregate subsystem stats.

## Control Flow
No functions are defined. Runtime initialization and printing occur in `venusutil.cc` through `StatsInit()`, `VFSPrint()`, `RPCPrint()`, and packet stat helpers.

## State and Persistence Behavior
These structures are transient runtime counters. They are not persisted, but they expose operational signals through Venus print/control paths and possibly pioctl status.

## Dependencies and Integration Points
It depends on RPC2 and Vice definitions, including `srvOPARRAYSIZE`, `SStats`, `RStats`, and `sftpStats`. `venus.private.h` declares global instances using these types.

## Risks and Test Signals
Risks include fixed `NVFSOPS`, fixed name buffer lengths, and protocol array size coupling. Tests should ensure VFS operation tables in `venusutil.cc` match `NVFSOPS`, RPC op initialization matches `srvOPARRAYSIZE`, and printed timing avoids divide-by-zero.
