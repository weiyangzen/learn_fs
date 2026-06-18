# sources/control-plane/external-snapshotter/release-tools/boilerplate/boilerplate.py

Purpose: verifies that source files contain the expected Kubernetes license boilerplate for their extension or basename.

Important APIs/functions: argument parsing for filenames/rootdir/boilerplate-dir/verbose, `get_refs`, `file_passes`, `file_extension`, `normalize_files`, `get_files`, `get_regexs`, and `main`.

Control flow: loads reference boilerplate text files by extension, discovers target files from explicit args or a tree walk, skips vendor/generated/cache paths, strips Go build tags and shell/Python shebangs, compares the beginning of each file against the reference after normalizing years, and prints failing filenames.

State and persistence: read-only over the repository; writes failures to stdout and optional verbose diagnostics to stderr.

Dependencies and integration: Python standard library only. Used by release-tools verification scripts and Prow.

Risks and test signals: exits with status `0` even when files fail because it prints failures rather than returning nonzero; callers must interpret output. Assumes every extension has a matching boilerplate reference and that year ranges start at 2014.
