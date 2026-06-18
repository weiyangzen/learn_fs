# sources/cloud-native/moby/contrib/systemd-sysusers/docker.conf

## Purpose
Defines systemd-sysusers configuration for creating the Docker group.

## APIs, Types, And Functions
The config uses sysusers syntax to declare a `docker` group entry with no fixed numeric ID unless assigned by the system.

## Control Flow, State, And Integration
At package install or boot, `systemd-sysusers` reads the file and ensures the group exists. Persistent state is the system group database entry.

## Risks And Test Signals
Risks include unintended API socket access for members of the docker group and distro-specific group policy. Integration is with Docker socket permissions and packaging.
