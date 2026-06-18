# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_channel.h

Purpose: channel abstraction interface for vidtv.

Important APIs/types/functions: `struct vidtv_channel` contains name, transport stream ID, SDT service, PAT program number/program, PMT streams, encoder chain, EIT events, and next pointer. Prototypes expose SI init/destroy, hardcoded channel init/destroy, and S302M channel construction.

Control flow: no executable flow; implementations build linked channel lists and derive PSI tables/encoder polling from them.

State and persistence: channel instances persist for the lifetime of a mux and own PSI fragments plus encoders.

Dependencies and integration points: includes `vidtv_encoder.h`, `vidtv_mux.h`, and `vidtv_psi.h`, making it the bridge between service metadata, mux operation, and elementary stream encoders.

Risks: ownership is pointer-heavy; callers must use the matching destroy helpers. Adding channel types requires careful PAT/PMT/SDT/EIT descriptor consistency and encoder/PID uniqueness.

Test signals: compile coverage, mux init/destroy, and service scan output for generated channels.
