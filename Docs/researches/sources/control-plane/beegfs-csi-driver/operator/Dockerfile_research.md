<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/Dockerfile -->
# sources/control-plane/beegfs-csi-driver/operator/Dockerfile

Purpose: packages the prebuilt BeeGFS CSI operator manager binary into a minimal distroless container.

Important APIs and flow: starts from `gcr.io/distroless/static:nonroot`, sets OCI labels, accepts `TARGETARCH`, copies `bin/manager$TARGETARCH` to `/manager`, runs as UID/GID 65532, and uses `/manager` as entrypoint. Build comments explain that binaries are built externally because the operator is inside the larger project module.

State and persistence: image contains only the manager binary and metadata; no writable state is declared.

Dependencies and integration points: depends on `make build` producing architecture-suffixed binaries and on buildx passing `TARGETARCH` for multi-arch builds.

Risks and test signals: missing `bin/manager$TARGETARCH` breaks image build; distroless limits debugging. Test with `make build`, `docker build`, and running manager health probes in cluster.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/Dockerfile -->
