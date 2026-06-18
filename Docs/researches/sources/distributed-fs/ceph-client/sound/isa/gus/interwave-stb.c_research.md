<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/interwave-stb.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/interwave-stb.c

Purpose: wrapper module for InterWave STB cards with TEA6330T tone control. It defines `SNDRV_STB` and includes `interwave.c`.

Important APIs/types/functions: this file contributes no functions itself. The `SNDRV_STB` macro enables STB-specific code in `interwave.c`: different driver names/descriptions, `port_tc` module parameter, PnP second logical device, bit-banged I2C ops, TEA6330T detection/update/restore, and mixer-control renaming.

Control flow: Kbuild builds `interwave-stb.o`, preprocessor includes the InterWave implementation with STB paths active, and the resulting module registers ISA/PNP drivers under STB-specific names.

State and persistence: runtime state is `struct snd_interwave` plus STB-only `i2c_bus` and `i2c_res`. Tone-control mixer state is restored on resume by STB code in the included implementation.

Dependencies and integration: depends on `interwave.c`, `sound/tea6330t.h`, ALSA I2C bit-bang support, and STB PnP IDs. Risks are include-template coupling and accidental divergence from non-STB InterWave behavior. Test signals are compile of `CONFIG_SND_INTERWAVE_STB`, TEA6330T detection at `port_tc`, PnP tone-control resource activation, mixer update, and resume restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/interwave-stb.c -->
