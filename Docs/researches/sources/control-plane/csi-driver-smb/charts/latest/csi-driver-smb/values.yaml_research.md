## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/values.yaml

Purpose: defines the default configuration surface for the latest SMB CSI Helm chart. It controls image repositories/tags, service accounts, RBAC names, driver features, controller and node scheduling/resources, Linux/Windows modes, labels/annotations, priority class, security context, and optional StorageClasses.

Important values include sidecar tags for provisioner, resizer, liveness probe, registrar, CSI Proxy, `feature.enableGetVolumeStats`, `feature.enableInlineVolume`, controller metrics/liveness ports, Linux Kerberos cache settings, Windows HostProcess defaults, Windows remove-mapping behavior, and commented StorageClass examples with SMB source and credential references.

State is declarative input to all templates. Dependencies include image registry conventions where repositories beginning with `/` are joined with `baseRepo`, cluster support for HostProcess and RuntimeDefault seccomp, and sidecar CLI compatibility. Risks include mutable `canary` plugin tag, Windows enabled by default, privileged host mounts, and default `noserverino` guidance only in comments. Test signal is Helm lint/render/install across value combinations.
