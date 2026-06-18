# sources/control-plane/longhorn-engine/pkg/frontend/tgt/frontend.go

Purpose: implements the iSCSI/tgt-facing frontend by combining a Longhorn device service with the local socket data frontend.

Important APIs/types/functions: `Tgt` stores a socket frontend, Longhorn device service, frontend name, state, and SCSI/iSCSI timeout settings. `New` constructs the socket and returns a `types.Frontend`. `Init` initializes the socket and creates/initializes a `longhorndev` device. `Startup` starts the socket server then the device. `Shutdown` unfreezes the filesystem at the endpoint, shuts down the device, and shuts down the socket. `Endpoint` returns the device endpoint when up. `Upgrade` creates a new device, runs `PrepareUpgrade`, initializes/starts the socket, then `FinishUpgrade`. `Expand` delegates to the device.

Control flow: data serving must start before the device is started or upgraded, because the device depends on the socket data path. Shutdown tolerates filesystem unfreeze failure but propagates device/socket shutdown errors. Upgrade is a multi-step device plus socket transition.

State and persistence: no direct durable state. Device service operations affect kernel/iSCSI target state. Socket state is delegated to `socket.Socket`.

Dependencies and integration points: integrates `github.com/longhorn/go-iscsi-helper/longhorndev`, `frontend/socket`, `types.Frontend`, and `util.UnfreezeFilesystemForDevice`. It is a primary frontend used by engine processes.

Risks: if socket startup succeeds but device start fails, the socket may be left running. `Endpoint` returns empty while down, so `Shutdown` calls unfreeze with an empty path when not up. Upgrade replaces `t.dev` before all steps succeed, which can complicate rollback. The socket frontend's shutdown limitations carry through here.

Test signals: no direct tests in this subset. Device lifecycle likely requires integration tests with iSCSI helpers and kernel state.
