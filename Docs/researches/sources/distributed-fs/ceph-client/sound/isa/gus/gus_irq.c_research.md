<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_irq.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_irq.c

Purpose: central GF1/InterWave interrupt dispatcher. It demultiplexes MIDI, voice wave/ramp, timers, and DRAM/record DMA events to handler callbacks installed in `gus->gf1`.

Important APIs/types/functions: exported `snd_gus_interrupt()` is used by board drivers and combined IRQ handlers. Debug-only `snd_gus_irq_profile_init()` creates a `gusirq` proc report. The file uses `STAT_ADD()` counters under `CONFIG_SND_DEBUG`.

Control flow: the handler reads `reg_irqstat`, returns unhandled if zero, and otherwise loops up to 100 dispatch cycles. MIDI bits call MIDI callbacks, voice bits drain `SNDRV_GF1_GB_VOICES_IRQ` until no pending voice IRQ remains, timer bits call timer handlers, and DMA bits inspect DMA control registers before invoking write/read DMA handlers. Lost voice IRQs stop wave and volume controls.

State and persistence: debug counters accumulate in `gus->gf1` and per-voice structs. Callback function pointers are mutable runtime state installed by reset, PCM, timer, DMA, and UART code.

Dependencies and integration: invoked directly from Classic/Extreme and indirectly from MAX/InterWave combined handlers. Depends on low-level locked GF1 reads/stops and ALSA proc info.

Risks: a stuck IRQ source can exhaust the loop and return `IRQ_NONE`, which is a diagnostic signal. Handler callbacks must be IRQ-safe. Voice deduping with a bitmask prevents repeated service of the same voice in one pass. Test signals are MIDI in/out interrupts, PCM wave period interrupts, timer interrupts, DMA completion, debug proc counters, and shared IRQ handlers routing only when status bits are set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_irq.c -->
