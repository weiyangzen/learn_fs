# sources/cloud-native/cri-o/server/sandbox_remove.go

Purpose: implements CRI `RemovePodSandbox` and internal sandbox removal cleanup.

Important APIs and functions: `RemovePodSandbox` handles CRI lookup/idempotency semantics; `removePodSandbox` deletes containers, unmounts SHM, removes infra container, cleans spoofed cgroup, stops network, removes namespaces, releases names, deletes sandbox/index entries, emits deletion event, and notifies NRI.

Control flow: missing sandboxes return empty success except empty ID and not-created sandbox errors. Internal removal processes workload containers first, then infra, then network/namespaces/indexes.

State and persistence: mutates runtime/storage container state, SHM mounts, network/CNI state, namespace resources, pod name reservation, sandbox store, pod ID index, CRI event channel, NRI state, and spoofed sandbox cgroups.

Dependencies and integration: depends on container removal helpers, sandbox state, cgroup manager, network teardown, NRI, CRI events, and indexes.

Risks: removal order is sensitive: network stop happens after container deletion and SHM/infra cleanup. Failures abort subsequent cleanup, so callers may need retries. NRI removal failure is logged but does not fail removal.

Test signals: `sandbox_remove_test.go` covers not-created sandbox error and empty-ID error through stop/remove entry points, but not full successful cleanup.
