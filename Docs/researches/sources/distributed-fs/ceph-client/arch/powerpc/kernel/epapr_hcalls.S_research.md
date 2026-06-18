<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_hcalls.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_hcalls.S

## Purpose
`epapr_hcalls.S` provides the patchable ePAPR hypercall entry sequence and, on supported non-64-bit or Book3E-64 builds, an ePAPR idle loop that repeatedly invokes the hypervisor idle call until an interrupt returns execution to the caller.

## Important APIs, Types, And Functions
Exported symbols are `epapr_ev_idle`, `epapr_ev_idle_start`, and exported `epapr_hypercall_start`. The hypercall instruction slots begin as `li r3, -1` plus NOPs and are patched from device-tree `hcall-instructions`.

## Control Flow
`epapr_ev_idle()` sets the thread napping flag, enables external interrupts, loads the EV_IDLE token, executes the patched hypercall instruction sequence at `epapr_ev_idle_start`, and loops to guard against spurious hypervisor wakeups. `epapr_hypercall_start` is the generic callable hypercall sequence and returns after the patched instructions.

## State And Persistence
State changes include thread local flags and patched text instructions. The patched instructions persist for the running kernel only.

## Dependencies And Integration Points
It integrates with `epapr_paravirt.c` text patching, ePAPR hypercall ABI, PowerPC interrupt/idle handling, thread-info flags, and machine descriptor power-save hooks.

## Risks
The instruction patch area is limited to four instructions, matching parser validation. Idle relies on `_TLF_NAPPING` exception return behavior; incorrect flag handling can loop or return incorrectly. Spurious wakeups are intentionally ignored.

## Test Signals
Signals include successful patching from DT `hcall-instructions`, functional ePAPR hypercalls, idle entry/exit under interrupts, and no use of the placeholder `-1` return path after early paravirt init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_hcalls.S -->
