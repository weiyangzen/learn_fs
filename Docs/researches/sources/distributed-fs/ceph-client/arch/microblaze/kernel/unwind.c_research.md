# sources/distributed-fs/ceph-client/arch/microblaze/kernel/unwind.c

Purpose: implements best-effort MicroBlaze stack unwinding without reliable frame-pointer support.

Important APIs and state: `microblaze_unwind()` is exported. Helpers find stack-frame prologue instructions (`addik r1,r1,-FRAME_SIZE`), compute frame sizes, locate previous frame/PC, and recognize trap-handler address ranges from `microblaze_trap_handlers`.

Control flow: for current tasks it starts from current regs or inline PC/SP; for sleeping tasks it starts at `_switch_to` and saved CPU context. The inner loop prints or records PCs, stops on invalid/unmapped text, and advances using inferred frame size or leaf return address. Trap unwinding is mostly a stub, with a special stop for hardware exception handler ranges.

State and persistence: mutates only the supplied stack_trace. It reads kernel text and stacks.

Dependencies and integration: used by traps and stacktrace wrappers; depends on compiler prologue shape and linker-visible trap handler table from `entry.S`.

Risks and test signals: arbitrary backward scanning can miss large/prologue-less functions or misidentify instructions. Trap unwinding is incomplete. Test current/sleeping task traces, leaf functions, large functions, exception/IRQ frames, and stacktrace limits.
