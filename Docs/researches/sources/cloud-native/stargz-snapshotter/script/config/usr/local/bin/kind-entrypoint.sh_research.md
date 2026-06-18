# sources/cloud-native/stargz-snapshotter/script/config/usr/local/bin/kind-entrypoint.sh

Purpose: Kind node entrypoint wrapper that enables cgroup-v2 nesting before running the requested command.
Important APIs/types/functions: cgroup-v2 controller setup block and final `exec $@`.
Control flow: moves existing root cgroup processes into `/init`, enables subtree controllers, then delegates to the original entrypoint command.
State and persistence: mutates cgroup files inside privileged kind node containers.
Dependencies and integration points: copied from Docker-in-Docker patterns and used by kind-compatible node images.
Risks: requires privileges and cgroup v2; `$@` is intentionally unquoted in source and could split unusual arguments.
Test signals: validated indirectly by kind/CRI tests that boot nodes successfully.
