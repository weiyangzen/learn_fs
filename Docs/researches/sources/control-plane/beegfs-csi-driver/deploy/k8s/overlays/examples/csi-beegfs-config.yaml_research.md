<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-config.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-config.yaml

Purpose: example BeeGFS CSI plugin configuration for Kustomize overlays, showing default, file-system-specific, node-specific, and node-plus-file-system-specific override shapes.

Important APIs and flow: this YAML maps to the driver's `PluginConfigFromFile` contract: top-level `config`, `fileSystemSpecificConfigs`, and `nodeSpecificConfigs`. `BeegfsConfig` fields include `grpcPort`, `connInterfaces`, `connNetFilter`, `connTcpOnlyFilter`, `connRDMAInterfaces`, and string-valued `beegfsClientConf` entries such as `connMgmtdPortTCP`, `connUseRDMA`, and `connTCPFallbackEnabled`. The runtime flow is precedence-driven: defaults apply broadly, file-system entries override by `sysMgmtdHost`, node entries override on matching nodes, and nested node file-system entries override both.

State and persistence: this file is consumed as configuration, typically rendered into a ConfigMap/Secret-backed deployment path by overlays or the operator. No Kubernetes object is declared directly.

Dependencies and integration points: depends on BeeGFS client config keys, BeeGFS 7.3+ for `connRDMAInterfaces`/TCP fallback, BeeGFS 8+ management gRPC port semantics, and deployment overlay wiring.

Risks and test signals: editing the example in place has no effect unless copied into an active overlay. Numeric and boolean BeeGFS client values must stay quoted strings. Test by deploying an overlay and checking node/controller driver logs for parsed config and successful mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-config.yaml -->
