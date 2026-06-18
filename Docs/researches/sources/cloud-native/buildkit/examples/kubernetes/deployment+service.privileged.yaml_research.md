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
