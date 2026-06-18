<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry_test.go

Purpose: tests registry host transformation and Docker image reference parsing.

Important tests: `TestConvertToVPCHost1` verifies a normal Aliyun registry host gains a `-vpc` suffix on the first label and an already-VPC host is unchanged. `TestParseImage` validates multi-segment repository paths, no-namespace repositories, a normal remote image, and one invalid reference.

Control flow and state: table-driven tests call pure functions and compare exact structs/errors.

Dependencies/integration: uses Go `reflect.DeepEqual` and testing package only.

Risks and test signals: coverage is limited to happy path parsing plus one invalid syntax case. It does not test Docker Hub implicit domain behavior, digest-only references, localhost without port, empty host input to VPC conversion, or auth transport creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry_test.go -->
