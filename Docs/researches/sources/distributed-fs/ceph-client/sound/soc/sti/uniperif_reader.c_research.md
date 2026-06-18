# sources/distributed-fs/ceph-client/sound/soc/sti/uniperif_reader.c

Purpose: STi uniperipheral capture implementation for PCM and TDM reader modes. It provides DAI ops and initialization used by common probe code for reader-compatible nodes.

Important APIs and types: exported `uni_reader_init()`; internal IRQ handler, PCM/TDM prepare helpers, prepare/start/stop/trigger/startup/shutdown functions, and reader DAI ops. Hardware constraints support 2-8 channel PCM capture up to 96 kHz or shared `uni_tdm_hw` for TDM.

Control flow: init sets device/state/ops, picks PCM or TDM hardware constraints, requests a shared IRQ, and initializes the IRQ lock. Startup stores the substream and adds TDM constraints when applicable. Prepare requires stopped state, computes transfer size and DMA trigger limit, configures FIFO trigger limit, programs TDM or PCM data format, applies DAI format and clock inversion, clears interrupts, enables DMA/FIFO/memory-block interrupt masks, optionally enables underflow recovery interrupts, and resets hardware. Start clears/enables FIFO errors, sets operation to PCM data, and marks started. Stop sets operation off, masks interrupts, and marks stopped. IRQ clears status and stops the PCM stream with XRUN on FIFO overflow/error.

State and persistence: state is minimal: `reader->state`, `substream`, `type`, `daifmt`, `tdm_slot`, IRQ lock, and shared MMIO state. Unlike player, no clock or IEC958 control state is owned here.

Dependencies and integration points: common `sti_uniperif.c` for resource setup and DAI registration, `uniperif.h` macros, dmaengine PCM, shared IRQ, ALSA PCM stream locking, and TDM slot helper rules.

Risks: trigger limit validation has the same `!trigger_limit % 2` precedence issue as player. The prepare path enables `MEM_BLK_READ` and DMA error interrupt masks, but the IRQ handler only handles FIFO error, so other enabled status bits may be ignored. Underflow recovery naming appears playback-oriented but is referenced in reader. Stop does not reset hardware, unlike player stop. TDM reader documents a hardware word-position limitation that must be handled by userspace for some layouts.

Test signals: capture PCM and TDM, invalid channel/format/slot masks, FIFO overflow interrupt causing XRUN, ignored interrupt status bits, repeated prepare/start/stop cycles, shutdown while active, and TDM word-position layouts with 16- and 32-bit slots.
