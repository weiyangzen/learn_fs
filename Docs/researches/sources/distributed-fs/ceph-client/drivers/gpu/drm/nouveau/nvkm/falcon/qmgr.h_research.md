# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/qmgr.h

## Purpose
Declares falcon queue manager, command queue, message queue, and sequence tracking structures.

## Important APIs, types, and functions
Defines `HDR_SIZE`, `QUEUE_ALIGNMENT`, `MSG_BUF_SIZE`, `NVKM_FALCON_QMGR_SEQ_NUM`, `struct nvkm_falcon_qmgr_seq`, `struct nvkm_falcon_qmgr`, `struct nvkm_falcon_cmdq`, and `struct nvkm_falcon_msgq`. It declares sequence acquire/release and queue logging macros.

## Control flow, state, and persistence
No code runs here. Sequence states include free, pending, used, and cancelled; each sequence has callback, private data, completion, async flag, and result.

## Dependencies and integration points
Includes `core/falcon.h` for firmware command/message callback types. Shared by command, message, and queue-manager implementations.

## Risks and test signals
Message buffer size is fixed at 128 bytes; larger firmware messages fail. Build coverage catches structural drift; runtime SEC2 command completion validates queue state.
