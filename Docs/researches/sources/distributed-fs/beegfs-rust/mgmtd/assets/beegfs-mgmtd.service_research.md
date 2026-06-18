<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/assets/beegfs-mgmtd.service -->
## sources/distributed-fs/beegfs-rust/mgmtd/assets/beegfs-mgmtd.service

**Purpose:** Systemd unit for running the BeeGFS management server from packaged installs.

**Important APIs/types/functions:** `[Unit]` describes BeeGFS Management Server, references BeeGFS documentation, requires and starts after `network-online.target`. `[Service]` uses `Type=notify` and `ExecStart=/opt/beegfs/sbin/beegfs-mgmtd --log-target=journald`. `[Install]` wants `multi-user.target`.

**Control flow:** Systemd waits for network-online, starts the packaged binary, expects sd-notify readiness, and logs to journald as instructed by the binary argument.

**State and persistence behavior:** No app state in the unit; it relies on the binary default/configured database and auth paths, typically under `/var/lib/beegfs` and `/etc/beegfs`.

**Dependencies and integration points:** Installed by RPM/DEB metadata in `mgmtd/Cargo.toml`; depends on the binary path and the `sd-notify` runtime behavior.

**Risks:** There is no explicit restart policy, user/group hardening, or config-file override in the unit. `Requires=network-online.target` line has trailing whitespace but should parse. If the binary fails to notify readiness, systemd may treat startup as failed.

**Test signals:** Install package, run `systemctl daemon-reload`, start the service, verify readiness notification and journald logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/assets/beegfs-mgmtd.service -->
