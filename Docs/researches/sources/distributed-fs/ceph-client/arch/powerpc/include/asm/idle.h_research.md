# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/idle.h

Purpose: Declares PowerPC CPU idle state, stop/winkle helpers, thread-sibling coordination, and idle wake/replay interfaces.

Important APIs, types, and functions: Provides idle state flags and prototypes for entering low-power states, saving/restoring SPRs, stop API helpers, `pnv_*` idle functions, and CPU/thread state tracking used by platform idle code.

Control flow: CPU idle paths select a platform state, prepare IRQ state, save required registers, enter nap/sleep/winkle/stop, resume through low-level wake code, restore state, and replay pending interrupts.

State and persistence: Runtime state includes per-CPU idle flags, saved SPRs, sibling thread state, and platform stop state. It is volatile across boot/runtime only.

Dependencies and integration points: Integrates cpuidle, OPAL/PowerNV, pSeries/QorIQ idle support, interrupt masking, timebase handling, and SMP CPU hotplug.

Risks: Idle entry interacts tightly with interrupt masking and firmware. Losing SPR state or missing a pending interrupt can hang a CPU. Deep states may affect sibling threads.

Test signals: cpuidle state residency, wake from decrementer/external interrupts, stop/winkle state save/restore, sibling-thread coordination, CPU hotplug from idle states, and suspend/resume stress.
