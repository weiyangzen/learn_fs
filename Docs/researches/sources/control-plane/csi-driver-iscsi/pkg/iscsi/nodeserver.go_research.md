## sources/control-plane/csi-driver-iscsi/pkg/iscsi/nodeserver.go

Purpose: implements CSI node operations for publishing and unpublishing iSCSI volumes.

Control flow validates volume capability, volume ID, and target path in `NodePublishVolume`, parses iSCSI info, constructs a disk mounter, and calls `ISCSIUtil.AttachDisk`. `NodeUnpublishVolume` validates volume ID/target path, constructs an unmounter, and calls `DetachDisk`. `NodeStageVolume` and `NodeUnstageVolume` are no-op successes; `NodeGetInfo` returns configured node ID; `NodeGetCapabilities` returns `UNKNOWN`; stats and expand are unimplemented.

State is host mount/session state through the util layer. Dependencies include CSI generated APIs and gRPC status codes. Risks include returning `Internal` for user attribute parse errors, no staging semantics despite CSI methods succeeding, no idempotency check beyond mountpoint detection, and unknown node capability. Test signal is csi-sanity and package tests; implementation lacks direct unit tests in this subset.
