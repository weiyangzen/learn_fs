## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/gen_vdso_offsets.sh

Purpose: Converts `nm` output for the vDSO debug shared object into C preprocessor defines containing offsets of exported `__kernel_*` symbols.

Important behavior: The script sets `LC_ALL=C` and runs a single `sed` expression that matches hexadecimal addresses followed by a symbol type and `__kernel_` name, emitting `#define vdso_offset_<name> 0x<addr>`.

Control flow: Kbuild pipes `$(NM) vdso.so.dbg` into this script and sorts the output. No files are opened directly by the script.

State and persistence: Stateless; generated persistence is handled by the Makefile target `include/generated/vdso-offsets.h`.

Dependencies and integration: Depends on stable `nm` output format, exported vDSO symbol naming, POSIX shell, and sed. Used by the vDSO Makefile.

Risks and test signals: Risks are symbol-name pattern drift or locale-sensitive sorting if `LC_ALL` were not set. Test signals are correct defines for all `__kernel_*` symbols and rebuild stability when vDSO inputs do not change.
