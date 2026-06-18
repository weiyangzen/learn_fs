# sources/distributed-fs/ceph-client/lib/crypto/s390/sha1.h

## Purpose

This s390 header accelerates SHA-1 block processing through CPACF KIMD. It was read as a complete 28-line file.

## Important APIs, Types, and Functions

It defines `have_cpacf_sha1`, implements `sha1_blocks`, and provides `sha1_mod_init_arch`.

## Control Flow

At init, the code checks MSA and `CPACF_KIMD_SHA_1`; if available, it enables the static key. Block processing either calls `cpacf_kimd` over `nblocks * SHA1_BLOCK_SIZE` bytes or falls back to `sha1_blocks_generic`.

## State and Persistence Behavior

The static key persists after initialization. Hash state remains caller-owned and is updated in place by either CPACF or generic compression.

## Dependencies and Integration Points

It depends on `<asm/cpacf.h>`, s390 CPU feature helpers, and `sha1.c`'s generic fallback. It is included by the generic SHA-1 library under architecture acceleration.

## Risks and Edge Cases

Risks include CPACF function availability mismatch and state layout compatibility with CPACF. SHA-1 is collision-weak cryptographically, but this file is a performance hook, not a policy gate.

## Test Signals

SHA-1/HMAC-SHA1 KUnit vectors, FIPS HMAC-SHA1 self-test when enabled, and generic-versus-CPACF comparisons are useful.
