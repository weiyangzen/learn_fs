# sources/cloud-native/soci-snapshotter/scripts/parallel-mode-install.sh

Purpose: installs a released SOCI snapshotter binary and configures it as a systemd service/socket for parallel pull/unpack mode.

Important APIs/types/functions: environment defaults control concurrency, chunk size, discard behavior, SOCI version, root dir, and gzip decompressor path. It downloads release tarball and checksum, installs `soci-snapshotter-grpc`, writes `/etc/soci-snapshotter-grpc/config.toml`, writes systemd service/socket units, reloads systemd, and enables the service.

Control flow: derive arch, download artifacts to `/tmp`, verify checksum, extract binary to `/usr/local/bin`, remove downloads, write config and units via heredocs, start service.

State and persistence: mutates system directories `/usr/local/bin`, `/etc/soci-snapshotter-grpc`, `/etc/systemd/system`, and starts/enables a systemd unit.

Dependencies/integration points: integrates containerd content store, CRI keychain socket, parallel pull/unpack config, and custom gzip decompressor stream. Requires curl, sha256sum, tar, systemd, permissions to write system paths.

Risks: service starts before/with containerd via unit ordering but assumes containerd socket locations. Downloaded version default can drift from docs. The script trusts release checksum fetched from the same release location as the tarball.

Test signals: no direct tests; operational validation is service startup and containerd snapshotter behavior.
