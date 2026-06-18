# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/systemd-ssh-proxy

Purpose: Python polyfill for `systemd-ssh-proxy`, forwarding an already-open stdout socket to a vsock connection via fd passing.

Important APIs/types/functions: argparse parser for `vsock/<cid>` and port, `socket.AF_VSOCK`, and `socket.send_fds`.

Control flow: parses address, wraps stdout as a socket, connects a new vsock stream to the guest, sends that fd through stdout, and closes the local vsock socket.

State/persistence: no persistent state; operates per ProxyCommand invocation.

Dependencies/integration: depends on Python fd-passing support and AF_VSOCK. Used where systemd's proxy binary is unavailable.

Risks/test signals: assumes stdout is a socket suitable for fd passing. SSH connection tests reveal breakage.
