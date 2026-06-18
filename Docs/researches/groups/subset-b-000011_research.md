# Group Research: subset-b-000011

This grouped report covers the BuildKit example, executor, resource-monitoring, attestation, and container-image exporter files assigned to `subset-b-000011`. Each source file has its own wrapped section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit4/buildkit.go -->
# Research: sources/cloud-native/buildkit/examples/buildkit4/buildkit.go

## Purpose
Example BuildKit LLB program that assembles a source-level BuildKit build graph for BuildKit, runc, and containerd artifacts.

## Important APIs, Types, and Functions
`buildOpt` carries version/output settings. `goBuildBase`, `goRepo`, `runc`, `containerd`, `buildkit`, and `prefixed` compose `llb.State` values using git sources, Go build steps, and copied outputs.

## Control Flow
`main` parses flags, builds an LLB state, marshals it to a definition, and writes stdout. Helpers fetch repositories, run Go builds, and copy selected artifacts into a prefixed result state.

## State and Persistence
No local daemon state is persisted; stdout contains the serialized LLB definition and BuildKit later owns cache/execution state.

## Dependencies and Integration Points
Depends on `client/llb` and `util/system`. Integrates with buildctl/gateway workflows that consume generated LLB.

## Risks and Edge Cases
Pinned versions and repository layouts can drift; generated graph debugging is harder than Dockerfile examples.

## Test Signals
No direct tests; signal is example compilation plus solver acceptance of emitted LLB.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit4/buildkit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/create-certs/Dockerfile -->
# Research: sources/cloud-native/buildkit/examples/create-certs/Dockerfile

## Purpose
Two-stage Dockerfile that generates daemon and client TLS certificate bundles for BuildKit examples using mkcert.

## Important APIs, Types, and Functions
Uses Alpine `gen` stage, `SAN` and `SAN_CLIENT` args, `mkcert`, and a final scratch export of `/certs`.

## Control Flow
Installs mkcert, writes SAN list, creates daemon and client cert/key pairs, copies the root CA to both bundles, removes root CA private material, and copies artifacts into scratch.

## State and Persistence
Persists generated PEM files in the build output image; no runtime state.

## Dependencies and Integration Points
Depends on Dockerfile frontend v1, Alpine edge testing, mkcert, and ca-certificates. Feeds Kubernetes and remote TLS BuildKit examples.

## Risks and Edge Cases
`alpine:edge` and testing repo reduce reproducibility; certs are development PKI and SAN quoting matters.

## Test Signals
No direct tests; validation is successful image build and TLS consumers starting correctly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/create-certs/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/dockerfile2llb/main.go -->
# Research: sources/cloud-native/buildkit/examples/dockerfile2llb/main.go

## Purpose
CLI example that converts a Dockerfile into BuildKit LLB JSON and optional metadata.

## Important APIs, Types, and Functions
`buildOpt`, `xmain`, and `writeJSON` use `dockerfile2llb.ConvertOpt`, `imagemetaresolver`, `dockerui`, `pb.Definition`, and appcontext/logrus.

## Control Flow
Reads CLI flags and Dockerfile input, configures frontend conversion, marshals the resulting definition, and writes JSON metadata when requested.

## State and Persistence
Only writes selected JSON outputs; no BuildKit daemon or cache state is mutated.

## Dependencies and Integration Points
Depends on Dockerfile frontend internals, solver protobufs, and image metadata resolver. Useful for inspecting Dockerfile frontend output and debugging LLB translation.

## Risks and Edge Cases
Frontend internal APIs and option names can drift; missing context/image metadata surfaces as conversion errors.

## Test Signals
Indirectly covered by Dockerfile frontend conversion tests, not by this example itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/dockerfile2llb/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/eksctl/bottlerocket.yaml -->
# Research: sources/cloud-native/buildkit/examples/eksctl/bottlerocket.yaml

## Purpose
eksctl cluster config for a Bottlerocket EKS node group suitable for BuildKit user namespace/rootless experiments.

## Important APIs, Types, and Functions
Declares `ClusterConfig` v1alpha5, cluster metadata, a `buildkit` node group, managed IAM policies, and Bottlerocket kernel sysctl `user.max_user_namespaces`.

## Control Flow
eksctl reads the YAML, creates cluster/node group resources, attaches IAM policies, and applies Bottlerocket settings.

## State and Persistence
State lives in AWS/EKS resources after application; this file is static desired state.

## Dependencies and Integration Points
Depends on eksctl schema, EKS/Bottlerocket support, AWS IAM policy names, and region/version availability. Supports the Kubernetes rootless/userns BuildKit manifests.

## Risks and Edge Cases
Pinned Kubernetes `1.27` can become unsupported; region, policies, and sysctl are example values needing review.

## Test Signals
No tests; validation is cluster creation and later BuildKit pod scheduling.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/eksctl/bottlerocket.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/gobuild/main.go -->
# Research: sources/cloud-native/buildkit/examples/gobuild/main.go

## Purpose
Programmatic Go build example using `llb-gobuild` to create BuildKit LLB for Go artifacts.

## Important APIs, Types, and Functions
`run` builds the graph. `copyAll`, `copyFrom`, and `copy` are `llb.StateOption` helpers for copying build outputs.

## Control Flow
Constructs Go build inputs, invokes the external gobuild helper, copies artifacts to a result state, marshals LLB to stdout.

## State and Persistence
No local persistent state besides stdout; BuildKit materializes artifacts/cache later.

## Dependencies and Integration Points
Depends on `client/llb` and `github.com/tonistiigi/llb-gobuild`. Demonstrates composing third-party LLB helper libraries with BuildKit.

## Risks and Edge Cases
Sensitive to llb-gobuild API/toolchain defaults and expected output paths.

## Test Signals
No direct tests; compilation and LLB solver acceptance are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/gobuild/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/consistenthash/main.go -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/consistenthash/main.go

## Purpose
Utility for selecting a BuildKit Kubernetes pod with consistent hashing.

## Important APIs, Types, and Functions
`xmain` reads stdin and argv; `doConsistentHash` builds a `hashring` and returns a node; `main` logs/exits.

## Control Flow
Reads pod names, validates a key, creates a ring from names, prints the selected pod.

## State and Persistence
No persistence; ring is rebuilt per invocation from live stdin.

## Dependencies and Integration Points
Depends on `serialx/hashring`, logrus, and pkg/errors. Pairs with `show-running-pods.sh` to route clients to stable BuildKit pods.

## Risks and Edge Cases
Empty/changing pod sets change routing; determinism only holds for the same node list.

## Test Signals
No direct tests; CLI behavior is small and library-backed.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/consistenthash/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/consistenthash/show-running-pods.sh -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/consistenthash/show-running-pods.sh

## Purpose
Shell helper that lists running Kubernetes BuildKit pods.

## Important APIs, Types, and Functions
Uses `kubectl get pods` with selector `app=buildkitd`, field selector `status.phase=Running`, Go template output, and name sorting.

## Control Flow
Sets strict shell flags, defines selector, and emits matching pod names one per line.

## State and Persistence
No state; reads current Kubernetes API state.

## Dependencies and Integration Points
Depends on kubectl, active context, and consistent labels. Feeds consistent-hash and scripting examples.

## Risks and Edge Cases
No namespace is specified, so active context/namespace mistakes matter.

## Test Signals
No tests; validate against a cluster with example manifests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/consistenthash/show-running-pods.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/create-certs.sh -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/create-certs.sh

## Purpose
Bash helper that generates mkcert TLS material and Kubernetes Secret YAMLs for BuildKit.

## Important APIs, Types, and Functions
Validates SAN args and `mkcert`; writes daemon/client PEM files and uses `kubectl create secret generic --dry-run=client -o yaml`.

## Control Flow
Creates `.certs`, generates server and client certs, copies CA files, deletes CA key material, and renders daemon/client secret manifests.

## State and Persistence
Persists `.certs` PEMs, SAN file, and secret YAMLs; does not apply them.

## Dependencies and Integration Points
Depends on bash, mkcert, kubectl, and filesystem permissions. Secret names match the Kubernetes deployment TLS mounts.

## Risks and Edge Cases
Development CA lifecycle, SAN mismatch, and shell splitting are main risks.

## Test Signals
No automated tests; validate by inspecting YAML and starting TLS BuildKit pods.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/create-certs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/deployment+service.privileged.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/deployment+service.privileged.yaml

## Purpose
Kubernetes example manifest for a BuildKit privileged Deployment plus Service.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: regular image, TCP/TLS port 1234, probes, cert secret, and `privileged: true`.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/deployment+service.privileged.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/deployment+service.rootless.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/deployment+service.rootless.yaml

## Purpose
Kubernetes example manifest for a BuildKit rootless Deployment plus Service.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: rootless image, uid/gid 1000, unconfined seccomp/AppArmor, no-process-sandbox flag, cert secret, and writable state `emptyDir`.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/deployment+service.rootless.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/deployment+service.userns.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/deployment+service.userns.yaml

## Purpose
Kubernetes example manifest for a BuildKit user-namespace Deployment plus Service.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: `hostUsers: false`, regular image, TCP/TLS serving, probes, and userns security context.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/deployment+service.userns.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/job.privileged.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/job.privileged.yaml

## Purpose
Kubernetes example manifest for a BuildKit privileged daemonless Job.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: init-created Dockerfile, daemonless build command, workspace `emptyDir`, and `privileged: true`.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/job.privileged.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/job.rootless.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/job.rootless.yaml

## Purpose
Kubernetes example manifest for a BuildKit rootless daemonless Job.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: uid/gid 1000 init/build containers, rootless image, `BUILDKITD_FLAGS`, workspace and BuildKit state volumes.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/job.rootless.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/job.userns.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/job.userns.yaml

## Purpose
Kubernetes example manifest for a BuildKit user-namespace daemonless Job.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: `hostUsers: false`, regular image, daemonless build command, and read-only workspace mount.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/job.userns.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/pod.privileged.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/pod.privileged.yaml

## Purpose
Kubernetes example manifest for a BuildKit minimal privileged Pod.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: single regular BuildKit container, probes, and privileged security context.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/pod.privileged.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/pod.rootless.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/pod.rootless.yaml

## Purpose
Kubernetes example manifest for a BuildKit minimal rootless Pod.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: rootless image, uid/gid 1000, no-process-sandbox, unconfined profiles, and writable state volume.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/pod.rootless.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/pod.userns.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/pod.userns.yaml

## Purpose
Kubernetes example manifest for a BuildKit minimal user-namespace Pod.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: `hostUsers: false`, regular image, probes, and userns-oriented security context.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/pod.userns.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/statefulset.privileged.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/statefulset.privileged.yaml

## Purpose
Kubernetes example manifest for a BuildKit privileged StatefulSet.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: stable pod identity with regular image, probes, and privileged context.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/statefulset.privileged.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/statefulset.rootless.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/statefulset.rootless.yaml

## Purpose
Kubernetes example manifest for a BuildKit rootless StatefulSet.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: stable pod identity with rootless image, uid/gid 1000, no-process-sandbox, unconfined profiles, and state volume.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/statefulset.rootless.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/statefulset.userns.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/statefulset.userns.yaml

## Purpose
Kubernetes example manifest for a BuildKit user-namespace StatefulSet.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: stable pod identity with `hostUsers: false`, regular image, and probes.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/statefulset.userns.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/sysctl-userns.privileged.yaml -->
# Research: sources/cloud-native/buildkit/examples/kubernetes/sysctl-userns.privileged.yaml

## Purpose
Kubernetes example manifest for a BuildKit privileged sysctl helper Pod.

## Important APIs, Types, and Functions
Declarative Kubernetes YAML defines workload kind, pod template, BuildKit image/args, probes, security context, and volumes. Notable settings: pod-level `user.max_user_namespaces` sysctl and privileged container for node/userns preparation.

## Control Flow
The API server stores desired state, controllers create pods, BuildKit starts, probes run `buildctl debug workers`, and Services or Jobs expose/run workloads depending on kind.

## State and Persistence
State is Kubernetes object/pod state. Rootless variants use `emptyDir` BuildKit state; TLS deployments mount Secret data; Jobs use workspace `emptyDir`.

## Dependencies and Integration Points
Depends on Kubernetes workload APIs, BuildKit images, node security feature support, and optional TLS secrets. Integrates with buildctl clients, certificate scripts, and consistent-hash pod selection helpers.

## Risks and Edge Cases
Security posture is central: privileged mode is broad, rootless disables process sandboxing, userns needs feature gates/sysctls, and `master` tags are mutable.

## Test Signals
No unit tests; readiness/liveness probes and successful buildctl operations are runtime signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/kubernetes/sysctl-userns.privileged.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/nested-llb/main.go -->
# Research: sources/cloud-native/buildkit/examples/nested-llb/main.go

## Purpose
Example demonstrating nested LLB construction, where a generated child definition is embedded into a parent BuildKit graph.

## Important APIs, Types, and Functions
Uses `llb` state construction and definition marshaling; the key API boundary is serialized child LLB consumed by a parent state.

## Control Flow
Builds an inner graph, serializes it, wires it into outer operations, and writes the final parent LLB definition to stdout.

## State and Persistence
No durable local state; definitions are in memory until stdout and solver state is external.

## Dependencies and Integration Points
Depends on BuildKit `client/llb` primitives. Shows frontend/client composition patterns for generated nested builds.

## Risks and Edge Cases
Nested definitions are harder to inspect and depend on solver/frontend compatibility.

## Test Signals
No direct tests; compilation and solver acceptance are the signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/nested-llb/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/system/buildkit.service -->
# Research: sources/cloud-native/buildkit/examples/systemd/system/buildkit.service

## Purpose
systemd unit example for a system BuildKit service.

## Important APIs, Types, and Functions
Uses standard `[Unit]`, `[Service]`/`[Socket]`, and `[Install]` sections. It runs buildkitd as a system daemon.

## Control Flow
systemd loads/enables the unit, creates sockets when applicable, and starts services on demand or target activation.

## State and Persistence
BuildKit daemon state lives under configured BuildKit roots; systemd stores enablement and runtime socket state.

## Dependencies and Integration Points
Depends on systemd, installed BuildKit binaries, runtime directory permissions, and user-service support for rootless units. Integrates with local buildctl clients through Unix sockets and OS service management.

## Risks and Edge Cases
Wrong socket paths or user/cgroup permissions cause connection failures; rootless units depend on session/lingering behavior.

## Test Signals
No tests; validate with systemctl and `buildctl debug workers`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/system/buildkit.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/system/buildkit.socket -->
# Research: sources/cloud-native/buildkit/examples/systemd/system/buildkit.socket

## Purpose
systemd unit example for a system BuildKit socket.

## Important APIs, Types, and Functions
Uses standard `[Unit]`, `[Service]`/`[Socket]`, and `[Install]` sections. It listens on the system Unix socket and activates the service.

## Control Flow
systemd loads/enables the unit, creates sockets when applicable, and starts services on demand or target activation.

## State and Persistence
BuildKit daemon state lives under configured BuildKit roots; systemd stores enablement and runtime socket state.

## Dependencies and Integration Points
Depends on systemd, installed BuildKit binaries, runtime directory permissions, and user-service support for rootless units. Integrates with local buildctl clients through Unix sockets and OS service management.

## Risks and Edge Cases
Wrong socket paths or user/cgroup permissions cause connection failures; rootless units depend on session/lingering behavior.

## Test Signals
No tests; validate with systemctl and `buildctl debug workers`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/system/buildkit.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/user/buildkit-proxy.service -->
# Research: sources/cloud-native/buildkit/examples/systemd/user/buildkit-proxy.service

## Purpose
systemd unit example for a user BuildKit proxy service.

## Important APIs, Types, and Functions
Uses standard `[Unit]`, `[Service]`/`[Socket]`, and `[Install]` sections. It bridges a user socket to BuildKit.

## Control Flow
systemd loads/enables the unit, creates sockets when applicable, and starts services on demand or target activation.

## State and Persistence
BuildKit daemon state lives under configured BuildKit roots; systemd stores enablement and runtime socket state.

## Dependencies and Integration Points
Depends on systemd, installed BuildKit binaries, runtime directory permissions, and user-service support for rootless units. Integrates with local buildctl clients through Unix sockets and OS service management.

## Risks and Edge Cases
Wrong socket paths or user/cgroup permissions cause connection failures; rootless units depend on session/lingering behavior.

## Test Signals
No tests; validate with systemctl and `buildctl debug workers`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/user/buildkit-proxy.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/user/buildkit-proxy.socket -->
# Research: sources/cloud-native/buildkit/examples/systemd/user/buildkit-proxy.socket

## Purpose
systemd unit example for a user BuildKit proxy socket.

## Important APIs, Types, and Functions
Uses standard `[Unit]`, `[Service]`/`[Socket]`, and `[Install]` sections. It activates the proxy in a user session.

## Control Flow
systemd loads/enables the unit, creates sockets when applicable, and starts services on demand or target activation.

## State and Persistence
BuildKit daemon state lives under configured BuildKit roots; systemd stores enablement and runtime socket state.

## Dependencies and Integration Points
Depends on systemd, installed BuildKit binaries, runtime directory permissions, and user-service support for rootless units. Integrates with local buildctl clients through Unix sockets and OS service management.

## Risks and Edge Cases
Wrong socket paths or user/cgroup permissions cause connection failures; rootless units depend on session/lingering behavior.

## Test Signals
No tests; validate with systemctl and `buildctl debug workers`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/user/buildkit-proxy.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/user/buildkit.service -->
# Research: sources/cloud-native/buildkit/examples/systemd/user/buildkit.service

## Purpose
systemd unit example for a user BuildKit service.

## Important APIs, Types, and Functions
Uses standard `[Unit]`, `[Service]`/`[Socket]`, and `[Install]` sections. It runs BuildKit in a rootless-compatible user systemd session.

## Control Flow
systemd loads/enables the unit, creates sockets when applicable, and starts services on demand or target activation.

## State and Persistence
BuildKit daemon state lives under configured BuildKit roots; systemd stores enablement and runtime socket state.

## Dependencies and Integration Points
Depends on systemd, installed BuildKit binaries, runtime directory permissions, and user-service support for rootless units. Integrates with local buildctl clients through Unix sockets and OS service management.

## Risks and Edge Cases
Wrong socket paths or user/cgroup permissions cause connection failures; rootless units depend on session/lingering behavior.

## Test Signals
No tests; validate with systemctl and `buildctl debug workers`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/systemd/user/buildkit.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerdexecutor/executor.go -->
# Research: sources/cloud-native/buildkit/executor/containerdexecutor/executor.go

## Purpose
Containerd-backed BuildKit executor implementation.

## Important APIs, Types, and Functions
`containerdExecutor`, `ExecutorOptions`, `RuntimeInfo`, `containerState`, `OnCreateRuntimer`, and methods `New`, `Run`, `Exec`, `runProcess`.

## Control Flow
`Run` validates IDs, tracks running state, selects network/proxy provider, prepares rootfs/DNS/hosts, ensures CWD, injects proxy env/CA, creates OCI spec/container/task, runs the task, handles signals/resizes, maps exit codes, and deletes task/container. `Exec` waits for the task and starts an exec process.

## State and Persistence
In-memory `running` map plus transient files under executor root and containerd container/task state.

## Dependencies and Integration Points
Depends on containerd client/task/cio, BuildKit executor/OCI/network/CDI helpers, identity, OpenTelemetry, and gateway exit errors. Selected by workers using containerd as runtime backend.

## Risks and Edge Cases
Cleanup ordering, cancellation/kill semantics, missing IO streams, and proxy CA/rootfs assumptions are high-risk.

## Test Signals
`executor_test.go` asserts interface compatibility; deeper behavior is integration-tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerdexecutor/executor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerdexecutor/executor_test.go -->
# Research: sources/cloud-native/buildkit/executor/containerdexecutor/executor_test.go

## Purpose
Compile-time contract test for the containerd executor.

## Important APIs, Types, and Functions
Blank identifier assignment proves `*containerdExecutor` implements `executor.Executor`.

## Control Flow
No runtime flow beyond type checking during tests.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on the executor interface and concrete type. Protects solver/backend interface integration.

## Risks and Edge Cases
Does not catch lifecycle bugs.

## Test Signals
Compile failure is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerdexecutor/executor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerdexecutor/executor_unix.go -->
# Research: sources/cloud-native/buildkit/executor/containerdexecutor/executor_unix.go

## Purpose
Unix-specific containerd executor environment setup.

## Important APIs, Types, and Functions
`getUserSpec`, `prepareExecutionEnv`, `ensureCWD`, `createOCISpec`, `getTaskOpts`, `setArgs`.

## Control Flow
Mounts root snapshot, writes hosts/resolv, creates CWD with mapped ownership, resolves user/group, calls `oci.GenerateSpec`, applies rootfs and TTY settings.

## State and Persistence
Transient mount state and generated host resolver files under executor root.

## Dependencies and Integration Points
Depends on containerd mounts, BuildKit OCI helpers, user identity mapping, and Unix FS semantics. Provides the Unix half of containerd executor execution.

## Risks and Edge Cases
Mount release, CWD creation, and user lookup inside rootfs are sensitive.

## Test Signals
Covered by integration more than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerdexecutor/executor_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerdexecutor/executor_windows.go -->
# Research: sources/cloud-native/buildkit/executor/containerdexecutor/executor_windows.go

## Purpose
Windows-specific containerd executor support.

## Important APIs, Types, and Functions
Windows variants of user lookup, environment prep, CWD check, spec creation, task opts, and argument setting.

## Control Flow
Stores root mounts, adapts command-line process fields, and delegates to Windows OCI spec helpers.

## State and Persistence
Transient containerd/root mount state.

## Dependencies and Integration Points
Depends on Windows containerd task/spec semantics. Allows the executor interface to support Windows containers.

## Risks and Edge Cases
Path, command-line quoting, and user identity differences are key risks.

## Test Signals
Windows integration/build tests are required.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerdexecutor/executor_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerid.go -->
# Research: sources/cloud-native/buildkit/executor/containerid.go

## Purpose
Validation helper for executor container IDs.

## Important APIs, Types, and Functions
`ValidContainerID` enforces safe runtime/filesystem ID syntax.

## Control Flow
Executors call it before registering or creating runtime state.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on simple string validation. Used by runc and containerd executors.

## Risks and Edge Cases
Rules must be safe for runtime names and paths without rejecting valid clients unnecessarily.

## Test Signals
`containerid_test.go` covers accepted/rejected IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerid_test.go -->
# Research: sources/cloud-native/buildkit/executor/containerid_test.go

## Purpose
Tests for container ID validation.

## Important APIs, Types, and Functions
Case-table calls to `ValidContainerID`.

## Control Flow
Runs validator and checks expected error state.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on Go testing. Protects executor ID safety.

## Risks and Edge Cases
Coverage depends on maintained case table.

## Test Signals
`go test ./executor` signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/containerid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/executor.go -->
# Research: sources/cloud-native/buildkit/executor/executor.go

## Purpose
Core executor package contract.

## Important APIs, Types, and Functions
`Meta`, `MountableRef`, `Mountable`, `Mount`, `WinSize`, `ProcessInfo`, `Executor`, `HostIP`.

## Control Flow
Solver passes mounts and process metadata; implementations materialize specs, run processes, stream IO/signals, and return optional recorders.

## State and Persistence
Contracts only; runtime state lives in implementations.

## Dependencies and Integration Points
Depends on gateway/solver protobufs, cache mounts, and resource recorder types. Boundary between BuildKit solver exec and runtime backends.

## Risks and Edge Cases
Metadata changes affect every backend and can carry security implications.

## Test Signals
Backend compile assertions and integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/executor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/hosts.go -->
# Research: sources/cloud-native/buildkit/executor/oci/hosts.go

## Purpose
OCI `/etc/hosts` generator.

## Important APIs, Types, and Functions
`GetHostsFile`, `makeHostsFile`, `initHostsFile`.

## Control Flow
Writes localhost/default hostname plus `ExtraHosts`, applies idmapped ownership, and returns a cleanup function.

## State and Persistence
Temporary hosts file under executor root.

## Dependencies and Integration Points
Depends on `os.Root`, id mapping, and executor host metadata. Used before spec generation mounts `/etc/hosts`.

## Risks and Edge Cases
Hostname and extra-host formatting plus cleanup failures affect networking.

## Test Signals
Covered indirectly by executor tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/hosts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/mounts.go -->
# Research: sources/cloud-native/buildkit/executor/oci/mounts.go

## Purpose
OCI mount manipulation helpers.

## Important APIs, Types, and Functions
`withRemovedMount`, `hasPrefix`, `dedupMounts`.

## Control Flow
Transform runtime-spec mount lists during spec generation.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on containerd OCI spec options and runtime-spec mounts. Used by `GenerateSpec` and platform helpers.

## Risks and Edge Cases
Path-prefix correctness is security-sensitive.

## Test Signals
`mounts_test.go` covers pure behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/mounts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/mounts_test.go -->
# Research: sources/cloud-native/buildkit/executor/oci/mounts_test.go

## Purpose
Tests for OCI mount helpers.

## Important APIs, Types, and Functions
Tests prefix matching, removal, and dedup ordering.

## Control Flow
Builds sample mounts, applies helpers, compares results.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on Go testing and runtime-spec mounts. Protects spec mount construction.

## Risks and Edge Cases
Does not exercise real kernel mounts.

## Test Signals
`go test ./executor/oci` signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/mounts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/resolvconf.go -->
# Research: sources/cloud-native/buildkit/executor/oci/resolvconf.go

## Purpose
Resolver configuration generator for containers.

## Important APIs, Types, and Functions
`DNSConfig`, `GetResolvConf`, and resolver path helpers.

## Control Flow
Selects host/filtered resolver source by network mode, applies DNS overrides, writes per-executor `resolv.conf`, returns name for bind mount.

## State and Persistence
Temporary resolver files under executor root.

## Dependencies and Integration Points
Depends on BuildKit net modes, resolvconf helpers, `os.Root`, id mapping. Used by both executor backends before OCI spec generation.

## Risks and Edge Cases
Host resolver variants and bad DNS overrides can break builds.

## Test Signals
`resolvconf_test.go` covers generated content.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/resolvconf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/resolvconf_test.go -->
# Research: sources/cloud-native/buildkit/executor/oci/resolvconf_test.go

## Purpose
Tests for resolver generation.

## Important APIs, Types, and Functions
Temporary-root tests for DNS nameserver/search/options and fallback behavior.

## Control Flow
Calls helper and inspects written files.

## State and Persistence
Temporary files only.

## Dependencies and Integration Points
Depends on Go testing. Protects executor DNS setup.

## Risks and Edge Cases
Cannot emulate every host resolver distribution.

## Test Signals
`go test ./executor/oci` signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/resolvconf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec.go -->
# Research: sources/cloud-native/buildkit/executor/oci/spec.go

## Purpose
Cross-platform OCI spec construction core.

## Important APIs, Types, and Functions
`ProcessMode`, `GenerateSpec`, `submounts`, `subMount`, `cleanup`, `bind`, `compactLongOverlayMount`.

## Control Flow
Composes cgroups, mounts, security, process mode, idmaps, rlimits/resources, env/cwd/hostname, CDI, network namespace, tracing, selected mounts, overlay compaction, dedup, and rootless fixups into an OCI spec and cleanup closure.

## State and Persistence
Transient local mounts/releasers and SELinux labels; no intended permanent state.

## Dependencies and Integration Points
Depends on containerd OCI, BuildKit snapshot/network/CDI/rootless/userns helpers, SELinux, and tracing. Central runtime-spec integration point for runc and containerd executors.

## Risks and Edge Cases
Security-sensitive: subpath resolution, no-process-sandbox, mount dedup, and cleanup on errors matter.

## Test Signals
Covered by helper/unit and runtime integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_darwin.go -->
# Research: sources/cloud-native/buildkit/executor/oci/spec_darwin.go

## Purpose
Darwin stubs for OCI spec helpers.

## Important APIs, Types, and Functions
No-op/unsupported implementations for mount/security/process/idmap/resource/CDI/tracing helpers.

## Control Flow
Allows common package compilation on Darwin while Linux-only features are absent.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on build tags and shared OCI types. Portability layer.

## Risks and Edge Cases
No-op behavior must not be mistaken for full runtime support.

## Test Signals
Cross-platform build signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_freebsd.go -->
# Research: sources/cloud-native/buildkit/executor/oci/spec_freebsd.go

## Purpose
FreeBSD stubs for OCI spec helpers.

## Important APIs, Types, and Functions
No-op/unsupported helper implementations matching common function names.

## Control Flow
Lets the package compile while omitting Linux runtime features.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on build tags and shared types. Portability layer.

## Risks and Edge Cases
Unsupported features should fail clearly when requested.

## Test Signals
Cross-platform build signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_linux.go -->
# Research: sources/cloud-native/buildkit/executor/oci/spec_linux.go

## Purpose
Linux OCI spec helper implementation.

## Important APIs, Types, and Functions
Linux implementations for process args, mounts, security, sandbox mode, ID maps, rlimits, resources, CDI, seccomp/AppArmor/SELinux, cgroup namespaces, tracing mount, and safe submount.

## Control Flow
Binds generated hosts/resolv, replaces mounts, applies sandbox/insecure policy, optionally binds host `/proc`, injects resources/CDI, resolves subpaths with `O_PATH`, and supports cgroup namespace detection.

## State and Persistence
Caches cgroup namespace support; creates transient mounts and SELinux labels.

## Dependencies and Integration Points
Depends on containerd OCI/seccomp/AppArmor, BuildKit entitlements/CDI, SELinux, Linux syscalls, and cgroup/proc files. Used by Linux executor runtime-spec generation.

## Risks and Edge Cases
Insecure mode, host PID namespace, CDI injection, and subpath race handling are high-risk.

## Test Signals
Helper tests plus runtime integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_unix.go -->
# Research: sources/cloud-native/buildkit/executor/oci/spec_unix.go

## Purpose
Unix build-tag placeholder for the OCI package.

## Important APIs, Types, and Functions
Package declaration only.

## Control Flow
No runtime flow.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on Go build tags. Participates in platform file selection.

## Risks and Edge Cases
Minimal risk except build organization mistakes.

## Test Signals
Cross-platform compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_windows.go -->
# Research: sources/cloud-native/buildkit/executor/oci/spec_windows.go

## Purpose
Windows OCI spec helper implementation.

## Important APIs, Types, and Functions
Windows process command-line, user-info mount, platform stubs, tracing mount, submount, and mount type normalization helpers.

## Control Flow
Adapts common spec generation to Windows command-line and mount semantics.

## State and Persistence
Transient spec/mount state only.

## Dependencies and Integration Points
Depends on containerd OCI and Windows runtime-spec fields. Used by Windows containerd executor.

## Risks and Edge Cases
Command-line quoting and Linux-feature omissions are key risks.

## Test Signals
Windows build/integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/spec_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/user.go -->
# Research: sources/cloud-native/buildkit/executor/oci/user.go

## Purpose
User/group resolution helpers for OCI process specs.

## Important APIs, Types, and Functions
`GetUser`, `ParseUIDGID`, `openUserFile`, `parseUID`, `WithUIDGID`, `setProcess`, `ensureAdditionalGids`.

## Control Flow
Reads passwd/group data in rootfs, parses numeric/user forms, and mutates OCI process user fields.

## State and Persistence
No durable state; reads rootfs and mutates in-memory specs.

## Dependencies and Integration Points
Depends on `moby/sys/user`, containerd OCI, and runtime-spec user fields. Used by runc/containerd run and exec process setup.

## Risks and Edge Cases
Rootfs path safety, malformed users, and missing group files are edge cases.

## Test Signals
Indirect executor coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/oci/user.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/proxyca_linux.go -->
# Research: sources/cloud-native/buildkit/executor/proxyca_linux.go

## Purpose
Linux proxy CA injection into build rootfs.

## Important APIs, Types, and Functions
`InjectProxyCA`, `firstCertificate`, `containsCertificate`, `removeInjectedCA`, `writeCertBundle`.

## Control Flow
Reads known CA bundle files, parses proxy cert, appends if absent, writes with preserved metadata, and returns cleanup to remove it.

## State and Persistence
Mutates temporary rootfs CA bundle files and later removes inserted cert content.

## Dependencies and Integration Points
Depends on Linux CA bundle paths, x509/pem parsing, and proxy namespace integration. Used when proxy capture needs trusted CA inside build containers.

## Risks and Edge Cases
Safe reversible mutation across distro bundle formats is the main risk.

## Test Signals
`proxyca_linux_test.go` covers insertion/detection/removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/proxyca_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/proxyca_linux_test.go -->
# Research: sources/cloud-native/buildkit/executor/proxyca_linux_test.go

## Purpose
Tests for proxy CA injection helpers.

## Important APIs, Types, and Functions
Exercises PEM parsing, existing cert detection, bundle insertion, and cleanup removal.

## Control Flow
Builds sample cert data and compares helper output.

## State and Persistence
Temporary/in-memory state only.

## Dependencies and Integration Points
Depends on Go testing and x509/PEM. Protects proxy-network executor behavior.

## Risks and Edge Cases
Does not cover every distro bundle path/permission.

## Test Signals
Linux `go test` signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/proxyca_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/proxyca_unsupported.go -->
# Research: sources/cloud-native/buildkit/executor/proxyca_unsupported.go

## Purpose
Unsupported-platform proxy CA stub.

## Important APIs, Types, and Functions
Build-tagged `InjectProxyCA` fallback.

## Control Flow
Compiles non-Linux executors without Linux bundle mutation.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on build tags. Portability for proxy-aware executor code.

## Risks and Edge Cases
Non-Linux proxy trust behavior may differ.

## Test Signals
Cross-platform compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/proxyca_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/cpu.go -->
# Research: sources/cloud-native/buildkit/executor/resources/cpu.go

## Purpose
CPU cgroup v2 sampler for BuildKit resource monitoring.

## Important APIs, Types, and Functions
The key local helper returns `CPU` stats in `executor/resources/types` and parses `cpu.stat` and `cpu.pressure`, converts usec to ns, and records throttling/PSI.

## Control Flow
`Monitor.sample` calls it during periodic sampling; it reads cgroup files, parses key/value records, tolerates absent optional files where intended, and returns a typed stat object.

## State and Persistence
No persistence; samples kernel cgroup files at a point in time.

## Dependencies and Integration Points
Depends on Linux cgroup v2 file formats, PSI where applicable, and shared resource types. Integrated into executor resource recorders.

## Risks and Edge Cases
Kernel config/version affects file availability; malformed fields or missing required files can fail sampling.

## Test Signals
The paired test file covers parser output and optional/missing files.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/cpu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/cpu_test.go -->
# Research: sources/cloud-native/buildkit/executor/resources/cpu_test.go

## Purpose
Unit tests for CPU cgroup resource parsing.

## Important APIs, Types, and Functions
Creates sample controller files and asserts the CPU parser populates expected typed fields.

## Control Flow
Uses temporary directories/files, calls the parser, and compares counters/optional pressure data.

## State and Persistence
Temporary test files only.

## Dependencies and Integration Points
Depends on Go testing and parser helpers. Protects resource reports consumed by executor recorders.

## Risks and Edge Cases
Synthetic fixtures do not cover every kernel variant.

## Test Signals
`go test ./executor/resources` signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/cpu_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/io.go -->
# Research: sources/cloud-native/buildkit/executor/resources/io.go

## Purpose
IO cgroup v2 sampler for BuildKit resource monitoring.

## Important APIs, Types, and Functions
The key local helper returns `IO` stats in `executor/resources/types` and parses `io.stat` across devices, sums byte/IO counters, and attaches IO pressure.

## Control Flow
`Monitor.sample` calls it during periodic sampling; it reads cgroup files, parses key/value records, tolerates absent optional files where intended, and returns a typed stat object.

## State and Persistence
No persistence; samples kernel cgroup files at a point in time.

## Dependencies and Integration Points
Depends on Linux cgroup v2 file formats, PSI where applicable, and shared resource types. Integrated into executor resource recorders.

## Risks and Edge Cases
Kernel config/version affects file availability; malformed fields or missing required files can fail sampling.

## Test Signals
The paired test file covers parser output and optional/missing files.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/io.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/io_test.go -->
# Research: sources/cloud-native/buildkit/executor/resources/io_test.go

## Purpose
Unit tests for IO cgroup resource parsing.

## Important APIs, Types, and Functions
Creates sample controller files and asserts the IO parser populates expected typed fields.

## Control Flow
Uses temporary directories/files, calls the parser, and compares counters/optional pressure data.

## State and Persistence
Temporary test files only.

## Dependencies and Integration Points
Depends on Go testing and parser helpers. Protects resource reports consumed by executor recorders.

## Risks and Edge Cases
Synthetic fixtures do not cover every kernel variant.

## Test Signals
`go test ./executor/resources` signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/io_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/memory.go -->
# Research: sources/cloud-native/buildkit/executor/resources/memory.go

## Purpose
memory cgroup v2 sampler for BuildKit resource monitoring.

## Important APIs, Types, and Functions
The key local helper returns `memory` stats in `executor/resources/types` and parses `memory.stat`, `memory.events`, `memory.peak`, `memory.swap.current`, and pressure.

## Control Flow
`Monitor.sample` calls it during periodic sampling; it reads cgroup files, parses key/value records, tolerates absent optional files where intended, and returns a typed stat object.

## State and Persistence
No persistence; samples kernel cgroup files at a point in time.

## Dependencies and Integration Points
Depends on Linux cgroup v2 file formats, PSI where applicable, and shared resource types. Integrated into executor resource recorders.

## Risks and Edge Cases
Kernel config/version affects file availability; malformed fields or missing required files can fail sampling.

## Test Signals
The paired test file covers parser output and optional/missing files.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/memory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/memory_test.go -->
# Research: sources/cloud-native/buildkit/executor/resources/memory_test.go

## Purpose
Unit tests for memory cgroup resource parsing.

## Important APIs, Types, and Functions
Creates sample controller files and asserts the memory parser populates expected typed fields.

## Control Flow
Uses temporary directories/files, calls the parser, and compares counters/optional pressure data.

## State and Persistence
Temporary test files only.

## Dependencies and Integration Points
Depends on Go testing and parser helpers. Protects resource reports consumed by executor recorders.

## Risks and Edge Cases
Synthetic fixtures do not cover every kernel variant.

## Test Signals
`go test ./executor/resources` signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/memory_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/monitor.go -->
# Research: sources/cloud-native/buildkit/executor/resources/monitor.go

## Purpose
Resource monitor for cgroup v2 execution samples.

## Important APIs, Types, and Functions
`Monitor`, `cgroupRecord`, `RecordOpt`, `NetworkSampler`, `nopRecord`; methods `RecordNamespace`, `Start`, `Close`, `CloseAsync`, `Wait`, `Samples`, `sample`, `NewMonitor`.

## Control Flow
Detects cgroup v2, optionally prepares controllers, records namespaces, samples CPU/memory/IO/PIDs/network every interval, captures final sample, computes host CPU delta, and removes records on close.

## State and Persistence
In-memory records/sample slices; reads cgroup/proc files but does not persist reports itself.

## Dependencies and Integration Points
Depends on procfs, cgroup v2 files, resource type definitions, and optional network samplers. Used by runc executor to return a resource `Recorder`.

## Risks and Edge Cases
No cgroup v2 or closed monitors degrade to no-op; permissions and sampling errors affect output.

## Test Signals
Parser tests cover components; full lifecycle needs cgroup integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/monitor_linux.go -->
# Research: sources/cloud-native/buildkit/executor/resources/monitor_linux.go

## Purpose
Linux entry point for resource monitor creation.

## Important APIs, Types, and Functions
Build-tag platform glue for real cgroup/proc monitoring.

## Control Flow
Routes monitor creation to the Linux implementation.

## State and Persistence
State is defined in `monitor.go`.

## Dependencies and Integration Points
Depends on Linux build tags and cgroup availability. Used by executors that enable resource collection.

## Risks and Edge Cases
Non-cgroup-v2 hosts degrade to no-op recorders.

## Test Signals
Build/resource integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/monitor_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/monitor_nolinux.go -->
# Research: sources/cloud-native/buildkit/executor/resources/monitor_nolinux.go

## Purpose
Non-Linux resource monitor stub.

## Important APIs, Types, and Functions
Build-tag fallback returning unsupported/no-op monitor behavior.

## Control Flow
No real sampling occurs.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on build tags and shared resource API. Keeps package portable.

## Risks and Edge Cases
Consumers must tolerate missing resource samples.

## Test Signals
Cross-platform compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/monitor_nolinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/pids.go -->
# Research: sources/cloud-native/buildkit/executor/resources/pids.go

## Purpose
PIDs cgroup v2 sampler for BuildKit resource monitoring.

## Important APIs, Types, and Functions
The key local helper returns `PIDs` stats in `executor/resources/types` and reads pids controller files for current/limit counts.

## Control Flow
`Monitor.sample` calls it during periodic sampling; it reads cgroup files, parses key/value records, tolerates absent optional files where intended, and returns a typed stat object.

## State and Persistence
No persistence; samples kernel cgroup files at a point in time.

## Dependencies and Integration Points
Depends on Linux cgroup v2 file formats, PSI where applicable, and shared resource types. Integrated into executor resource recorders.

## Risks and Edge Cases
Kernel config/version affects file availability; malformed fields or missing required files can fail sampling.

## Test Signals
The paired test file covers parser output and optional/missing files.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/pids.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/pids_test.go -->
# Research: sources/cloud-native/buildkit/executor/resources/pids_test.go

## Purpose
Unit tests for PIDs cgroup resource parsing.

## Important APIs, Types, and Functions
Creates sample controller files and asserts the PIDs parser populates expected typed fields.

## Control Flow
Uses temporary directories/files, calls the parser, and compares counters/optional pressure data.

## State and Persistence
Temporary test files only.

## Dependencies and Integration Points
Depends on Go testing and parser helpers. Protects resource reports consumed by executor recorders.

## Risks and Edge Cases
Synthetic fixtures do not cover every kernel variant.

## Test Signals
`go test ./executor/resources` signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/pids_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/sampler.go -->
# Research: sources/cloud-native/buildkit/executor/resources/sampler.go

## Purpose
Generic adaptive sampling utility.

## Important APIs, Types, and Functions
`WithTimestamp`, `Sampler[T]`, `Sub[T]`, `NewSampler`, `Record`, `run`, `Sub.Close`, `Sampler.Close`.

## Control Flow
A goroutine ticks at a minimum interval, calls a callback once per active tick, appends samples, and increases subscriber intervals to bound sample count; close downsamples and can capture a final sample.

## State and Persistence
In-memory subscriber map and sample/error fields.

## Dependencies and Integration Points
Depends on sync/time only. Used by cgroup and system resource samplers.

## Risks and Edge Cases
Concurrency around close vs sample callback and error propagation is important.

## Test Signals
Indirect tests through resource monitor behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/sampler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/sys.go -->
# Research: sources/cloud-native/buildkit/executor/resources/sys.go

## Purpose
Public system sampler constructor wrapper.

## Important APIs, Types, and Functions
`SysSampler` alias and `NewSysSampler` platform-dispatched constructor.

## Control Flow
Returns the platform sampler for host-level resource samples.

## State and Persistence
No state beyond returned sampler.

## Dependencies and Integration Points
Depends on resource system types and platform files. Used by monitoring/reporting code needing host samples.

## Risks and Edge Cases
Availability differs by platform.

## Test Signals
Platform build coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/sys.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/sys_linux.go -->
# Research: sources/cloud-native/buildkit/executor/resources/sys_linux.go

## Purpose
Linux system-wide resource sampler.

## Important APIs, Types, and Functions
`newSysSampler` and `sampleSys` use procfs to sample host CPU and memory.

## Control Flow
Creates a generic sampler whose callback reads `/proc/stat` and memory info into `SysSample`.

## State and Persistence
In-memory samples; read-only procfs access.

## Dependencies and Integration Points
Depends on prometheus procfs and Linux `/proc`. Adds host context to resource reports.

## Risks and Edge Cases
Procfs availability/field variation can affect output.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/sys_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/sys_nolinux.go -->
# Research: sources/cloud-native/buildkit/executor/resources/sys_nolinux.go

## Purpose
Non-Linux system sampler stub.

## Important APIs, Types, and Functions
Build-tagged `newSysSampler` fallback.

## Control Flow
No system sampling occurs.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on build tags. Portability for resource package.

## Risks and Edge Cases
Consumers must tolerate absent host samples.

## Test Signals
Cross-platform compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/sys_nolinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/types/systypes.go -->
# Research: sources/cloud-native/buildkit/executor/resources/types/systypes.go

## Purpose
System-wide resource sample types.

## Important APIs, Types, and Functions
`SysCPUStat`, custom `MarshalJSON`, `ProcStat`, `SysMemoryStat`, `SysSample`, `Timestamp`.

## Control Flow
Samplers populate structs; JSON marshaling makes API/report output valid.

## State and Persistence
Data-only types.

## Dependencies and Integration Points
Depends on encoding/json, math, time. Used by system sampler and resource report consumers.

## Risks and Edge Cases
NaN/Inf CPU JSON handling is a serialization risk addressed by custom marshaling.

## Test Signals
Consumer serialization tests are expected.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/types/systypes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/types/types.go -->
# Research: sources/cloud-native/buildkit/executor/resources/types/types.go

## Purpose
Shared resource sample data model and recorder interface.

## Important APIs, Types, and Functions
`Recorder`, `Samples`, `Sample`, `NetworkSample`, `CPUStat`, `MemoryStat`, `IOStat`, `PIDsStat`, `Pressure`, `PressureValues`.

## Control Flow
Executors return recorders; callers start/close/wait and retrieve nested stat samples.

## State and Persistence
In-memory data contract, serialized by higher layers as needed.

## Dependencies and Integration Points
Depends on context/time. Boundary between runtime collection and BuildKit reporting/API layers.

## Risks and Edge Cases
Pointer fields encode absent vs zero and must be preserved.

## Test Signals
Parser tests indirectly assert schema use.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/resources/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/runcexecutor/executor.go -->
# Research: sources/cloud-native/buildkit/executor/runcexecutor/executor.go

## Purpose
runc-backed BuildKit executor for Linux workers.

## Important APIs, Types, and Functions
`Opt`, `runcExecutor`, `forwardIO`, `procKiller`, `procHandle`, and methods/functions `New`, `Run`, `Exec`, `exitError`, process killer/handle helpers.

## Control Flow
Locates runc, prepares root, registers running state, creates network/proxy namespace, writes hosts/resolv, mounts rootfs bundle, injects proxy CA, resolves user, generates/writes OCI `config.json`, records resources, calls platform `run`/`exec`, maps exits, and releases container/network.

## State and Persistence
Executor root bundles, rootfs mounts, runc state, running map, namespaces, and optional resource samples.

## Dependencies and Integration Points
Depends on go-runc, containerd mounts/OCI, BuildKit OCI/resource/network/proxy/CDI/rootless helpers, OpenTelemetry, and gateway errors. Used by OCI workers that execute through runc directly.

## Risks and Edge Cases
Cancellation/kill semantics, mount/namespace cleanup, rootless/no-process-sandbox isolation, and resource recorder release are high-risk.

## Test Signals
Runtime integration tests are the meaningful signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/runcexecutor/executor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/runcexecutor/executor_common.go -->
# Research: sources/cloud-native/buildkit/executor/runcexecutor/executor_common.go

## Purpose
Common package placeholder for runc executor builds.

## Important APIs, Types, and Functions
Package declaration only.

## Control Flow
No runtime flow.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on Go package layout. Supports build-tag organization.

## Risks and Edge Cases
Minimal risk.

## Test Signals
Compilation signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/runcexecutor/executor_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/runcexecutor/executor_linux.go -->
# Research: sources/cloud-native/buildkit/executor/runcexecutor/executor_linux.go

## Purpose
Linux runc invocation and IO/signal handling.

## Important APIs, Types, and Functions
`updateRuncFieldsForHostOS`, `run`, `exec`, `callWithIO`, `detectOOM`, `readMemoryEvent`.

## Control Flow
Sets up go-runc started channels, IO/TTY/resize, signal forwarding, process handles, kill behavior, waits for completion, and decorates OOM exits from cgroup memory events.

## State and Persistence
Transient runc monitor processes, pidfiles, IO pipes, console state, and cgroup reads.

## Dependencies and Integration Points
Depends on go-runc, containerd console, Linux signals, gateway errors, and cgroup files. Completes runc executor `Run`/`Exec` lifecycle.

## Risks and Edge Cases
SIGKILL routing, pidfile races, missing started messages, and OOM parsing are subtle.

## Test Signals
Requires actual runc integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/runcexecutor/executor_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/executor/stubs.go -->
# Research: sources/cloud-native/buildkit/executor/stubs.go

## Purpose
Mount-stub cleanup helper.

## Important APIs, Types, and Functions
`MountStubsCleaner` returns a cleanup closure for mount destination stubs.

## Control Flow
After execution it scans requested mount destinations and removes empty files/directories or recursive stubs while avoiding mounted paths.

## State and Persistence
Mutates temporary rootfs contents only.

## Dependencies and Integration Points
Depends on continuity fs helpers, syscall mount checks, and path safety. Used by runc executor rootfs cleanup.

## Risks and Edge Cases
Must not escape rootfs or remove real content; recursive cleanup is sensitive.

## Test Signals
Integration tests should catch leaks/unsafe removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/executor/stubs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/attestation/filter.go -->
# Research: sources/cloud-native/buildkit/exporter/attestation/filter.go

## Purpose
Predicate-type filter for BuildKit attestations.

## Important APIs, Types, and Functions
`Filter` accepts attestations plus include/exclude predicate maps.

## Control Flow
Iterates attestations, checks predicate-type metadata, applies include/exclude rules, and preserves accepted order.

## State and Persistence
Pure slice filtering; no state.

## Dependencies and Integration Points
Depends on exporter attestation metadata layout. Used by image writer to omit inline-only or selected attestations.

## Risks and Edge Cases
Missing/unexpected predicate metadata can filter incorrectly.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/attestation/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/attestation/make.go -->
# Research: sources/cloud-native/buildkit/exporter/attestation/make.go

## Purpose
Creates in-toto statements from BuildKit attestation results.

## Important APIs, Types, and Functions
`ReadAll`, `MakeInTotoStatements`, and `makeInTotoStatement`.

## Control Flow
Reads attestation content from refs/remotes or inline data, parses/wraps JSON, normalizes predicate type and subjects, and returns statements concurrently.

## State and Persistence
No persistence; reads session/snapshot content and returns memory objects.

## Dependencies and Integration Points
Depends on in-toto, exporter/result/session/snapshot APIs, gateway metadata, errgroup. Used by image writer before committing attestation manifests.

## Risks and Edge Cases
Statement format/subject defaults and concurrent ordering/error propagation are correctness-sensitive.

## Test Signals
Covered by provenance/SBOM export integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/attestation/make.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/attestation/unbundle.go -->
# Research: sources/cloud-native/buildkit/exporter/attestation/unbundle.go

## Purpose
Unbundles and validates attestation bundles.

## Important APIs, Types, and Functions
`Unbundle`, `sort`, `unbundle`, `Validate`, `validate`.

## Control Flow
Materializes bundle refs, walks files, parses in-toto JSON, validates shape, sorts deterministically, and returns individual attestations.

## State and Persistence
Temporary mounted/read snapshot content; output is in-memory.

## Dependencies and Integration Points
Depends on session/snapshot/result APIs, in-toto JSON, continuity fs, path handling. Called by image writer for per-platform attestations.

## Risks and Edge Cases
Malformed bundles and path/statement assumptions should fail early; sorting matters for reproducibility.

## Test Signals
Covered by attestation/export integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/attestation/unbundle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/annotations.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/annotations.go

## Purpose
Container image exporter annotation parser/merger.

## Important APIs, Types, and Functions
`Annotations`, `AnnotationsGroup`, `ParseAnnotations`, `Platform`, `Merge`, `merge`.

## Control Flow
Scans metadata for annotation keys, parses target/platform groups, returns annotation buckets and remaining metadata, and merges sources.

## State and Persistence
Pure map transformation.

## Dependencies and Integration Points
Depends on OCI platforms, containerd platform matching, and exptypes annotation parsing. Used before image manifest/index commit.

## Risks and Edge Cases
Wrong key parsing can place annotations on wrong descriptors or reject valid exports.

## Test Signals
Indirect exporter tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/attestations.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/attestations.go

## Purpose
SBOM/attestation helpers for image export.

## Important APIs, Types, and Functions
`intotoPlatform`, `supplementSBOM`, SPDX encode/decode, `fileLayerFinder` helpers.

## Control Flow
Decodes SPDX SBOMs, finds source files in target layers/remotes, supplements package/layer references, and returns amended attestations.

## State and Persistence
Uses temporary refs/remotes and releases finder resources; data is in-memory until written.

## Dependencies and Integration Points
Depends on cache refs, solver remotes, session content, SPDX libs, OCI descriptors. Integrated into `ImageWriter.Commit` per-platform attestation flow.

## Risks and Edge Cases
Layer lookup, lazy remotes, and SPDX format assumptions can break supplementation.

## Test Signals
SBOM exporter integration tests expected.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/attestations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/export.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/export.go

## Purpose
Container image exporter implementation.

## Important APIs, Types, and Functions
`Opt`, `imageExporter`, `imageExporterInstance`, `New`, `Resolve`, `Export`, `pushImage`, `unpackImage`, `DefaultOCITypes`, descriptor reference helpers.

## Control Flow
Parses exporter options, clones source metadata, parses annotations, opens a lease, asks `ImageWriter.Commit` for a descriptor, tags/stores images, optionally unpacks, materializes lazy refs, returns response metadata and optional push finalize callback.

## State and Persistence
Persists content/images/snapshots in containerd stores, uses temporary leases, and may push to registries.

## Dependencies and Integration Points
Depends on containerd content/images/leases/rootfs, BuildKit cache/session/snapshot/exporter APIs, registry push, compression, OCI descriptors. Implements BuildKit `type=image` export/store/push flow.

## Risks and Edge Cases
Option conflicts, lazy ref completion, image create/update races, and push errors are important.

## Test Signals
Covered by image exporter integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/exptypes/annotations.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/exptypes/annotations.go

## Purpose
Annotation key grammar for container image exporter.

## Important APIs, Types, and Functions
Target constants, regex/parser state, `AnnotationKey`, string constructors, and `ParseAnnotationKey`.

## Control Flow
Parses metadata keys into target type, optional platform, and annotation key; constructors produce canonical keys.

## State and Persistence
Only compiled regex/global parser state.

## Dependencies and Integration Points
Depends on containerd platform parsing and OCI platforms. Shared contract for clients setting exporter annotations.

## Risks and Edge Cases
Grammar changes are compatibility-sensitive.

## Test Signals
Parser/exporter annotation tests expected.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/exptypes/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/exptypes/keys.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/exptypes/keys.go

## Purpose
Container image exporter option key constants.

## Important APIs, Types, and Functions
`ImageExporterOptKey` and keys for names, push, OCI media types, compression, annotations, unpack/store, timestamps, attestations, and response metadata.

## Control Flow
No runtime flow; constants are consumed by parsers and clients.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends only on string constants. String contract between BuildKit clients/frontends and image exporter.

## Risks and Edge Cases
Renaming keys is compatibility-breaking.

## Test Signals
Coverage is indirect through option parsing tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/exptypes/keys.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/exptypes/parse.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/exptypes/parse.go

## Purpose
Image exporter metadata parser.

## Important APIs, Types, and Functions
`ParsePlatforms` and `ParseKey`.

## Control Flow
Decodes platform metadata JSON and fetches global or platform-scoped metadata values.

## State and Persistence
Pure metadata transformation.

## Dependencies and Integration Points
Depends on JSON, containerd platform normalization, OCI platforms. Critical for multi-platform ref mapping in image export.

## Risks and Edge Cases
Bad/missing platform metadata causes multi-ref export failures.

## Test Signals
Covered indirectly by multi-platform exporter tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/exptypes/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/exptypes/types.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/exptypes/types.go

## Purpose
Container image exporter internal data types.

## Important APIs, Types, and Functions
Known metadata keys, `Platforms`, `Platform`, `InlineCacheEntry`, `InlineCache`.

## Control Flow
Frontends/solver populate these and writer/exporter consume them.

## State and Persistence
Data contract only.

## Dependencies and Integration Points
Depends on context, solver result generics, OCI platforms. Connects frontend metadata to image export internals.

## Risks and Edge Cases
Changes affect cache/config/base-image and platform compatibility.

## Test Signals
Integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/exptypes/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/image/docker_image.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/image/docker_image.go

## Purpose
Aliases for Docker image-spec types.

## Important APIs, Types, and Functions
`HealthConfig`, `ImageConfig`, `Image` aliases.

## Control Flow
No runtime flow.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on Docker image-spec v1. Local import path for Docker config structures.

## Risks and Edge Cases
Tracks upstream alias compatibility.

## Test Signals
Compile-time signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/image/docker_image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/opts.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/opts.go

## Purpose
Image commit option parser/validator.

## Important APIs, Types, and Functions
`ImageCommitOpts`, `Load`, `Validate`, `SetOCITypesDefault`, `OCITypesEnabled`, bool/map helpers.

## Control Flow
Parses exporter option strings into compression/ref config, names, OCI media behavior, annotations, epoch/rewrite, attestation flags, and returns unconsumed metadata.

## State and Persistence
Per-export struct only.

## Dependencies and Integration Points
Depends on cache config, compression, epoch parsing, exptypes keys. Used by `Resolve` and `ImageWriter.Commit`.

## Risks and Edge Cases
Option compatibility and clear validation errors are critical.

## Test Signals
Exporter integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/patch.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/patch.go

## Purpose
Default image layer patch hook.

## Important APIs, Types, and Functions
Non-Nydus `patchImageLayers` no-op.

## Control Flow
Writer calls it before config/manifest commit and receives unchanged remote/history.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on cache/session/solver/OCI types. Build-tag extension point for Nydus.

## Risks and Edge Cases
Low default risk; behavior changes under Nydus tags.

## Test Signals
Build-tag coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/patch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/patch_nydus.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/patch_nydus.go

## Purpose
Nydus-specific image layer patch hook.

## Important APIs, Types, and Functions
Build-tagged `patchImageLayers` for Nydus compression/export.

## Control Flow
Validates Nydus options and adjusts remote descriptors/history before manifest commit.

## State and Persistence
Returned remote/history carry state; content mutations are delegated.

## Dependencies and Integration Points
Depends on BuildKit Nydus compression, cache refs, solver remotes, sessions, OCI history. Integrates Nydus export into generic writer.

## Risks and Edge Cases
Wrong descriptor/history patching breaks pull/runtime behavior.

## Test Signals
Nydus integration tests needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/patch_nydus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/writer.go -->
# Research: sources/cloud-native/buildkit/exporter/containerimage/writer.go

## Purpose
Image writer for OCI/Docker manifests, configs, indexes, layers, inline cache, timestamps, and attestations.

## Important APIs, Types, and Functions
`WriterOpt`, `ImageWriter`, `Commit`, `exportLayers`, timestamp rewrite helpers, manifest commit helpers, config/history helpers, annotation cleanup, ref metadata helpers.

## Control Flow
Validates options, parses platforms, chooses single manifest vs index, exports layers, rewrites timestamps, patches config/history/rootfs/inline cache, writes blobs with GC labels, unbundles/supplements attestations, commits attestation manifests, and writes indexes.

## State and Persistence
Persists blobs in content store; inline cache in config JSON; attestations as separate manifests/layers. Lease lifetime is managed by the exporter.

## Dependencies and Integration Points
Depends on containerd content/diff/images labels, BuildKit cache/session/solver/exporter/attestation/epoch/compression utilities, Docker/OCI specs, in-toto, package-url, tracing/progress. Central content producer for `type=image` export.

## Risks and Edge Cases
Multi-platform mapping, media type modes, annotations, reproducible timestamps, lazy providers, attestation subjects, and layer/history normalization are high-risk.

## Test Signals
Broad image exporter integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/containerimage/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/exporter.go -->
# Research: sources/cloud-native/buildkit/exporter/exporter.go

## Purpose
Generic exporter interfaces and config.

## Important APIs, Types, and Functions
`Source`, `Attestation`, `Exporter`, `ExporterInstance`, `FinalizeFunc`, `ExportBuildInfo`, `DescriptorReference`, `Config`.

## Control Flow
Solver resolves an exporter instance, calls `Export`, receives metadata/finalize/descriptors, and runs finalize when needed.

## State and Persistence
Contracts only; persistence depends on implementation.

## Dependencies and Integration Points
Depends on cache refs, solver result generics, compression config, OCI descriptors. Common boundary for all BuildKit exporters.

## Risks and Edge Cases
Finalize and descriptor release lifetimes must be respected to avoid leaks/GC races.

## Test Signals
Compile and integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/exptypes/keys.go -->
# Research: sources/cloud-native/buildkit/exporter/exptypes/keys.go

## Purpose
Shared exporter option key constants.

## Important APIs, Types, and Functions
`ExporterOptKey` plus common keys such as source date epoch and build info image config attrs.

## Control Flow
No runtime flow; constants are consumed by exporter parsers and frontend metadata plumbing.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on strings only. Stable client/frontend contract outside image-specific keys.

## Risks and Edge Cases
Changing strings is compatibility-breaking.

## Test Signals
Indirect exporter option tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/exptypes/keys.go -->
