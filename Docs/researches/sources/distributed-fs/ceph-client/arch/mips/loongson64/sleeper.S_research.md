<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/sleeper.S -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/sleeper.S

Purpose: Implements the assembly trampoline for LEFI firmware suspend/resume.

Important APIs/types/functions: `loongson_lefi_sleep(unsigned long sleep_addr)` saves suspend CPU state, calls firmware with wake label and stack pointer, restores SMP slave setup, and returns through resume register restoration.

Control flow: `SUSPEND_SAVE` preserves context, `t9` holds firmware sleep function, `a0` receives wake label, `a1` receives stack pointer, and firmware returns to `wake`.

State and persistence: Saves/restores CPU register state around firmware sleep.

Dependencies and integration: Called by `pm.c`; uses MIPS suspend macros and `kernel-entry-init.h`.

Risks: Firmware must honor the wake callback ABI. Incorrect register preservation would corrupt resume.

Test signals: Suspend-to-RAM should resume through the `wake` label and return to C code without register corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/sleeper.S -->
