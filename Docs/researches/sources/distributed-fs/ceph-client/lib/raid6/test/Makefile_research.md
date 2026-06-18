## sources/distributed-fs/ceph-client/lib/raid6/test/Makefile

Purpose: builds a standalone userspace RAID-6 test library and `raid6test` executable from the kernel RAID-6 sources.

Important targets/variables: `OBJS` starts with generic integer, recovery, algorithm, and table objects, then conditionally adds architecture-specific objects. `ARCH` is derived from `uname -m`; x86 adds MMX/SSE/AVX objects, ARM/AArch64 adds NEON, PowerPC probes Altivec, LoongArch probes LSX/LASX, and RISC-V adds RVV objects. Targets include `raid6.a`, `raid6test`, generated `int*.c`, `neon*.c`, `altivec*.c`, `vpermxor*.c`, `tables.c`, `clean`, and `spotless`.

Control flow: pattern rules copy `.c` and `.uc` files from the parent RAID-6 directory into the test directory, use `unroll.awk` to expand unrolled templates, build a static archive, then link `raid6test` with the test program. `mktables` generates `tables.c`.

State and persistence: generated source/object/archive/binary files are local build artifacts and removed by `clean`.

Dependencies/integration: depends on GCC, `ld`, `awk`, `ar`, `ranlib`, kernel headers under `../../../include` and architecture include directories. It mirrors kernel config macros to userspace CFLAGS so algorithm files compile outside the kernel.

Risks/test signals: feature probes are shell/compiler dependent and architecture detection is simple. The Makefile itself is a test signal: successful build/run validates many RAID-6 algorithm implementations in userspace without booting a kernel.
