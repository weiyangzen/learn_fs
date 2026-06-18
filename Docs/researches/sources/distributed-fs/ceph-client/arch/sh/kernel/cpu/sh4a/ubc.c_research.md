# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/ubc.c

Purpose: registers SH-4A on-chip User Break Controller support for hardware breakpoints.

Important APIs, types, and functions: `sh4a_ubc_init()` initializes hardware and calls `register_sh_ubc(&sh4a_ubc)` at `arch_initcall`. `sh4a_ubc_enable()`, `sh4a_ubc_disable()`, `sh4a_ubc_enable_all()`, `sh4a_ubc_disable_all()`, `sh4a_ubc_active_mask()`, `sh4a_ubc_triggered_mask()`, and `sh4a_ubc_clear_triggered_mask()` implement `struct sh_ubc`.

Control flow: init optionally obtains clock `ubc0`, enables it if present, clears the breakpoint control register, initializes each of two channels by clearing CAMR/CBR, programming CRR with break interrupt and PC break bits, performs dummy reads for posting, disables the clock, stores it in the UBC descriptor, and registers the backend.

State and persistence: `sh4a_ubc` advertises two events and trap number `0x1e0`. Breakpoint state persists in UBC channel registers CBR/CRR/CAR/CAMR and the common match flag register. The optional clock pointer is retained for later core use.

Dependencies and integration points: depends on Linux clock API, raw MMIO, and `<asm/hw_breakpoint.h>`. It integrates with ptrace/perf hardware breakpoint infrastructure through `register_sh_ubc()`.

Risks: `clk_enable(NULL)` and `clk_disable(NULL)` rely on clock API tolerance when no `ubc0` clock exists. Triggered-mask clearing writes `read & ~mask`, which must match hardware write semantics. Only two channels are exposed.

Test signals: hardware watchpoint/breakpoint tests through ptrace or perf should hit trap `0x1e0`, active and triggered masks should reflect channels, and platforms without `ubc0` should still boot without clock errors.
