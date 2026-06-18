# sources/compression/zlib/MODULE.bazel

Purpose: Bazel module metadata for the zlib package.

Important APIs/settings: declares `module(name = "zlib", version = "0.0.0", compatibility_level = 1)` and `bazel_dep` entries for `platforms`, `rules_cc`, and `rules_license`.

Control flow: declarative Bzlmod configuration only; Bazel resolves dependencies before loading `BUILD.bazel`.

State and persistence: affects Bazel external dependency resolution; no source-tree mutation.

Dependencies and integration: paired with `BUILD.bazel` to make the package buildable under Bazel/Bzlmod.

Risks: version `0.0.0` is a placeholder, so consumers relying on module version semantics may need registry-provided metadata instead. Dependency versions must remain compatible with the BUILD file APIs.

Test signals: Bazel module resolution and `:z` build success are the main signals.
