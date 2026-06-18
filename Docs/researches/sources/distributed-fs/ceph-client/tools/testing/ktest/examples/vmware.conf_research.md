# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/vmware.conf

## Purpose

This is a VMware guest example for ktest. It documents serial-pipe setup and configures ktest to monitor the VMware serial socket, install kernels in the guest, and power cycle the VM through `vmrun`.

## Important APIs, Types, And Data

The config sets `MACHINE=Guest`, VMware-specific variables `VMWARE_SERIAL_NAME`, `VMWARE_VM_NAME`, `VMWARE_VM_DIR`, `VMWARE_VM_BASE_DIR`, `CONSOLE=/usr/bin/ncat -U ...`, `VMWARE_HOST_TYPE=ws`, and `VMWARE_POWER_CYCLE=/usr/bin/vmrun -T ... reset ... nogui`. It then mirrors the generic test selection variables, includes defaults, sets `POST_INSTALL` to run `dracut`, configures reboot/halt fallback delays, overrides `POWER_CYCLE=${VMWARE_POWER_CYCLE}`, and includes patchcheck, tests, bisect, and min-config definitions.

## Control Flow

`ktest.pl` parses VMware variables before defaults so later options can reference them. `DEFAULTS OVERRIDE` replaces the generic power script with the VMware reset command. Runtime console monitoring reads the Unix serial pipe with `ncat`; reboot stalls and forced recovery use `vmrun reset`.

## State And Persistence Behavior

Persistent state includes the VM disk, generated initramfs, installed kernel image/modules, VMware VM runtime state, and ktest logs/build outputs. The serial pipe is external state created by VMware configuration. Placeholders such as `<virtual machine name>` must be replaced before use.

## Dependencies And Integration Points

It depends on VMware Workstation/Fusion/Player tooling, `/usr/bin/ncat`, a configured serial port socket, root SSH to the guest, `dracut`, and the included ktest fragments. It integrates with ktest's console, power-cycle, post-install, and shared test-selection options.

## Risks And Edge Cases

The file uses `.kmx` in comments and paths; many VMware Linux configurations use `.vmx`, so users must verify actual VM file naming. Placeholder values will produce invalid paths if left unchanged. `vmrun reset` is abrupt. Serial-pipe setup must choose server/from-VM options correctly or ktest will hang waiting for console output.

## Test Signals

Dry-run should show the ncat Unix-socket console and `vmrun` reset command after placeholders are replaced. Runtime validation includes readable serial output, successful `dracut` post-install, and a forced VMware reset after configured reboot timeouts.
