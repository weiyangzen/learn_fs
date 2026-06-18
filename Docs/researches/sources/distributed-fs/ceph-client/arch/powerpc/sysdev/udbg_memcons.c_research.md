<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/udbg_memcons.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/udbg_memcons.c

Purpose: Provides a memory-backed early debug console for PowerPC udbg output and polling input.

Important APIs/types/functions: Defines `struct memcons`, global `memcons`, `memcons_putc()`, `memcons_getc_poll()`, `memcons_getc()`, and `udbg_init_memcons()`.

Control flow: Initialization installs udbg callbacks. Output writes one byte at `output_pos`, issues a write memory barrier, and advances circularly. Input polling checks the current input byte, advances circularly or wraps to start on NUL, clears consumed bytes, barriers, and returns `-1` when empty. Blocking get spins with `cpu_relax()` until input appears.

State and persistence: Persistent static buffers are sized by `CONFIG_PPC_MEMCONS_OUTPUT_SIZE` and `CONFIG_PPC_MEMCONS_INPUT_SIZE`. Global `memcons` exposes buffer starts/positions/ends for external inspection/injection.

Dependencies and integration points: Depends on PowerPC udbg callback globals, memory barriers, and early debug users that can inspect or populate the buffers.

Risks: There is no locking; this is early/debug infrastructure and concurrent writers/readers can race. The output ring overwrites old data. Input emptiness relies on zero-filled/zero-cleared bytes.

Test signals: Early boot debug output, wraparound behavior, injected input consumption, and visibility of `memcons` from debugger or simulator.

Source read size: 100 lines, 2205 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/udbg_memcons.c -->
