# sources/distributed-fs/ceph-client/lib/zlib_inflate/Makefile

Purpose: Kbuild recipe for the kernel zlib inflate module/object.

Important entries:
- `obj-$(CONFIG_ZLIB_INFLATE) += zlib_inflate.o`.
- `zlib_inflate-objs := inffast.o inflate.o infutil.o inftrees.o inflate_syms.o`.

Control flow: Build-time composition only. The object combines the state machine, fast decoder, table builder, utility blob helper, and symbol exports.

State and persistence: No runtime state.

Dependencies and integration:
- Selected by `CONFIG_ZLIB_INFLATE`.
- Used by boot decompressors, crypto, firmware, AppArmor, and other kernel decompression consumers.

Risks:
- Object list order must include symbol provider files. Omitting `inflate_syms.o` breaks modular users.
- Comments emphasize static allocation/no blocking allocation; callers still must provide per-stream workspace.

Test signals:
- Build with `CONFIG_ZLIB_INFLATE` built-in and modular if supported.
- Link checks for all exported inflate symbols.
