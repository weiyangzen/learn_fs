# sources/cloud-native/containerd/pkg/oci/spec_opts_nonwindows.go

Purpose: non-Windows default PATH option for OCI process specs.

Important APIs/types/functions: `WithDefaultPathEnv` sets or replaces `PATH` with `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` through `WithEnv`.

Control flow: option delegates to env merge logic, so an existing `PATH` entry is replaced while other environment variables are preserved.

State/persistence: generated spec process environment only.

Dependencies/integration: selected on all non-Windows platforms. Used by callers that want Docker-like default Unix PATH behavior.

Risks: hardcoded Unix path may be inappropriate for unusual images or minimal rootfs layouts. It only mutates the spec and does not verify path existence.

Test signals: `spec_opts_nonwindows_test.go` verifies exact PATH value and replacement behavior.
