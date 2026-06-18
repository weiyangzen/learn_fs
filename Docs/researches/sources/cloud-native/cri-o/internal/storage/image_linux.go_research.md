# sources/cloud-native/cri-o/internal/storage/image_linux.go

Purpose: Linux implementation for moving the reexeced image-pull process into a transient systemd cgroup.

Important APIs/types/functions: `moveSelfToCgroup(cgroup string)`.

Control flow: chooses `system.slice` or `user.slice` for rootless mode, validates an explicit cgroup contains `.slice`, derives the slice base, builds a `crio-pull-image-PID.scope` unit name, and calls `utils.RunUnderSystemdScope` through a dbus connection manager.

State and persistence behavior: creates/moves the current process into a transient systemd scope. No image state is changed directly.

Dependencies and integration points: used by `pullImageChild` before opening the store. Depends on rootless detection, dbus manager, systemd scope utility, PID, and cgroup naming.

Risks: invalid cgroup names fail pulls using new cgroup mode. Systemd/dbus failures abort child pulls. Rootless slice selection must match the user session environment.

Test signals: no direct test in this subset; pull tests exercise error paths mostly before actual cgroup movement.
