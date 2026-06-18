# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_viewlog.h

Purpose: Defines view-log state and declares service/server log viewer entry points.

Important APIs/types: `SVC_VIEWLOG_PACKET` contains service/server identities, remote and local file paths, and download attempt count. `Services_ShowServiceLog` and `Services_ShowServerLog` open modeless log viewers.

Control flow/state: Packet state drives discovery, download, display, and cleanup in the implementation.

Dependencies/integration: Used from service properties and server commands.

Risks/test signals: `fTriedDownload` is defined but unused by the implementation, while `nDownloadAttempts` is authoritative.
