# sources/cloud-native/nydus/contrib/nydusify/pkg/compactor/compactor_test.go

Purpose: tests compactor configuration and command wrapper behavior.

Important APIs and flow: `TestCompactConfigRoundTrip` writes and reloads JSON config. `TestNewCompactor` validates defaults, workdir-assigned `BlobsDir`, and missing config errors. `TestCompactorCompact` uses fake `nydus-image` scripts to assert compact arguments are issued and stale outputs are removed, and checks builder failure wrapping.

State and persistence: uses temporary directories, fake executable scripts, bootstrap files, and stale output files.

Dependencies and integration: verifies CLI wrapper plumbing without requiring real compaction.

Risks and test signals: strong for config and command invocation. It does not inspect the complete argument vector in order or validate compact output bootstrap contents.
