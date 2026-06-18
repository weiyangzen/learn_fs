# sources/distributed-fs/coda/coda-src/vv/nettohost.h

## Purpose

`nettohost.h` declares byte-order conversion helpers for Coda store ids and version vectors.

## Important APIs, Types, and Functions

It declares `ntohsid`, `htonsid`, `ntohvv`, and `htonvv`, all using pointer parameters to `ViceStoreId` or `ViceVersionVector`.

## Control Flow

No runtime flow exists in the header.

## State and Persistence Behavior

No state is stored. Implementations overwrite caller-provided output objects.

## Dependencies and Integration Points

The header relies on the including translation unit already knowing `ViceStoreId` and `ViceVersionVector`; unlike `nettohost.cc`, it does not include `vice.h` itself.

## Risks and Test Signals

Consumers that include this header alone before Coda type definitions will fail to compile. Tests should include it in both normal library order and standalone-with-required-types order, and link against `nettohost.cc`.
