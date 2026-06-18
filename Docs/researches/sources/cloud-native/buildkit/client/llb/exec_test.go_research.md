# sources/cloud-native/buildkit/client/llb/exec_test.go

Purpose: regression tests for exec operation mount validation, output index stability, Linux resource metadata, and deterministic marshaling.

Important APIs/types/functions: `TestTmpfsMountError`, `TestValidGetMountIndex`, `TestLinuxResourcesMarshal`, `TestLinuxResourcesNotInCacheKey`, `TestLinuxResourcesMerge`, and `TestExecOpMarshalConsistency`.

Control flow: tests build LLB states with exec options, marshal them, inspect protobuf definitions/metadata, and compare repeated marshals. Tmpfs tests distinguish using tmpfs output as parent, valid scratch tmpfs mount, and invalid tmpfs with non-scratch source. Mount-index test verifies sorted tmpfs mounts do not shift writable mount output indexes. Resource tests verify `OpMetadata.LinuxResources` and that resources do not alter op bytes/cache key.

State and persistence: in-memory marshaled definitions only.

Dependencies/integration points: exec options, file ops for mount sources, protobuf metadata, and parse helpers.

Risks/test signals: strong coverage for subtle deterministic-index and cache-key behavior. It does not cover all secrets, SSH, CDI, network, security, proxy, or cache mount modes.
