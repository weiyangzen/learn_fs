# sources/cloud-native/containerd/pkg/oci/spec_opts_unix_test.go

Purpose: Unix-specific tests for image config defaults and umask option.

Important APIs/types/functions: `TestWithImageConfigNoEnv` verifies default Unix environment is applied when image config has no env. `TestWithUmask_SetsUmaskOnEmptySpec` and `TestWithUmask_WithDefaultSpec` assert `WithUmask` initializes process state and stores a pointer to the requested umask value.

Control flow: create fake image/spec, apply options, inspect process env and user umask fields.

State/persistence: in-memory fake image content only.

Dependencies/integration: uses shared fake image helpers from `spec_opts_test.go`.

Risks: does not cover invalid umask ranges because the option stores raw uint32 without validation.

Test signals: guards default Unix env fallback in image config and confirms `WithUmask` works both before and after default spec population.
