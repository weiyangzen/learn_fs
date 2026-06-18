# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_command_header_abi.h

Purpose: Defines the packed Intel GSC MTL HECI command header used by xe GSC packet submission.

Important APIs/types: `struct intel_gsc_mtl_header`, `GSC_HECI_VALIDITY_MARKER`, `MTL_GSC_HEADER_VERSION`, `GSC_OUTFLAG_MSG_PENDING`, and `GSC_INFLAG_MSG_CLEANUP`.

Control flow: Producers fill marker, client id, session/message handles, size, flags, and version before firmware submission. Consumers validate marker/size/status and reuse `gsc_message_handle` when firmware reports pending output.

State/persistence: Header state is transient in shared command buffers; session/message handles link multi-step firmware exchanges.

Dependencies/integration: Used by `xe_gsc_submit.c` and GSC clients over mapped BO memory.

Risks/test signals: Packed firmware ABI layout, lower-20-bit size rule, input/output flag confusion, pending resubmission, malformed marker/status tests, and structure-size coverage.
