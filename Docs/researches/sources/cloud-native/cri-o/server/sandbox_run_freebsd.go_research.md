# sources/cloud-native/cri-o/server/sandbox_run_freebsd.go

Purpose: FreeBSD implementation of pod sandbox creation, adapted to jails and reduced Linux feature support.

Important APIs and functions: `getSandboxIDMappings` returns nil, `runPodSandbox` performs full sandbox setup, `configureGeneratorForSysctls`, and `configureGeneratorForSandboxNamespaces`.

Control flow: similar high-level flow to Linux: build sandbox, reserve pod/container names, wait for CNI, validate runtime handler, filter annotations, create storage sandbox, build OCI spec annotations, add indexes, create namespaces, start storage, configure infra resources, save config, create/start infra container, run CNI, call NRI, and mark created. It uses a `ResourceCleaner` for failure cleanup except context-error cases.

State and persistence: mutates name reservations, storage containers, log directories, metadata labels/annotations, sandbox store, ID indexes, namespace manager state, storage mounts, generated config files, runtime container state, CNI state/IP annotations, resource store, and NRI state.

Dependencies and integration: storage runtime server, namespace manager with FreeBSD jail/VNET annotations, CNI, runtime handler hooks, CRI-O sandbox builder, OCI runtime, cgroup manager, resource store, NRI.

Risks: FreeBSD implementation duplicates significant Linux logic and can drift. Some Linux concepts are stubbed or simplified: no user namespace mappings, hostPID forced true, hostIPC unsupported, SELinux labels disabled when hostPID/IPC. Context-error cleanup behavior differs from Linux by skipping cleanup when `isContextError(retErr)`.

Test signals: no FreeBSD-specific tests in this subset; generic sandbox run tests may not cover this file on Linux CI.
