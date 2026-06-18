<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/__init__.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/__init__.py

## Purpose
This empty marker makes the kernel-doc helper directory importable as the `kdoc` Python package.

## Important APIs, Types, and Functions
The file defines no names. Functional modules include tokenization, parser support, file orchestration, output formatting, YAML fixtures, and list transforms.

## Control Flow and State
There is no runtime logic, mutable state, or persistence behavior.

## Dependencies and Integration Points
Several modules use package imports such as `from kdoc.kdoc_parser import KernelDoc` and `from kdoc.kdoc_output import OutputFormat`, so this marker supports package-style imports.

## Risks and Test Signals
Adding import-time work here would slow or alter all kdoc CLI invocations. Removing it can break package imports depending on Python execution context. Basic import smoke tests for `kdoc.c_lex`, `kdoc.kdoc_files`, and `kdoc.kdoc_output` cover it indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/__init__.py -->
