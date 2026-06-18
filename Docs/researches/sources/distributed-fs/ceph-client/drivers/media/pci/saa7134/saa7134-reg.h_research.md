# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-reg.h

Purpose: defines SAA7130/7133/7134/7135 PCI IDs, MMIO register offsets, and bit masks used by the SAA7134 driver family. It is the hardware register contract shared by core, video, VBI, TS, audio, I2C, input, DVB, Empress, GO7007, and ALSA-related code.

Important APIs, types, and definitions: PCI IDs are defined if missing from PCI headers. Register macros include DMA channel base/pitch/control (`SAA7134_RS_*`), FIFO/threshold, SAA7133/7135 audio registers, `SAA7134_MAIN_CTRL` task/PLL/processing enable bits, AV status, IRQ enable/report/status bits, video decoder/scaler registers, task-specific VBI/video/scaler paths, clipping/output format registers, I2C control/data registers, analog audio/NICAM/I2S/DSP registers, video port controls, TS interface registers, GPIO mode/status/rescan registers, special/test modes, and SAA7135 DSP status/clear bits.

Control flow: this header has no runtime flow; other files include it to compute byte or dword MMIO offsets for `saa_readb`, `saa_writeb`, `saa_readl`, `saa_writel`, and bit-update helpers. Some 32-bit register offsets are pre-shifted with `>> 2`, while many 8-bit registers are byte offsets.

State and persistence: no storage is declared. The definitions describe hardware state maintained in MMIO registers and manipulated by implementation files.

Dependencies and integration points: included by SAA7134 implementation files and depends on consistent MMIO accessor conventions in `saa7134.h`. The split between byte offsets and dword offsets is central to correct register access.

Risks: wrong offset units or bit masks can corrupt unrelated hardware blocks, especially DMA channel programming, IRQ masking, GPIO control, and audio DSP access. Duplicate-style definitions for SAA7135 DSP clear bits also appear in TV audio code and must stay semantically aligned. Because many macros are raw constants, compiler type checking provides little protection.

Test signals: successful build of all SAA7134 modules, correct probe-time hardware initialization, DMA IRQ completion, I2C transfers, GPIO IR events, TS/VBI/video capture, audio mute/stereo behavior, GO7007 HPI GPIO traffic, and register traces matching datasheet expectations.
