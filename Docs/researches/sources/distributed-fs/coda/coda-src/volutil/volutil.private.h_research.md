# sources/distributed-fs/coda/coda-src/volutil/volutil.private.h

## Purpose

`volutil.private.h` declares shared private definitions for Coda volume utility implementation files. The complete 60-line header was read.

## Important APIs, Types, and Functions

It defines `VOLUTIL_TIMEOUT`, `VOLUTIL_RESTART`, and `VOLUTIL_ABORT`, and declares `CloneVnode()` and `PrintVersionVector()`. `CloneVnode()` is annotated as requiring a transaction.

## Control Flow

The header has no executable flow. It centralizes prototypes and constants used by implementation files in the volutil subsystem.

## State and Persistence Behavior

There is no state in this header. `CloneVnode()`'s contract implies persistent RVM/vnode mutation in its implementation, while the header only exposes the transaction expectation.

## Dependencies and Integration Points

It depends on `coda_tsa.h` for transaction annotations and assumes volume/vnode types are visible to consumers. It is included by salvage and clone-related volutil code.

## Risks and Test Signals

Risks are interface drift and weak type isolation: this private header exposes low-level helpers but not their owning modules. Tests are indirect through clone and volume utility code that uses `CloneVnode()` and version-vector printing.
