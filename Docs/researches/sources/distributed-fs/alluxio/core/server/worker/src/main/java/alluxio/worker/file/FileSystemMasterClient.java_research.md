# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/file/FileSystemMasterClient.java

Purpose: Worker-side master client wrapper for file-system-master worker RPCs.

Important APIs: `getRemoteServiceType`, `getServiceName`, `getServiceVersion`, `afterConnect`, `getFileInfo`, `getPinList`, and `getUfsInfo`.

Control flow: After connecting, it creates a blocking gRPC stub. RPC methods use `retryRPC`; `getPinList` applies the configured worker-master periodic RPC deadline.

State and persistence: Holds the blocking stub after connect. No local persistence.

Dependencies and integration: Extends `AbstractMasterClient`; talks to `FileSystemMasterWorkerServiceGrpc`; used by worker components for pin lists, file info, and UFS mount info.

Risks and test signals: Stub is null before connection and refreshed after reconnect. Tests should cover retry wrapper behavior, deadline application for pin list, proto-to-wire conversion for file info, and service identity constants.
