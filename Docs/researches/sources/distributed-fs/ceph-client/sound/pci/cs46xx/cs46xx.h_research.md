# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx.h

## Purpose

`cs46xx.h` is the main private hardware contract for the ALSA CS46xx driver. It declares register offsets, bit definitions, DMA descriptor fields, MIDI/gameport/AC97/DSP constants, core runtime structures, and function prototypes shared by `cs46xx.c`, `cs46xx_lib.c`, and optional DSP SPOS sources.

## Important APIs, Types, and Definitions

The header is dominated by hardware definitions:

- BA0 direct register offsets cover host interrupt/status/control, host DMA, PCI config mirrors, clocks/PLL, serial ports, AC97 command/status, joystick, MIDI, GPIO, extended GPIO, I/O trap, PC/PCI, and power-management registers.
- BA1 offsets cover DSP memories (`SP_DMEM0`, `SP_DMEM1`, `SP_PMEM`, `SP_REG`), DSP control/debug registers, Omni memory, and legacy playback/capture parameter areas.
- Bit masks define host interrupt bits (`HISR_*`), host signal bits, DMA status/control bits, clock/PLL fields, feature reporting, serial/AC97 slots, joystick bits, MIDI bits, DSP control/debug state, scatter/gather descriptor fields, and generic DMA requestor fields.
- MIDI mode constants `CS46XX_MODE_OUTPUT` and `CS46XX_MODE_INPUT` track UART open state.
- AC97 limits and indices define up to four codecs, primary/secondary slots, and secondary offset.
- Mixer constants identify SPDIF input/output element indices.

Core structures:

- `struct snd_cs46xx_pcm` stores DMA buffer metadata, control value, frame/byte shift, ALSA indirect PCM state, substream pointer, optional DSP channel descriptor, and PCM channel ID.
- `struct snd_cs46xx_region` describes one mapped hardware region with name, physical base, remapped address, and size.
- `struct snd_cs46xx` is the central device state. It stores IRQ, BA0/BA1 physical addresses, named/array region mappings, mode, capture state, AC97 bus/codecs, PCI/card/PCM/rawmidi pointers, MIDI substreams, locks, MIDI control shadows, amplifier/active/mixer callbacks, ACPI port, EAPD control, mmap-valid flag, suspend flag, optional gameport, optional new-DSP SPOS state/modules, fallback old-DSP playback state, and PM saved registers.

Exported prototypes include creation, PM ops, primary/rear/IEC958/center-LFE PCM creation, mixer creation, MIDI creation, DSP startup, and gameport setup.

## Control Flow and Integration

The header itself has no executable control flow, but it defines the register and structure vocabulary used by the implementation. `cs46xx.c` includes this header and calls the declared construction functions in probe order. The implementation library uses the BA0/BA1 constants to initialize hardware, service interrupts, program AC97/MIDI/DSP state, and build ALSA devices.

Conditional compilation around `CONFIG_SND_CS46XX_NEW_DSP` changes the shape of `struct snd_cs46xx`: new-DSP builds include an SPOS mutex, DSP SPOS instance, rear/center-LFE/IEC958 PCM devices, and module descriptors; compatibility builds include older playback PCM and BA1 state. The Makefile mirrors this by adding DSP source objects only for new-DSP builds.

## State and Persistence Behavior

`struct snd_cs46xx` holds all per-card runtime state for the driver lifetime. It includes both software state (substream pointers, codec pointers, flags, callback hooks) and hardware shadows (MIDI control, mode, saved PM registers). The header defines `SAVE_REG_MAX` and `POWER_DOWN_ALL` for suspend/power handling. No on-disk persistence is represented.

## Dependencies and Integration Points

The header depends on ALSA PCM, PCM indirect helpers, rawmidi, AC97 codec support, and local DSP SPOS declarations from `cs46xx_dsp_spos.h`. It is a private driver header, not a stable userspace ABI. It integrates CS46xx hardware logic with ALSA subsystems for PCM, mixer/AC97, rawmidi, gameport, and optional DSP routing.

## Risks and Edge Cases

- Because the header encodes large numbers of hardware bitfields, incorrect masks or shifts can cause silent hardware misprogramming.
- Several definitions are conditional on `NO_CS4612`, `NO_CS4610`, or `NO_CS4615`; build configurations must keep implementation assumptions aligned with those conditionals.
- `CS46XX_DSP_CAPTURE_CHANNEL` is defined twice with the same value, which is harmless but signals historical duplication.
- `struct snd_cs46xx` layout changes with `CONFIG_SND_CS46XX_NEW_DSP`, so implementation files must guard field access consistently.
- The function prototypes expose a broad internal API; mismatches between `cs46xx.c`, `cs46xx_lib.c`, and DSP objects are compile-time failures.

## Test Signals

Build tests should cover configurations with and without `CONFIG_SND_CS46XX_NEW_DSP` and any supported CS461x feature macros. Runtime tests should validate that register definitions support successful hardware init, PCM routing, AC97 codec enumeration, MIDI traffic, DSP startup, gameport behavior, suspend/resume saved-register restoration, and mixer/SPDIF controls. Static analysis should watch for conditional field access and duplicated or inconsistent masks.
