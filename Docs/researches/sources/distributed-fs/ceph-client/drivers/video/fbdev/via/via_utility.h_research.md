<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.h

Purpose: Header for viafb utility/query and gamma helper functions.

Important APIs/types/functions: Declares device support/connect queries, LCD expansion support query, gamma set/get, and gamma support-state reporting.

Control flow and state: No standalone flow. Implementations mutate or read hardware LUT state and global device/chip state.

Dependencies and integration points: Included where ioctl handling needs these helpers. Risks are prototype drift and the absence of explicit locking/error details in the API. Test signals are compile coverage and ioctl paths that call each declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.h -->
