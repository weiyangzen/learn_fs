# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle.h

## Purpose
`msnd_pinnacle.h` defines Pinnacle/Fiji-specific hardware constants for the MultiSound driver. It covers ISA logical-device configuration registers, DSP control ports, DSP message codes, queue sizes, MIDI routing constants, SMA shared-memory layout, firmware filenames, and user-visible long name.

## Important APIs, Types, and Functions
Important definitions include config registers `IREG_LOGDEVICE`, `IREG_ACTIVATE`, `IREG_IO*_BASE*`, `IREG_IRQ_*`, `IREG_MEM*`; DSP registers `HP_DSPR` and `HP_BLKS`; reset and bank-select values; Pinnacle DSP messages such as `HIDSP_PLAY_UNDER`, `HIDSP_RECQ_OVERFLOW`, and `HIDSP_DAT_IN_OFF`; queue sizes `MIDQ_BUFF_SIZE` and `DSPQ_BUFF_SIZE`; full Pinnacle `SMA_*` offsets for PCM format, mixer, DAT, peaks, and play count; and firmware files `turtlebeach/pndspini.bin` and `turtlebeach/pndsperm.bin`.

## Control Flow
The header contributes compile-time constants consumed by `msnd_pinnacle.c` and `msnd_pinnacle_mixer.c`. Logical-device writes in the board driver rely on the `IREG_*` definitions, while mixer and PCM code rely on the Pinnacle SMA offsets.

## State and Persistence
No state is stored in the header. Its constants describe volatile hardware state in ISA configuration registers and DSP SRAM.

## Dependencies and Integration Points
It integrates with `msnd.h` as the Pinnacle-specific extension and is required by the mixer because the mixer writes Pinnacle-only fields such as mic pot and synth/MHDR volume.

## Risks and Test Signals
Risks are wrong register constants or offsets corrupting card configuration or DSP memory. Test signals include successful logical device activation for DSP/MPU/IDE/joystick, correct firmware request names, successful mixer writes to master/PCM/mic/synth, and correct interpretation of Pinnacle DSP status messages.
