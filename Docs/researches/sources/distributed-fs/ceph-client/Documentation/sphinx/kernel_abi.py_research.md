# sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_abi.py

Purpose: this Sphinx extension implements the `kernel-abi` reStructuredText directive, rendering parsed Linux ABI documentation into the Sphinx doctree.

Important APIs, types, and functions: module initialization reads `srctree` from the environment, adds `tools/lib/python` to `sys.path`, imports `abi.abi_parser.AbiParser`, and defines global ABI path `Documentation/ABI`. `get_kernel_abi()` lazily creates and parses a singleton `AbiParser`, then runs issue checks. `KernelCmd` is the directive class with required ABI path argument and options `debug`, `no-symbols`, and `no-files`. `run()` iterates `kernel_abi.doc()` records, optionally wraps generated reST in a code block, adds source dependencies via `env.note_dependency()`, and parses content symbol by symbol through `do_parse()`.

Control flow: Sphinx loads `setup()`, registers the directive, and later `KernelCmd.run()` validates file insertion, selects display mode, streams ABI parser output into `ViewList`, notes dependencies when input files change, nested-parses each symbol-sized chunk, logs summary counts, and returns section children.

State and persistence: `_kernel_abi` caches parsed ABI data for the process. Sphinx environment dependencies persist in the build environment cache. No source files are modified.

Dependencies and integration: depends on `srctree`, `tools/lib/python/abi/abi_parser.py`, docutils directive APIs, Sphinx logging, and `switch_source_input` for correct source attribution.

Risks: missing `srctree` fails at import time. The singleton parser may hold stale data if files change within one process. Large ABI output is parsed incrementally to avoid Sphinx parser limits, but errors still surface through nested parsing. Test signals include Sphinx builds using `kernel-abi`, debug/no-symbols/no-files combinations, dependency invalidation after ABI file edits, and import behavior when `srctree` is unset.
