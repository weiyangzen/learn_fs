<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/romimage.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/romimage.h

Purpose: declares the common ROM-image progress hook.

Important APIs/types/functions: `mmcif_update_progress(int nr)` prototype.

Control flow: early ROM/image loaders can call the hook while copying/loading storage blocks.

State and persistence: no state in this common declaration.

Dependencies/integration: implemented by board ROM headers or platform ROM code that can signal progress.

Risks: signature mismatch would break early boot builds where normal driver infrastructure is unavailable.

Test signals: build ROM image configurations and check progress hook references resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/romimage.h -->
