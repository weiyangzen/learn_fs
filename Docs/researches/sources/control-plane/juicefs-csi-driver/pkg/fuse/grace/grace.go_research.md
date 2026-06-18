# sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/grace.go

Purpose: implements the Unix-socket graceful upgrade control plane for JuiceFS mount pods, including single-pod upgrades, batch dispatch, canary validation, FUSE fd handoff, SIGHUP, and optional pod recreation tracking.

Important APIs and types: `ServeGfShutdown` starts a Unix socket listener and dispatches connections to `handleShutdown`. `upgradeRequest` and `parseRequest` decode socket messages. `SinglePodUpgrade`, `NewPodUpgrade`, and `(*PodUpgrade).gracefulShutdown` orchestrate one pod. Supporting methods include `prepareShutdown`, `sighup`, `isInUpgradeProcess`, `waitForUpgrade`, `uploadBinary`, `TriggerShutdown`, and `sendMessage`.

Control flow: incoming messages either list known FUSE fds, start a batch upgrade, or run a single-pod upgrade under a 30-minute timeout. A single upgrade fetches the mount pod, checks node and hash, verifies eligibility, reads JuiceFS `.config` from the mount point, creates and waits for a canary job, optionally annotates the pod as upgrading, captures/closes FUSE fd for recreate flows, uploads binaries for non-recreate flows, sends SIGHUP to the mount process, creates an event, and for recreate waits for a replacement ready pod with the same upgrade UUID.

State and persistence behavior: persistent side effects are Kubernetes annotations (`JfsUpgradeProcess`), events, Jobs, and possibly modified files inside the mount container. It reads mount-point config files and uses `passfd.GlobalFds` for FUSE session ID/fd state. Socket messages are transient progress output to the caller.

Dependencies and integration points: integrates Kubernetes client operations, `resource` upgrade eligibility and job/pod status helpers, `builder.NewCanaryJob`, `passfd`, config image feature detection, mount pod labels/annotations, and Unix domain socket clients.

Risks and test signals: errors from `NewPodUpgrade` can return nil `err` in some validation branches such as wrong node or missing hash, which can make failure diagnosis ambiguous. `waitForUpgrade` closes `done` in a defer while informer handlers may send to it, risking send-on-closed-channel if events race after return. Test coverage in the listed set only covers `parseRequest`; the operational Kubernetes/socket/fd paths require integration testing.
