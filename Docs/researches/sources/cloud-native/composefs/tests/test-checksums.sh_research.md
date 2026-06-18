# sources/cloud-native/composefs/tests/test-checksums.sh

## Purpose
This shell test verifies that known dump fixtures produce byte-stable composefs images with expected SHA-256 checksums, pass optional `fsck.erofs`, and round-trip through dump tools reproducibly.

## Important APIs, Types, And Functions
It sources `test-lib.sh`, checks for `fsck.erofs`, maintains a `nonstrict` associative array, and loops over formats/assets. It invokes `mkcomposefs --from-file`, `sha256sum`, `composefs-dump`, and `composefs-info dump`.

## Control Flow
For each fixture, it detects `.gz`, optional version constraints, strict parse mode, builds an image, optionally runs fsck, checks dump reproduction via `composefs-dump`, checks text dump piped back to `mkcomposefs`, and compares the image checksum to the fixture `.sha256`.

## State And Persistence
Uses temporary image files and removes them via trap. Environment variable `CFS_PARSE_STRICT` is set/unset per fixture.

## Dependencies And Integration Points
Depends on built tools, assets, gzip, sha256sum, optional fsck.erofs, and `VALGRIND_PREFIX`.

## Risks
Checksum tests are intentionally brittle: any legitimate image-layout change requires fixture checksum updates. Non-strict fixture exceptions document tolerated legacy malformed inputs.

## Test Signals
High-value regression signal for deterministic serialization, loader/dumper reproducibility, parser strictness, and EROFS structural validity.
