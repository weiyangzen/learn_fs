<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/Dockerfile -->
## sources/control-plane/longhorn-engine/package/Dockerfile

Purpose: multi-stage container build for Longhorn Engine runtime image on SUSE BCI 15.7.

Important build steps: builder stage updates zypper, adds snappy and network utilities repos, installs build tools, clones `longhorn/dep-versions`, optionally checks out `SRC_TAG`, builds `liblonghorn` and TGT, and downloads `grpc_health_probe` selected by `ARCH`. release stage installs NFS/CIFS/iSCSI/network/qemu/e2fsprogs tools, copies TGT binaries and health probe from builder, copies `bin/longhorn`, `bin/longhorn-instance-manager`, and launch scripts, adds Tini, and defaults to `longhorn`.

Control flow and state: image build pulls remote repositories and release assets, so output depends on branch/tag arguments and external availability. Runtime entrypoint is `/tini --`, command `longhorn`.

Dependencies and integration points: integrates with `dep-versions` scripts, TGT, liblonghorn, `longhorn-instance-manager`, health checks, and launch scripts.

Risks: `grpc_health_probe` uses GitHub latest release at build time, reducing reproducibility. `SRC_BRANCH=master` default can drift. zypper repo availability and GPG import are external dependencies. The image includes storage tools with privileged runtime expectations.

Test signals: image build in CI, container start smoke tests, `grpc_health_probe` availability, and simple launch script tests are primary signals.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/Dockerfile -->
