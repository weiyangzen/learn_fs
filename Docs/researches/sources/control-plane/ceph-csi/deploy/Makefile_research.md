# sources/control-plane/ceph-csi/deploy/Makefile

Purpose: regeneration entrypoint for generated deploy manifests under `deploy/`.

Important APIs/types/functions: `all` depends on SCC, CephFS/NFS/RBD CSIDriver and config-map manifests, plus NFS provisioner RBAC. Each target depends on source files under `api/deploy/...` and runs `$(MAKE) -C ../tools generate-deploy`.

Control flow: any stale target invokes the central yaml generator rather than editing deploy YAML directly.

State and persistence behavior: updates generated YAML files in the deploy tree through the tools generator.

Dependencies and integration points: depends on API deploy sources and the `tools` make target. Comments in generated YAML point maintainers back to this pipeline.

Risks: several deploy files in this subset are generated and should not be modified directly. Target coverage is selective; not every manifest listed here has an explicit Makefile target.

Test signals: generator diffs, CI checks for generated manifests, and `make -C deploy all`.
