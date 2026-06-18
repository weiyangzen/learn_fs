## sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_emu_64.S

Purpose: defines the physical contents of the legacy vsyscall emulation page.

Important symbol: global object `__vsyscall_page`, exactly one page in size. It contains three 1024-byte slots corresponding to vsyscall functions and places `ret` instructions at the expected call targets, with padding to 4096 bytes.

Control flow: in emulate mode the page can be mapped execute-only/read semantics according to the C mode; executing at a valid slot traps/emulates via fault handling or returns depending on mapping mode details. The code content mainly preserves fixed offsets.

State/persistence: page text is mapped through `map_vsyscall()` and fixed at `VSYSCALL_ADDR`.

Integration points: `vsyscall_64.c`, fixmap, legacy user ABI, and linker symbols.

Risks: page size and offsets are ABI-critical. Test signals include map address checks, readelf/nm symbol size checks, and legacy calls to all three vsyscall slots.
