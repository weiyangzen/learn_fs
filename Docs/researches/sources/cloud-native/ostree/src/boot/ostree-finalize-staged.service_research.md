# sources/cloud-native/ostree/src/boot/ostree-finalize-staged.service

Purpose: This systemd service finalizes a staged OSTree deployment during shutdown by running its command in `ExecStop`.

Important APIs, types, and functions: Unit conditions require `/run/ostree-booted`. It has no default dependencies, requires mounts for `/sysroot`, `/boot`, and `/etc`, runs after `local-fs.target`, `systemd-journal-flush.service`, and the hold service, before `basic.target` and `final.target`, and conflicts with `final.target`. It wants `ostree-finalize-staged-hold.service`. Service uses `Type=oneshot`, `RemainAfterExit=yes`, `ExecStop=/usr/bin/ostree admin finalize-staged`, `TimeoutStopSec=5m`, `ProtectHome=yes`, and `ReadOnlyPaths=/etc`.

Control flow: The service starts and remains active during boot; finalization occurs when systemd stops it during shutdown. Ordering is designed so logs are flushed and `/boot` remains available before the staged deployment is committed.

State and persistence behavior: `finalize-staged` mutates deployment and bootloader state under `/sysroot` and `/boot`, and may remove `/var/.updated`. It explicitly avoids changing the current deployment's `/etc` by making `/etc` read-only.

Dependencies and integration points: Integrates with the staged deployment machinery, bootloader updates, journal flushing, hold service, systemd shutdown transaction, and mounted sysroot/boot filesystems.

Risks: This is high-risk boot state mutation. Timeout, mount, or bootloader failures can leave upgrades unfinalized. Running at shutdown makes observability harder, hence journal ordering. Sandboxing must allow required `/sysroot` and `/boot` writes while limiting unrelated state access.

Test signals: No direct test in this subset. End-to-end staged upgrade tests and bootloader state inspections are needed.
