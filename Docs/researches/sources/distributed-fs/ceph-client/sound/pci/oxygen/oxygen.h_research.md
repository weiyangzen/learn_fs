
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen.h

Purpose: central internal ABI for the Oxygen driver family. It defines PCM channel IDs, device configuration flags, control IDs, PCI ID helpers, the `oxygen_model` callback table, the runtime `oxygen` device state, and exported helper prototypes.

Important types/APIs: `struct oxygen_model` supplies board callbacks for init, mixer filtering/init, cleanup, PM, PCM hardware filtering, DAC/ADC params, volume/mute/routing, GPIO/UART/AC97 handling, proc dumps, and static capabilities. `struct oxygen` stores I/O base, locks, ALSA objects, model data, interrupt mask, DAC/SPDIF/PCM state, control pointers, work items, AC97 waitqueue, saved MMIO/AC97 registers, UART buffer, and active model.

Control/state: model flags (`PLAYBACK_*`, `CAPTURE_*`, MIDI, AC97) drive PCM and mixer creation. `saved_registers` and `saved_ac97_registers` are maintained by I/O helpers for suspend/resume.

Risks: this header is the contract between all board files and shared code; changing enum order, bit mappings, or callback semantics can silently route DMA or mixers incorrectly. Test signals include full-module build, all model probes, PM restore, PCM open/hw_params/trigger, mixer add/filter paths, and exported symbol users.
