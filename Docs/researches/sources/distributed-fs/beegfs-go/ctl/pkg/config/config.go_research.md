# sources/distributed-fs/beegfs-go/ctl/pkg/config/config.go

Purpose: provides the backend/global configuration and process-wide clients used by CTL as both CLI and library.

Important APIs/types/functions: config key constants; output type constants; `GlobalConfig`; `InitViperFromExternal`; `InitLoggerFromExternal`; `ManagementClient`; `BeeRemoteClient`; `BeeRemoteRegistry`; `BeeGFSClient`; `NodeStore`; `Cleanup`; `GetLogger`.

Control flow: external initialization binds a synthetic pflag set into Viper once and rejects later different configs. `ManagementClient` lazily reads TLS cert/auth, auto-discovers management address and auth file from mounted clients when configured as `auto`, then creates a cached gRPC management client. `BeeRemoteClient` reuses management auth secret and creates a cached BeeRemote gRPC client. `BeeGFSClient` lazily determines mounted/unmounted filesystem provider. `NodeStore` initializes once under a mutex by fetching nodes from management and converting protobuf IDs/NICs/root metadata. `GetLogger` lazily creates stderr logging or uses an external logger.

State and persistence: heavy process-global state: cached management client, BeeRemote client, BeeRemote registry, filesystem provider, node store, external-init flags, global config snapshot, and logger. It reads local files (`cert.pem`, auth file, procfs client config) but does not persist changes except setting Viper auth-file when auto-discovered.

Dependencies and integration points: central dependency for nearly every backend package. Integrates Viper, pflag, BeeGFS filesystem/procfs, gRPC client construction, registry feature discovery, BeeMsg node store, management protobuf APIs, logger, and OS/root checks.

Risks: global singleton state complicates tests and dynamic reconfiguration. `NodeStore` has a double-check pattern that reads `nodeStore` before taking the read lock, so race detector scrutiny is warranted. Auto-management discovery can fail with multiple mounts using different mgmtd addresses. BeeRemote access requires management access first. Unmounted BeeGFS mode requires root. `Cleanup` currently cleans node store and nils it, but other cached clients/registry/logger remain.

Test signals: no direct tests in this work item. High-value coverage would mock procfs, management responses, auth-file fallback, TLS cert failures, external initialization idempotency, unmounted root checks, and node-store concurrency.
