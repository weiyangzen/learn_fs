<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kerneldoc.py -->
# sources/distributed-fs/ceph-client/Documentation/sphinx/kerneldoc.py

## Purpose
Sphinx extension that implements the Linux documentation `kernel-doc` directive. It converts kernel-doc comments from C source files into ReST during documentation builds by using the in-tree Python `kdoc` library instead of shelling out to `tools/docs/kernel-doc`.

## Important APIs, Types, And Functions
- `KernelDocDirective` is the directive implementation registered as `kernel-doc`.
- Directive options include `doc`, `export`, `internal`, `identifiers`, `no-identifiers`, and legacy alias `functions`.
- `handle_args()` converts directive arguments/options into `KernelFiles.parse()` and `KernelFiles.msg()` argument dictionaries while also building a diagnostic command string.
- `parse_msg()` consumes generated ReST, strips `.. LINENO` markers, and preserves source line offsets for Sphinx diagnostics.
- `run_kdoc()` calls the shared `KernelFiles` instance and nests returned ReST into the document.
- `setup_kfiles()` initializes global `kfiles` with `RestFormat`.

## Control Flow
At Sphinx builder initialization, `setup_kfiles()` constructs a global parser. When a directive is encountered, `run()` calls `handle_args()`, records source/export-file dependencies, translates filtering options into symbol and export arguments, and invokes `run_kdoc()`. Generated output is parsed into a temporary section through `switch_source_input()` so errors are attributed to the original kernel-doc output lines.

## State And Persistence
The module depends on `srctree` from the environment and mutates `sys.path` to import kernel documentation helpers. Persistent build state is limited to Sphinx dependency tracking via `env.note_dependency()`. The global `kfiles` parser may cache kernel-doc information across directive invocations within a build.

## Dependencies And Integration Points
Integrates with docutils directives, Sphinx config values `kerneldoc_srctree` and `kerneldoc_verbosity`, `tools/lib/python/kdoc`, and source files under the configured kernel tree. It reports a command-line equivalent using `tools/docs/kernel-doc` for debugging even though normal execution uses Python classes.

## Risks And Edge Cases
Missing `srctree`, import-path changes, missing `kfiles` initialization, or exceptions from the parser produce a warning and a generic error node. Globbed export files are silently absent if patterns do not match. The directive declares parallel safety while sharing a module-level `kfiles`, so parser internals must remain safe for Sphinx parallel reads.

## Test Signals
Healthy signals are successful `make htmldocs`/`make pdfdocs`, correct dependency rebuilds when referenced source or export files change, expected output for `:doc:`, `:export:`, `:internal:`, identifier filtering, and line-accurate warnings for malformed kernel-doc comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kerneldoc.py -->
