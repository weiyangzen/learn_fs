# sources/cloud-native/stargz-snapshotter/script/demo/run.sh

Purpose: Builds, installs, and starts containerd plus stargz snapshotter in the demo container.
Important APIs/types/functions: `retry`, `kill_all`, `cleanup`; daemon root/socket constants.
Control flow: copies demo configs, kills old daemons, unmounts/clears roots, builds and installs binaries, starts `containerd-stargz-grpc`, waits for socket, and starts containerd with optional extra args.
State and persistence: clears `/var/lib/containerd` and `/var/lib/containerd-stargz-grpc`; installs binaries from local build output.
Dependencies and integration points: depends on demo compose environment, make, FUSE, containerd, and CNI config file outside this subset.
Risks: destructive cleanup; missing `config.cni.conflist` would fail copy; broad process matching can kill unrelated processes in non-isolated environments.
Test signals: manual demo signal is running containerd and snapshotter socket readiness.
