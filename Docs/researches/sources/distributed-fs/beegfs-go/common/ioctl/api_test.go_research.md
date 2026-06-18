<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/api_test.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/api_test.go

Purpose: BeeGFS integration tests for ioctl API functions.

Important APIs/types/functions: build tag `beegfs`, constants for expected client config and mount point, `getTempBeeGFSPathForTesting`, `TestBeeGFSGetConfigFile`, `TestGetEntryInfo`, `TestCreateFileStripeHints`, and `TestSetAccessAndState`.

Control flow: tests create temporary directories under `/mnt/beegfs`, call ioctl APIs, and assert expected config path, entry types, non-invalid stripe pattern types, successful stripe-hint creation, and file state setting.

State and persistence: creates and deletes real BeeGFS files/directories; requires `/mnt/beegfs` and `/etc/beegfs/beegfs-client.conf`.

Dependencies and integration points: depends on build environment with BeeGFS mounted, `testify`, `beegfs` types, and API functions from `api.go`.

Risks: not run by default without `-tags beegfs`; environment constants are hard-coded. Tests do not assert detailed entry info fields because IDs vary by filesystem.

Test signals: valuable integration signal when the required BeeGFS test mount exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/api_test.go -->
