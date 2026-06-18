<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-core.c

Purpose: core platform driver for the ImgTec IR decoder hardware block. It maps device resources, manages clocks and interrupts, initializes raw and hardware decode subcomponents, and dispatches IRQ status to the enabled decode path.

Important APIs and functions: main functions are `img_ir_isr`, `img_ir_setup`, `img_ir_ident`, `img_ir_probe`, and `img_ir_remove`. It uses helper APIs declared in `img-ir.h`, including `img_ir_read/write`, `img_ir_setup_raw/hw`, `img_ir_probe_raw/hw`, `img_ir_remove_raw/hw`, `img_ir_raw_enabled`, `img_ir_hw_enabled`, `img_ir_isr_raw`, `img_ir_isr_hw`, and PM callbacks `img_ir_suspend/resume`.

Control flow: probe gets IRQ and MMIO resources, allocates `img_ir_priv`, initializes a spinlock, maps registers, obtains optional core and sys clocks, enables sys clock before register access, probes raw and hardware decoders and requires at least one to succeed, requests IRQ, logs identity/modes, disables IRQs, sets up raw/hw subcomponents, and enables the core clock. ISR locks, reads and clears IRQ status, masks it by enabled bits, dispatches edge interrupts to raw handling when raw is enabled, dispatches data match/valid interrupts to hardware handling when hardware decode is enabled, then unlocks.

State and persistence: `img_ir_priv` stores device, register base, clocks, IRQ, spinlock, and raw/hardware substate. Clock and register state are runtime-only and restored through setup/resume paths.

Dependencies and integration points: depends on platform device resources, OF compatible `img,ir-rev1`, MMIO, clocks, IRQs, spinlocks, and local raw/hardware decode modules. It registers as one platform driver named `img-ir`.

Risks: core clock is enabled in `img_ir_setup` after raw/hw setup, while sys clock is enabled earlier for register access; clock ordering is hardware-sensitive. IRQ status is cleared before handler dispatch, so missed status capture would lose events. Probe succeeds if either raw or hardware decoder initializes, making partial-mode failures nonfatal. Error paths must remove whichever subcomponent succeeded.

Test signals: device-tree probe, sys/core clock availability and failure injection, IRQ dispatch for edge and data-valid/match bits, raw-only and hardware-only configurations, suspend/resume, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-core.c -->
