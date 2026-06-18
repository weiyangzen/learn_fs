<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_timer_wakeup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_timer_wakeup.c

Purpose: module exposing an MPIC global timer as a sysfs-programmable wakeup timer.

Important APIs/types/functions: `struct fsl_mpic_timer_wakeup`, global `fsl_wakeup`, sysfs attribute `timer_wakeup`, `fsl_timer_wakeup_show()`, `fsl_timer_wakeup_store()`, IRQ handler `fsl_mpic_timer_irq()`, deferred cleanup `fsl_free_resource()`, and module init/exit.

Control flow: module init allocates state, initializes cleanup work, gets the MPIC bus root device, and creates `timer_wakeup`. Writing zero cancels/free any existing timer. Writing a positive interval requests an MPIC timer with the file's IRQ handler, enables IRQ wake, starts it, and stores it. IRQ handling schedules work, which disables wake and frees the timer under the sysfs mutex. Reading returns remaining time plus one when a timer exists or zero otherwise.

State and persistence: global module state holds one active timer and cleanup work. Sysfs file state is global to the MPIC subsystem root.

Dependencies and integration points: depends on MPIC timer APIs, `mpic_subsys`, IRQ wake support, sysfs device files, workqueues, and module lifecycle.

Risks: the IRQ handler checks `wakeup->timer` after scheduling work; concurrent sysfs writes are serialized by the mutex in store/free work, but IRQ/work ordering is subtle. Exit frees the state while holding the mutex after removing sysfs; pending work should be considered in module unload testing.

Test signals: creating/removing `/sys/.../timer_wakeup`, programming a timer, seeing remaining-time reads decrease, system wake from suspend, timer auto-free after IRQ, and cancellation via writing zero validate the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_timer_wakeup.c -->
