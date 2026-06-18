<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/boilerplate/boilerplate.py -->
# sources/control-plane/csi-driver-smb/release-tools/boilerplate/boilerplate.py

Purpose: Scans repository files and reports those whose license boilerplate headers do not match reference templates.

Important APIs/functions: CLI arguments accept optional file names, `--rootdir`, `--boilerplate-dir`, and `--verbose`. `get_refs` loads `boilerplate.*.txt` templates by extension or basename. `file_passes` reads a file, strips Go build constraints and shell/Python shebangs, compares the top lines against the reference after normalizing one date to `YEAR`, and emits verbose diffs. `file_extension`, `normalize_files`, `get_files`, and `get_regexs` support filtering. `main` prints failing paths.

Control flow: Without explicit files, it walks the root directory while pruning skipped directories, filters by template extensions, tests each file, and prints only failures. It returns 0 even when failures are found; callers decide failure by checking non-empty output.

State and persistence behavior: Read-only scanner; no persistent changes.

Dependencies and integration points: Called by `verify-boilerplate.sh`. Template files in the same directory define supported file types. Uses Python stdlib only.

Risks: The date substitution stops after the first matching line, so unconventional headers with multiple date fields may not normalize as expected. Returning 0 for failures is intentional for shell capture but surprising if run directly.

Test signals: The verify wrapper treats any output as failure. There are no in-file unit tests despite a comment in the wrapper about unit test output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/boilerplate/boilerplate.py -->
