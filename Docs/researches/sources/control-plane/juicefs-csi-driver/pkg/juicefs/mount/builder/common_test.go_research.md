# sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/common_test.go

Purpose: tests selected common builder helpers for metadata and init command generation.

Important APIs and functions: `TestGenMetadata` verifies delete-delay and clean-cache annotations, user labels/annotations, internal JuiceFS UUID/unique ID annotations, pod hash/upgrade labels, and that internal annotations override user-provided values. `TestGenInitCommand` checks raw format command retention, CE RSA key addition, EE RSA ignore behavior, init-config copy command generation, EE ACL symlink addition, and CE ACL ignore behavior.

Control flow: each table case constructs a minimal `config.JfsSetting` or `BaseBuilder`, invokes the helper, and compares exact maps or strings.

State and persistence behavior: no external state. Tests operate on in-memory settings only.

Dependencies and integration points: depends on common label/annotation constants and builder/config types. It gives focused regression signal for metadata consumed by mount-pod selection and graceful upgrade logic.

Risks and test signals: useful coverage for two helper surfaces, but it does not cover `genCommonJuicePod`, volume generation, lifecycle/probe behavior, metrics port parsing, mount command generation, job command generation, or serverless builders.
