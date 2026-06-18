# sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_feat.py

Purpose: this Sphinx extension implements the `kernel-feat` directive, rendering kernel feature matrix data from `Documentation/features` or a requested feature subdirectory.

Important APIs, types, and functions: it reads `srctree`, adds `tools/lib/python`, imports `feat.parse_features.ParseFeature`, defines `ErrorString()`, and registers `KernelFeat`. The directive accepts one required path argument and optional second architecture argument, with a `debug` option. `warn()` formats Sphinx warnings, though it is not used in the visible control path. `run()` creates `ParseFeature(feature_dir, False, True)`, parses features, emits either `output_arch_table(arch)` or `output_matrix()`, strips dependency marker lines matching `.. FILE <path>`, and nested-parses the generated reST. `nestedParse()` optionally wraps output in a code block for debug mode.

Control flow: during directive execution, feature files are parsed, generated text is scanned line by line, file marker lines become Sphinx dependencies via `env.note_dependency()`, and all other lines are parsed into a temporary section node returned to the doctree.

State and persistence: runtime state is local to directive execution. Sphinx dependency records persist in the build environment cache. No files are modified.

Dependencies and integration: depends on `srctree`, `tools/lib/python/feat/parse_features.py`, the Sphinx/docutils directive stack, and feature files under `Documentation/<argument>`.

Risks: missing `srctree` fails at import. The `buf` tuple in `nestedParse()` is assigned but unused, suggesting leftover code. `app.warn` used by `warn()` is deprecated/removed in newer Sphinx versions, though the method is not on the main path. Test signals include matrix and per-arch directive builds, debug rendering, dependency detection from `.. FILE` markers, and feature parse failures.
