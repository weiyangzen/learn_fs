# File Research: sources/block-storage/util-linux/sys-utils/fstrim.service.in

Purpose: systemd unit template for running periodic discard through `fstrim`.

Core behavior:
- Defines a oneshot service with `ExecStart=@sbindir@/fstrim --listed-in /etc/fstab:/proc/self/mountinfo --verbose --quiet-unsupported`.
- Runs only outside containers via `ConditionVirtualization=!container`.
- Applies service hardening while permitting device access needed for filesystem discard: `PrivateDevices=no`, `PrivateNetwork=yes`, `PrivateUsers=no`, kernel/control-group protections, `MemoryDenyWriteExecute=yes`, and a constrained `SystemCallFilter`.

Dependencies and integration:
- `@sbindir@` is substituted by the build/install system.
- Paired with `fstrim.timer` for weekly scheduling.

Risks and edge cases:
- The service intentionally leaves `PrivateDevices` disabled because FITRIM/mount-device probing needs real device visibility.
