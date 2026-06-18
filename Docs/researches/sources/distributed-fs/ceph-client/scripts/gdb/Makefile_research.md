# sources/distributed-fs/ceph-client/scripts/gdb/Makefile

Purpose: Top-level Kbuild makefile for GDB helper scripts.

Important APIs/rules: `subdir-y := linux` includes the `linux` helper package subdirectory in the build traversal.

Control flow: Kbuild descends into `scripts/gdb/linux`.

State/persistence: No direct outputs.

Dependencies/integration: Kbuild subdirectory mechanism.

Risks: If omitted, generated constants and out-of-tree symlinks for the GDB helpers would not be handled.

Test signals: Kernel build should descend into `scripts/gdb/linux` and produce expected helper artifacts.
