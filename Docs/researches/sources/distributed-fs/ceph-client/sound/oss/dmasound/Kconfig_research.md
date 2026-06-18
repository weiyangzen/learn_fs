# sources/distributed-fs/ceph-client/sound/oss/dmasound/Kconfig

Purpose: Defines legacy OSS `dmasound` platform-driver configuration for Atari, Amiga Paula, and Q40 sound, plus the internal `DMASOUND` core symbol.

Important APIs/types/functions: Config entries are `DMASOUND_ATARI`, `DMASOUND_PAULA`, `DMASOUND_Q40`, and hidden `DMASOUND`. Each platform option is `tristate`, depends on the matching architecture/platform plus `SOUND`, and selects `DMASOUND`; `DMASOUND` selects `SOUND_OSS_CORE`.

Control flow: Enabling a platform option causes the matching objects in `sound/oss/dmasound/Makefile` to build with `dmasound_core.o`. User help describes `/dev/audio` and Linux/i386 OSS compatibility plus module availability.

State and persistence: No runtime state. Build configuration controls whether the legacy OSS device implementation and its platform backend are present.

Dependencies/integration: Integrates platform architecture symbols with the OSS sound core. Risks are mostly configurational: these legacy drivers depend on obsolete OSS interfaces and architecture-specific hardware symbols, so accidental enablement on unsupported platforms should be prevented by dependencies. Test signals are correct Kconfig visibility per architecture, `SOUND_OSS_CORE` selection, and successful module/built-in builds for each platform.
