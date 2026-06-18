# sources/cloud-native/ostree/tests/test-symbols.sh

## Purpose
This shell test enforces the public libostree symbol ABI and documentation contract.

## Important APIs, Types, And Functions
It uses released and optional devel symbol files, `eu-readelf`, `grep`, `sed`, `sort`, `diff`, `assert_file_has_content_once`, `assert_not_file_has_content`, documentation file `apidoc/ostree-sections.txt`, and `sha256sum -c`.

## Control Flow
The script builds `expected-symbols.txt` from symbol definition files and `found-symbols.txt` from exported dynamic symbols in `.libs/libostree-1.so`, then diffs them. It checks the example devel symbol exists only in devel symbols and not released symbols. It filters private exceptions and verifies all public symbols are documented. Finally it checks the released symbol file SHA-256, with a comment that it should change only in release commits.

## State And Persistence
Temporary expected/found text files are written in the test directory. It reads build artifacts and source symbol/docs files but does not modify them.

## Dependencies And Integration Points
This integrates build-system output, ELF symbol versioning, API docs, devel feature gating, and release ABI policy.

## Risks
Any new public symbol must update symbol files, documentation, and sometimes the release checksum. Tooling availability (`eu-readelf`) and symbol version grep patterns are required.

## Test Signals
Three TAP results cover exported symbols, documented symbols, and released symbol checksum stability.
