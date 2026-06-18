# sources/control-plane/csi-driver-iscsi/release-tools/verify-boilerplate.sh

Purpose: enforcement wrapper around `boilerplate/boilerplate.py`.

Important APIs and types: accepts an optional root directory, defaults to the parent of release-tools, ensures `python` exists by linking python3 through `update-alternatives` if necessary, and collects failing files with `mapfile`.

Control flow: sets strict shell options, resolves `TOOLS` and `ROOT`, executes the boilerplate checker in verbose mode, prints each failing file, and exits nonzero when any file lacks the expected header.

State and persistence: may modify system alternatives to provide `/usr/bin/python`. Creates a temp file and removes it on exit, although the temp file is not used for test output.

Dependencies and integration: used by release-tools `.prow.sh` and importing repo Prow scripts. Depends on bash, Python, and boilerplate reference files.

Risks: `update-alternatives` may require privileges and is surprising in a verifier. The unused temp file/trap is harmless but noisy.

Test signals: Prow verifier pass/fail and printed failing file list.
