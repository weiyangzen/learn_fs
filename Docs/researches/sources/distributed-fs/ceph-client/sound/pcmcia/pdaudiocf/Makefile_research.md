# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/Makefile

Purpose: Defines the build composition for the Sound Core PDAudioCF PCMCIA/CompactFlash ALSA module.

Important APIs/types/functions: `snd-pdaudiocf-y` links `pdaudiocf.o`, `pdaudiocf_core.o`, `pdaudiocf_irq.o`, and `pdaudiocf_pcm.o`. `obj-$(CONFIG_SND_PDAUDIOCF)` conditionally emits `snd-pdaudiocf.o`.

Control flow: Kbuild aggregates the card-service/probe file, core hardware helpers, IRQ handling, and PCM implementation into one module when `CONFIG_SND_PDAUDIOCF` is enabled.

State and persistence: No runtime state. Object composition determines which implementation files are linked.

Dependencies/integration: Integrates with ALSA PCMCIA build and the PDAudioCF header shared by all four C files.

Risks: Omitting any listed object would remove required probe, core, interrupt, or PCM behavior. New helper files must be added here.

Test signals: Build with `CONFIG_SND_PDAUDIOCF=m` and confirm `snd-pdaudiocf.ko` links all four source objects without unresolved `snd_pdacf_*` or IRQ/PCM symbols.
