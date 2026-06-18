<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/utils.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/utils.go

Purpose: helper for converting fixed-size C string buffers to Go string lengths.

Important APIs/types/functions: `cStringLen`.

Control flow: scans a byte slice until the first null byte and returns that index; if none exists, returns the full length.

State and persistence: none.

Dependencies and integration points: used by `GetConfigFile` to trim the kernel-filled config path buffer.

Risks: no UTF-8 validation or trimming beyond the first null, which is appropriate for C paths.

Test signals: indirectly exercised by `api_test.go` when BeeGFS integration tests run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/utils.go -->
