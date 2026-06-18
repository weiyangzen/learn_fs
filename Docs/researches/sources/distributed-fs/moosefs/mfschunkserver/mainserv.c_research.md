# sources/distributed-fs/moosefs/mfschunkserver/mainserv.c

## Purpose
`mainserv.c` implements the chunkserver client/peer data path for direct reads, chained writes, and write forwarding. It wraps socket I/O with stats, timeout helpers, keepalive NOP handling, optional mmap allocation, and `hddspacemgr` calls.

## Important APIs and control flow
Public entry points are `mainserv_stats()`, `mainserv_read()`, `mainserv_write()`, and `mainserv_init()`. Reads validate packet shape, chunk id/version, offset, and size; open the chunk; precache data; send one `CSTOCL_READ_DATA` packet per block segment; and finish with `CSTOCL_READ_STATUS`. Zero-length and bounds errors return status packets immediately.

Writes parse `CLTOCS_WRITE` with optional protover 1 and optional downstream peer list. The last node path writes each incoming data packet locally and acknowledges by write id. The middle-node path connects to the next peer, forwards write data and finish packets, writes locally in a worker thread, reads downstream statuses, and acknowledges upstream only once local and downstream results agree. Periodic `ANTOAN_NOP` packets keep long operations alive.

## State, persistence, and dependencies
The module keeps bytes-in/out and high-level read/write counters. Persistent mutation happens through `hdd_open`, `hdd_write`, and `hdd_close`; write close currently does not force fsync. Dependencies include `MFSCommunication`, `sockets`, `cfg`, `mfslog`, `datapack`, `hddspacemgr`, `lwthread`, `clocks`, optional `conncache`, and optional mmap.

## Risks and test signals
The write-middle path is the highest-risk control flow because upstream, downstream, and HDD-worker events must be reconciled. Tests should cover chunk/version mismatches, partial forwarding, downstream failures, local write failures, NOP interleaving, timeout, connection-cache reuse, multi-block reads, boundary offsets, and builds with `HAVE_MMAP`.
