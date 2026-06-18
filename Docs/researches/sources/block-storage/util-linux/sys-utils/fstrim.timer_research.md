# File Research: sources/block-storage/util-linux/sys-utils/fstrim.timer

Purpose: systemd timer that schedules the `fstrim` service.

Core behavior:
- Runs weekly with `AccuracySec=1h`, `Persistent=true`, and `RandomizedDelaySec=100min`.
- Avoids containers and initrd environments with `ConditionVirtualization=!container` and `ConditionPathExists=!/etc/initrd-release`.
- Installs under `timers.target`.

Dependencies and integration:
- Activates the service unit of the same base name, expected to be `fstrim.service`.

Risks and edge cases:
- Randomization and one-hour accuracy intentionally make execution time approximate rather than exact.
