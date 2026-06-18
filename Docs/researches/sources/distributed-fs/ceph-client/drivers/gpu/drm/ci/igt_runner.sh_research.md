# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/igt_runner.sh

Purpose: runs IGT on the device under test, applying driver-specific xfail lists, sharding the generated CI test list, producing JUnit output, and converting lockdep failures into a special allowed-failure exit code.

Important behavior: the script sources Mesa CI `setup-test-env.sh`, exports `IGT_FORCE_DRIVER=$DRIVER_NAME`, extends `PATH` and `LD_LIBRARY_PATH` for `/igt`, dumps DRM debug state, optionally moves installed modules into `/lib/modules` and modprobes `amdgpu`, `vkms`, or `panthor`, loads skip/flake/fail baseline files from `/install/xfails/$DRIVER_NAME-$GPU_VERSION-*`, maps `uname -m` to artifact arch, downloads `${PIPELINE_ARTIFACTS_BASE}/$ARCH/igt.tar.gz` and extracts it to `/`, shards `/igt/libexec/igt-gpu-tools/ci-testlist.txt` using `CI_NODE_INDEX/CI_NODE_TOTAL`, ensures `core_getversion` is present, runs `igt-runner`, converts failures CSV to JUnit with `deqp-runner junit`, then checks `/proc/lockdep_stats` and returns 101 if lockdep disabled itself while tests otherwise passed.

Control flow: `set +e` surrounds IGT so reporting can still run. The final exit code is IGT's return unless lockdep overrides success to 101. Sharding uses in-place `sed -ni`.

State and persistence: writes results under `$RESULTS_DIR`, mutates `/lib/modules`, downloads/extracts `/igt`, edits the test list in place, and writes JUnit XML.

Dependencies and integration points: depends on Mesa setup scripts, `curl`, IGT archive from `build-igt.sh`, deqp-runner, module install artifacts, xfail files, GitLab sharding variables, and driver variables from `test.yml`.

Risks: `cd $oldpath` references a variable not set in this file; it may rely on sourced environment. Download uses `tar --zstd` on a `.tar.gz` filename, which assumes GNU tar auto-detect or a mismatched option tolerance. Missing xfail files are tolerated. Sharding and appending `core_getversion` can mutate shared test list if multiple runners share extraction, though jobs normally have isolated rootfs.

Test signals: successful module load for module-backed drivers, artifact download per architecture, xfail application, sharded test list includes `core_getversion`, JUnit artifact creation, and lockdep exit 101 path.
