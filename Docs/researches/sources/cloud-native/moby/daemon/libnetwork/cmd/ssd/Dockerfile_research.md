<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/Dockerfile -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/Dockerfile

## Purpose
Builds the legacy `docker/ssd` service-state diagnostic image used by `ssd.py` to inspect swarm service discovery, ingress NAT, and IPVS programming.

## Important APIs, Types, And Functions
The Dockerfile is Alpine-based, installs networking/debug tools, Python 2, `pip`, Docker Python client from Git, adds `ssd.py`, and sets `ENTRYPOINT ["python", "/ssd.py"]`.

## Control Flow
Image build installs packages, creates Python 2 compatibility symlinks, bootstraps pip with `easy_install`, installs docker-py from Git, and then runs the script at container startup.

## State And Persistence
The image has no runtime persistence by itself. Diagnostics depend on a mounted Docker socket and host/network namespace files.

## Dependencies And Integration Points
Depends on Alpine `apk`, Python 2 packages, `ipvsadm`, `iproute2`, `iptables`, `nsenter`, `bash`, and a reachable Git repository for docker-py during build.

## Risks And Edge Cases
Python 2 and `easy_install` are obsolete, and `git://` is unauthenticated and often blocked. `pip install --upgrade pip` on Python 2 can select unsupported versions unless constrained by package indexes. The image needs privileged host access to be useful.

## Test Signals
A successful build and `docker/ssd <network>` run that can import `docker`, access `/var/run/docker.sock`, and invoke host namespace tools are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/Dockerfile -->
