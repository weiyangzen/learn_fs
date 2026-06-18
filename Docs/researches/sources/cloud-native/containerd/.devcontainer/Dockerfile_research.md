# sources/cloud-native/containerd/.devcontainer/Dockerfile

## Purpose
This Dockerfile defines the base image for containerd development in VS Code/devcontainers. It layers containerd build and integration-test dependencies onto Ubuntu 22.04.

## Important APIs, Types, And Functions
It uses `mcr.microsoft.com/devcontainers/base:1-ubuntu-22.04`, installs packages such as `gperf`, `dmsetup`, `libseccomp-dev`, `xfsprogs`, `iptables`, autotools, C++ compiler, `libtool`, and `acl`, then adds the CRIU PPA and installs `criu`.

## Control Flow
The image updates apt metadata, installs dependencies without recommends, cleans apt lists, adds `ppa:criu/ppa`, installs CRIU, sets default ACLs on `/tmp`, and copies the devcontainer welcome message.

## State And Persistence
Persistent image state is installed packages, apt configuration for the CRIU PPA, `/tmp` default ACLs, and the first-run notice file.

## Dependencies And Integration Points
It integrates with `.devcontainer/devcontainer.json` as the build Dockerfile and supports scripts in `.devcontainer/setup.sh`, Makefile builds, and rootful integration tests.

## Risks
The base image and PPA are external moving dependencies. Package versions are not pinned, so rebuilds can change behavior. `/tmp` ACL changes affect permissions inside the development container and should be intentional.

## Test Signals
A devcontainer build followed by `.devcontainer/setup.sh`, `make binaries`, `make test`, and root tests is the main validation signal.
