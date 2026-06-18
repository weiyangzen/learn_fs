# sources/distributed-fs/ceph-client/sound/pci/ice1712/stac946x.h

## Purpose
`stac946x.h` defines register addresses for STAC9460/STAC946x codecs used by the Waveterminal 192M board code.

## Important APIs, Types, and Functions
The header exports register constants for reset/status, master and per-channel DAC volumes, mic/ADC volumes, de-emphasis, general purpose, audio port control, master clocking, powerdown, revision, and address-control registers.

## Control Flow
No executable control flow is present. `wtm.c` uses these constants to read/write STAC9460 codecs over I2C.

## State and Persistence
No runtime state is stored. The constants encode the register map assumed by `wtm.c`.

## Dependencies and Integration Points
The header is standalone and consumed by the Envy24HT WTM board driver. It indirectly couples to `snd_vt1724_read_i2c()` and `snd_vt1724_write_i2c()` call sites through register numbering.

## Risks and Test Signals
Risks are wrong or incomplete register definitions causing mixer controls to touch the wrong STAC registers. Test signals are correct WTM mixer behavior for DAC mute/volume, ADC gain/mute, MIC/Line switching, and master clock changes.
