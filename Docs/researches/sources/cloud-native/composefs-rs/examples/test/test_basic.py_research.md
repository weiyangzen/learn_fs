# sources/cloud-native/composefs-rs/examples/test/test_basic.py

Purpose: async pytest smoke test for composefs booted example images.

Important APIs/types/functions: `machine` async fixture, `test_basic`, `testthing.IpcDirectory`, and `testthing.VirtualMachine`.

Control flow: fixture requires `TEST_IMAGE`, starts a VM with verbose logging, and yields it. Test verifies root is read-only, `/sysroot` contains expected entries, writes to `/etc` and `/var`, reboots, checks both persisted, and removes them.

State/persistence: tests persistence of mutable deployment state across reboot while using VM snapshot mode by default.

Dependencies/integration: depends on QEMU/OVMF/vsock/SSH harness, example image bootability, and filesystem layout.

Risks/test signals: strong end-to-end signal for root immutability and `/etc`/`/var` overlays. It is expensive and host-dependent.
