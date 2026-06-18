# sources/compression/zlib/BUILD.bazel

Purpose: Bazel build definition for zlib, adapted from Bazel Central Registry and protobuf third-party packaging.

Important APIs/targets: loads `cc_library` and `license`; defines `:license`, `copy_public_headers` genrule, `mingw_gcc_compiler` config setting, public `cc_library(name = "z")`, and alias `:zlib`.

Control flow: `_ZLIB_HEADERS` enumerates internal/public headers. `copy_public_headers` copies headers into `zlib/include/` so `includes` propagation is contained. `cc_library :z` compiles core zlib sources and includes unprefixed headers in `srcs` to handle mixed quote/angle includes. `copts` vary for MinGW, Windows, and default platforms.

State and persistence: Bazel-generated header copies live under the genrule output tree, not the source tree. No runtime persistence.

Dependencies and integration: depends on `rules_cc`, `rules_license`, and `platforms` declared in `MODULE.bazel`. Exposes a public Bazel target for downstream users.

Risks: suppresses several compiler diagnostics on default platforms, which may hide issues outside CI. Header copying command assumes output directory layout exists as Bazel creates it. Source list must stay synchronized with zlib core files.

Test signals: no tests are defined here; build success validates compilation only.
