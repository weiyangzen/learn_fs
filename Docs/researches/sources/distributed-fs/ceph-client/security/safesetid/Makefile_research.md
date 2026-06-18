<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/Makefile -->
# sources/distributed-fs/ceph-client/security/safesetid/Makefile

## Purpose

The SafeSetID Makefile builds the SafeSetID composite object from enforcement and securityfs policy-editor sources.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_SECURITY_SAFESETID) := safesetid.o` includes the LSM when enabled.
- `safesetid-y := lsm.o securityfs.o` links the hook implementation and securityfs interface into one object.

## Control Flow

There is no runtime flow. Kbuild creates `safesetid.o` from both component objects when `SECURITY_SAFESETID` is enabled.

## State and Persistence Behavior

No runtime state is defined here. Ruleset state and initialization flags are in the C sources.

## Dependencies and Integration Points

This file integrates the SafeSetID directory with the kernel security build.

## Risks and Edge Cases

If either component is omitted, SafeSetID would either enforce without a policy interface or expose an interface without hooks. The composite object list avoids that split.

## Test Signals

Configured builds should compile both `lsm.o` and `securityfs.o` into `safesetid.o`; disabled builds should omit them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/safesetid/Makefile -->
