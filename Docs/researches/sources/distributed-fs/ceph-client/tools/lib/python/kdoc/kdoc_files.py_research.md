<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_files.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_files.py

## Purpose
This module orchestrates kernel-doc parsing across files and directories. It finds C sources, configures parser/output behavior, parses documentation and exported symbols, and yields formatted messages.

## Important APIs, Types, and Functions
- `GlobSourceFiles` recursively yields files with configured extensions from explicit files or directories, optionally under `srctree`.
- `KdocConfig` stores verbosity, warning policy, warning categories, logger, and a replaceable `warning` callback.
- `KernelFiles` is the main controller.
- `KernelFiles.parse_file` runs `KernelDoc.parse_kdoc`, caches entries and export tables, and optionally stores source for YAML tests.
- `process_export_file` parses only `EXPORT_SYMBOL*` macros.
- `file_not_found_cb`, `warning`, and `error` count diagnostics.
- `__init__` resolves verbosity from `KBUILD_VERBOSE`, warning mode from arguments/env, output style, transforms, YAML test output, `SRCTREE`, and internal caches.
- `parse(file_list, export_file=None)` processes input docs and export-only files.
- `msg(...)` applies filters and yields `(fname, msg)` output tuples or writes YAML test files.

## Control Flow and State
The controller caches parsed files in `files`, export-parsed files in `export_files`, per-file parser results in `results`, and export symbol sets in `export_table`. Output filtering combines explicit symbols, exported/internal mode, no-symbol exclusions, line-number mode, and doc-section suppression.

## Dependencies and Integration Points
It depends on `KernelDoc`, `CTransforms`, `OutputFormat`, and `KDocTestFile` modules. It also reads build environment variables and is the primary bridge between CLI arguments and parser/output modules.

## Risks and Test Signals
The `KCFLAGS` `-Werror` regex includes a trailing slash in the pattern, likely preventing intended matches. `export_file` defaults can cause current file exports to be parsed repeatedly unless caches work correctly. Directory traversal follows real directories but not symlink directories. Tests should cover file discovery, missing files, caching, export/internal filters, env-driven verbosity/werror, YAML mode, and no-doc-section filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_files.py -->
