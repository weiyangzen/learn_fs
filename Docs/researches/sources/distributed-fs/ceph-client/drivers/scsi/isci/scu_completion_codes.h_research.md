# sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_completion_codes.h

Purpose: defines SCU hardware completion-code bitfields, extraction macros, and normalized transport-layer completion status constants used by request completion handling.

Important APIs/macros: completion type bits live at bits 28-30 and distinguish task, SDMA, unsolicited frame, event, and notify completions. Status masks split transport-layer status, SDMA status, PEG/port/protocol-engine fields, and completion index. `SCU_GET_COMPLETION_TYPE()`, `SCU_GET_COMPLETION_STATUS()`, `SCU_GET_COMPLETION_TL_STATUS()`, `SCU_MAKE_COMPLETION_STATUS()`, `SCU_NORMALIZE_COMPLETION_STATUS()`, `SCU_GET_COMPLETION_SDMA_STATUS()`, `SCU_GET_COMPLETION_INDEX()`, `SCU_GET_FRAME_INDEX()`, and `SCU_GET_FRAME_ERROR()` are the main decoders. Status constants cover success, response/check-response, CRC/NAK/link/FIS/data errors, SMP errors, task abort, open rejects, invalid VIIT/IIT/RNC, and STP resource/protocol/rate rejects.

Control flow: `request.c` compares `SCU_GET_COMPLETION_TL_STATUS(code)` against `SCU_MAKE_COMPLETION_STATUS(status)` in request-state handlers, normalizes unknown failures into `scu_status`, detects suspending completion classes, and maps open rejects into libsas open-reject reasons. Controller code can use type/index macros to dispatch completions to request, frame, event, or notification handlers.

State and persistence behavior: no runtime state; the header is an ABI contract for decoding hardware completion dwords. Aliased constants intentionally share numeric values where hardware meaning depends on protocol or context, for example CRC/check-response and ACK/NAK/link errors.

Dependencies/integration: relies on `u32` definitions from includers. It integrates with `scu_event_codes.h`, `scu_task_context.h`, and request/RNC state machines that post commands and decode completions.

Risks: the header contains two constants cast as `U32` rather than `u32`; if those paths compile in a context without `U32`, they are hazardous. Aliased numeric values require protocol-aware handling; a flat mapping can mark incomplete target tasks as complete or vice versa. Test signals include macro extraction for representative completion dwords, all request completion switch cases, frame index decoding, open-reject mapping, and suspend-trigger classification.
