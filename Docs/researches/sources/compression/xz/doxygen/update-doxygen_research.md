<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doxygen/update-doxygen -->
# sources/compression/xz/doxygen/update-doxygen

Purpose: wrapper script for generating versioned Doxygen HTML documentation for liblzma API or XZ Utils internals.

Important APIs/types/functions: `show_usage`, modes `api` and `internal`, optional absolute source/output directories, `build-aux/version.sh`, `doxygen -q -`, and appended Doxyfile overrides.

Control flow: validate mode and doxygen availability, resolve in-tree or out-of-tree paths, check Doxyfile/output directory, compute package version, remove old target docs, pipe base Doxyfile plus mode-specific overrides into Doxygen.

State and persistence: deletes and recreates `doc/api` or `doc/internal` under the chosen output directory.

Dependencies and integration: depends on `/bin/sh`, Doxygen, source-tree layout, and `build-aux/version.sh`. Called by documentation build workflows.

Risks: uses `rm -rf` on computed output subdirectories; path validation limits but does not eliminate operator mistakes. Output directory must preexist.

Test signals: run `update-doxygen api` and `internal`, verify generated HTML contains current package version and correct input scope.
<!-- END_FILE_RESEARCH: sources/compression/xz/doxygen/update-doxygen -->
