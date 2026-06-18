# sources/cloud-native/cri-o/internal/dbusmgr/user.go

Purpose: detects and opens a rootless user systemd D-Bus connection, including special handling for user namespaces.

Important APIs/types/functions: `newUserSystemdDbus`, `DetectUID`, and `DetectUserDbusSessionBusAddress`.

Control flow: `newUserSystemdDbus` finds a bus address and UID, dials D-Bus, authenticates with external auth for that UID, sends Hello, and wraps the connection for go-systemd. `DetectUID` returns `os.Getuid` outside user namespaces; inside, it executes `busctl --user --no-pager status` and parses `OwnerUID=...`. `DetectUserDbusSessionBusAddress` prefers `DBUS_SESSION_BUS_ADDRESS`, then `$XDG_RUNTIME_DIR/bus`, then parses `DBUS_SESSION_BUS_ADDRESS=` from `systemctl --user --no-pager show-environment`.

State and persistence behavior: reads environment variables, checks filesystem existence for the user bus path, and shells out to busctl/systemctl. No persistent writes.

Dependencies/integration points: godbus, go-systemd, moby userns detection, CRI-O cmdrunner. Called from `DbusConnManager` when rootless mode uses user systemd.

Risks: rootless operation depends on user session D-Bus availability and external commands. Scanner parsing is strict about key prefixes. Authentication errors close the connection before returning.

Test signals: no direct tests here; command execution is abstracted through cmdrunner and could be mocked.
