<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_lbc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_lbc.c

Purpose: Freescale local bus controller and UPM support, including bank lookup, UPM pattern execution, event/error interrupt handling, and suspend register save/restore.

Important APIs/types/functions: exported `fsl_lbc_ctrl_dev`, `fsl_lbc_addr()`, `fsl_lbc_find()`, `fsl_upm_find()`, `fsl_upm_run_pattern()`, internal `fsl_lbc_ctrl_init()`, `fsl_lbc_ctrl_irq()`, `fsl_lbc_ctrl_probe()`, suspend `fsl_lbc_syscore_suspend/resume()`, and init `fsl_lbc_init()`.

Control flow: platform probe allocates the singleton controller, maps registers, maps one or two IRQs, clears/enables event registers, applies the eLBC monitor timeout workaround, requests IRQ handlers, and enables event interrupts. Bank helpers read BR/OR registers to match a physical base and derive UPM register pointer/width. UPM pattern execution writes MAR then performs a dummy bus write of the correct width. The IRQ handler reads/clears LTESR/LTEATR/LTEAR, records status, logs known errors, and wakes waiters for command completion, timeout, parity/ECC, or completion bits. Syscore suspend copies the whole register block and resume restores it.

State and persistence: global singleton `fsl_lbc_ctrl_dev`, mapped registers, IRQ numbers, waitqueue, last `irq_status`, and optional saved register image. Hardware bank, UPM, error, and interrupt-enable registers persist across normal runtime and are restored after suspend.

Dependencies and integration points: depends on OF platform matching (`fsl,elbc`, `fsl,pq*-localbus`), `asm/fsl_lbc.h`, NAND/UPM/localbus consumers, IRQ subsystem, and syscore suspend hooks.

Risks: singleton design assumes one controller. Error paths need to unmap/free partial resources; second IRQ setup failure frees the first. Full-register save/restore may include volatile or write-1-clear fields, but matches existing hardware expectations. UPM pattern execution must hold the shared lock around MAR and dummy access.

Test signals: localbus NAND/flash access, UPM devices executing patterns, LTESR error injection/logging, waitqueue wake on completion/error bits, and suspend/resume preserving localbus configuration validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_lbc.c -->
