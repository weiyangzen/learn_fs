# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-regs.h

Purpose: CAMIF register map and hardware helper declarations. It defines register offsets, field masks, bit constructors, status decoders, DMA address formulas, scaler/control bits, image effect bits, and prototypes for the MMIO helper functions implemented in `camif-regs.c`.

Important APIs and constants: register macros cover global source/offset/control registers (`CISRCFMT`, `CIWDOFST`, `CIGCTRL`), DMA output addresses (`CIYSA`, `CICBSA`, `CICRSA`), path target/scaler/control/status registers (`CITRGFMT`, `CICTRL`, `CISCPRERATIO`, `CISCPREDST`, `CISCCTRL`, `CISTATUS`), capture control (`CIIMGCPT`), image effects, memory input DMA, and scan-line offsets. `CISTATUS_FRAMECNT()` is central to IRQ buffer-slot selection.

Control flow role: capture and register code use these macros to program SoC-specific paths without duplicating numeric offsets. `_offs` and `id` parameters allow one macro family to address codec and preview paths and S3C6410 register offsets.

State and persistence: the header itself owns no runtime state, but the bit definitions encode the hardware state model: capture enable, scaler enable, overflow flags, frame count, last IRQ, bus polarity, test pattern, input/output format, and DMA offsets.

Dependencies and integration: includes `linux/bitops.h`, `camif-core.h`, and Samsung platform bus definitions. The prototypes form the MMIO layer consumed by `camif-capture.c`.

Risks: macro correctness is critical because a wrong offset or mask corrupts hardware programming. Some comments note SoC-specific differences and disabled bits, so future changes must verify variant behavior rather than applying one register interpretation globally.

Test signals: compile checks for macro use, hardware register dump sanity after stream start, tests across codec/preview ids, and specific verification that `CISTATUS_FRAMECNT()` maps to the buffer index expected by IRQ rotation.
