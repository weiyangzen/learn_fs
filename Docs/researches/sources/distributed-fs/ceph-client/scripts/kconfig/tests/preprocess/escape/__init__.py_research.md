# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/escape/__init__.py

## Purpose
This pytest module validates preprocessor escaping behavior.

## Important APIs, Types, and Functions
The test runs `conf.oldaskconfig()` and matches stderr against `expected_stderr`.

## Control Flow
All warnings should be emitted, and parsing should exit successfully.

## State and Persistence
Only stderr output is checked.

## Dependencies and Integration Points
Depends on the escape Kconfig fixture and preprocessor implementation.

## Risks and Edge Cases
Text expectations are sensitive to quote and whitespace preservation.

## Test Signals
Pass means literal dollar/paren/comma handling remains correct.
