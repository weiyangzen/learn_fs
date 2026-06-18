
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_lib.c

Purpose: shared PCI/ALSA driver core for Oxygen cards. It owns interrupt handling, card probe/init, AC97 codec setup, proc diagnostics, PM suspend/resume, shutdown, and bridge quirks.

Important functions: `oxygen_interrupt` acknowledges DMA/SPDIF/GPIO/AC97/MIDI events and schedules work; SPDIF work toggles input clock when sense exists without lock; GPIO work delegates to model callback. `oxygen_search_pci_id` reads EEPROM subdevice IDs; `oxygen_restore_eeprom` repairs broken EEPROM PCI subsystem words. `oxygen_init` programs default chip registers and AC97 codecs. `__oxygen_pci_probe` allocates ALSA card, enables PCI, selects model, initializes hardware, requests IRQ, creates PCM/mixer/MIDI/proc, enables interrupts, and registers the card. PM helpers save/restore selected registers and AC97 state.

State/persistence: shared `oxygen` state tracks active/running streams, interrupt mask, saved MMIO/AC97 registers, UART buffer, work items, and model data. Resume restores only bitmap-selected registers plus AC97 register subsets, then calls model resume.

Dependencies/integration: called by `oxygen.c`, `se6x.c`, and `virtuoso.c`; depends on `oxygen_io`, PCM/mixer init, ALSA core, PCI, MPU401, and CM9780 constants.

Risks: interrupt races, stale work items during suspend/free, EEPROM repair side effects, AC97 unreliable transactions, and model callback assumptions during init/cleanup. Test signals: IRQ period elapsed, SPDIF lock/rate changes, GPIO power events, MIDI input, probe/remove, PM cycles, proc output, and broken-EEPROM matching.
