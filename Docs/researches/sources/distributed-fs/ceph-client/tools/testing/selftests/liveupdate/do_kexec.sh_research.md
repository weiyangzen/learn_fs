# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/do_kexec.sh

## Purpose

`do_kexec.sh` is a helper that loads and executes a replacement kernel for liveupdate tests using kexec file loading and command-line reuse.

## Important APIs, Types, and Functions

It uses `/bin/sh`, `set -e`, environment variables `KERNEL` and `INITRAMFS`, default paths `/boot/bzImage` and `/boot/initramfs`, and commands `kexec -l -s --reuse-cmdline`, optional `--initrd=...`, and `kexec -e`.

## Control Flow and State

The script builds the `kexec` argument vector with `set --`, conditionally appends an initrd if the file exists, loads the kernel, then immediately executes it. State changes are system-wide: a kernel image is loaded into kexec state and then booted.

## Dependencies and Integration Points

It depends on root privileges, kexec tooling, a valid kernel image, optional initramfs, and kernel support declared in `liveupdate/config`.

## Risks and Test Signals

Risks are destructive by design: successful `kexec -e` replaces the running kernel. Other risks are wrong default paths and missing initrd. Signals are shell exit on failed load and actual transition to the new kernel on success.
