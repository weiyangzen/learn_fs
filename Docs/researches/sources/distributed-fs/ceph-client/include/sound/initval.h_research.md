# sources/distributed-fs/ceph-client/include/sound/initval.h

Source read summary: 90 lines, default module parameter and legacy resource discovery helpers.

Purpose: supplies standard ALSA defaults for card index, enable flags, ports, IRQs, DMA channels, DMA sizes, and optional legacy ISA/PnP resource probing helpers.

Important APIs, types, and functions: macros include `SNDRV_AUTO_PORT`, `SNDRV_AUTO_IRQ`, `SNDRV_AUTO_DMA`, `SNDRV_AUTO_DMA_SIZE`, single-card `SNDRV_DEFAULT_*1`, and array initializers for `SNDRV_CARDS`. Conditional helper functions are `snd_legacy_find_free_ioport()`, `snd_legacy_empty_irq_handler()`, `snd_legacy_find_free_irq()`, and `snd_legacy_find_free_dma()`.

Control flow: legacy drivers use these macros for module parameter defaults and, when enabled, scan candidate port/IRQ/DMA tables by temporarily requesting resources.

State and persistence behavior: no persistent state is stored. Probe helpers momentarily reserve and release resources and return the first available candidate.

Dependencies and integration points: depends on resource, interrupt, and DMA request APIs only when the corresponding `SNDRV_LEGACY_FIND_FREE_*` macros are defined. Used by ISA/legacy ALSA drivers.

Risks and edge cases: probing can race with real device claims, shared IRQ probing has side effects, defaults differ with `CONFIG_PNP`, and `SNDRV_AUTO_*` sentinel values must not be programmed into hardware.

Test signals: compile legacy drivers with each helper enabled, probe with occupied/free resources, PnP and non-PnP default enable arrays, and invalid resource table termination.
