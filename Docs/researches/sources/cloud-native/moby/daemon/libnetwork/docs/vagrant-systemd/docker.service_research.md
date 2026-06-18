<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/docs/vagrant-systemd/docker.service -->
# sources/cloud-native/moby/daemon/libnetwork/docs/vagrant-systemd/docker.service

## Purpose
Systemd unit file used by libnetwork Vagrant documentation to run the Docker daemon with socket activation and optional `/etc/default/docker` options.

## Important APIs, Types, And Functions
The unit declares `After=network.target docker.socket`, `Requires=docker.socket`, `EnvironmentFile=-/etc/default/docker`, `ExecStart=/usr/bin/docker daemon -H fd:// $DOCKER_OPTS`, `MountFlags=slave`, and high process/file/core limits.

## Control Flow
Systemd starts Docker after the network target and required socket, passes file descriptor socket activation with `-H fd://`, and enables the unit under `multi-user.target`.

## State And Persistence
No repository state. Runtime daemon state is managed by Docker and systemd on the Vagrant host.

## Dependencies And Integration Points
Depends on systemd, `docker.socket`, `/usr/bin/docker`, and optional `/etc/default/docker`.

## Risks And Edge Cases
`docker daemon` is historical syntax and may be obsolete in newer Docker versions. `MountFlags=slave` is legacy systemd behavior. This is documentation support, not production packaging.

## Test Signals
In the documented Vagrant environment, `systemctl start docker` should launch the daemon and socket activation should work.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/docs/vagrant-systemd/docker.service -->
