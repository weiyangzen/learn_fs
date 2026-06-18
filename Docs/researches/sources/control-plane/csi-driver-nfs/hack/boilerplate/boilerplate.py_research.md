<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/boilerplate/boilerplate.py -->
# sources/control-plane/csi-driver-nfs/hack/boilerplate/boilerplate.py

## Purpose
Checks repository files for required Kubernetes license boilerplate headers. It is used by the boilerplate verification script to list files whose header does not match the language-specific template.

## Important APIs, Types, and Functions
The script uses `argparse` options for file names, `--rootdir`, `--boilerplate-dir`, and `--verbose`. Key functions are `get_refs()`, `file_passes()`, `file_extension()`, `normalize_files()`, `get_files()`, `get_regexs()`, and `main()`. Reference templates are loaded from `boilerplate.*.txt` and matched by extension or basename.

## Control Flow, State, and Persistence
It walks the root directory unless explicit file names are provided, prunes skipped directories such as vendor and `.git`, selects files with supported extensions, strips Go build constraints and script shebangs before comparing, normalizes real years to `YEAR`, and prints failing file paths to stdout. It does not mutate the repository.

## Dependencies and Integration Points
It depends only on Python standard library modules and local boilerplate templates. `hack/verify-boilerplate.sh` invokes it with `--rootdir` and `--verbose` and treats any printed path as a failure.

## Risks and Test Signals
Risks include brittle path defaults, missing template keys for unusual extensions, `/dev/null` assumptions for quiet mode, and false failures from new build-tag/shebang shapes. Signals are empty stdout for a clean tree, verbose unified diffs for bad headers, and coverage of Go, shell, Python, Makefile, Dockerfile, and Bazel templates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/boilerplate/boilerplate.py -->
