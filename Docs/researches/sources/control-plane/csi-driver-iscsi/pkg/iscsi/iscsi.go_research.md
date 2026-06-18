## sources/control-plane/csi-driver-iscsi/pkg/iscsi/iscsi.go

Purpose: parses CSI `NodePublishVolumeRequest` attributes into iSCSI connection structures and builds mounter/unmounter objects.

Important APIs include `getISCSIInfo`, `buildISCSIConnector`, `getISCSIDiskMounter`, `getISCSIDiskUnmounter`, `portalMounter`, `parseSecret`, `parseSessionSecret`, `parseDiscoverySecret`, and structs `iscsiDisk`, `iscsiDiskMounter`, `iscsiDiskUnmounter`. Control flow requires `targetPortal`, `iqn`, and `lun`; parses optional JSON `secret` and `portals`; defaults portals to port 3260; converts LUN; and builds a Kubernetes `SafeFormatAndMount`, exec interface, device handler, and iscsilib connector.

State is request-derived only. Dependencies include CSI request fields, `pkg/iscsilib`, Kubernetes mount/device utilities, JSON, strconv, and exec. Risks include secrets passed via volume context instead of CSI secrets, parseSecret silently returning nil on invalid JSON, CHAP booleans not gating required secret fields, no block-volume support, and portal strings detected by any colon which can mis-handle IPv6. Test signal is indirect via node publish and sanity tests.
