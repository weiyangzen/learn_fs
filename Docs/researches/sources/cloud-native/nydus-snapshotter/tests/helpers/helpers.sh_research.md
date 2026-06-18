<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/helpers.sh -->
## sources/cloud-native/nydus-snapshotter/tests/helpers/helpers.sh

Purpose: project-specific shell helpers for e2e setup, wrapping Docker/Kind/Kubectl/Nydus commands, installing tools, configuring Docker, logging in, and starting a local authenticated registry.

Important functions: `configure::rootful`, `configure::dockerd`, `exec::docker`, `exec::kind`, `exec::kubectl`, `exec::nydusify`, `docker::configpath`, `docker::login`, installers for kind/kubectl/nydus/nerdctl, and `start::registry`.

Control flow and state: rootful mode prepends `sudo` to selected commands and changes Docker config path. Installers download release artifacts into temp dirs and install binaries into `/usr/local/bin`. `start::registry` creates an htpasswd file with an httpd container, starts a registry container on port 5000, and returns `<host eth0 ip>:5000`.

Dependencies/integration: sourced by `kind.sh` after generic `lib.sh`. Depends on Docker, curl/download helpers, tar extraction, GitHub/Nydus releases, and host install privileges.

Risks and test signals: mutates `/etc/docker/daemon.json` and restarts Docker, installs host binaries, and uses a fixed registry container/port. `ip addr show eth0` assumes host interface naming. It is operational test infrastructure, not production code.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/helpers.sh -->
