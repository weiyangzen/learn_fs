# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_lib.c

## Purpose
Implements low-level access, detection, object creation, and ALSA device registration for Yamaha OPL4 chips. It also creates the paired OPL3 FM device because OPL4 includes an FM-compatible portion.

## Important APIs, Types, And Functions
Exports `snd_opl4_write()`, `snd_opl4_read()`, `snd_opl4_read_memory()`, `snd_opl4_write_memory()`, and `snd_opl4_create()`. Internal helpers include `snd_opl4_wait()`, `snd_opl4_enable_opl4()`, `snd_opl4_detect()`, and optional sequencer device creation.

## Control Flow
`snd_opl4_create()` allocates `struct snd_opl4`, reserves FM and PCM/MIX I/O regions, initializes locks, enables OPL4 mode through the FM register block, detects device ID and mixer readback behavior, registers an ALSA codec device, creates an integrated OPL3 object on the FM ports, re-enables OPL4 after OPL3 initialization, then creates mixer/proc and sequencer devices when configured. Memory read/write temporarily sets memory-access mode, loads the 24-bit address registers, streams bytes through the memory data port, then restores the configuration register.

## State And Persistence
Runtime state includes I/O resources, hardware variant, locks, proc entry, sequencer device pointer, and the paired OPL3 object returned to callers. OPL4 external ROM/SRAM contents are hardware state; the driver does not persist copies.

## Dependencies And Integration
Depends on ALSA device registration, OPL3 library creation, raw I/O port access, resource management, OPL4 mixer/proc helpers, and optional sequencer device creation.

## Risks And Test Signals
The wait loop is bounded but silently continues after timeout, so absent or wedged hardware can produce misleading follow-up I/O. Detection writes mixer registers and memory configuration, making restore behavior important. Tests should cover OPL4 versus OPL4-ML detection, resource conflicts, OPL3 pairing, memory read/write through procfs, mixer creation, and sequencer device creation only for supported variants.
