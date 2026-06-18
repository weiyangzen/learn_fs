## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/gen_vdso_offsets.sh

### Purpose
`gen_vdso_offsets.sh` converts `nm` output for the native VDSO into C preprocessor defines for symbols named `VDSO_*`.

### Important APIs, Types, And Functions
The script sets `LC_ALL=C` and uses one `sed` expression to emit lines like `#define vdso_offset_name 0xoffset`.

### Control Flow
It normalizes leading zeroes in symbol addresses, matches text/data symbol lines whose name starts with `VDSO_`, strips that prefix for the define suffix, and prints hexadecimal offsets for later sorting by the Makefile.

### State, Persistence, And Dependencies
The only output is generated header text on stdout. There is no persistent state unless the Makefile redirects it to `include/generated/vdso-offsets.h`.

### Integration Points
Called by `vdso/Makefile` as part of the `VDSOSYM` rule. It relies on stable `nm` output and VDSO symbol naming conventions.

### Risks
Changes in `nm` format or symbol naming can silently omit offsets. Locale must stay deterministic, hence `LC_ALL=C`.

### Test Signals
Feed representative `nm` output with and without leading zeroes, verify generated defines, and ensure the VDSO offset header changes when VDSO symbols move.
