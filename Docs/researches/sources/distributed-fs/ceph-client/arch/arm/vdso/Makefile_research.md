## sources/distributed-fs/ceph-client/arch/arm/vdso/Makefile

### Purpose
Builds the ARM 32-bit vDSO shared object, validates it, munges ELF flags for ABI compatibility, strips the runtime `.so`, and embeds it into `vdso.o`.

### Important APIs, Types, And Functions
Defines host program `vdsomunge`, vDSO objects `vgettimeofday.o` and `note.o`, targets `vdso.so`, `vdso.so.dbg`, `vdso.so.raw`, and `vdso.lds`, and commands `vdsold_and_vdso_check` and `vdsomunge`.

### Control Flow
Kbuild preprocesses the linker script, compiles PIC vDSO objects with branch profiling disabled, links `vdso.so.raw`, runs generic vDSO checks, runs `vdsomunge` to clear soft-float ABI flags, strips debug symbols for `vdso.so`, and ensures `vdso.o` depends on the final shared object.

### State, Persistence, And Dependencies
Build artifacts persist under the object directory. Dependencies include `lib/vdso/Makefile.include`, host compiler support, linker flags, `c-gettimeofday-y`, and config-controlled endianness.

### Integration Points
The generated `vdso.so` is included by `vdso.S` and later mapped into userspace by ARM kernel vDSO setup.

### Risks
Wrong C flags can introduce libgcc, stack protector, profiling, or randomization dependencies unsuitable for vDSO. ABI flags must be compatible with both soft- and hard-float userspace. Linker script and check command failures are runtime ABI risks.

### Test Signals
Build with `CONFIG_VDSO=y` for little and BE8 configurations, run `readelf -h/-l/-s`, and execute gettimeofday/clock_gettime vDSO tests under ARM userspace.
