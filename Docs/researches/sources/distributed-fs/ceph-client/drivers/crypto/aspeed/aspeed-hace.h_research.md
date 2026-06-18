# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace.h

## Purpose

`aspeed-hace.h` is the shared hardware contract and internal interface for the Aspeed HACE hash and symmetric cipher drivers. It defines register offsets, command/status bits, SoC version identifiers, DMA buffer sizing, scatter-gather descriptor layout, per-engine runtime state, crypto transform/request contexts, and registration prototypes used by `aspeed-hace.c`, `aspeed-hace-crypto.c`, and `aspeed-hace-hash.c`.

## Important APIs, Types, And Functions

Important definitions include `ASPEED_HACE_*` register offsets, `HACE_CMD_*` cipher mode/key/interrupt/SG bits, `HASH_CMD_*` hash algorithm/control bits, SHA flag bits, and fixed coherent buffer sizes. `struct aspeed_sg_list` is the little-endian hardware SG descriptor. `struct aspeed_engine_hash` and `struct aspeed_engine_crypto` hold active request, DMA buffers, tasklet, busy flag, and resume callbacks. `struct aspeed_sham_reqctx`, `struct aspeed_cipher_ctx`, and `struct aspeed_cipher_reqctx` define per-request/per-transform crypto API state. `ast_hace_read()` and `ast_hace_write()` wrap MMIO.

## Control Flow

This header does not execute control flow, but it defines how callers program HACE: write source/destination/context/digest buffer addresses, data length, and command bits; receive status through `ASPEED_HACE_STS`; and use resume callbacks from IRQ tasklets to finish queued crypto-engine work. Version values distinguish AST2500 from AST2600 feature sets.

## State And Persistence Behavior

The structures distinguish device-lifetime state (`struct aspeed_hace_dev`), engine-lifetime DMA/tasklet state, transform-lifetime keys and fallback tfms, and request-lifetime offsets, counters, command bits, and digest buffers. Digest buffers are aligned for DMA. SG descriptors use little-endian length/address fields with high-bit end markers for hash and cipher code paths.

## Dependencies And Integration Points

The header pulls in AES, hash, SHA2, crypto-engine, interrupt, and Linux type definitions. It exposes the internal registration functions for optional hash and crypto compilation units and centralizes AST2500/AST2600 differences so the implementation files agree on register bits and buffer sizes.

## Risks And Test Signals

Risks include stale register bit definitions, buffer constants that are too small for descriptor-heavy requests, mismatched endian expectations in `aspeed_sg_list`, and context-layout assumptions shared by cipher completion and hardware. Test signals are compile coverage for all Kconfig combinations, sparse/endian checks on SG descriptors, and runtime selftests that exercise every command bit combination advertised by the algorithm tables.
