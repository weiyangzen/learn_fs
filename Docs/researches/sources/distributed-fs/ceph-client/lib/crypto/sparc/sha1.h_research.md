# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha1.h

## Purpose

This SPARC64 header dispatches SHA-1 block compression to SPARC crypto opcodes when available. It was read as a complete 43-line file.

## Important APIs, Types, and Functions

It defines `have_sha1_opcodes`, declares `sha1_sparc64_transform`, implements `sha1_blocks`, and defines `sha1_mod_init_arch`.

## Control Flow

Initialization checks `HWCAP_SPARC_CRYPTO`, reads ASR26, tests `CFR_SHA1`, and enables the static key. Block processing then either calls `sha1_sparc64_transform` or falls back to `sha1_blocks_generic`.

## State and Persistence Behavior

The static key persists after init. Hash state remains caller-owned and is updated in place by either assembly or generic code.

## Dependencies and Integration Points

It depends on SPARC ELF hwcap, opcode, and PSTATE headers, plus `sparc/sha1_asm.S`. It is included by generic `sha1.c` when architecture acceleration is configured.

## Risks and Edge Cases

Feature detection and assembly ABI compatibility are the main risks. SHA-1 collision weakness is a broader algorithm risk outside this dispatch code.

## Test Signals

SHA-1/HMAC-SHA1 KUnit vectors, FIPS HMAC-SHA1 self-test, SPARC accelerated boot logs, and fallback comparison validate behavior.
