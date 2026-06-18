<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-mirror.yaml -->
# sources/control-plane/rook/deploy/examples/filesystem-mirror.yaml

Purpose: deploys a CephFS mirror daemon managed by Rook.
Important APIs/types/functions: `CephFilesystemMirror` `my-fs-mirror`, placement hooks, annotations, resource requests/limits, and optional priority class.
Control flow: Rook reconciles the mirror CR into cephfs-mirror daemon pods used for filesystem mirroring between clusters when peers/schedules are configured on filesystems. State is the mirror CR and daemon deployment status; mirrored data state is in Ceph. Dependencies are CephFS mirroring support, Rook operator, and any filesystem mirroring configuration elsewhere. Risks: this file alone does not configure peers or schedules, resource limits may need tuning, and placement is mostly commented. Test signals: mirror pod Running, Ceph reports mirror daemon, and configured mirrored filesystems show healthy replay/sync.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-mirror.yaml -->
