# sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil.h

Purpose: declares shared SPARC signal helpers for saving/restoring FPU state and register-window state into signal-frame side buffers.

Important APIs/functions: declares `save_fpu_state()`, `restore_fpu_state()`, `save_rwin_state()`, and `restore_rwin_state()`.

Control flow: no executable logic is present. The header provides common prototypes for `signal_32.c`, `signal32.c`, `signal_64.c`, and the SPARC32 implementation in `sigutil_32.c` or corresponding 64-bit implementation.

State and persistence: no state is owned by the header.

Dependencies and integration points: depends on `struct pt_regs`, SPARC signal-frame FPU/window types, and user pointer annotations from architecture headers.

Risks: prototypes must remain synchronized with all signal implementations. These helpers are ABI-facing because they serialize task state into user signal frames.

Test signals: compile coverage for all signal files and runtime signal tests that include FPU and saved register-window state.
