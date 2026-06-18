## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_hw.h

Purpose: central register map and bit-field contract for the Armada LCD/SPU display engine used by the Armada DRM CRTC, primary plane, overlay plane, interrupt, cursor, clock, SRAM, color-key, and output-pad code.

Important APIs/types are the anonymous enums defining MMIO offsets such as `LCD_SPU_DMA_CTRL0`, `LCD_CFG_GRA_START_ADDR0`, `LCD_SPU_IRQ_ISR`, and bit macros including `CFG_DMA_FMT`, `CFG_GRA_FMT`, `CFG_CKMODE`, `CFG_ALPHA`, `CFG_PDWN*`, and `SCLK_*`. There are no functions; the integration surface is compile-time symbolic access to memory-mapped hardware registers.

Control flow is indirect: update paths queue writes to these offsets, often from IRQ-driven register flush paths as noted by the header comment. State is persistent in display controller registers: frame addresses, pitches, FIFO power, format selection, color conversion, gamma/palette SRAM, interrupt enable/status, and dumb-panel polarity. Dependencies are Linux `BIT()` and the surrounding Armada DRM helpers that interpret these masks.

Risks include incorrect preserve masks corrupting unrelated register bits, Armada 510 versus Armada 16x clock/register differences, and register writes from IRQ context requiring queued/atomic-safe sequencing. Test signals are mode-set success, no FIFO underflow IRQs, correct pixel format/color-key behavior, vblank/frame interrupts, and stable output after suspend/resume or plane flips.
