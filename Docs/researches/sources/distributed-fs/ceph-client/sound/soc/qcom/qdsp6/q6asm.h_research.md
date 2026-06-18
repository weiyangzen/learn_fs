# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm.h

Purpose: `q6asm.h` is the public interface to the legacy Q6 ASM service. It defines client event constants, simple command IDs, token masks, performance modes, codec parameter structs, and exported session/buffer/stream operations.

Important APIs and types: event macros pair high-level commands with callback events such as pause, flush, EOS, close, run done, write done, and read done. Codec structs `q6asm_flac_cfg`, `q6asm_wma_cfg`, `q6asm_alac_cfg`, and `q6asm_ape_cfg` carry ALSA compress parameters into packed ASM format blocks. The opaque `struct audio_client` is created with `q6asm_audio_client_alloc` and freed with `q6asm_audio_client_free`. Exports cover open read/write, media-format programming, silence removal, run/run_nowait, generic commands, memory map/unmap, async read/write, session ID, and hardware pointer.

Control flow: a caller allocates an audio client, maps memory, opens a stream, sends format/config commands, runs, queues reads/writes, reacts to callbacks, then stops/closes, unmaps, and frees the client. The header separates blocking command APIs from `*_nowait` variants.

State and persistence: no state is stored in the header. Constants such as `ASM_WRITE_TOKEN_*` encode the token layout used by both DAI code and callback parsing, so they are part of the in-kernel contract.

Dependencies and integration points: includes `q6dsp-common.h` for channel constants and `PCM_MAX_NUM_CHANNEL`. Used by `q6asm.c` and the legacy frontend DAI. ALSA codec IDs passed to these functions come from UAPI headers.

Risks: stream IDs, session IDs, and direction values are plain integers; misuse can address the wrong ASM stream. Codec structs must match firmware expectations but are not self-validating. `FORMAT_LINEAR_PCM` duplicates a constant also used in APM headers.

Test signals: compile all ASM users after API changes, verify callback event values match `q6asm.c`, and run playback/capture/compress paths for every exported operation order.
