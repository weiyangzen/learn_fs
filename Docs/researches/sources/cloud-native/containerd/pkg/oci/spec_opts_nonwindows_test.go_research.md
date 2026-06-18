# sources/cloud-native/containerd/pkg/oci/spec_opts_nonwindows_test.go

Purpose: tests non-Windows default PATH injection.

Important APIs/types/functions: `TestWithDefaultPathEnv` applies `WithDefaultPathEnv` to a spec and asserts the expected Unix PATH appears in `s.Process.Env`.

Control flow: create spec, apply option, inspect env.

State/persistence: none.

Dependencies/integration: same-package test for the build-tagged non-Windows implementation.

Risks: narrow coverage; it does not test replacement of a preexisting PATH or interaction with other env vars in this file, though shared env tests cover merge behavior.

Test signals: guards the exact default PATH string used by non-Windows containers.
