# sources/compression/lz4/tests/test-lz4-dict.sh

## Purpose
This shell test validates dictionary compression/decompression behavior, including normal dictionaries, empty dictionaries, stdin-loaded dictionaries, and dictionary tail truncation to the last 64 KiB.

## Important Control Flow
It builds sample files with `datagen`, compresses using `lz4 -D`, decompresses with `lz4 -dD`, and compares streams with `diff`. It measures compressed sizes with and without a dictionary to ensure the dictionary improves compression for the generated corpus. A loop tests dictionary lengths around important boundaries from 0 through 131073 bytes and uses `dd` to generate the expected 64 KiB tail.

## State, Dependencies, and Integration
State is temporary `tmp-dict*` files. Dependencies include `datagen`, `lz4`, `dd`, `wc`, `diff`, and shell arithmetic. The script tests CLI dictionary plumbing and indirectly validates frame dictionary-id-independent decoding behavior when the same dictionary bytes are provided.

## Risks and Test Signals
Strong signals include round-trip correctness, dictionary effectiveness, zero-length dictionary handling, and boundary behavior around 32 KiB/64 KiB/128 KiB. The compression-efficiency assertion depends on deterministic generated data and may be sensitive to algorithm changes that are correct but less favorable for this corpus.
