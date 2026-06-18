# sources/compression/lz4/tests/test-lz4-testmode.sh

## Purpose
This shell test validates benchmark decode-only mode, test-mode rejection of uncompressed input, pass-through behavior under force flags, and clean errors for missing sources.

## Important Control Flow
It runs `lz4 -bi0`, creates a compressed file, tests decode-only benchmark modes with and without CRC, then expects `lz4 -t` and `lz4 -tf` on generated raw data to fail. It creates plaintext `.lz4` and normal files to check pass-through failures/successes for `-dc`, `-df`, `-dcf`, and multi-file force mode. Missing-file commands must fail.

## State, Dependencies, and Integration
Temporary files use `tmp-ltm*`. Dependencies are `datagen`, `lz4`, shell redirection, and `test`-style exit checks. It exercises CLI mode selection and error paths.

## Risks and Test Signals
The script gives clear signals that test mode is not pass-through mode and that force changes pass-through semantics. It does not compare pass-through output contents except by successful execution and visible stdout.
