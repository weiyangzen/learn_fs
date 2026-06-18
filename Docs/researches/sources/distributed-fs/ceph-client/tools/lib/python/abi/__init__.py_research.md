<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/__init__.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/__init__.py

## Purpose
This empty package marker makes the ABI documentation tooling directory importable as `abi`.

## Important APIs, Types, and Functions
The file exports no symbols directly. Functional code lives in `abi_parser.py`, `abi_regex.py`, `helpers.py`, and `system_symbols.py`.

## Control Flow and State
There is no runtime control flow or stored state.

## Dependencies and Integration Points
Modules in this package use absolute imports such as `from abi.helpers import AbiDebug`, so the package marker supports those import paths when `tools/lib/python` is on `PYTHONPATH`.

## Risks and Test Signals
Removing or populating this file incorrectly could break imports or introduce unintended import-time side effects. Basic import tests for `abi.abi_parser`, `abi.abi_regex`, and `abi.system_symbols` cover this marker indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/__init__.py -->
