# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/kvm.conf

## Purpose

This is a machine-specific example for running ktest against a libvirt/KVM guest named `Guest`. It demonstrates how to reuse the generic include files while replacing physical power control and serial console handling with `virsh` commands.

## Important APIs, Types, And Data

The config sets `MACHINE=Guest`, `CONSOLE=virsh console ${MACHINE}`, `CLOSE_CONSOLE_SIGNAL=KILL`, `TEST:=patchcheck`, `MULTI:=0`, `BITS:=64`, and `REBOOT:=empty`. It includes `include/defaults.conf`, sets `POST_INSTALL` to run `dracut` on the guest, defines `POWERCYCLE_AFTER_REBOOT=3` and `POWEROFF_AFTER_HALT=20`, then uses `DEFAULTS OVERRIDE` to replace `POWER_CYCLE` with `virsh destroy/start`. It includes patchcheck, tests, bisect, min-config, and bootconfig test definitions.

## Control Flow

`ktest.pl` reads the top-level machine settings, imports defaults, then overrides `POWER_CYCLE` after defaults have already defined it. Later includes materialize test sections according to `TEST` and `MULTI`, which by default means patchcheck. At runtime, console monitoring is through a child process running `virsh console`; reboot failures trigger a delayed `virsh destroy`/`virsh start` power cycle.

## State And Persistence Behavior

Persistent state exists in the guest disk and host libvirt domain. Kernel images/modules/initramfs are installed inside the guest via SSH/SCP and `dracut`; libvirt domain state is mutated by destroy/start operations. ktest writes logs and build outputs under paths inherited from defaults.

## Dependencies And Integration Points

It depends on libvirt `virsh`, a guest named `Guest`, passwordless root SSH, a Fedora-like guest with `/sbin/dracut`, a working serial console, and the generic include files. It integrates with ktest's `CONSOLE`, `CLOSE_CONSOLE_SIGNAL`, `POWER_CYCLE`, `POST_INSTALL`, and reboot fallback options.

## Risks And Edge Cases

`virsh destroy` is abrupt and can corrupt guest state if filesystems are not stable. Killing `virsh console` with `KILL` avoids stuck console sessions but prevents graceful cleanup. `POST_INSTALL` assumes the target image path and initramfs name match the guest bootloader. `REBOOT:=empty` falls into the default reboot-on-success/error policy from defaults.

## Test Signals

Dry-run should resolve `POWER_CYCLE` to the virsh destroy/start sequence and show patchcheck as the default test. Runtime validation includes seeing serial console output through `virsh console`, successful `dracut` post-install commands, and correct forced power cycles after reboot stalls.
