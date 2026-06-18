# sources/distributed-fs/ceph-client/include/uapi/linux/ultrasound.h

Purpose: Provides legacy OSS sequencer macros for programming Gravis Ultrasound synthesizer private events.

Important APIs/types/functions: `_GUS_*` command constants identify voice count, voice on/off/fade/mode/balance/frequency/volume, ramp configuration, volume scale, and voice position operations. `_GUS_CMD` writes an 8-byte `SEQ_PRIVATE` event into the OSS sequencer buffer using `_SEQ_NEEDBUF`, `_seqbuf`, `_seqbufptr`, and `_SEQ_ADVBUF`. Public macros such as `GUS_VOICEON`, `GUS_VOICEFREQ`, and `GUS_RAMPRANGE` pack parameters.

Control flow: Userspace sequencer code invokes a macro, which appends a private event to the sequencer buffer. The OSS sequencer/GUS driver interprets bytes as channel, command, voice, and two 16-bit parameters.

State and persistence behavior: Commands alter synthesizer voice state and hardware playback/ramp settings. State is device runtime state, not persisted by the header.

Dependencies and integration points: Requires OSS sequencer macros and buffer globals from other sound headers. Integrates with legacy GUS hardware support.

Risks: Macros perform unaligned `unsigned short *` writes into byte buffers and assume little host behavior matching legacy ABI. Parameters must be zeroed when unused as documented.

Test signals: Compile legacy OSS clients, verify emitted 8-byte event encoding, run with OSS/GUS emulation if available, and test buffer-advance behavior under near-full sequencer buffers.
