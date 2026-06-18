# sources/distributed-fs/ceph-client/sound/core/seq/Kconfig

Purpose: defines build-time configuration for ALSA sequencer support and optional sequencer clients/transports.

Important symbols: `SND_SEQUENCER` enables the sequencer core and selects `SND_TIMER` plus `SND_SEQ_DEVICE`. `SND_SEQ_DUMMY` builds the MIDI-through client. `SND_SEQUENCER_OSS` enables `/dev/sequencer` and `/dev/music` OSS emulation and selects `SND_SEQ_MIDI_EVENT`. `SND_SEQ_HRTIMER_DEFAULT` controls default timer backend. Internal tristates include `SND_SEQ_MIDI_EVENT`, `SND_SEQ_MIDI`, `SND_SEQ_MIDI_EMUL`, `SND_SEQ_VIRMIDI`, and `SND_SEQ_UMP_CLIENT`; `SND_SEQ_UMP` enables Universal MIDI Packet support.

Control flow: the menu is nested under `if SND_SEQUENCER`, so optional clients only exist when the core sequencer is enabled. Default selections wire MIDI rawmidi support into the sequencer and let UMP client support follow both `SND_UMP` and `SND_SEQ_UMP`.

State and persistence: no runtime state; persistent impact is kernel configuration and module availability.

Dependencies and integration: integrates the source files in this folder with ALSA timer, rawmidi, OSS emulation, MIDI event conversion, and UMP support.

Risks: disabling `SND_SEQ_MIDI_EVENT` indirectly by omitting OSS or MIDI sequencer features removes conversion helpers needed by compatibility paths. Timer default choices alter runtime behavior even though the sequencer module parameters can override timer IDs.

Test signals: config-matrix builds for built-in/module/off combinations, with OSS emulation requiring `SND_OSSEMUL`, hrtimer default with and without `SND_HRTIMER`, and UMP support with and without `SND_UMP`.
