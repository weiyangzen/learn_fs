# sources/distributed-fs/orangefs/src/io/description/dist-simple-stripe.c

## Purpose
Implements the default simple stripe distribution that round-robin stripes fixed-size strips across all selected data files.

## Important APIs, Types, And Functions
Defines methods for `logical_to_physical_offset`, `physical_to_logical_offset`, `next_mapped_offset`, `contiguous_length`, `logical_file_size`, parameter encode/decode, registration/unregistration, params string, block-size reporting, and exports `PINT_dist simple_stripe_dist`.

## Control Flow
Logical-to-physical divides the logical offset into full global stripes and leftover bytes, then determines whether the leftover belongs to this server's strip. Physical-to-logical reverses by combining physical strip number, server number, and strip remainder. `logical_file_size` maps each server's physical size back to a logical endpoint and returns the maximum. `next_mapped_offset` moves arbitrary logical offsets to the next byte mapped to this server. Registration exposes `strip_size` to default parameter setting.

## State And Persistence
Static state is default `PVFS_simple_stripe_params` and method table. Per-file distribution copies hold their own parameter blob after creation/decoding.

## Dependencies And Integration Points
Uses distribution registry APIs, PVFS encode helpers, `pvfs2-dist-simple-stripe.h`, and `pvfs2-util.h`. Called by request distribution logic through `PINT_dist_methods`.

## Risks And Test Signals
Risks include divide/modulo by zero if strip size is invalid, subtle off-by-one handling around exact strip boundaries, and `next_mapped_offset` handling negative modulo cases. Tests should round-trip physical/logical offsets across multiple server counts, strip sizes, boundary offsets, logical file size reconstruction, and parameter encode/decode.
