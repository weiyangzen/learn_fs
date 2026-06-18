# sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-ni-asm.S

## Purpose
Intel SHA extension implementation of SHA-256 compression plus a two-message finalization helper. It accelerates normal complete-block updates and can finalize two equal-length messages in parallel from one starting context.

## APIs, Control Flow, And Integration
Exports `sha256_ni_transform` and `sha256_ni_finup2x`. `do_4rounds` runs one-message SHA-NI rounds and schedule updates; `do_4rounds_2x` interleaves two independent messages. The transform loads state into `ABEF/CDGH`, loops through 64 rounds per block, feeds forward, advances input, and stores canonical state. `finup2x` handles existing buffered bytes from `struct __sha256_ctx`, loops over paired data blocks, constructs padding and count-only blocks when needed, and writes two byte-swapped 32-byte digests.

## State, Dependencies, Risks, And Tests
The transform mutates state; `finup2x` treats `ctx` as read-only and writes outputs. It depends on SHA-NI dispatch in `sha256.h` and hard-coded context offsets guarded by C static assertions. Risks include `finup2x` precondition violations (`len >= 64`, same length, `len <= 65536`), tail-buffer assumptions, and state ordering mistakes. Tests should compare transform and finup outputs to generic SHA-256 across buffered lengths 0..63 and padding boundaries 56/64/120.
