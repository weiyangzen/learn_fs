<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/smb.go

Purpose: Defines the SMB CSI `Driver`, deployment options, driver initialization, CSI capability registration, Kubernetes client setup, and common helper functions used by controller and node paths.

Important APIs/types/functions: `DriverOptions` carries node identity, driver name, stats cache settings, Windows unmount behavior, working mount dir, Kerberos cache settings, default delete policy, Windows HostProcess mode, and kubeconfig path. `Driver` embeds `csicommon.CSIDriver` and CSI unimplemented server structs, then stores the mounter, volume lock map, caches, Kubernetes client, and feature flags. `NewDriver` constructs caches, normalizes Kerberos defaults, initializes `volumeLocks`, and tries to create a Kubernetes client from `getKubeConfig`. `Run` logs version metadata, creates the safe mounter, registers controller/node capabilities, starts a non-blocking gRPC server, and waits. Helper functions include `GetUserNamePasswordFromSecret`, `IsCorruptedDir`, `getMountOptions`, `hasGuestMountOptions`, case-insensitive `setKeyValueInMap`, `replaceWithMap`, `validateOnDeleteValue`, `appendMountOptions`, `getRootDir`, kubeconfig helpers, `inClusterConfig`, and `validatePath`.

Control flow: Driver construction is tolerant of kubeconfig/client creation failures and logs warnings instead of aborting. `Run` is stricter and fatal-exits if version metadata or mounter creation fails. `inClusterConfig` mirrors Kubernetes client-go logic while adjusting service account token/CA paths for Windows HostProcess by prefixing `CONTAINER_SANDBOX_MOUNT_POINT`.

State and persistence behavior: The driver keeps in-memory timed caches for volume stats and deletion records using Azure cloud-provider cache utilities. Kubernetes secrets are read live through `kubeClient`; no secret material is persisted here. Path validation is stateless and rejects any slash- or backslash-separated segment equal to `..`.

Dependencies and integration points: Integrates CSI spec types, the repo's `csi-common` server, `pkg/mounter`, Kubernetes client-go, klog, mount-utils, and `sigs.k8s.io/cloud-provider-azure/pkg/cache`. Constants define StorageClass/volume context keys consumed by controller/node code and by e2e manifests.

Risks: `appendMountOptions` treats any option with a prefix matching a key as already included, so keys that are prefixes of other options can suppress intended additions. `NewDriver` can return a driver with nil `kubeClient`, which is valid for many paths but makes secret-backed ephemeral volume staging fail. `validatePath` blocks literal `..` segments but does not canonicalize SMB server/share semantics beyond segment splitting.

Test signals: `smb_test.go` covers constructor, run, helper functions, kubeconfig parsing, secret nil-client behavior, and path traversal validation. Node tests exercise constants and helpers indirectly in staging/publishing.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb.go -->
