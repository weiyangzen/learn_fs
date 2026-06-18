# sources/cloud-native/cri-o/server/sandbox_network.go

Purpose: manages CNI network setup, status restoration, teardown, garbage collection, and CNI readiness waiting for pod sandboxes.

Important APIs and functions: `networkStart`, `getSandboxIPs`, `networkStop`, `cleanupCNIResultFiles`, `newPodNetwork`, `networkGC`, and `waitForCNIPlugin`.

Control flow: `networkStart` skips host network, builds `ocicni.PodNetwork`, runs CNI setup with a bounded context, fetches network status, records IPs, and adds hostport mappings once per IP family. A deferred cleanup calls `networkStop` if setup partially succeeds then later fails. `networkStop` removes hostports, builds the pod network, validates/may remove the netns, always attempts CNI teardown to avoid IP leaks, cleans stale CNI result files on failure, and marks network stopped even on many teardown failures to prevent retry loops.

State and persistence: mutates CNI state, hostport rules, sandbox network-stopped state, sandbox IPs in callers, netns filesystem paths, and `/var/lib/cni/results` cache files. `networkGC` delegates stale network cleanup to the configured CNI plugin.

Dependencies and integration: CNI current result parsing, ocicni, Kubernetes bandwidth annotations, hostport manager, sandbox annotations/cgroup parent/netns, platform-specific netns validation/cleanup, and metrics latency updates.

Risks: `cleanupCNIResultFiles` removes any cache file whose name contains the container ID, which is practical but string-based. Marking network stopped after teardown failure avoids loops but may leave external CNI state requiring GC. Startup timeout is based on the request deadline plus five minutes, which can still be long.

Test signals: no direct network tests in this subset; stop/remove/sandbox creation tests exercise some paths indirectly through mocks.
