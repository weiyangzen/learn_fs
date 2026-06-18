# sources/cloud-native/composefs-rs/examples/testthing.py

Purpose: standalone async VM harness used by pytest and manually to boot qcow2 images, wait for guest readiness over vsock, and execute commands over SSH.

Important APIs/types/functions: `IpcDirectory`, `_vsock_listen`, `_find_qemu`, `_find_ovmf`, `_qmp_command`, `_ssh_direct_args`, `GuestPath`, `VirtualMachine`, `SubprocessError`, `cleanup_on_signal`, and `_main`.

Control flow: allocates `/run/user/$uid/test.thing/tt.n`, generates an ephemeral SSH key, starts a vsock sd-notify server, launches QEMU with OVMF, QMP, virtio disk, vhost-vsock, credentials, and console logging, waits for guest `multi-user.target` notification, establishes an SSH control socket, then exposes `execute`, `write`, `reboot`, port-forwarding, and QMP operations. Shutdown cancels background tasks and quits or powers down the VM depending on snapshot mode.

State/persistence: IPC directories, SSH keys, control sockets, QMP socket, console logs, and copied OVMF VARS are host-side transient state. Guest disk writes are transient when `snapshot=True` and persistent with `--maintain`.

Dependencies/integration: depends on Python asyncio, QEMU/KVM, OVMF, OpenSSH, AF_VSOCK, systemd credentials, guest notifier units, and pytest fixtures. It integrates tightly with the workaround files in this subset.

Risks/test signals: startup timeout reports console logs, giving good diagnostics. Risks include distro-specific QEMU/OVMF paths, vsock CID assignment by chosen port, SSH ProxyCommand availability, snapshot semantics, and a formatting bug in one timeout string literal that lacks an `f` prefix.
