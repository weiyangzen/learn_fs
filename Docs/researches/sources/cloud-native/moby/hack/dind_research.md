# sources/cloud-native/moby/hack/dind

## Purpose
Docker-in-Docker wrapper for privileged containers that need to run Docker/Moby tests or daemons.

## Important APIs and Types
Shell entrypoint using environment variable `container=docker`, mounts, cgroup v2 setup, and final `exec "$@"`.

## Control Flow, State, and Persistence
The script mounts securityfs for AppArmor detection when available, mounts `/tmp` as tmpfs if needed, enables cgroup v2 nesting by moving processes to `/init` and writing subtree controllers in a retry loop, makes `/` recursively shared, and executes the requested command. If no command is supplied it prints an error.

## Dependencies, Integration Points, Risks, and Test Signals
Requires privileged container permissions, `mountpoint`, cgroup files, and kernel support. Used by CI/development containers. Risks are broad privileged mount changes, securityfs exposure, infinite cgroup retry if controllers cannot be enabled, and host-dependent behavior. Test signals are integration jobs that run daemon and archive/network tests inside DinD.
