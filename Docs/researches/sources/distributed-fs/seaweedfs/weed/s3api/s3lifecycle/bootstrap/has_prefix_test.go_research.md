# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/has_prefix_test.go

Purpose: pins coverage for the exported `bootstrap.HasPrefix` helper.

Important APIs/types: `TestHasPrefix` checks path/prefix combinations against `HasPrefix`.

Control flow: table-driven test compares expected booleans for matching, exact, non-matching, shorter path, empty prefix, both empty, and empty input.

State and persistence behavior: none.

Dependencies and integration points: uses testify `assert`. It documents the helper as a thin wrapper around `strings.HasPrefix`.

Risks: low. The helper is trivial; the main risk is that call sites might treat it as path-component aware, but it is byte-prefix only.

Test signals: complete behavioral coverage for the wrapper.
