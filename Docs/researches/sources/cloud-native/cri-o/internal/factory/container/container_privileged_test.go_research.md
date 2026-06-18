# sources/cloud-native/cri-o/internal/factory/container/container_privileged_test.go

Purpose: tests privileged-container gating against sandbox privilege state and nil Linux/security-context cases.

Important APIs/types/functions: exercises `SetConfig`, `SetPrivileged`, and `Privileged`.

Control flow: examples cover a privileged container in a privileged sandbox succeeding, an unprivileged container staying false, a privileged container in an unprivileged sandbox failing, and missing pod/container Linux or security context paths returning success while leaving `Privileged` false.

State and persistence behavior: in-memory CRI config only.

Dependencies/integration points: Ginkgo/Gomega and CRI API types.

Risks: tests do not assert exact error messages. Some duplicated cases have similar setup for missing container security context.

Test signals: good coverage for privilege escalation guard behavior.
