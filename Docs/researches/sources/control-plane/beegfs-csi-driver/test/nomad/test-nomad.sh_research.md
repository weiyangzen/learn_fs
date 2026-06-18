<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/nomad/test-nomad.sh -->
# sources/control-plane/beegfs-csi-driver/test/nomad/test-nomad.sh

Purpose: automated Nomad smoke test for deploying and removing BeeGFS CSI controller, node service, volume, and a consuming job.
Important APIs/functions: parses `<directory> [start|stop]`, uses `CONTAINER_DRIVER` defaulting to docker, optional `CSI_CONTAINER_IMAGE` substitution via sed, `nomad job run`, `nomad plugin status`, `nomad volume create/delete`, and `nomad job stop -purge`.
Control flow/state: start deploys controller and node jobs, polls controller and node health counts for up to 30 seconds each, creates a volume, and launches the test job with podman substitution when requested. stop tears down job, volume, controller, and node service. With no second arg it performs both.
Dependencies/integration: requires `NOMAD_ADDR`, `NOMAD_CACERT`, nomad CLI, docker/podman job files, `volume.hcl`, and local `job.nomad`.
Risks/test signals: many variable expansions are unquoted; health polling assumes numeric plugin status output; existing Nomad artifacts can make the script fail. Healthy plugin counts and successful volume/job operations are the signals.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/nomad/test-nomad.sh -->
