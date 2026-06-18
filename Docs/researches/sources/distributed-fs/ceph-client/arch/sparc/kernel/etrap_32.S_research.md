# sources/distributed-fs/ceph-client/arch/sparc/kernel/etrap_32.S

## Purpose
`etrap_32.S` builds 32-bit SPARC kernel trap frames and handles register-window preparation when entering Linux from traps. It turns raw trap-time PSR/PC/NPC/WIM state into a `pt_regs` frame on the correct kernel stack.

## Important APIs, Types, and Functions
Primary labels are `trap_setup`, `trap_setup_from_user`, `trap_setup_kernel_spill`, `trap_setup_user_spill`, and `tsetup_srmmu_stackchk`. Patch labels `tsetup_patch*` and `tsetup_7win_patch*` are modified at boot for 7-window CPUs.

## Control Flow and State
Trap callers enter with `%l0` PSR, `%l1` PC, `%l2` NPC, `%l3` WIM, and `%l6` return PC. Kernel traps allocate a frame below `%fp`, store registers, and spill a kernel window if the trap landed in the invalid window. User traps load `current_thread_info`, compute the top-of-thread trap frame, store `pt_regs`, update `TI_UWINMASK`, and clear `TI_W_SAVED`. If a user stack window must be spilled, it temporarily adjusts WIM, turns on SRMMU/LEON no-fault behavior, stores the window, and falls back to `SAVE_BOLIXED_USER_STACK` on bad user stacks.

## Persistence and Dependencies
It mutates WIM, `thread_info` window masks, kernel/user stack memory, and trap-frame contents. Dependencies include SRMMU/LEON ASIs, `winmacro.h`, generated offsets, and boot-time patching in `head_32.S`.

## Integration Points, Risks, and Test Signals
This code integrates with every sparc32 trap path using `SAVE_ALL`. Risks are severe: wrong window masks corrupt user registers, bad no-fault handling loops on user stack faults, and patching errors break 7-window CPUs. Test signals include signal delivery/return, deep call stacks, user stack fault handling, ptrace register visibility, and stress that forces window spills from user and kernel mode.
