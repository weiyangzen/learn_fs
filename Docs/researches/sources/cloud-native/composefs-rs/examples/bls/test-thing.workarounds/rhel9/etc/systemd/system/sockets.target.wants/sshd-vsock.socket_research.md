# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sockets.target.wants/sshd-vsock.socket

Purpose: enables the RHEL9 SSH-via-vsock socket for VM tests.

Important APIs/types/functions: socket unit content `ListenStream=vsock::22`, `Accept=yes`, `Wants=ssh-access.target`, `Before=ssh-access.target`.

Control flow: systemd socket activation listens on guest vsock port 22 and starts an instance service per connection.

State/persistence: persistent socket enablement in `sockets.target.wants`.

Dependencies/integration: depends on systemd socket units, AF_VSOCK, and `sshd-vsock@.service`.

Risks/test signals: duplicated unit can drift from canonical socket file. Without it, the host cannot connect over the expected vsock path.
