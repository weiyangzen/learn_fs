# sources/distributed-fs/juicefs/pkg/object/gluster_test.go


Purpose: wires GlusterFS into JuiceFS shared object and filesystem contract tests.

Important APIs and flow: `TestGluster` checks `GLUSTER_VOLUME`, creates a Gluster backend with `newGluster`, and calls `testStorage`. `TestGluster2` does the same but calls `testFileSystem`.

State and persistence: tests mutate the configured external Gluster volume, so they are skipped unless explicitly configured.

Dependencies and integration: compiled only with the `gluster` build tag. Depends on `newGluster`, `testStorage`, and `testFileSystem`.

Risks and gaps: no unit-level mocking; failures require a live Gluster environment to reproduce. The constructor error is ignored in both tests, so a nil backend could cause less clear downstream failures. Coverage is broad when enabled but absent in default builds.

Test signal: environment-gated integration coverage for both object-store semantics and filesystem-specific semantics.
