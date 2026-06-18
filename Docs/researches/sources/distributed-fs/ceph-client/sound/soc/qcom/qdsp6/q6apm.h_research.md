# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm.h

Purpose: `q6apm.h` is the exported interface and core data model for AudioReach APM graph clients. It defines channel constants, callback events, graph/session limits, shared-memory buffer records, and public graph APIs.

Important APIs and types: `struct q6apm` mirrors the service state used by `q6apm.c`. `struct audio_buffer` is a physical address/size pair. `struct audioreach_graph_data` stores fragment arrays, period count, next DSP buffer index, and atomic hardware pointer. `struct audioreach_graph` caches topology graph state and refcount. `struct q6apm_graph` is the per-client handle used by DAI code. Public functions include graph lifecycle, media format for PCM and shared memory endpoints, read/write, fixed-region memory map/unmap, fragment allocation/free, synchronous command send, module lookup, ADSP/APM readiness, compressed decoder controls, and hardware pointer query.

Control flow: callers open a graph by topology graph ID and direction, configure media formats, map memory, allocate fragments, prepare/start, exchange read/write buffers, stop/flush, then close and unmap/free resources. The callback typedef `q6apm_cb` allows lower-level graph events to be translated into ALSA notifications.

State and persistence: the header exposes enough struct fields for cooperating in-tree drivers to read graph IDs, buffer data, and topology info directly. That speeds integration but increases coupling: external users can observe or mutate state that `q6apm.c` expects to own.

Dependencies and integration points: includes Linux kernel primitives, ALSA SoC, APR/GPR support, `../common.h`, and `audioreach.h`. It is consumed by APM frontend, LPASS backend, and clock/port integration code.

Risks: ABI is not stable for external modules because structs are public and lack accessors. `APM_PORT_MAX` depends on `LPASS_MAX_PORT`; any DT/table mismatch can produce out-of-bounds indexing in users. Direction conventions are ALSA `SNDRV_PCM_STREAM_*` values and must match the rx/tx naming used inside `q6apm.c`.

Test signals: compile all users after field changes, verify event constants match callback dispatch, and exercise both playback/capture directions to confirm shared-memory endpoint selection.
