# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-errno.h

Purpose: `q6dsp-errno.h` defines firmware ADSP error/status codes used by QDSP6 audio service drivers.

Important APIs and types: it provides numeric `ADSP_E*` macros for OK, failed, bad param, unsupported, version mismatch, unexpected, panic, resource, handle, already, not ready, pending, busy, aborted, preempted, continue, immediate, not implemented, need more, no memory, and not exist.

Control flow: service callbacks compare firmware status fields to these constants, especially `ADSP_EUNSUPPORTED` in q6core fallback logic.

State and persistence: no state; constants are firmware protocol values.

Dependencies and integration points: included by q6core, q6afe, q6asm, and DAI code for interpreting DSP response status. These values bridge APR/GPR payloads to Linux errno handling.

Risks: many drivers collapse nonzero ADSP status to `-EINVAL`, so preserving distinct constants here does not automatically preserve diagnostic fidelity. Any value change would break protocol decoding.

Test signals: compile coverage and mocked DSP responses for unsupported, busy, bad param, and no-memory statuses.
