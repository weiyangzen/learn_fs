# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sshd-vsock.socket

Purpose: systemd socket definition for accepting OpenSSH connections over AF_VSOCK.

Important APIs/types/functions: `[Socket] ListenStream=vsock::22` and `Accept=yes`, with ordering around `ssh-access.target`.

Control flow: when a host connection arrives on vsock port 22, systemd activates `sshd-vsock@.service`.

State/persistence: persistent guest service configuration; runtime state is the listening socket.

Dependencies/integration: integrates with OpenSSH, systemd socket activation, and the `testthing` ProxyCommand.

Risks/test signals: depends on guest kernel/systemd vsock support. VM tests will fail to connect if socket activation breaks.
