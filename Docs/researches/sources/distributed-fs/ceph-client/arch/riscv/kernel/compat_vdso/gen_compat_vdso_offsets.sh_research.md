# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/gen_compat_vdso_offsets.sh

Purpose: Generates C preprocessor definitions for compat VDSO symbol offsets from the linked debug VDSO image.

Important APIs/types/functions: Invokes the common `vdso/gen_vdso_offsets.sh` script with a `compat_` prefix.

Control flow: During the build, Kbuild runs this shell script against `compat_vdso.so.dbg`; the common script extracts selected symbols and emits offset definitions used by kernel C code.

State and persistence: The generated header persists in the build tree and tracks the linked VDSO image layout.

Dependencies and integration points: Depends on shell, the common VDSO offset generator, objdump/readelf tooling used by that generator, and compat VDSO mapping code.

Risks and test signals: Prefix or symbol extraction errors cause kernel code to reference wrong offsets. Test by rebuilding after VDSO symbol changes and comparing generated offsets against `readelf -s`.
