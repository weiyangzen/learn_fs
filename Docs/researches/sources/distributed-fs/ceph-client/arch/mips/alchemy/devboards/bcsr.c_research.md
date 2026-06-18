## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/bcsr.c

Purpose: abstracts DB/PB1xxx board CPLD registers, known as BCSR, and provides a cascaded CPLD interrupt controller for boards with interrupt-capable CPLDs. BCSR registers are 16-bit registers spaced on 32-bit boundaries and can reside in two physical windows.

Important APIs and functions: `bcsr_init()` maps register IDs to KSEG1 virtual addresses and initializes per-register spinlocks. `bcsr_read()`, `bcsr_write()`, and `bcsr_mod()` are exported for board files and drivers. `bcsr_init_irq()` installs a chained IRQ handler and maps a range of Linux IRQs to CPLD interrupt bits. Internal IRQ methods are `bcsr_irq_mask()`, `bcsr_irq_maskack()`, `bcsr_irq_unmask()`, and `bcsr_csc_handler()`.

Control flow: board setup calls `bcsr_init()` with board-specific BCSR physical base addresses. Later, DB1200/DB1300-style boards call `bcsr_init_irq()`, which masks/enables/acks all CPLD IRQs, assigns the `CPLD` irq chip to each cascaded line, and chains the parent GPIO IRQ to `bcsr_csc_handler()`. The handler reads `BCSR_REG_INTSTAT`, dispatches the first set bit with `generic_handle_irq()`, and exits the chained IRQ.

State and persistence: static `bcsr_regs[]` stores register addresses and locks. `bcsr_virt` and `bcsr_csc_base` record the active CPLD mapping and IRQ base. Hardware register changes persist until board reset.

Dependencies and integration: depends on `asm/mach-db1x00/bcsr.h`, raw I/O, Linux IRQ core, chained IRQ helpers, and board-specific setup files.

Risks: no bounds checks protect `enum bcsr_id`; callers must pass valid IDs. The chained handler dispatches only the lowest pending bit per parent interrupt entry. Wrong BCSR base addresses can corrupt unrelated external bus registers. IRQ ack/mask order is hardware-specific.

Test signals: BCSR read/write should identify the board through `BCSR_WHOAMI`; LEDs, resets, power bits, and card-detect signals should respond. Cascaded IRQ tests include MMC/card/PCMCIA insert and no stuck interrupt storm.
