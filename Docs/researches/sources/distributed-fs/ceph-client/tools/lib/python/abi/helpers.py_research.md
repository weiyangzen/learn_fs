<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/helpers.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/helpers.py

## Purpose
This helper module defines shared constants and debug bit flags for the ABI documentation parser and live-system symbol checker.

## Important APIs, Types, and Functions
- `ABI_DIR = "Documentation/ABI/"` centralizes the path fragment used by parsers to recognize ABI documentation roots.
- `class AbiDebug` defines integer bit flags for parser state, file opens, structure dumps, undefined-symbol diagnostics, regex conversion, subgroup maps/dicts/sizes, and graph output.
- `DEBUG_HELP` documents the flags for CLI help or diagnostics.

## Control Flow and State
The module has no dynamic control flow beyond class and constant definition.

## Dependencies and Integration Points
It is imported by `abi_parser.py`, `abi_regex.py`, and `system_symbols.py`. The flags are used as bitmasks, so callers can combine debug categories.

## Risks and Test Signals
Flag values are part of the CLI/debug contract; changing values can break saved invocations or documentation. The help string has a typo in "reference", but it does not affect behavior. Import tests and CLI debug-option tests cover this file indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/helpers.py -->
