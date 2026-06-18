# sources/cloud-native/stargz-snapshotter/script/demo/init.sh

Purpose: Initializes cgroup-v2 nesting for the demo container and keeps it alive.
Important APIs/types/functions: cgroup setup block and final `exec sleep infinity`.
Control flow: moves cgroup processes, enables controllers, then sleeps forever for interactive use.
State and persistence: mutates cgroup files but no app data.
Dependencies and integration points: entrypoint for `script/demo/docker-compose.yml`.
Risks: requires privileged container and cgroup v2; does not start daemons by itself.
Test signals: demo user runs `demo/run.sh` after container startup.
