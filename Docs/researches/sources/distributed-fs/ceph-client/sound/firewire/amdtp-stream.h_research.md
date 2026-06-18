# sources/distributed-fs/ceph-client/sound/firewire/amdtp-stream.h

Purpose: declares the shared AMDTP/CIP streaming abstraction used by ALSA FireWire audio drivers. It models packet descriptors, stream directions, CIP quirks, sampling frequency codes, PCM integration, and multi-stream `amdtp_domain` coordination.

Important APIs/types: `enum cip_flags`, `enum cip_sfc`, `struct pkt_desc`, `struct amdtp_stream`, `amdtp_stream_process_ctx_payloads_t`, `struct seq_desc`, and `struct amdtp_domain`. Public calls initialize/destroy streams, set parameters, update after bus changes, add PCM constraints, prepare/abort PCM, add streams to a domain, start/stop domains, and expose PCM pointer/ack callbacks.

Control flow and state: backends initialize an `amdtp_stream` with direction, CIP format, flags, and a payload callback, then configure rate/data-block shape before adding it to an `amdtp_domain`. Runtime state includes FireWire ISO context, packet buffers/descriptors, current DBC/SYT state, PCM buffer/period pointers, ready wait queues, and domain stream lists. Persistence is in-memory only and reset by destroy/stop paths.

Dependencies/integration: depends on Linux FireWire ISO contexts, ALSA PCM/runtime types, `packets-buffer.h`, and backend protocols such as AM824 or DOT. Risks center on protocol quirk flags, concurrency around `pcm` pointer updates, ready wait timeouts, and DBC/SYT discontinuity handling. Test signals are successful stream start/stop, PCM pointer monotonicity, no XRUN under bus reset recovery, and correct behavior for devices requiring unusual CIP flags.
