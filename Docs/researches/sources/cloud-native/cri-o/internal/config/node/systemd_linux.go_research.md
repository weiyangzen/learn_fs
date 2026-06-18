# sources/cloud-native/cri-o/internal/config/node/systemd_linux.go

Purpose: detects whether the host systemd supports specific cgroup properties used by CRI-O.

Important APIs/types/functions: globals `systemdHasAllowedCPUsOnce`, `systemdHasAllowedCPUs`, and `systemdHasAllowedCPUsErr`; `SystemdHasAllowedCPUs`; and `systemdSupportsProperty(property string)`.

Control flow: `SystemdHasAllowedCPUs` caches a call to `systemdSupportsProperty("AllowedCPUs")`. The helper connects to systemd D-Bus with `dbus.NewSystemdConnection`, closes it on return, and calls `GetManagerProperty` to see whether the property is available.

State and persistence behavior: caches the boolean and error in package globals. It opens a transient D-Bus connection but writes no persistent state.

Dependencies/integration points: depends on `github.com/coreos/go-systemd/v22/dbus`; used by `node.ValidateConfig` as a nonfatal feature check for cgroup/systemd CPU controls.

Risks: startup behavior depends on systemd D-Bus availability. Result caching means a systemd upgrade/restart after first check is not observed until process restart.

Test signals: no direct tests in this subset.
