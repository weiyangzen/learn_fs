## sources/distributed-fs/ceph-client/include/linux/cdx/mcdi.h

**Purpose:** This header defines the CDX Management Controller Diagnostic Interface (MCDI) protocol state, command tracking, and request/response helpers.

**Important APIs/types/functions:** `enum cdx_mcdi_mode` selects event wait or fail-fast mode. `enum cdx_mcdi_cmd_state` tracks queued, retry, running, cancelled, and finished commands. `struct cdx_mcdi` stores protocol data, ops, remoteproc/RPMsg endpoints, and post-probe work. `struct cdx_mcdi_cmd` tracks refcount, lists, work, state, buffers, sequence, timing, completion cookie/callback, handle, command number, return code, and output. `struct cdx_mcdi_iface` stores locks, command lists, workqueue, waitqueue, doorbell/sequence owners, previous handle/seq, mode, and epoch. APIs include `cdx_mcdi_init()`, `cdx_mcdi_finish()`, `cdx_mcdi_process_cmd()`, and `cdx_mcdi_rpc()`. Macros declare buffers and access dword fields.

**Control flow, state, persistence:** RPCs allocate/queue commands, serialize through `iface_lock`, submit through `mcdi_request`, wait for RPMsg/event completion, retry on MC resource rejection, and complete callbacks/waiters. State is transient protocol/queue state.

**Dependencies/integration:** Depends on mutexes, krefs, RPMsg, remoteproc, workqueues, waitqueues, CDX bitfield helpers, and generated `MC_CMD_*` field constants.

**Risks and test signals:** Risks include sequence/doorbell ownership races, timeout handling, reboot epoch recovery, cancelled-command cleanup, and buffer alignment assumptions. Test signals include firmware RPC success/failure, timeout/retry injection, RPMsg disconnect, command cancellation, and lockdep/refcount checks.
