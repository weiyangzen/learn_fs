# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/terminal.go

## Purpose
`terminal.go` implements websocket-backed pod log streaming, shell exec, mount access log viewing, JuiceFS debug/warmup/stats commands, and debug file download.

## Important APIs, Types, And Functions
Methods include `WatchPodLogs`, `ExecPod`, `WatchMountPodAccessLog`, `DebugPod`, `WarmupPod`, `StatsPod`, and `DownloadDebugFile`.

## Control Flow
Each websocket method upgrades the request, creates a cancellable context and terminal/log pipe, fetches the target pod when mount path resolution is needed, determines sidecar vs mount-pod mount paths, then calls `resource.ExecInPod` or Kubernetes log streaming. Warmup builds a `juicefs warmup` command from query params and adds enterprise-only retry flags for non-CE pods. Debug runs `juicefs debug` into `/debug`; stats runs `juicefs stats`; download streams the latest `/debug/*.zip` from the container.

## State And Persistence
Runtime state is websocket sessions and remote processes inside target pods. `DebugPod` creates files inside the pod at `/debug`; `DownloadDebugFile` reads those files. No local persistent state is created here.

## Dependencies And Integration Points
It depends on `resource.NewTerminalSession`, `resource.ExecInPod`, `resource.DownloadPodFile`, `utils.NewLogPipe`, `util.GetMountPathOfPod`, `util.GetMountPathOfSidecar`, `util.GetJfsInternalFileName`, and Kubernetes pod/log APIs.

## Risks
Query parameters are passed directly as command arguments; they are not shell-interpolated except access-log `cat`, but validation would still improve UX and safety. The access-log command concatenates a path into `sh -c`, relying on trusted mount paths/internal names. These operations require high Kubernetes privileges and should be protected by external authorization.

## Test Signals
No tests are present. Valuable tests would validate command construction for sidecar/non-sidecar pods, CE vs non-CE warmup flags, and error handling for missing mount paths.
