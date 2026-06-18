<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/tools/yamlgen/main.go -->
## sources/control-plane/ceph-csi/tools/yamlgen/main.go

Purpose: generates checked-in Kubernetes/OpenShift deployment YAMLs from Go API defaults.

APIs and control flow: `yamlArtifacts` lists output filenames, YAML constructor functions, and defaults for OCP SCC, CephFS/NFS/RBD CSI drivers and config maps/RBAC. `main` iterates artifacts. `writeArtifact` creates parent dirs, creates/truncates output file, writes a generated-file header, invokes the constructor via reflection with defaults, and writes returned YAML, panicking on failures or empty output.

State and persistence: writes files under `../deploy/...` relative to `tools/yamlgen`.

Dependencies: Ceph-CSI API deploy packages, `reflect`, `os`, path handling.

Integration points: `tools/Makefile generate-deploy` and release manifest maintenance.

Risks: reflection hides compile-time function signature checking for artifact entries. `os.Create` truncates outputs before validating generated YAML. Directory mode is `0775` despite gosec note because generated files are public.

Test signals: no unit tests; generated manifest diffs and build compile are validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/tools/yamlgen/main.go -->
