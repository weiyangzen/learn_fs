## sources/cloud-native/moby/daemon/libnetwork/support/Dockerfile

Purpose: Defines a diagnostic support container image for collecting Docker/libnetwork datapath and control-plane state inside a Docker-in-Docker environment.

Important instructions: Starts from `docker:18-dind`, adds Alpine edge repositories, installs networking/debugging tools (`util-linux`, `bridge-utils`, `iptables`, `iputils`, `iproute2`, `ipvsadm`, `conntrack-tools`, `jq`, `bash`), copies shell scripts into `/bin`, and runs `/bin/run.sh` by default.

Control flow and state: Build-time state is limited to package installation and script copy. Runtime behavior is delegated fully to `run.sh`, which may update `support.sh` before execution.

Dependencies and integration points: Depends on Docker-in-Docker, Alpine packages, and the support scripts in the same directory. The image is coupled to Docker networking internals such as `/var/run/docker/netns` and expects privileged/network access when run for diagnostics.

Risks: Base image `docker:18-dind` is old and may contain outdated tooling or package compatibility issues. Adding Alpine edge repositories can reduce reproducibility. The support image is diagnostic rather than production code, but it may need privileged host access and should be handled accordingly.

Test signals: No local tests; correctness is operational and depends on successful package install plus script behavior.
