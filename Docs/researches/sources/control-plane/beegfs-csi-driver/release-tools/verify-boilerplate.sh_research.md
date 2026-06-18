# sources/control-plane/beegfs-csi-driver/release-tools/verify-boilerplate.sh

Purpose: CI wrapper that verifies source files contain the expected boilerplate headers.

Important APIs/types/functions: Sets strict bash options, ensures `python` exists by creating an `update-alternatives` link to python3 if missing, locates `TOOLS` and `ROOT`, invokes `boilerplate/boilerplate.py --rootdir --verbose`, and fails if returned file list is non-empty.

Control flow: Creates a temp file and trap cleanup, runs the Python checker into a bash array with `mapfile`, prints each offending file, exits 1 on failures, or prints `Done` on success.

State and persistence: May modify system alternatives by installing `/usr/bin/python` link, which is a significant side effect in CI images. Creates and removes a temp file that is otherwise unused.

Dependencies and integration points: Called by `.prow.sh` and likely `make test` targets. Depends on bash, Python, and `boilerplate.py`.

Risks: Attempting `update-alternatives --install` requires permissions and assumes Debian-like systems. The temp file is not used except cleanup. Because `boilerplate.py` itself exits zero, this wrapper must correctly check output length.

Test signals: Emits offending file paths and exits nonzero when headers are wrong.
