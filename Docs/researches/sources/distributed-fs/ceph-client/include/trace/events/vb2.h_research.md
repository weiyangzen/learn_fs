# sources/distributed-fs/ceph-client/include/trace/events/vb2.h

Purpose: Defines core videobuf2 tracepoints for buffer done, queue, dequeue, and queue-buffer operations.

Important APIs/types/functions: `vb2_event_class` backs `vb2_buf_done`, `vb2_buf_queue`, `vb2_dqbuf`, and `vb2_qbuf`, capturing queue pointer, buffer pointer, buffer index, type, memory model, and state.

Control flow: vb2 core emits events at buffer lifecycle transitions. The shared event class keeps a consistent field layout across operations.

State/persistence: No queue state is changed. Trace records persist selected buffer state for postmortem ordering analysis.

Dependencies/integration: Depends on `media/videobuf2-core.h`; integrated with media subsystem drivers and tracefs.

Risks: Buffer state values are internal and may change with vb2 refactors. Events must avoid dereferencing freed buffers around completion paths.

Test signals: Stream with vb2-backed drivers and verify qbuf/dqbuf/done sequences under tracefs.
