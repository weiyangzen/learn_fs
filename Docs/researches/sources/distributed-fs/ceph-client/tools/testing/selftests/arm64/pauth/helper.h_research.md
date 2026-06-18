# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/helper.h

## Purpose

This header defines the PAUTH helper ABI shared between the parent test, exec worker, and assembly corruptor.

## Important APIs, Types, and Functions

It defines `NKEYS`, `struct signatures`, declares `pac_corruptor()`, and declares five signing helpers for IA, IB, DA, DB, and generic keys.

## Control Flow and Data Flow

There is no control flow. The fixed field order in `struct signatures` is the binary pipe protocol between `pac.c` and `exec_target.c`.

## State and Persistence Behavior

The header owns no storage. The structure persists only in process memory or pipe payloads.

## Dependencies and Integration Points

It depends on `size_t` from `<stdlib.h>` and is consumed by all PAUTH selftest sources.

## Risks and Edge Cases

Changing field order or `NKEYS` breaks comparisons and worker protocol. The structure is not versioned or endian-neutral because parent and worker are the same local binary set.

## Test Signals

Compilation and correct parent/worker signature comparison validate the header contract.
