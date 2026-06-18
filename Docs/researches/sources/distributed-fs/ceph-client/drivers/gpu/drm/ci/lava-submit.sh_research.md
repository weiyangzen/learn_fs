# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/lava-submit.sh

Purpose: prepares and submits a LAVA hardware test job for DRM CI, assembling the rootfs, kernel artifact overlay, optional firmware overlays, DUT environment variables, and structured job metadata.

Important behavior: sources `${FDO_CI_BASH_HELPERS}`, uses `fdo_find_s3_path "$LAVA_ROOTFS_PATH"` to locate a rootfs, creates `results/`, writes filtered environment variables to `dut-env-vars.sh`, appends `SCRIPTS_DIR=$CI_PROJECT_DIR/install`, tails `results/lava.log`, builds `LAVA_EXTRA_OVERLAYS` for optional firmware tarballs and mandatory `kernel-files.tar.zst`, then calls `lava-job-submitter` with farm, device type, boot method, timeout, rootfs, kernel URL prefix, DTB, env file, JWT file, kernel image details, visibility group, tags, Mesa job name, structured log path, SSH client image, project metadata, start section, and submit action.

Control flow: if rootfs lookup fails, the script emits a structured error and exits 1 before submission. The `tail -f` keeps LAVA log output streaming during submit.

State and persistence: writes `results/lava.log`, `results/lava_job_detail.json`, and `dut-env-vars.sh`; submits an external LAVA job; consumes S3 artifacts from build jobs.

Dependencies and integration points: depends on Mesa CI bash helpers, `lava-job-submitter`, MinIO/S3 paths, LAVA farm variables from `test.yml`, firmware variables from `image-tags.yml`, kernel artifacts uploaded by `build.sh`, and GitLab JWT file.

Risks: artifact lookup is time/order sensitive; the error text explicitly calls out missing dependencies. Word-splitting is intentionally allowed for several LAVA variables. Firmware overlay URLs are constructed from unvalidated names. A long-running `tail -f` is backgrounded and relies on job teardown to clean it.

Test signals: rootfs lookup success/failure, generated DUT env file excluding sensitive vars, overlay list with kernel and firmware, submitted LAVA YAML/log, structured job detail JSON, and correct timeout derived from `CI_JOB_TIMEOUT`.
