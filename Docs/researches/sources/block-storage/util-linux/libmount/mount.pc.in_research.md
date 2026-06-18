# File Research: sources/block-storage/util-linux/libmount/mount.pc.in

## Scope

Pkg-config template for libmount.

## Behavior

- Defines prefix, exec prefix, libdir, and includedir substitutions.
- Publishes package name `mount`, description, version, Cflags, public libs, private requirements, and private dl libs.
- Requires private blkid, SELinux, and cryptsetup substitutions as configured.

## Dependencies And Risks

- Consumers get `-I${includedir}/libmount` and `-lmount`.
- Static/private linking depends on correct substitution of `@LIBSELINUX@`, `@LIBCRYPTSETUP@`, and `@LIBDL@`.
