# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_proc.c

## Purpose
`ac97_proc.c` implements ALSA procfs diagnostics for AC97 and MC97 codecs. It prints codec identity, capabilities, current mixer/rate/SPDIF/modem status, optional AC97 2.3 function information, raw register dumps, and creates/removes per-bus proc directories.

## Important APIs, Types, And Functions
- `snd_ac97_proc_init()` creates `ac97#addr-num` or `mc97#addr-num` and a matching `+regs` entry.
- `snd_ac97_proc_done()` removes per-codec proc entries.
- `snd_ac97_bus_proc_init()` and `snd_ac97_bus_proc_done()` manage the `codec97#N` proc directory.
- `snd_ac97_proc_read_main()` formats most codec status.
- `snd_ac97_proc_read_functions()` prints AC97 2.3 function/gain/location details by selecting function IDs.
- `snd_ac97_proc_regs_read()` dumps even AC97 registers from `0x00` to `0x7e`; under `CONFIG_SND_DEBUG`, `snd_ac97_proc_regs_write()` allows direct register writes.

## Control Flow
Proc reads lock `ac97->page_mutex`, then either read a single codec or iterate AD1881-family subcodecs by selecting each codec through `AC97_AD_SERIAL_CFG`. The main reader prints base audio capabilities, current setup, extended ID/status, VRA/VRM rate registers, SPDIF status with codec-specific interpretation, AC97 2.3 function info, then modem extended status when present. Register dumps follow the same AD18xx multi-codec selection pattern.

## State And Persistence
The file does not create durable state beyond `ac97->proc`, `ac97->proc_regs`, and `bus->proc` pointers. Reads temporarily change `AC97_INT_PAGING`, `AC97_FUNC_SELECT`, and AD serial config, then restore page/selection where needed. Debug writes update the AC97 hardware and cache via `snd_ac97_write_cache()`.

## Dependencies And Integration Points
It depends on ALSA info/proc APIs, `sound/ac97_codec.h`, AES/SPDIF definitions, `ac97_local.h`, and `ac97_id.h`. It consumes register cache and quirk state from generic AC97 setup and `ac97_patch.c`, especially AD18xx multi-codec state and Realtek/Cirrus/Yamaha SPDIF quirks.

## Risks
- Proc reads touch hardware registers and paging, so locking and restoration are critical.
- Debug register writes can alter hardware state arbitrarily and are guarded by `CONFIG_SND_DEBUG` plus writable proc mode.
- String output interprets many vendor bits; incorrect codec flags can produce misleading diagnostics.
- AD18xx iteration assumes `spec.ad18xx` has been initialized correctly by patch code.

## Test Signals
- Proc entries should appear under the card proc root after AC97 bus and codec initialization and disappear on teardown.
- Reads should not leave AC97 page or AD serial selection changed.
- Register dump should include all even registers and each detected AD18xx subcodec.
- Debug write tests should reject odd/out-of-range registers and values above 16 bits.
