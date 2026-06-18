<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/Dockerfile -->
# sources/control-plane/ceph-csi/actions/retest/Dockerfile

Purpose: Docker image for the local retest GitHub Action.
Important surface: multi-stage build from `golang:1.25` by default, copies action source into `/home/src`, builds `retest` from `main.go` with `-mod=vendor`, then installs it into `/usr/local/bin/retest` in the runtime image.
Control flow/state: no runtime state other than executing the binary as ENTRYPOINT.
Dependencies/integration: used by `actions/retest/action.yaml` and tested by `test-retest-action.yaml`; depends on vendored Go modules.
Risks/test signals: runtime image includes full Go base instead of a minimal image; base image tag is mutable unless overridden. Docker build success is the main signal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/Dockerfile -->
