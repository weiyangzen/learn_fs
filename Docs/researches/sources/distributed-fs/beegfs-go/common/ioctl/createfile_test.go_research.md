<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/createfile_test.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/createfile_test.go

Purpose: BeeGFS integration test for `CreateFile`.

Important APIs/types/functions: build tag `beegfs`; `TestCreateFile`.

Control flow: temporarily sets umask to zero, creates a temp BeeGFS directory, calls `CreateFile` for a regular file and a symlink, then checks permissions and file type via `os.Stat`/`os.Lstat`.

State and persistence: creates real BeeGFS entries and removes them through the shared cleanup helper.

Dependencies and integration points: depends on the test mount constants/helper from `api_test.go`, `testify`, and actual BeeGFS ioctl support.

Risks: does not test UID/GID, preferred targets, storage pool, buddy-mirrored parent detection, or error cases. Requires root or environment capabilities for some untested options.

Test signals: good integration coverage for default regular files and symlink option behavior when run with `-tags beegfs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/createfile_test.go -->
