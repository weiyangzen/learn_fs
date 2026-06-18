# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_priv.h

## Purpose
Private cross-file Speakup header for internal constants, transport prototypes, synth helpers, buffer access, variable sysfs callbacks, and global subsystem state.

## Important APIs, Types, And Functions
Defines `SYNTH_CHECK`, `SYNTH_START`, `KT_SPKUP`, `SPK_SYNTH_TIMEOUT`, default synth device/serial, and prototypes for serial/tty I/O, synth buffer functions, variable lookup/show/store, synth output helpers, region reservation, `synth_add/remove/current`, and exported I/O ops.

## Control Flow
No executable flow, but `module_spk_synth()` users rely on `synth_add()`/`synth_remove()` contracts and all drivers rely on these helper prototypes.

## State And Persistence Behavior
Declares `speakup_info`, `synth_time_vars`, `spk_serial_io_ops`, and `spk_ttyio_ops`; actual state is stored in implementation files.

## Dependencies, Integration Points, Risks, And Test Signals
Includes `spk_types.h` and `spk_priv_keyinfo.h`. Risks are broad compile/runtime breakage from constant or prototype changes, especially `SYNTH_CHECK`. Test full Speakup build, loading several synth drivers, sysfs variable reads/writes, and transport probes.
