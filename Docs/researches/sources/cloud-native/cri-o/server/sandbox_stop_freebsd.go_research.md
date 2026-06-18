# sources/cloud-native/cri-o/server/sandbox_stop_freebsd.go

Purpose: FreeBSD implementation for stopping a pod sandbox.

Important APIs and functions: `stopPodSandbox` serializes stop operations with the sandbox stop mutex, stops network, stops workload containers in parallel, stops infra, removes namespaces, unmounts SHM, notifies NRI, marks stopped, and emits a stopped event.

Control flow: returns early if already stopped after network cleanup. Splits request timeout between workload containers and infra. Uses `errgroup` for parallel workload container stops and handles unknown/stopped infra errors as non-fatal.

State and persistence: mutates runtime container states, network/CNI state, namespace resources, SHM mounts, NRI state, sandbox stopped flag, and CRI event channel.

Dependencies and integration: storage/OCI errors, stop timeout helper, CRI-O stopContainer, NRI, sandbox managed namespaces.

Risks: similar cleanup-order sensitivity as Linux. Event generation is unconditional on FreeBSD after setting stopped, unlike Linux's spoofed-infra special case.

Test signals: generic stop tests may not execute this file on Linux CI.
