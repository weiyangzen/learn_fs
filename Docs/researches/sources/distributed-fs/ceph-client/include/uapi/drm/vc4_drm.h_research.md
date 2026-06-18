# sources/distributed-fs/ceph-client/include/uapi/drm/vc4_drm.h

## Purpose
This header defines the Broadcom VC4 DRM UAPI for VideoCore IV GPUs. It exposes command-list submission, sequence/BO waits, BO creation/mapping, immutable shader BO creation, hang-state capture, parameter queries, tiling metadata, BO debug labels, madvise/purge hints, and performance monitors.

## Important APIs and types
`drm_vc4_submit_cl` is the central submission record. It passes userspace pointers to bin CL, shader records, uniforms, BO-handle arrays, render dimensions, tile bounds, RCL surfaces, clear values, flags, returned seqno, perfmon ID, and syncobj in/out handles. The comments explain an important design choice: because VC4 lacks an MMU, userspace submits command/state in plain memory for kernel copy and validation rather than in GPU BOs. `drm_vc4_create_shader_bo` creates non-mmappable shader BOs to prevent shader modification during execution. Waits are available by seqno or by BO. `drm_vc4_get_hang_state` returns register and BO state after GPU hangs. Perfmon records select up to 16 events and return counter arrays.

## Control flow and state
Userspace creates BOs and shader BOs, prepares bin CL/shader/uniform streams with BO handle indices, submits through `SUBMIT_CL`, receives a seqno, and waits by seqno or by BO. Syncobj input delays render start and syncobj output receives a completion fence. Tiling get/set and madvise calls adjust BO metadata and purge behavior. Perfmon objects are created, attached to jobs by ID, synchronized externally, then read.

## State and persistence behavior
GEM BOs persist by handle; shader BOs are immutable and not mappable. Submit seqnos are returned as persistent wait tokens. BO tiling modifiers, labels, and madvise retained state are persistent metadata. Hang-state ioctls expose a snapshot of fault-time hardware registers and BO physical addresses. Perfmon IDs persist until destroyed and require explicit synchronization before reading values.

## Dependencies and integration points
The header depends on `drm.h`, DRM GEM, syncobjs, VC4 CL validation, QPU shader validation, render command list surface layout, and Mesa VC4 userspace. It also integrates with DRM format modifiers for tiling and memory pressure handling through GEM madvise.

## Risks and test signals
Risks include command validation mistakes without an MMU, mutable shader security bugs, incorrect BO-handle indexing in uniforms/shader records, invalid tile bounds or RCL surfaces, missing syncobj waits, and perfmon reads without synchronization. Tests should cover malformed CL/shader records, immutable shader mapping denial, seqno and BO waits, hang-state BO count negotiation, get-param feature gates, tiling round trips, label length validation, madvise purge/retained states, and perfmon event count bounds.
