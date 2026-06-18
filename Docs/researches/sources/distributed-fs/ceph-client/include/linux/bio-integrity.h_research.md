# sources/distributed-fs/ceph-client/include/linux/bio-integrity.h

## Purpose
Declares block-layer data integrity payload support for bios, including protection information vectors, mapping helpers, cloning, trimming, and filesystem-generated integrity metadata.

## Important APIs, types, and functions
- `enum bip_flags` describes ownership, remapping, disk check suppression, checksum mode, user bounce buffer, guard/ref/app tag checks, and mempool ownership.
- `struct bio_integrity_payload` stores an integrity iterator, vector counts, flags, app tag, and integrity `bio_vec` array.
- `bio_integrity()`, `bio_integrity_flagged()`, `bip_get_seed()`, and `bip_set_seed()` are inline helpers when integrity support is enabled.
- Enabled APIs allocate/init payloads, add pages, map user or metadata iterators, unmap, prepare, advance, trim, and clone.
- Always-declared helpers allocate/free buffers, set up defaults, and generate/verify filesystem integrity metadata.

## Control flow and state
When a bio carries `REQ_INTEGRITY`, `bio_integrity()` returns its payload. Callers allocate/map integrity vectors, prepare them for the requested operation, advance them as data completes, and trim/clone with the parent bio. Filesystem helpers allocate/generate/verify protection metadata around bios.

## State and persistence behavior
Integrity payload state is attached to a bio for one I/O. Protection information may be written to disk or verified on read depending on device format and flags. User mapping may allocate bounce buffers that must be unmapped/freed correctly.

## Dependencies and integration points
Depends on `bio.h` and block integrity configuration. Integrated by block layer, filesystem direct I/O, devices with T10 PI/DIF/DIX-like protection, and metadata verification paths.

## Risks
Config-disabled stubs return `-EINVAL`, NULL, false, or no-op, so callers must handle absence. Seed sector must track remapping and trimming. Mismatched guard/ref/app tag flags can silently skip or over-apply checks.

## Test signals
Build with and without `CONFIG_BLK_DEV_INTEGRITY`; test user metadata mapping, cloning/splitting/trimming, remapped sector seeds, guard/ref/app tag verification, bounce-buffer cleanup, and filesystem generate/verify failures.
