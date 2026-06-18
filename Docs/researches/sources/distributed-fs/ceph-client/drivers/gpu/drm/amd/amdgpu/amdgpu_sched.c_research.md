## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sched.c

Purpose: implements the AMDGPU scheduler ioctl that lets privileged/user API paths override process-wide or context-specific AMDGPU context priorities for another DRM file descriptor.

Important APIs and functions: `amdgpu_sched_ioctl()` validates the UAPI op and priority, then dispatches to `amdgpu_sched_process_priority_override()` or `amdgpu_sched_context_priority_override()`. The process helper resolves an FD to `amdgpu_fpriv`, locks its context manager, and applies `amdgpu_ctx_priority_override()` to each context in the IDR. The context helper resolves a single context by ID and overrides only that context.

Control flow: the ioctl first rejects unknown ops before validating arguments. FD acquisition uses `CLASS(fd, f)(fd)` cleanup style and returns `-EINVAL` for empty descriptors. Priority validity is checked via `amdgpu_ctx_priority_is_valid()`. Context-manager updates are serialized by `mgr->lock`; single-context lookup uses `amdgpu_ctx_get/put`.

State and persistence: mutates runtime context priority override fields in `struct amdgpu_ctx`; no persistent storage. Changes affect subsequent scheduler entity priority decisions until context reset/destruction or another override.

Dependencies and integration points: depends on DRM AMDGPU UAPI, Linux fd helpers, `amdgpu_ctx`, `amdgpu_vm`, and `amdgpu_file_to_fpriv`. It is part of the DRM ioctl surface and interacts with context priority conversion in `amdgpu_ctx.c`/scheduler code.

Risks: FD-based override can affect all contexts owned by a different DRM file, so access control must be enforced by surrounding ioctl policy. Races are managed for context manager enumeration, but priority changes can still interact with active scheduling. Invalid context IDs and non-AMDGPU fds must be handled cleanly.

Test signals: ioctl tests for both ops, invalid op/priority/fd/context ID, multiple contexts under one file, and observable scheduler priority changes in submitted jobs.
