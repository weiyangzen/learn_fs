<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp_api.h -->
# sources/distributed-fs/ceph-client/include/linux/gfp_api.h

Purpose: Compatibility include wrapper that exposes the GFP allocation API by including `linux/gfp.h`.

Important APIs/types/functions: This file declares no APIs of its own; all visible symbols are inherited from `gfp.h`.

Control flow: Preprocessor-only include indirection.

State and persistence behavior: No state.

Dependencies and integration points: Depends entirely on `linux/gfp.h`; useful for source compatibility where code includes a more API-oriented header name.

Risks: Because it is a one-line include, any include-cycle or layering concern is inherited from `gfp.h`.

Test signals: Header self-include/compile tests and include-what-you-use checks for consumers expecting GFP allocation declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp_api.h -->
