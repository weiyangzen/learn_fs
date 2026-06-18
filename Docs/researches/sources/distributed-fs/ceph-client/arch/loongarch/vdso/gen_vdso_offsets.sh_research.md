<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/gen_vdso_offsets.sh -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/gen_vdso_offsets.sh

### Purpose
`gen_vdso_offsets.sh` converts vDSO symbol addresses from `nm` output into C preprocessor constants.

### Important APIs, Types, And Functions
The script is a shell wrapper around one `sed` command that matches symbols named `VDSO_*` and emits `#define vdso_offset_<name> 0x<addr>`.

### Control Flow
It reads standard input, strips leading zeroes from hex addresses, filters matching symbol lines, captures the suffix after `VDSO_`, and prints defines. The Makefile sorts its output.

### State, Persistence, And Dependencies
No runtime state. Build output is `include/generated/vdso-offsets.h`. Dependencies are POSIX shell, `sed`, `nm` output format, and `LC_ALL=C` sorting in the caller.

### Integration Points
The vDSO Makefile invokes it after linking `vdso.so.dbg`.

### Risks
Any change in `nm` output format, symbol type character, or `VDSO_*` naming can omit offsets. The regex only matches lines with ` . ` as the type field.

### Test Signals
Build vDSO and verify generated offsets for `sigreturn` and all exported vDSO entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/gen_vdso_offsets.sh -->
