# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irq-pm-s3c64xx.c

Purpose: S3C64xx interrupt controller power-management save/restore support.

Important APIs/types/functions: defines suspend/resume helpers that snapshot and restore VIC/interrupt mask state around sleep.

Control flow: PM suspend records relevant interrupt controller registers; resume writes them back so wake-capable and masked interrupts return to pre-suspend state.

State and persistence: in-memory saved register arrays hold IRQ controller state across suspend; hardware VIC/mask registers are restored on resume.

Dependencies and integration points: used by Samsung PM code with S3C64xx IRQ register definitions and wake-mask handling.

Risks: missing a register can leave interrupts masked/unmasked incorrectly after resume. Wake source configuration must align with system PM policy.

Test signals: suspend/resume with UART/GPIO/RTC wake sources, interrupt mask comparison before/after suspend, and no lost interrupts after resume.
