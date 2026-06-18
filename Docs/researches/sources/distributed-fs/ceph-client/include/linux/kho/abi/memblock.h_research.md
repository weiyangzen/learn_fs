# sources/distributed-fs/ceph-client/include/linux/kho/abi/memblock.h

## Purpose

`memblock.h` defines the KHO ABI constants for preserving `reserve_mem` memblock reservations across kexec. The source was read as a complete 73-line file.

## Important APIs, Types, and Functions

The file defines `MEMBLOCK_KHO_FDT`, `MEMBLOCK_KHO_NODE_COMPATIBLE`, and `RESERVE_MEM_KHO_NODE_COMPATIBLE`. The documented FDT schema has a root `memblock` entry compatible with `memblock-v1`, with child reserve-memory nodes compatible with `reserve-mem-v1` and `start`/`size` u64 properties.

## Control Flow

There is no local code. The old kernel serializes named reserve-mem regions into the memblock KHO FDT; the new kernel parses those nodes and recreates reservations at the same physical addresses.

## State and Persistence Behavior

The ABI persists physical reservation names, start addresses, and sizes across kexec. The header owns no runtime state.

## Dependencies and Integration Points

It integrates with memblock reservation handling, command-line `reserve_mem`, KHO subtree registration, and FDT parsing.

## Risks and Edge Cases

FDT node names are user-defined reservation names and must be validated. Any property or compatible-string change requires versioning. The new kernel must reject overlapping, unavailable, or malformed reservations rather than blindly trusting preserved data.

## Test Signals

Kexec handover tests for named reserve-mem regions, malformed FDT property tests, overlap rejection tests, and compatible-version checks are useful.
