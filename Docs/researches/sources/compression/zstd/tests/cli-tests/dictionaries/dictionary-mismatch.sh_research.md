# sources/compression/zstd/tests/cli-tests/dictionaries/dictionary-mismatch.sh

## Purpose
This test verifies that a frame compressed with one dictionary can be tested with the matching dictionary but is rejected with a different or missing dictionary.

## APIs, control flow, and integration
It sources platform helpers and uses fixtures copied by `dictionaries/setup`: `files/0`, `dicts/0`, and `dicts/1`. It compresses `files/0` with `-D dicts/0`, tests the result with the same dictionary, then asserts `zstd -t` fails with `dicts/1` and with no dictionary. A disabled block documents how the dictionaries were originally generated.

## State, dependencies, risks, and test signals
State is `files/0.zst`. The test depends on the two fixture dictionaries having different IDs/content and on the decompressor enforcing dictionary identity. Risks include fixture regeneration accidentally producing compatible dictionaries. Pass confirms mismatch detection and missing-dictionary failure paths.
