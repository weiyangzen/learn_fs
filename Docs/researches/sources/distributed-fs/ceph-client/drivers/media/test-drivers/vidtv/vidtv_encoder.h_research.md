# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_encoder.h

Purpose: generic encoder abstraction for vidtv elementary streams.

Important APIs/types/functions: defines `enum vidtv_encoder_id` with `S302M`, `struct vidtv_access_unit` for payload slices with PTS/DTS/size/offset, note-frequency enum for generated audio sources, and `struct vidtv_encoder` with buffers, source offsets, encoder callbacks, stream IDs/PIDs, timing, sync pointer, and linked-list chaining.

Control flow: no executable flow; concrete encoders such as S302M implement `encode`, `clear`, and `destroy`, and the mux polls each encoder and packetizes its access units.

State and persistence: encoder instances persist under channel objects during mux lifetime. They own encoded buffers, access-unit lists, source state, sample count, and encoder-specific context.

Dependencies and integration points: used by `vidtv_channel.c`, `vidtv_mux.c`, `vidtv_pes.c`, and concrete S302M code.

Risks: callback and ownership contracts are manual. Mux assumes `encode()` populates access units and `clear()` resets state after packetization. Adding encoders requires PID/stream ID correctness and cleanup symmetry.

Test signals: S302M stream generation, mux polling of chained encoders, access-unit packetization, and destroy-path leak checks.
