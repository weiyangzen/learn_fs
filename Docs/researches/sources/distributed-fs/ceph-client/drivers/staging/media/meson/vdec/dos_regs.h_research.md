# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/dos_regs.h

Purpose: this header defines register offsets and bit fields for the Meson DOS/VDEC_1 block, firmware scratch interface, VIFIFO stream buffer, MPEG/H.264 decoder control, reset, clock, and memory power-down registers.

Important APIs and constants: it defines mailbox registers (`ASSIST_MBOX1_CLR_REG`, `ASSIST_MBOX1_MASK`), firmware control registers (`MPSR`, `CPSR`, `MCPU_INTR_MSK`), IMEM DMA registers, decoder/post-scaler controls, canvas address register base (`ANC0_CANVAS_ADDR`), scratch registers `AV_SCRATCH_0` through `AV_SCRATCH_L`, MPEG and VLD controls, VIFIFO start/current/end/control/write/read/level registers, and top-level DOS reset/clock/memory registers. Bit helpers include VIFIFO fill/empty control bits and manual buffer control.

Control flow and integration: `vdec_1.c` uses these offsets to power/reset VDEC_1, load firmware through IMEM DMA, configure VIFIFO, and enable mailbox IRQs. MPEG-1/2 and H.264 codec files use scratch registers as their firmware ABI. `vdec_helpers.c` wraps read/write access to the DOS base, but this header defines the address contract.

State and persistence behavior: register values represent live hardware state. Scratch registers persist as firmware mailboxes across IRQs. VIFIFO pointer registers track the DMA bitstream ring. Reset and memory power registers control hardware block lifetime around streaming.

Dependencies: depends on Linux `BIT()`/GENMASK availability through including source files. It is paired with `amvdec_read_dos()` and `amvdec_write_dos()` helpers that add these offsets to `core->dos_base`.

Risks: wrong offsets or bit definitions can hang firmware, corrupt DMA, or prevent IRQ delivery. Scratch register reuse is codec-specific and not type-safe. Some registers are shared by multiple codec paths, so changes need cross-codec review.

Test signals: firmware load success, mailbox IRQ delivery, VIFIFO fill-level accounting, stream start/stop reset sequencing, MPEG/H.264 scratch ABI behavior, and register tracing against vendor documentation or known-good downstream trees.
