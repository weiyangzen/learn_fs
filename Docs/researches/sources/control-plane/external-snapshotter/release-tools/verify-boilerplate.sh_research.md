<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-boilerplate.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-boilerplate.sh

## Purpose
`verify-boilerplate.sh` enforces Kubernetes license/header boilerplate across a repository by delegating the actual scan to `boilerplate/boilerplate.py`.

## Important APIs, Types, and Functions
The script sets `errexit`, `nounset`, and `pipefail`, resolves `TOOLS`, `ROOT`, and `boiler`, and uses `mapfile -t files_need_boilerplate < <("${boiler}" --rootdir="${ROOT}" --verbose)`. It defines a `cleanup` trap that removes a temporary file, although that file is not used by the final check.

## Control Flow, State, and Persistence
It ensures a `python` command exists by installing an alternatives link to Python 3 when missing, resolves the target root, runs the boilerplate scanner, prints each offending file, exits 1 on any violation, and prints `Done` otherwise. Persistent side effects can include modifying `/usr/bin/python` alternatives when run with sufficient privilege.

## Dependencies and Integration Points
It depends on Bash, Python, `update-alternatives`, the release-tools `boilerplate.py`, and repository source files. It is normally called from `make verify` or release-tools CI.

## Risks and Test Signals
Risks include requiring root privileges for `update-alternatives`, a cleanup trap declared before function definition but valid at exit time, and relying entirely on `boilerplate.py` for file filtering. Test signals are zero files returned by the scanner and the `Done` message.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-boilerplate.sh -->
