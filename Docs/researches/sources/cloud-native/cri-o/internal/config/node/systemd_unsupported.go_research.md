# sources/cloud-native/cri-o/internal/config/node/systemd_unsupported.go

Purpose: provides non-Linux systemd feature stubs.

Important APIs/types/functions: `SystemdHasCollectMode`, `SystemdHasAllowedCPUs`, and `systemdSupportsProperty`. Both public checks return false; the helper returns false with nil error.

Control flow: no D-Bus probing.

State and persistence behavior: none.

Dependencies/integration points: selected on unsupported platforms to keep shared node validation code compiling.

Risks: all systemd-dependent feature detection is disabled on non-Linux builds.

Test signals: no tests.
