# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-messages.h

Purpose: reserves structured log message IDs for `nl-cache`.

Important APIs, types, and functions: `GLFS_MSGID(NLC, NLC_MSG_NO_MEMORY, NLC_MSG_EINVAL, NLC_MSG_NO_TIMER_WHEEL, NLC_MSG_DICT_FAILURE)` defines stable IDs used by allocation, argument, timer-wheel, and dictionary failure paths.

Control flow: none; preprocessor metadata only.

State and persistence: no runtime state.

Dependencies and integration: includes `<glusterfs/glfs-message-id.h>` and must match the `NLC` component namespace.

Risks and test signals: IDs should only be appended, never removed or reused, to preserve log compatibility. Compile-time use in `gf_msg` calls is the primary validation.
