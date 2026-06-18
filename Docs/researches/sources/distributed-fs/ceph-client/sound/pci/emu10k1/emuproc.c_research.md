# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emuproc.c

## Purpose
`emuproc.c` exposes EMU10K1 diagnostic and debug state through ALSA proc entries. It reports card identity, FX routing, S/PDIF lock/status, capture rates, voice allocator state, FX8010 GPR/TRAM/code dumps, and an FX8010 instruction disassembly. With `CONFIG_SND_DEBUG`, it also creates raw I/O and pointer-register read/write proc files for low-level hardware inspection.

## Important APIs, Types, and Functions
The public entry point is `snd_emu10k1_proc_init()`. Read callbacks include `snd_emu10k1_proc_read()`, `snd_emu10k1_proc_spdif_read()`, `snd_emu10k1_proc_rates_read()`, `snd_emu10k1_proc_acode_read()`, `snd_emu10k1_fx8010_read()`, and `snd_emu10k1_proc_voices_read()`. `struct emu10k1_reg_entry` plus `sblive_reg_entries[]`, `audigy_reg_entries[]`, and `emu10k1_const_entries[]` support symbolic FX8010 disassembly. Debug-only helpers read and write I/O registers, PTR/DATA register banks, and E-MU 1010 FPGA routes.

## Control Flow
Initialization registers read-only proc entries unconditionally for `emu10k1`, `voices`, FX8010 binary dumps, and `fx8010_acode`; additional S/PDIF and capture-rate entries are conditional on card capabilities. Reads query live hardware registers with `snd_emu10k1_ptr_read()`, `snd_emu10k1_efx_read()`, or FPGA helpers and format into `snd_info_buffer`. Binary FX8010 reads select an offset based on the entry name, allocate a temporary buffer, read register words, adjust Audigy TRAM address layout, and copy bytes to userspace.

## State and Persistence
The file does not own persistent state. It observes live `struct snd_emu10k1` fields, FX8010 program metadata, voice flags, masks, and hardware registers. Debug write proc files, when compiled in, directly mutate hardware I/O/PTR registers and therefore can alter device state outside normal ALSA control flows.

## Dependencies and Integration Points
It depends on ALSA proc/info APIs, `sound/emu10k1.h`, `p16v.h` capture-rate register definitions, FX8010 register accessors, E-MU 1010 FPGA helpers in `io.c`, and card capability flags initialized by the main driver. Proc output uses mixer route-name tables such as `snd_emu10k1_audigy_ins`, `snd_emu10k1_sblive_outs`, and `snd_emu10k1_fxbus`.

## Risks
Most production entries are read-only, but they still read live hardware and may have side effects on E-MU FPGA GPIO reads, as documented in `io.c`. `CONFIG_SND_DEBUG` write entries are intentionally sharp: they accept register/value text and write raw I/O or pointer registers with minimal validation. FX8010 binary reads allocate `count + 8`; callers with huge reads could stress memory, though proc read sizes are normally bounded by userspace. Disassembly tables encode hardware knowledge and can become misleading if register maps change.

## Test Signals
After driver load, verify proc entries appear only for matching capabilities and can be read without warnings or sleeps in atomic context. For FX8010 dumps, compare reported sizes with Audigy versus SB Live limits. For debug builds, test invalid register ranges are rejected or ignored, and raw writes do not overrun channel counts. S/PDIF and capture-rate output should track actual input lock/rate changes.
