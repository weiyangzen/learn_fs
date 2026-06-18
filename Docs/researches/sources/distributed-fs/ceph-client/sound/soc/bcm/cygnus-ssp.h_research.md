# sources/distributed-fs/ceph-client/sound/soc/bcm/cygnus-ssp.h

Purpose: shared Cygnus audio definitions for the SSP CPU DAI driver and PCM platform. It defines port limits, operating modes, ring-buffer register descriptors, per-port state, global audio device state, and exported helper prototypes.

Important APIs, types, and functions: `CYGNUS_MAX_PLAYBACK_PORTS`, `CYGNUS_MAX_CAPTURE_PORTS`, `CYGNUS_MAX_I2S_PORTS`, and `CYGNUS_MAX_PORTS` define the three I2S/TDM ports plus one playback-only SPDIF port. `struct ringbuf_regs` describes MMIO offsets and runtime period/buffer metadata for a source or destination ring buffer. `RINGBUF_REG_PLAYBACK()` and `RINGBUF_REG_CAPTURE()` construct those descriptors from register-offset macros supplied by `cygnus-pcm.c`. `struct cygnus_ssp_regs` bundles per-port I2S and buffer-fabric offsets. `struct cygnus_track_clk`, `struct cygnus_aio_port`, and `struct cygnus_audio` hold stream, clock, MMIO, and substream state. Prototypes expose custom fsync width and PCM registration helpers.

Control flow: the header has no executable control flow; it is the contract used by `cygnus-ssp.c` to populate ports and by `cygnus-pcm.c` to look up ring-buffer and substream data.

State and persistence: all state is in in-memory structs attached to the platform device. `cygnus_aio_port` is the per-DAI state object; `cygnus_audio` is the aggregate device object. No persistent storage exists.

Dependencies and integration: requires the C files to define ring-buffer offset macros before using the ring-buffer constructor macros. Its exported prototypes are consumed inside the Broadcom Cygnus audio driver set and by possible machine drivers.

Risks: `CYGNUS_AUIDO_MAX_NUM_CLKS` is misspelled but consistently used. The header declares `cygnus_ssp_set_custom_fsync_width()` twice. Comments contain minor spelling errors but do not alter behavior. Structural contracts are tightly coupled to hardware register layout and array bounds.

Test signals: compile both `cygnus-pcm.c` and `cygnus-ssp.c` together with sparse/W=1 to catch duplicate prototype or type issues; run DT configurations for all allowed port counts and validate array bounds for `portinfo` and `audio_clk`.
