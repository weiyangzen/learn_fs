# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/notify-multiuser.py

Purpose: RHEL9 workaround script that notifies the host VM harness when the guest reaches `multi-user.target`.

Important APIs/types/functions: reads `$CREDENTIALS_DIRECTORY/vmm.notify_socket`, parses `vsock:cid:port`, creates an `AF_VSOCK` `SOCK_SEQPACKET` socket, and sends `X_SYSTEMD_UNIT_ACTIVE=multi-user.target`.

Control flow: run by a systemd service after multi-user target; connects to host-provided vsock notification endpoint and sends one sd-notify-like line.

State/persistence: no persistent state; consumes systemd credentials at runtime.

Dependencies/integration: integrates with `testthing.VirtualMachine` sd-notify server and systemd credential injection.

Risks/test signals: assumes credential format and vsock support. Failure can make VM tests time out even if guest booted.
