<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/kernel-doc -->
# sources/distributed-fs/ceph-client/tools/docs/kernel-doc

Purpose: Python implementation of the kernel-doc extractor. It reads C source/header files, parses `/** ... */` documentation comments, and prints ReST, manpage, YAML, or warnings-only output.

Important APIs/types/functions: `MsgFormatter` preserves legacy capitalized warning/error prefixes. `main()` defines the CLI. Selection flags include `--export`, `--internal`, `--symbol`, `--nosymbol`, and `--no-doc-sections`; warning controls include `--wreturn`, `--wshort-desc`, `--wall`, and `--werror`; output controls include `--man`, `--rst`, `--none`, `--yaml`, and `--kdoc`. After Python-version checks it imports `kdoc.kdoc_files.KernelFiles` and output formatters `RestFormat`/`ManFormat`.

Control flow: Argparse normalizes warning flags, logging is configured, Python versions below 3.6 are rejected except for `--none`, and output mode is chosen. `KernelFiles.parse()` indexes input and export files, then `kfiles.msg()` yields selected rendered messages which are printed to stdout. Exit code is `3` only when warnings exist and `--werror` is set.

State and persistence: No persistent local state unless `--yaml` writes a requested YAML file. Runtime state includes parsed comments, export-symbol maps, warning counters, and selected output formatter.

Dependencies/integration: Integrated into Sphinx documentation builds through `.. kernel-doc::` directives and wrapper scripts. Depends on kernel-local `tools/lib/python/kdoc` modules and C/UAPI source files.

Risks/tests: Parser behavior is compatibility-sensitive because many documentation builds depend on legacy Perl-compatible output and exit semantics. Test signals include the kernel-doc parser unit tests, representative C files with functions/structs/enums/DOC sections, export/internal filtering, YAML round trips, old Python graceful-failure behavior, and `--werror` return-code checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/kernel-doc -->
