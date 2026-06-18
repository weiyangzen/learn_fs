<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_freebsd.go -->
# sources/cloud-native/cri-o/server/container_create_freebsd.go

## Purpose

This file supplies FreeBSD-specific implementations for helpers that Linux creation shares through common names. It lets the common `container_create.go` path compile while omitting Linux-only behavior such as AppArmor, sysfs setup, FIPS toggles, systemd mounts, and user-namespace remapping.

## Important APIs, Types, and Functions

`finalizeUserMapping`, `setContainerConfigSecurityContext`, `disableFipsForContainer`, `addSysfsMounts`, `setOCIBindMountsPrivileged`, `addOCIBindMounts`, `addShmMount`, `setupSystemdMounts`, `getSpecGen`, `specSetApparmorProfile`, `specSetBlockioClass`, and `specSetDevices` mirror the Linux helper surface. `addOCIBindMounts` is the substantial function and supports CRI bind mounts with simple read-only/read-write options.

## Control Flow

FreeBSD bind mount setup sorts CRI mounts, removes default OCI mounts shadowed by explicit `/dev` or `/sys` mounts, validates container and host paths, warns on mounting host `/` over container `/`, resolves symlinks, creates missing sources except during restore, rejects configured absent sources, and returns `oci.ContainerVolume` plus OCI mount specs. `getSpecGen` clears rlimits, adds configured ulimits, applies root read-only state, and adds tmpfs mounts for read-only roots where CRI did not override them. Device setup still delegates to configured devices and annotation parsing.

## State and Persistence Behavior

The file mutates the in-memory OCI spec generator by clearing and adding mounts and rlimits. It may create missing host source directories with `os.MkdirAll`. It has no runtime persistence of its own beyond data consumed by the common creation pipeline.

## Dependencies and Integration Points

It depends on CRI types, runtime-tools generate, OpenContainers runtime spec, internal device parsing, sandbox metadata, storage container info, CRI-O annotation helpers, and the common server/runtime objects. It integrates as the FreeBSD counterpart for helper functions called from the shared create path.

## Risks and Edge Cases

Compared to Linux, mount propagation, recursive read-only, ID-mapped mounts, image volume mounts, SELinux, AppArmor, blockio, and systemd behavior are largely absent or no-op. The function still creates missing host paths, which can surprise restore flows if the restore check regresses. The use of `golang.org/x/net/context` instead of the standard package is harmless but atypical.

## Test Signals

There are no FreeBSD-specific tests in this subset. Linux tests exercise the richer shared helper contract but do not validate this simplified platform behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_freebsd.go -->
