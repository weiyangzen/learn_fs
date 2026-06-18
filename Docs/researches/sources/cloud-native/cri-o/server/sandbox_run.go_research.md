# sources/cloud-native/cri-o/server/sandbox_run.go

Purpose: shared, platform-independent helpers for pod sandbox creation.

Important APIs and functions: constants `PodInfraOOMAdj` and `PodInfraCPUshares`; `privilegedSandbox`; `runtimeHandler`; `RunPodSandbox`; `convertPortMappings`; `getHostname`; `setPodSandboxMountLabel`.

Control flow: `RunPodSandbox` dispatches to platform-specific `runPodSandbox`. `privilegedSandbox` derives elevated sandbox status from privileged flag or host network/pid/ipc namespace modes. `runtimeHandler` validates non-empty handlers. `convertPortMappings` drops entries without host ports. `getHostname` uses host hostname for host-network pods or sandbox ID prefix for pod-network pods when no hostname is provided.

State and persistence: `setPodSandboxMountLabel` reads and writes storage runtime metadata to persist the sandbox mount label.

Dependencies and integration: CRI runtime types, Kubernetes port protocols, hostport manager, storage metadata, runtime handler validation.

Risks: hostname derivation assumes sandbox IDs are at least 12 characters. Privileged classification treats any host namespace mode as privileged for runtime/storage behavior.

Test signals: sandbox run tests exercise dispatch and several validation/failure paths; platform-specific creation has much broader behavior than this shared file.
