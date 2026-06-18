<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/tools/Makefile -->
## sources/control-plane/ceph-csi/tools/Makefile

Purpose: provides a Make target for regenerating deployment YAML artifacts.

Behavior: phony `generate-deploy` depends on `yamlgen/main.go` and runs `go run yamlgen/main.go`.

State and persistence: generator writes deployment YAMLs under `deploy/`.

Dependencies: Go toolchain and yamlgen source dependencies.

Integration points: developer/release workflow for syncing generated manifests from API definitions.

Risks: running from the wrong working directory may affect relative output paths because yamlgen uses `../deploy/...`.

Test signals: no tests; generated file diff is the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/tools/Makefile -->
