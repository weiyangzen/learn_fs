# sources/control-plane/csi-driver-iscsi/release-tools/boilerplate/boilerplate.py

Purpose: validates that source files contain the expected Kubernetes copyright/license boilerplate for their extension or basename.

Important APIs and types: argparse options accept explicit filenames, `--rootdir`, `--boilerplate-dir`, and `--verbose`. Core functions are `get_refs`, `file_passes`, `file_extension`, `normalize_files`, `get_files`, `get_regexs`, and `main`.

Control flow: reference boilerplates are loaded from `boilerplate.*.txt`. Candidate files are either supplied explicitly or discovered by walking the root, pruning skipped directories. For Go files, leading build constraints are stripped; for shell and Python files, shebangs are stripped. The header is normalized by replacing a year with `YEAR` and compared to the reference. Failing paths are printed to stdout, with optional diffs to stderr.

State and persistence: read-only filesystem scan. It opens `/dev/null` when not verbose.

Dependencies and integration: used by `verify-boilerplate.sh`; depends on Python standard library modules `argparse`, `difflib`, `glob`, `os`, `re`, `sys`, and `datetime`.

Risks: `refs[extension]` and `refs[basename]` assume a matching boilerplate exists. The skipped directory list is substring based and may skip unexpected paths. It returns exit code 0 even when files fail; the wrapper enforces failure by inspecting stdout.

Test signals: wrapper execution in Prow and GitHub CI reveals missing or malformed headers.
