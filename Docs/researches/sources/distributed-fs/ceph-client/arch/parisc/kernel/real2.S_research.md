<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/real2.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/real2.S

### Purpose
`real2.S` provides real-mode firmware call bridges and mode-switch helpers used when kernel virtual mode must call PDC/IODC routines.

### Important APIs, Types, And Functions
Assembly entry points include `real32_call_asm`, `real64_call_asm` on 64-bit builds, `save_control_regs`, `restore_control_regs`, `rfi_virt2real`, `rfi_real2virt`, and `__canonicalize_funcptr_for_compare`. It exports `real_stack` and `real64_stack`.

### Control Flow
The call bridges save return state, adopt a firmware stack, load argument registers from a saved argument area, translate the stack pointer to physical, switch from virtual to real mode with `rfi`, save control registers, call the firmware function, restore control registers, switch back to virtual mode, and restore the original stack/registers. `real32_call_asm` also toggles wide mode when needed.

### State, Persistence, And Dependencies
Temporary control-register snapshots live in static BSS. The code depends on PSW constants, address translation macros, PA-RISC calling conventions, and firmware stack layout.

### Integration Points
Used by PDC/IODC firmware wrappers during boot and runtime firmware calls.

### Risks
Interrupt, Q-bit, PSW, and control-register sequencing is fragile; a fault before control-register restore can strand the CPU in the wrong mode. 64-bit function descriptors require special handling.

### Test Signals
Boot firmware calls, PDC console access, 32-bit firmware on 64-bit kernels, and repeated real-mode calls under interrupt pressure are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/real2.S -->
