<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/Kconfig -->
# sources/distributed-fs/ceph-client/security/loadpin/Kconfig

## Purpose

`loadpin/Kconfig` defines configuration options for the LoadPin LSM, which pins kernel-read files such as modules, firmware, kexec images, and policies to the first filesystem used for such loads.

## Important APIs, Types, and Functions

- `SECURITY_LOADPIN` enables the LSM and depends on `SECURITY` and `BLOCK`.
- `SECURITY_LOADPIN_ENFORCE` makes LoadPin enforcing at boot and depends on module compression being compatible with in-kernel decompression when modules are compressed.
- `SECURITY_LOADPIN_VERITY` allows trusted dm-verity-backed filesystems outside the pinned root and depends on built-in `DM_VERITY` and `SECURITYFS`.

## Control Flow

Kconfig selection controls whether `loadpin.o` is built, whether enforcement defaults to on, and whether the securityfs dm-verity digest interface is compiled. Runtime behavior is implemented in `loadpin.c`.

## State and Persistence Behavior

The configuration determines default boot state. `SECURITY_LOADPIN_ENFORCE` seeds the `enforce` module parameter; `SECURITY_LOADPIN_VERITY` adds persistent in-kernel trusted root digest state populated once at runtime.

## Dependencies and Integration Points

The options integrate with the LSM framework, block-device read-only checks, module loading, firmware loading, kernel file-reading hooks, dm-verity, and securityfs.

## Risks and Edge Cases

Enabling enforcement on systems with initrds, writable roots, or module compression not decompressed in-kernel can block legitimate loads. Verity support expands the trust model and depends on a carefully supplied digest list.

## Test Signals

Build matrix tests should cover LoadPin disabled, permissive, enforcing, and dm-verity-enabled configurations. Boot tests should verify enforcement defaults and kernel parameter override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/Kconfig -->
