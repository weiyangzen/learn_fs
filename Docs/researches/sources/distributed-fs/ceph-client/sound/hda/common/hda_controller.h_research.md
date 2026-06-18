# sources/distributed-fs/ceph-client/sound/hda/common/hda_controller.h

## Purpose
Defines the shared data model and public API for HD-audio controller implementations built around `struct azx`. It centralizes driver capability bits, stream wrappers, controller callbacks, PCM bookkeeping, and exported controller helpers.

## Important APIs, Types, And Functions
Important definitions include `AZX_DCAPS_*` quirk/capability flags, snoop type enum, `struct azx_dev`, `struct hda_controller_ops`, `struct azx_pcm`, position/delay callback typedefs, and `struct azx`. It declares register access macros, stream allocation/free helpers, controller init/stop/interrupt functions, codec probe/configuration functions, and stream initialization functions.

## Control Flow
Platform or PCI drivers allocate/fill `struct azx`, initialize the bus with `azx_bus_init()`, initialize streams, probe/configure codecs, and expose PCM devices. Runtime PCM paths use `get_azx_dev()` to recover the assigned stream from ALSA runtime private data.

## State And Persistence Behavior
`struct azx` persists controller-wide flags and configuration: card/pci identity, stream counts and offsets, driver caps, ops callbacks, position callbacks, codec probe mask, beep/control options, PM flags, snoop settings, and stream list ownership via the embedded HDA bus.

## Dependencies And Integration Points
Depends on Linux interrupt/timecounter support, ALSA core/PCM/initval, HDA codec and register headers, and hdac bus/stream abstractions. It is the contract between bus-specific controller drivers and `controller.c`.

## Risks And Test Signals
Risks are incorrect capability flags, mismatched stream indices/counts, broken callback assumptions, and register accessor misuse. Test signals include successful probe across controller families, correct stream enumeration, no IRQ storms, reliable position reporting, and behavior under driver-specific quirks such as MSI disable, LPIB position, 4K BDLE boundaries, and PIO commands.
