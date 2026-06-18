# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sshd-vsock@.service

Purpose: per-connection OpenSSH service for vsock socket activation on RHEL9 test images.

Important APIs/types/functions: `ExecStart=-/usr/sbin/sshd -i $OPTIONS -o "AuthorizedKeysFile ${CREDENTIALS_DIRECTORY}/ssh.ephemeral-authorized_keys-all .ssh/authorized_keys"`, `StandardInput=socket`, `LoadCredential=ssh.ephemeral-authorized_keys-all`, and optional `/etc/sysconfig/sshd`.

Control flow: spawned for each accepted socket connection, runs sshd in inetd mode, and uses systemd credentials for ephemeral host-generated SSH keys.

State/persistence: persistent service definition; runtime credentials and socket fd are provided per activation.

Dependencies/integration: depends on OpenSSH, systemd credentials, socket activation, and the host VM harness.

Risks/test signals: credential path syntax and sshd options are distro-sensitive. Connection failure is caught by VM startup and test command execution.
