<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.h -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.h

Source path: `sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.h`

## Purpose
Defines the public extension contract for blobfuse/blobfuse2 extension modules using FUSE2 `FUSE_USE_VERSION 29`.

## Important APIs, Types, And Functions
Functions/prototypes: none declared. Includes: `stddef.h`, `stdio.h`, `fuse.h`. Defines: `__EXTENSION_H__`, `FUSE_USE_VERSION`.

## Control Flow
The header exposes the handshake, initialization, FUSE callback registration, and backend storage callback registration functions. It also declares a global `struct fuse_operations storage_callbacks` that extension handlers use to call back into the storage implementation.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stddef.h`, `stdio.h`, `fuse.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
The global callback declaration in a header can create multiple definitions if included in more than one compilation unit without external linkage controls. ABI compatibility depends on matching the exact libfuse version and `struct fuse_operations` layout expected by the loader.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.c -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.c

Source path: `sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.c`

## Purpose
Implements the sample FUSE3 extension callback layer. Each `ext_*` function logs the operation and forwards it to the `storage_callbacks` table supplied by blobfuse/blobfuse2, with one explicit filter that hides `/subtree.sh` by returning `-ENOENT` from `ext_getattr`.

## Important APIs, Types, And Functions
Functions/prototypes: `ext_init`, `ext_destroy`, `ext_statfs`, `ext_getattr`, `ext_opendir`, `ext_releasedir`, `ext_readdir`, `ext_mkdir`, `ext_rmdir`, `ext_open`, `ext_create`, `ext_read`, `ext_write`, `ext_flush`, `ext_truncate`, `ext_release`, `ext_unlink`, `ext_rename`, plus 5 more. Includes: `stdio.h`, `stdlib.h`, `syslog.h`, `errno.h`, `string.h`, `extension3.h`. Defines: none declared.

## Control Flow
Runtime flow is extension entrypoint to callback handler to stored backend operation: `extension3.c` registers these functions into a `struct fuse_operations`, blobfuse calls them through libfuse, and the handlers delegate to the original storage callbacks. `ext_init` and `ext_destroy` include extra presence checks, while most file, directory, symlink, sync, and chmod handlers assume the corresponding backend callback is populated.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stdio.h`, `stdlib.h`, `syslog.h`, `errno.h`, `string.h`, `extension3.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
Several delegated callbacks are called without null checks; an incomplete storage callback table can crash the process. The `/subtree.sh` filter is hard-coded and should be treated as test behavior rather than a general policy engine. Because all state is a global callback table, concurrent extension instances would share backend pointers.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.h -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.h

Source path: `sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.h`

## Purpose
Declares the FUSE3 callback-handler functions implemented by the sample extension.

## Important APIs, Types, And Functions
Functions/prototypes: `ext_destroy`, `ext_statfs`, `ext_getattr`, `ext_opendir`, `ext_releasedir`, `ext_readdir`, `ext_mkdir`, `ext_rmdir`, `ext_open`, `ext_create`, `ext_read`, `ext_write`, `ext_flush`, `ext_truncate`, `ext_release`, `ext_unlink`, `ext_rename`, `ext_symlink`, plus 4 more. Includes: `stddef.h`, `stdio.h`, `fuse3/fuse.h`. Defines: `__CALLBACK_HANDLERS_H__`, `FUSE_USE_VERSION`.

## Control Flow
The exported `ext_*` prototypes mirror the supported FUSE operation subset: lifecycle, stat/getattr, directory operations, file open/create/read/write/flush/truncate/release, unlink/rename, symlink/readlink, fsync/fsyncdir, and chmod. `extension3.c` imports this header to populate the operation table.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stddef.h`, `stdio.h`, `fuse3/fuse.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
Prototype compatibility is tied to FUSE3 signatures, especially `readdir`, `rename`, and `truncate`. Any mismatch with the libfuse headers used by blobfuse2 would fail at build time or produce unsafe callback dispatch.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.c -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.c

Source path: `sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.c`

## Purpose
Provides the FUSE3 sample extension entrypoints that blobfuse2 loads from a shared object or static library.

## Important APIs, Types, And Functions
Functions/prototypes: `validate_signature`, `init_extension`, `register_fuse_callbacks`, `register_storage_callbacks`. Includes: `stdio.h`, `stdlib.h`, `syslog.h`, `string.h`, `extension3.h`, `callback_handler.h`. Defines: none declared.

## Control Flow
`validate_signature` compares the launcher token with `ola-amigo-3!!`, sets global `signature_verified`, and returns the extension token. `register_fuse_callbacks` refuses registration until the handshake passes, then fills a FUSE operation table with `ext_*` handlers. `register_storage_callbacks` stores blobfuse's callback table in the global `storage_callbacks` value.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stdio.h`, `stdlib.h`, `syslog.h`, `string.h`, `extension3.h`, `callback_handler.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
The handshake is a fixed string check, not cryptographic authentication. `signature_verified` and `storage_callbacks` are process globals, so reloads or multiple consumers can overwrite shared state. `init_extension` only logs the config path and does not validate or persist configuration.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.h -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.h

Source path: `sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.h`

## Purpose
Defines the public extension contract for blobfuse/blobfuse2 extension modules using FUSE3 `FUSE_USE_VERSION 35`.

## Important APIs, Types, And Functions
Functions/prototypes: none declared. Includes: `stddef.h`, `stdio.h`, `fuse3/fuse.h`. Defines: `__EXTENSION3_H__`, `FUSE_USE_VERSION`.

## Control Flow
The header exposes the handshake, initialization, FUSE callback registration, and backend storage callback registration functions. It also declares a global `struct fuse_operations storage_callbacks` that extension handlers use to call back into the storage implementation.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stddef.h`, `stdio.h`, `fuse3/fuse.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
The global callback declaration in a header can create multiple definitions if included in more than one compilation unit without external linkage controls. ABI compatibility depends on matching the exact libfuse version and `struct fuse_operations` layout expected by the loader.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/build_kernel.sh -->
# sources/user-network-fs/blobfuse2/test/longhaul/build_kernel.sh

Source path: `sources/user-network-fs/blobfuse2/test/longhaul/build_kernel.sh`

## Purpose
Builds a specified Linux kernel version on top of a blobfuse-mounted path to stress long-running compile and filesystem workloads.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `version`. External commands observed: `git`, `wget`, `make`, `apt`, `apt-get`.

## Control Flow
Installs build dependencies, changes to the supplied mount path, downloads a kernel tarball, extracts it, runs `make defconfig`, and builds with `make`.

## State And Persistence
Creates and mutates a full kernel source tree under the caller-provided path.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Runs package installation and large downloads/builds without `set -e`; partial failures can continue and consume significant mount capacity.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/build_kernel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/longhaul.sh -->
# sources/user-network-fs/blobfuse2/test/longhaul/longhaul.sh

Source path: `sources/user-network-fs/blobfuse2/test/longhaul/longhaul.sh`

## Purpose
Longhaul watchdog and workload script for continuously validating blobfuse2 with periodic kernel builds.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `SERVICE`, `SCRIPT`, `WORKDIR`. External commands observed: `blobfuse2`, `blobfuse`, `mail`, `top`, `ps`.

## Control Flow
If blobfuse2 is running, a lock file gates one test run that logs memory/elapsed time, removes old mount data, builds a kernel under `/blob_mnt/kernel`, copies logs to the mount, and clears the lock. If blobfuse2 is down, it unmounts/remounts with MSI auth and sends a restart email.

## State And Persistence
Mutates `/blob_mnt`, local logs, `longhaul.lock`, environment variables, and live mount state.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Hard-coded account/client IDs, paths, email address, and broad deletes make this host-specific and unsafe outside the intended longhaul VM.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/longhaul.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/stresstest.sh -->
# sources/user-network-fs/blobfuse2/test/longhaul/stresstest.sh

Source path: `sources/user-network-fs/blobfuse2/test/longhaul/stresstest.sh`

## Purpose
GNU parallel stress workload that creates, reads, and deletes many files on a hard-coded blobfuse mount.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `parallel`.

## Control Flow
Creates 500 50 MB files from random data with 20-way parallelism, reads each file through `hexdump`, then removes the files. Medium and large profiles are present but commented out.

## State And Persistence
Writes and removes `myfile_small_*` data under `/home/vibhansa/blob_mnt2`.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Hard-coded paths and heavy random-data generation can saturate disk, network, and storage accounts.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/stresstest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/telemetrytest.sh -->
# sources/user-network-fs/blobfuse2/test/longhaul/telemetrytest.sh

Source path: `sources/user-network-fs/blobfuse2/test/longhaul/telemetrytest.sh`

## Purpose
Loops through telemetry settings, remounts blobfuse2, and runs the longhaul stress test for each setting.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `blobfuse2`.

## Control Flow
For each line in the supplied file, it cleans mount and ramdisk paths, unmounts all blobfuse2 mounts, mounts with `--telemetry=<line>`, logs the pid, runs `stresstest.sh`, then sleeps before the next run.

## State And Persistence
Continuously mutates `~/blob_mnt2`, `/mnt/ramdisk`, blobfuse2 mount state, and `longhaul2.log`.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Infinite outer loop and `rm -rf` on shell-expanded dotfiles require a controlled test host.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/telemetrytest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/mlperf/checkpoint.sh -->
# sources/user-network-fs/blobfuse2/test/mlperf/checkpoint.sh

Source path: `sources/user-network-fs/blobfuse2/test/mlperf/checkpoint.sh`

## Purpose
MLPerf Storage helper for preparing or running benchmark workloads against a blobfuse-mounted path.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `OMPI_MCA_btl_tcp_if_include`, `MOUNT_PATH`, `BENCHMARK_RESULTS`, `START_HOST_INDEX`, `COUNT`, `EXCLUDE_LIST`, `NUM_HOSTS`. External commands observed: `mlpstorage`.

## Control Flow
Builds a comma-separated host list from `ccw-hpc-*` host indexes while honoring an exclude list, then runs `mlpstorage checkpointing run` with benchmark-specific model, memory, mount, and result settings.

## State And Persistence
Writes benchmark output under `~/mlperf/benchmark_results` and reads/writes workload data under `/mnt/blob_mnt`.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Assumes a specific HPC host naming scheme, OpenMPI network interface, large memory, and pre-mounted blobfuse path.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/mlperf/checkpoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/mlperf/setup.sh -->
# sources/user-network-fs/blobfuse2/test/mlperf/setup.sh

Source path: `sources/user-network-fs/blobfuse2/test/mlperf/setup.sh`

## Purpose
MLPerf Storage helper for preparing or running benchmark workloads against a blobfuse-mounted path.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `REPO_PATH`. External commands observed: `python3`, `python`, `git`, `apt`, `mlpstorage`.

## Control Flow
Installs Python/OpenMPI prerequisites, creates a virtualenv, clones MLCommons storage v2.0 if missing, installs it editable, and verifies `mlpstorage`.

## State And Persistence
Creates `~/.venvs/myenv` and `~/mlperf/storage`, and installs Python dependencies.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Assumes a specific HPC host naming scheme, OpenMPI network interface, large memory, and pre-mounted blobfuse path.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/mlperf/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/mlperf/train.sh -->
# sources/user-network-fs/blobfuse2/test/mlperf/train.sh

Source path: `sources/user-network-fs/blobfuse2/test/mlperf/train.sh`

## Purpose
MLPerf Storage helper for preparing or running benchmark workloads against a blobfuse-mounted path.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `OMPI_MCA_btl_tcp_if_include`, `MOUNT_PATH`, `BENCHMARK_RESULTS`, `START_HOST_INDEX`, `COUNT`, `EXCLUDE_LIST`, `NUM_HOSTS`. External commands observed: `mlpstorage`.

## Control Flow
Builds a comma-separated host list from `ccw-hpc-*` host indexes while honoring an exclude list, then runs `mlpstorage training run` with benchmark-specific model, memory, mount, and result settings.

## State And Persistence
Writes benchmark output under `~/mlperf/benchmark_results` and reads/writes workload data under `/mnt/blob_mnt`.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Assumes a specific HPC host naming scheme, OpenMPI network interface, large memory, and pre-mounted blobfuse path.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/mlperf/train.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/mount_test/mount_test.go -->
# sources/user-network-fs/blobfuse2/test/mount_test/mount_test.go

Source path: `sources/user-network-fs/blobfuse2/test/mount_test/mount_test.go`

## Purpose
End-to-end Go test suite for the `blobfuse2 mount`, `mount list`, and `unmount all` CLI surfaces.

## Important APIs, Types, And Functions
Package functions: `remountCheck`, `listBlobfuseMounts`, `blobfuseUnmount`, `TestMountCmd`, `TestMountDirNotExists`, `TestMountDirNotEmptyFailure`, `TestMountDirNotEmptySuccess`, `TestMountPathNotProvided`, `TestConfigFileNotProvided`, `TestEnvVarMountFailure`, `TestEnvVarMount`, `mountAndValidate`, `TestWriteBackCacheAndIgnoreOpenFlags`, `TestMountSuite`, `TestMain`. Types: `mountSuite`. Imports: `bytes`, `crypto/rand`, `flag`, `fmt`, `os`, `os/exec`, `path/filepath`, `testing`, `time`, `github.com/spf13/viper`, `github.com/stretchr/testify/suite`.

## Control Flow
The suite invokes the configured binary with `os/exec`, checks success and error messages, waits for FUSE mount stabilization, lists active mounts, verifies remount rejection, and cleans up with global unmount. `TestMain` wires flags for binary path, mount directory, config file, and tags.

## State And Persistence
Mutates the real mount directory, temporary cache directories, process environment variables for Azure auth, and live blobfuse2 mount state. The tests rely on sleeps and global unmounts to settle asynchronous FUSE teardown.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/suite`, `os/exec` calls to the blobfuse2 CLI, real mount directories, environment variables, and active FUSE mount state.

## Risks
High integration-test risk: failures can leave mounts behind, hard-coded error text can drift, and global `unmount all` can affect unrelated blobfuse2 mounts on the same host.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/mount_test/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/perf_test/generate_perf_report.py -->
# sources/user-network-fs/blobfuse2/test/perf_test/generate_perf_report.py

Source path: `sources/user-network-fs/blobfuse2/test/perf_test/generate_perf_report.py`

## Purpose
Compares a current performance JSON report with a base report and emits regression/improvement signals.

## Important APIs, Types, And Functions
Functions: `compare_numbers`. Classes: none declared. Imports: `json`, `argparse`, `sys`, `os`, `math`.

## Control Flow
`argparse` collects current/base/report paths, JSON is loaded, numeric values are compared with `compare_numbers`, and output is printed or written in a report-friendly format.

## State And Persistence
Reads JSON input files and may write a generated comparison report; no durable application state.

## Dependencies And Integration Points
Integrates with Python runtime packages, benchmark datasets, mounted filesystem paths, and JSON/Parquet/report artifacts used by blobfuse2 performance experiments.

## Risks
Comparison quality depends on stable JSON schema and numeric parsing. Threshold logic can hide non-numeric regressions.

## Test Signals
Signals are successful script exit, valid generated JSON/Parquet/report files, timing metrics, and absence of unexpected read/classification/data-generation exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/perf_test/generate_perf_report.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/perf_test/resnet50_classify.py -->
# sources/user-network-fs/blobfuse2/test/perf_test/resnet50_classify.py

Source path: `sources/user-network-fs/blobfuse2/test/perf_test/resnet50_classify.py`

## Purpose
TensorFlow ResNet50 image classification workload for measuring mounted-image read performance.

## Important APIs, Types, And Functions
Functions: `classify_images`, `chunks`. Classes: none declared. Imports: `os`, `sys`, `time`, `json`, `argparse`, `numpy`, `multiprocessing.*`, `tensorflow.keras.applications.*`, `tensorflow.keras.preprocessing.image.*`, `tensorflow.keras.preprocessing.image.*`, `tensorflow.keras.applications.imagenet_utils.*`.

## Control Flow
Parses arguments, partitions image files into chunks, uses multiprocessing workers to load/preprocess images, runs ResNet50 classification, and records timing/summary output.

## State And Persistence
Reads images from the target path and writes timing/report JSON or stdout summaries; model weights may be cached by TensorFlow/Keras.

## Dependencies And Integration Points
Integrates with Python runtime packages, benchmark datasets, mounted filesystem paths, and JSON/Parquet/report artifacts used by blobfuse2 performance experiments.

## Risks
Requires TensorFlow, NumPy, enough memory, and model download/cache availability. GPU/CPU differences and image cache effects can dominate filesystem measurements.

## Test Signals
Signals are successful script exit, valid generated JSON/Parquet/report files, timing metrics, and absence of unexpected read/classification/data-generation exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/perf_test/resnet50_classify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/create_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/create_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/create_test.go`

## Purpose
Scenario-level filesystem semantics test for `create` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestFileCreate`. Types: none declared. Imports: `os`, `path/filepath`, `testing`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/fsync_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/fsync_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/fsync_test.go`

## Purpose
Scenario-level filesystem semantics test for `fsync` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestFsync`, `TestFsyncWhileWriting`, `TestParallelFsyncCalls`, `TestParallelFsyncCallsByDuping`. Types: none declared. Imports: `crypto/rand`, `fmt`, `io`, `os`, `path/filepath`, `sync`, `syscall`, `testing`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/fsync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/init_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/init_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/init_test.go`

## Purpose
Scenario-level filesystem semantics test for `init` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `calculateMD5`, `checkFileIntegrity`, `removeFiles`, `expandPath`, `TestMain`. Types: none declared. Imports: `crypto/md5`, `encoding/hex`, `flag`, `io`, `os`, `os/user`, `path/filepath`, `strings`, `testing`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/init_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/mmap_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/mmap_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/mmap_test.go`

## Purpose
Scenario-level filesystem semantics test for `mmap` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestMmapReadWrite`, `TestMmapLargeFileRead`, `TestMmapWithMsync`, `TestMmapAfterFileClose`. Types: none declared. Imports: `os`, `path/filepath`, `syscall`, `testing`, `github.com/stretchr/testify/assert`, `golang.org/x/sys/unix`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/mmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/o_trunc_flag_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/o_trunc_flag_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/o_trunc_flag_test.go`

## Purpose
Scenario-level filesystem semantics test for `o_trunc_flag` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestOTruncFlag`, `TestOTruncWhileWriting`, `OTruncWhileWritingHelper`, `TestOTruncWhileReading`, `OTruncWhileReadingHelper`. Types: none declared. Imports: `crypto/rand`, `io`, `os`, `path/filepath`, `testing`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/o_trunc_flag_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/open_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/open_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/open_test.go`

## Purpose
Scenario-level filesystem semantics test for `open` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestFileOpen`. Types: none declared. Imports: `os`, `path/filepath`, `testing`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/open_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/read_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/read_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/read_test.go`

## Purpose
Scenario-level filesystem semantics test for `read` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestFileRead`, `TestStripeReading`, `TestStripeReadingWithDup`, `TestReadingUncommittedData`. Types: none declared. Imports: `crypto/rand`, `io`, `os`, `path/filepath`, `syscall`, `testing`, `time`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/read_write_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/read_write_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/read_write_test.go`

## Purpose
Scenario-level filesystem semantics test for `read_write` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestOpenWriteRead`, `TestReadWrittenData`, `TestWriteReadData`, `TestOpenWriteReadMultipleHandles`. Types: none declared. Imports: `crypto/rand`, `io`, `os`, `path/filepath`, `testing`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/read_write_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/truncate_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/truncate_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/truncate_test.go`

## Purpose
Scenario-level filesystem semantics test for `truncate` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestFileTruncateSameSize`, `TestFileTruncateShrink`, `TestFileTruncateExpand`, `TestTruncateNoFile`, `TestWriteTruncateClose`, `TestWriteTruncateWriteClose`, `FileTruncate`. Types: none declared. Imports: `crypto/rand`, `fmt`, `io`, `os`, `path/filepath`, `sync`, `testing`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/truncate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/unlink_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/unlink_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/unlink_test.go`

## Purpose
Documents a not-yet-enabled unlink-on-open scenario.

## Important APIs, Types, And Functions
Package functions: none declared. Types: none declared. Imports: none declared.

## Control Flow
The only test body is commented out. It describes the desired behavior: deletion should be deferred while an open file handle remains readable, then a new file at the same path should be distinct after close.

## State And Persistence
No runtime state is currently mutated because the test is disabled.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
The TODO marks a known semantic gap; the absence of an active test means regressions or eventual support will not be caught until the test is re-enabled.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/unlink_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/write_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/write_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/write_test.go`

## Purpose
Scenario-level filesystem semantics test for `write` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestFileWrite`, `TestWrite10MB`, `TestStripeWriting`, `TestStripeWritingWithDup`, `TestRandSparseWriting`, `TestSparseWritingBlockOverlap`. Types: none declared. Imports: `crypto/rand`, `io`, `os`, `path/filepath`, `syscall`, `testing`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/write_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/coveragecheck.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/coveragecheck.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/coveragecheck.sh`

## Purpose
Developer utility for coverage gating or dependency graph inspection.

## Important APIs, Types, And Functions
Shell functions: `overall_check`, `file_check`. Key variables: none declared. External commands observed: none declared.

## Control Flow
`coveragecheck.sh` parses coverage reports and fails when overall coverage is below 80% or per-file coverage below 70%. `depends.sh` builds `go mod graph` output and recursively prints reverse dependency sources for a requested module.

## State And Persistence
Reads generated coverage or Go module graph files and writes temporary graph files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Parsing is format-sensitive and uses shell arithmetic/string processing that can fail on unexpected report values.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/coveragecheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/cpp3run.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/cpp3run.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/cpp3run.sh`

## Purpose
Ad hoc mount/stress runner for repeated blobfuse/blobfuse2 validation.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `blobfuse`, `fusermount`.

## Control Flow
Unmounts or prepares mount/cache directories, mounts a configured blobfuse version, runs test scripts or Go tests repeatedly, logs output, and unmounts before the next iteration.

## State And Persistence
Mutates user home mount paths, `/mnt/ramdisk`, log files, and live FUSE state.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Host-specific absolute paths, broad cleanup commands, and looped execution require isolation.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/cpp3run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/cppparrun.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/cppparrun.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/cppparrun.sh`

## Purpose
Performance comparison harness for blobfuse/blobfuse2 workloads.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `mntPath`, `tmpPath`, `config`, `outputPath`, `cnt`, `sed_line`. External commands observed: `blobfuse`, `fusermount3`, `ps`.

## Control Flow
The script prepares mount/tmp/output paths, mounts blobfuse variants with supplied configs, runs workload commands such as `fio`, `git clone`, or parallel read/write helpers, parses throughput/IOPS/timing output, writes Markdown-style result tables, and unmounts between runs.

## State And Persistence
Creates output report files, test data in the mount, temp-cache contents, and live FUSE mounts.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Relies on external binaries, fragile text parsing, `sed -i` table mutation, and unguarded cleanup of mount/tmp directories.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/cppparrun.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/depends.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/depends.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/depends.sh`

## Purpose
Developer utility for coverage gating or dependency graph inspection.

## Important APIs, Types, And Functions
Shell functions: `getSource`. Key variables: `level`. External commands observed: `go`.

## Control Flow
`coveragecheck.sh` parses coverage reports and fails when overall coverage is below 80% or per-file coverage below 70%. `depends.sh` builds `go mod graph` output and recursively prints reverse dependency sources for a requested module.

## State And Persistence
Reads generated coverage or Go module graph files and writes temporary graph files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Parsing is format-sensitive and uses shell arithmetic/string processing that can fail on unexpected report values.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/depends.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/file_block_compare.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/file_block_compare.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/file_block_compare.sh`

## Purpose
Performance comparison harness for blobfuse/blobfuse2 workloads.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `mntPath`, `tmpPath`, `fileConfigPath`, `blockConfigPath`, `dataPath`, `outputPath`, `outputPath`. External commands observed: `blobfuse2`, `fio`, `dd`.

## Control Flow
The script prepares mount/tmp/output paths, mounts blobfuse variants with supplied configs, runs workload commands such as `fio`, `git clone`, or parallel read/write helpers, parses throughput/IOPS/timing output, writes Markdown-style result tables, and unmounts between runs.

## State And Persistence
Creates output report files, test data in the mount, temp-cache contents, and live FUSE mounts.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Relies on external binaries, fragile text parsing, `sed -i` table mutation, and unguarded cleanup of mount/tmp directories.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/file_block_compare.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/file_edit_md5.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/file_edit_md5.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/file_edit_md5.sh`

## Purpose
File IO helper used by higher-level stress/performance scripts.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `list`. External commands observed: `parallel`, `md5sum`.

## Control Flow
The helper performs repeated reads/writes or checksum comparisons with caller-provided size/thread/path parameters, often using GNU parallel or Python threads to increase concurrency.

## State And Persistence
Creates, reads, modifies, or deletes local and mounted test files plus intermediate checksum/result files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Correctness depends on caller path isolation and consistent cache state; missing quoting and hard-coded paths can redirect writes unexpectedly.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/file_edit_md5.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/fio.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/fio.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/fio.sh`

## Purpose
Performance comparison harness for blobfuse/blobfuse2 workloads.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `mntPath`, `tmpPath`, `v2configPath`, `v1configPath`, `testname`, `outputPath`, `fiocmd`, `fiocmd`, `fiocmd`, `sed_line`, `blobfuse2_write_average`, `blobfuse2_read_average`, `sed_line`, `blobfuse_write_average`, `blobfuse_read_average`, `blobfuse2_write_average`, `blobfuse2_read_average`, `blobfuse_write_average`, plus 5 more. External commands observed: `blobfuse2`, `blobfuse`, `fusermount3`, `fio`, `ps`.

## Control Flow
The script prepares mount/tmp/output paths, mounts blobfuse variants with supplied configs, runs workload commands such as `fio`, `git clone`, or parallel read/write helpers, parses throughput/IOPS/timing output, writes Markdown-style result tables, and unmounts between runs.

## State And Persistence
Creates output report files, test data in the mount, temp-cache contents, and live FUSE mounts.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Relies on external binaries, fragile text parsing, `sed -i` table mutation, and unguarded cleanup of mount/tmp directories.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/fio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/fsync_sample.c -->
# sources/user-network-fs/blobfuse2/test/scripts/fsync_sample.c

Source path: `sources/user-network-fs/blobfuse2/test/scripts/fsync_sample.c`

## Purpose
Tiny command-line helper that opens a file, writes data, and calls `fsync` to exercise explicit flush behavior through a mount.

## Important APIs, Types, And Functions
Functions/prototypes: `main`. Includes: `stdio.h`, `stdlib.h`, `fcntl.h`, `sys/types.h`, `sys/stat.h`, `string.h`, `unistd.h`. Defines: none declared.

## Control Flow
The program validates arguments, opens the target with POSIX file APIs, writes the provided buffer, calls `fsync`, and exits with non-zero status on failure.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stdio.h`, `stdlib.h`, `fcntl.h`, `sys/types.h`, `sys/stat.h`, `string.h`, `unistd.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
It is intentionally minimal: no retry logic, limited diagnostics, and no verification that data reached remote storage beyond the local `fsync` return code.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/fsync_sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/git_clone.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/git_clone.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/git_clone.sh`

## Purpose
Performance comparison harness for blobfuse/blobfuse2 workloads.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `mntPath`, `tmpPath`, `v2configPath`, `v1configPath`, `outputPath`, `sed_line`, `blobfuse2_average`, `sed_line`, `blobfuse_average`, `blobfuse2_average`, `blobfuse_average`, `diff`, `percent`. External commands observed: `blobfuse2`, `blobfuse`, `fusermount3`, `git`, `ps`.

## Control Flow
The script prepares mount/tmp/output paths, mounts blobfuse variants with supplied configs, runs workload commands such as `fio`, `git clone`, or parallel read/write helpers, parses throughput/IOPS/timing output, writes Markdown-style result tables, and unmounts between runs.

## State And Persistence
Creates output report files, test data in the mount, temp-cache contents, and live FUSE mounts.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Relies on external binaries, fragile text parsing, `sed -i` table mutation, and unguarded cleanup of mount/tmp directories.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/git_clone.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/go3run.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/go3run.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/go3run.sh`

## Purpose
Ad hoc mount/stress runner for repeated blobfuse/blobfuse2 validation.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `blobfuse2`, `fusermount`.

## Control Flow
Unmounts or prepares mount/cache directories, mounts a configured blobfuse version, runs test scripts or Go tests repeatedly, logs output, and unmounts before the next iteration.

## State And Persistence
Mutates user home mount paths, `/mnt/ramdisk`, log files, and live FUSE state.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Host-specific absolute paths, broad cleanup commands, and looped execution require isolation.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/go3run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/goparrun.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/goparrun.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/goparrun.sh`

## Purpose
Performance comparison harness for blobfuse/blobfuse2 workloads.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `mntPath`, `tmpPath`, `config`, `outputPath`, `cnt`, `sed_line`. External commands observed: `blobfuse2`, `fusermount3`, `ps`.

## Control Flow
The script prepares mount/tmp/output paths, mounts blobfuse variants with supplied configs, runs workload commands such as `fio`, `git clone`, or parallel read/write helpers, parses throughput/IOPS/timing output, writes Markdown-style result tables, and unmounts between runs.

## State And Persistence
Creates output report files, test data in the mount, temp-cache contents, and live FUSE mounts.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Relies on external binaries, fragile text parsing, `sed -i` table mutation, and unguarded cleanup of mount/tmp directories.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/goparrun.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/multi_write.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/multi_write.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/multi_write.sh`

## Purpose
File IO helper used by higher-level stress/performance scripts.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `dd`.

## Control Flow
The helper performs repeated reads/writes or checksum comparisons with caller-provided size/thread/path parameters, often using GNU parallel or Python threads to increase concurrency.

## State And Persistence
Creates, reads, modifies, or deletes local and mounted test files plus intermediate checksum/result files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Correctness depends on caller path isolation and consistent cache state; missing quoting and hard-coded paths can redirect writes unexpectedly.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/multi_write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/overnight.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/overnight.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/overnight.sh`

## Purpose
Ad hoc mount/stress runner for repeated blobfuse/blobfuse2 validation.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `logFile`. External commands observed: `blobfuse`.

## Control Flow
Unmounts or prepares mount/cache directories, mounts a configured blobfuse version, runs test scripts or Go tests repeatedly, logs output, and unmounts before the next iteration.

## State And Persistence
Mutates user home mount paths, `/mnt/ramdisk`, log files, and live FUSE state.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Host-specific absolute paths, broad cleanup commands, and looped execution require isolation.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/overnight.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/overnightstress.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/overnightstress.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/overnightstress.sh`

## Purpose
Ad hoc mount/stress runner for repeated blobfuse/blobfuse2 validation.

## Important APIs, Types, And Functions
Shell functions: `unmount_fuse`, `mount_blobfuse`, `mount_blobfuse2`, `stress_test`. Key variables: `logFile`, `mntPath`, `tmpPath`, `blobfuse`, `blobfusecfg`. External commands observed: `blobfuse2`, `blobfuse`, `fusermount`.

## Control Flow
Unmounts or prepares mount/cache directories, mounts a configured blobfuse version, runs test scripts or Go tests repeatedly, logs output, and unmounts before the next iteration.

## State And Persistence
Mutates user home mount paths, `/mnt/ramdisk`, log files, and live FUSE state.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Host-specific absolute paths, broad cleanup commands, and looped execution require isolation.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/overnightstress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/parallel_batch_read.py -->
# sources/user-network-fs/blobfuse2/test/scripts/parallel_batch_read.py

Source path: `sources/user-network-fs/blobfuse2/test/scripts/parallel_batch_read.py`

## Purpose
Threaded batch-reader helper that repeatedly reads random files and hashes or validates content to create concurrent read pressure.

## Important APIs, Types, And Functions
Functions: `read_batch`. Classes: none declared. Imports: `os`, `threading`, `hashlib`, `datetime`, `random`.

## Control Flow
`read_batch` workers choose files, read data, and track timing/status while Python threads coordinate batches.

## State And Persistence
Reads mounted files and prints/logs timing; no intended writes.

## Dependencies And Integration Points
Integrates with Python runtime packages, benchmark datasets, mounted filesystem paths, and JSON/Parquet/report artifacts used by blobfuse2 performance experiments.

## Risks
Python threading, random selection, and OS page cache can make throughput noisy.

## Test Signals
Signals are successful script exit, valid generated JSON/Parquet/report files, timing metrics, and absence of unexpected read/classification/data-generation exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/parallel_batch_read.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/pread.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/pread.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/pread.sh`

## Purpose
File IO helper used by higher-level stress/performance scripts.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `thread`, `count`, `size`, `mntPath`, `outputPath`, `sed_line`, `start_time`, `end_time`, `time_diff`, `total_size`, `rate`. External commands observed: `parallel`, `dd`.

## Control Flow
The helper performs repeated reads/writes or checksum comparisons with caller-provided size/thread/path parameters, often using GNU parallel or Python threads to increase concurrency.

## State And Persistence
Creates, reads, modifies, or deletes local and mounted test files plus intermediate checksum/result files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Correctness depends on caller path isolation and consistent cache state; missing quoting and hard-coded paths can redirect writes unexpectedly.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/pread.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/profile-latency-hiding.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/profile-latency-hiding.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/profile-latency-hiding.sh`

## Purpose
Ad hoc mount/stress runner for repeated blobfuse/blobfuse2 validation.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `BLOBFUSE2_DIR`, `RAMDISK_DIR`. External commands observed: `blobfuse2`, `blobfuse`, `fusermount`.

## Control Flow
Unmounts or prepares mount/cache directories, mounts a configured blobfuse version, runs test scripts or Go tests repeatedly, logs output, and unmounts before the next iteration.

## State And Persistence
Mutates user home mount paths, `/mnt/ramdisk`, log files, and live FUSE state.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Host-specific absolute paths, broad cleanup commands, and looped execution require isolation.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/profile-latency-hiding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/pwrite.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/pwrite.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/pwrite.sh`

## Purpose
File IO helper used by higher-level stress/performance scripts.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `thread`, `count`, `size`, `mntPath`, `outputPath`, `sed_line`, `start_time`, `end_time`, `time_diff`, `total_size`, `rate`. External commands observed: `parallel`, `dd`.

## Control Flow
The helper performs repeated reads/writes or checksum comparisons with caller-provided size/thread/path parameters, often using GNU parallel or Python threads to increase concurrency.

## State And Persistence
Creates, reads, modifies, or deletes local and mounted test files plus intermediate checksum/result files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Correctness depends on caller path isolation and consistent cache state; missing quoting and hard-coded paths can redirect writes unexpectedly.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/pwrite.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/read.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/read.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/read.sh`

## Purpose
File IO helper used by higher-level stress/performance scripts.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `in_file`. External commands observed: `dd`.

## Control Flow
The helper performs repeated reads/writes or checksum comparisons with caller-provided size/thread/path parameters, often using GNU parallel or Python threads to increase concurrency.

## State And Persistence
Creates, reads, modifies, or deletes local and mounted test files plus intermediate checksum/result files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Correctness depends on caller path isolation and consistent cache state; missing quoting and hard-coded paths can redirect writes unexpectedly.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/read.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/readwrite.c -->
# sources/user-network-fs/blobfuse2/test/scripts/readwrite.c

Source path: `sources/user-network-fs/blobfuse2/test/scripts/readwrite.c`

## Purpose
Small C utility for repeated read/write timing through mounted storage.

## Important APIs, Types, And Functions
Functions/prototypes: `main`. Includes: `stdio.h`, `stdlib.h`, `time.h`, `unistd.h`. Defines: none declared.

## Control Flow
The utility loops over simple POSIX file operations and uses wall-clock timing to produce a throughput-oriented signal for scripts.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stdio.h`, `stdlib.h`, `time.h`, `unistd.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
The helper is benchmark scaffolding rather than a correctness oracle; OS cache effects and missing fsync semantics can skew results.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/readwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/rman_backup.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/rman_backup.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/rman_backup.sh`

## Purpose
Oracle RMAN backup or backup-simulation workload targeting a blobfuse-mounted backup directory.

## Important APIs, Types, And Functions
Shell functions: `setup_oracle_env`, `cleanup`, `run_sqlplus`, `run_rman`, `install_oracle_xe`, `create_tablespace`, `rman_full_backup`, `rman_incremental_backup`, `rman_backup_and_restore_verify`. Key variables: `MOUNT_POINT`, `DATA_DIR`, `SIZES`, `GREEN`, `RED`, `CYAN`, `NC`, `BACKUP_BASE`, `PASSED`, `FAILED`, `IFS`, `ARCHIVELOG_STATUS`. External commands observed: `blobfuse2`, `wget`, `sqlplus`, `rman`, `yum`.

## Control Flow
Defines setup/cleanup helpers, generates or backs up data at multiple sizes, runs full/incremental/multi-channel backup paths, verifies restore or checksum behavior, and reports pass/fail counters.

## State And Persistence
Mutates backup/source directories, Oracle environment/database state for the real RMAN script, and mounted blobfuse backup storage.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
The real RMAN script can install Oracle XE and operate on database files; hard-coded mount/data locations and privileged package operations make it unsuitable for casual execution.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/rman_backup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/rman_backup_simulation.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/rman_backup_simulation.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/rman_backup_simulation.sh`

## Purpose
Oracle RMAN backup or backup-simulation workload targeting a blobfuse-mounted backup directory.

## Important APIs, Types, And Functions
Shell functions: `cleanup`, `generate_datafile`, `full_backup`, `incremental_backup`, `multi_channel_backup`. Key variables: `MOUNT_POINT`, `DATA_DIR`, `SIZES`, `GREEN`, `RED`, `CYAN`, `NC`, `BACKUP_DIR`, `SOURCE_DIR`, `PASSED`, `FAILED`, `IFS`. External commands observed: `parallel`, `dd`, `md5sum`.

## Control Flow
Defines setup/cleanup helpers, generates or backs up data at multiple sizes, runs full/incremental/multi-channel backup paths, verifies restore or checksum behavior, and reports pass/fail counters.

## State And Persistence
Mutates backup/source directories, Oracle environment/database state for the real RMAN script, and mounted blobfuse backup storage.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
The real RMAN script can install Oracle XE and operate on database files; hard-coded mount/data locations and privileged package operations make it unsuitable for casual execution.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/rman_backup_simulation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/run.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/run.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/run.sh`

## Purpose
Performance comparison harness for blobfuse/blobfuse2 workloads.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `mntPath`, `tmpPath`, `v2configPath`, `v1configPath`, `v2blockconfigPath`, `outputPath`, `cnt`, `count`, `sed_line`, `totalWriteImprove`, `totalReadImprove`. External commands observed: `blobfuse2`, `blobfuse`, `fusermount3`.

## Control Flow
The script prepares mount/tmp/output paths, mounts blobfuse variants with supplied configs, runs workload commands such as `fio`, `git clone`, or parallel read/write helpers, parses throughput/IOPS/timing output, writes Markdown-style result tables, and unmounts between runs.

## State And Persistence
Creates output report files, test data in the mount, temp-cache contents, and live FUSE mounts.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Relies on external binaries, fragile text parsing, `sed -i` table mutation, and unguarded cleanup of mount/tmp directories.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/stresstest.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/stresstest.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/stresstest.sh`

## Purpose
Ad hoc mount/stress runner for repeated blobfuse/blobfuse2 validation.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `go`.

## Control Flow
Unmounts or prepares mount/cache directories, mounts a configured blobfuse version, runs test scripts or Go tests repeatedly, logs output, and unmounts before the next iteration.

## State And Persistence
Mutates user home mount paths, `/mnt/ramdisk`, log files, and live FUSE state.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Host-specific absolute paths, broad cleanup commands, and looped execution require isolation.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/stresstest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/write.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/write.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/write.sh`

## Purpose
File IO helper used by higher-level stress/performance scripts.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `size`, `out_file`, `curr_time`, `last_mod`, `upload_time`, `rate`. External commands observed: `dd`.

## Control Flow
The helper performs repeated reads/writes or checksum comparisons with caller-provided size/thread/path parameters, often using GNU parallel or Python threads to increase concurrency.

## State And Persistence
Creates, reads, modifies, or deletes local and mounted test files plus intermediate checksum/result files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Correctness depends on caller path isolation and consistent cache state; missing quoting and hard-coded paths can redirect writes unexpectedly.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/sdk_test/sdk_test.go -->
# sources/user-network-fs/blobfuse2/test/sdk_test/sdk_test.go

Source path: `sources/user-network-fs/blobfuse2/test/sdk_test/sdk_test.go`

## Purpose
Azure SDK comparison test that downloads and uploads blobs directly against Azure Blob Storage.

## Important APIs, Types, And Functions
Package functions: `TestMain`, `TestDownloadUpload`. Types: none declared. Imports: `context`, `fmt`, `io`, `os`, `path`, `time`, `errors`, `flag`, `testing`, `github.com/Azure/azure-sdk-for-go/sdk/storage/azblob/blob`, `github.com/Azure/azure-sdk-for-go/sdk/storage/azblob/blockblob`, `github.com/Azure/azure-sdk-for-go/sdk/storage/azblob/container`.

## Control Flow
Flags provide account, SAS, container, and blob prefix. The test builds a SAS container client, loops over six blob names, downloads each blob to `/mnt/ramdisk`, uploads it back using block blob upload, logs timings, and removes the local file.

## State And Persistence
Persists temporary files under `/mnt/ramdisk` and overwrites or updates the target blob names via SDK upload. Remote Azure state is part of the test surface.

## Dependencies And Integration Points
Integrates with Go's `testing` package, Azure Blob Storage SDK clients, SAS-authenticated container/blob URLs, `/mnt/ramdisk`, and remote Azure Blob state.

## Risks
Requires valid SAS credentials and network access. The test can mutate real blobs, and errors are often logged rather than failing immediately.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/sdk_test/sdk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/stress_test/stress_test.go -->
# sources/user-network-fs/blobfuse2/test/stress_test/stress_test.go

Source path: `sources/user-network-fs/blobfuse2/test/stress_test/stress_test.go`

## Purpose
Parallel upload/download stress test for mounted storage with small, big, and huge file profiles.

## Important APIs, Types, And Functions
Package functions: `downloadWorker`, `uploadWorker`, `BytesCount`, `stressTestUpload`, `stressTestDownload`, `TestStress`, `StressSmall`, `StressBig`, `StressHuge`, `TestMain`. Types: `workItem`. Imports: `crypto/rand`, `flag`, `fmt`, `os`, `path/filepath`, `strconv`, `testing`, `time`.

## Control Flow
Worker goroutines consume directory/file creation or read jobs from channels. `TestStress` runs small, big, and huge profiles; `TestMain` parses mount path and quick-mode flags, prepares the stress root, and cleans up afterward.

## State And Persistence
Creates many directories and files below the selected mount path, reads them back, logs throughput, and removes the stress tree after each profile and at process exit.

## Dependencies And Integration Points
Integrates with Go's `testing` package, host filesystem calls, configured mounted FUSE paths, worker goroutines/channels, and throughput logs.

## Risks
The full mode allocates and writes very large buffers, including 2 GiB files, so memory, disk, network, and service throttling can dominate results. The global `noOfWorkers` is mutated by small profiles and may affect later profiles.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/stress_test/stress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/test_utils/dir_list_seek.c -->
# sources/user-network-fs/blobfuse2/test/test_utils/dir_list_seek.c

Source path: `sources/user-network-fs/blobfuse2/test/test_utils/dir_list_seek.c`

## Purpose
Exercises low-level directory listing and seek behavior, including direct syscall-level directory reads.

## Important APIs, Types, And Functions
Functions/prototypes: `main`. Includes: `dirent.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `sys/stat.h`, `sys/syscall.h`. Defines: `handle_error`, `BUF_SIZE`.

## Control Flow
The program opens a directory, reads entries into a fixed buffer, and inspects listing offsets to catch directory cursor behavior that higher-level APIs may hide.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `dirent.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `sys/stat.h`, `sys/syscall.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
It depends on Linux directory syscall semantics and fixed buffer sizing, so portability is low and failures may be kernel/libc-specific.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/test_utils/dir_list_seek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_block_bench.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_block_bench.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_block_bench.yaml`

## Purpose
Blobfuse2 test configuration selecting `block cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `ignore-open-flags`, `block_cache`, `block-size-mb`, `azstorage`, `mode`, `container`, `account-name`, `account-key`. Pipeline components: `libfuse`, `block_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `key`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_block_bench.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_block_perf.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_block_perf.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_block_perf.yaml`

## Purpose
Blobfuse2 test configuration selecting `block cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `fuse-trace`, `ignore-open-flags`, `block_cache`, `block-size-mb`, `mem-size-mb`, `prefetch`, `parallelism`, `disk-timeout-sec`, `prefetch-on-open`, plus 12 more. Pipeline components: `libfuse`, `block_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: controls mount-time block listing.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_block_perf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_cli.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_cli.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_cli.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 8 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_cli.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 9 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_bc.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_bc.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_bc.yaml`

## Purpose
Blobfuse2 test configuration selecting `block cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `block_cache`, `block-size-mb`, `attr_cache`, `timeout-sec`, `azstorage`, `type`, `endpoint`, `use-http`, plus 5 more. Pipeline components: `libfuse`, `block_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_bc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_directio.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_directio.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_directio.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `direct-io`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `azstorage`, plus 8 more. Pipeline components: `libfuse`, `file_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: enables direct I/O.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_directio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_emptyfile.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_emptyfile.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_emptyfile.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `create-empty-file`, `attr_cache`, plus 10 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: changes empty-file creation behavior.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_emptyfile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_hmon.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_hmon.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_hmon.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 15 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: enables health-monitor configuration.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_hmon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_huge.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_huge.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_huge.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 11 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: controls mount-time block listing.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_huge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_lru_purge.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_lru_purge.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_lru_purge.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, `azstorage`, plus 8 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_lru_purge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_perf.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_perf.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_perf.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `allow-non-empty-temp`, `cleanup-on-start`, `sync-to-flush`, `attr_cache`, `timeout-sec`, plus 5 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `key`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: syncs on flush for performance tests.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_perf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_proxy.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_proxy.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_proxy.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 10 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: sets an HTTPS proxy.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_proxy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_symlink.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_symlink.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_symlink.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 10 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: configures symlink handling.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_symlink.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_xload.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_xload.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_xload.yaml`

## Purpose
Blobfuse2 test configuration selecting `xload` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `xload`, `block-size-mb`, `path`, `export-progress`, `consistency`, `attr_cache`, `timeout-sec`, `azstorage`, plus 7 more. Pipeline components: `libfuse`, `xload`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_xload.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_msi.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_msi.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_msi.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 9 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_msi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_msi_sysid.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_msi_sysid.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_msi_sysid.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 6 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_msi_sysid.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_sas.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_sas.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_sas.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 9 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_sas.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_sas_proxy.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_sas_proxy.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_sas_proxy.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 10 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `block`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: sets an HTTPS proxy.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_sas_proxy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_spn.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_spn.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_spn.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 11 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_spn.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_spn_proxy.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_spn_proxy.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_spn_proxy.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `attr_cache`, `timeout-sec`, plus 12 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `block`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: sets an HTTPS proxy.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_spn_proxy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_stream.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_stream.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_stream.yaml`

## Purpose
Blobfuse2 test configuration selecting `streaming` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `stream`, `block-size-mb`, `max-buffers`, `buffer-size-mb`, `attr_cache`, `timeout-sec`, `azstorage`, `type`, plus 7 more. Pipeline components: `libfuse`, `stream`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_stream.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/config_key.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/config_key.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/config_key.yaml`

## Purpose
Blobfuse2 test configuration selecting `loopback` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `account-name`, `container-name`, `auth`, `type`, `account-account-key`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `ignore-open-flags`, `loopbackfs`, `path`. Pipeline components: `libfuse`, `loopbackfs`. Authentication/config mode: `key`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/config_key.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/config_msi.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/config_msi.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/config_msi.yaml`

## Purpose
Blobfuse2 test configuration selecting `loopback` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `account-name`, `container-name`, `auth`, `type`, `client-id`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `ignore-open-flags`, `loopbackfs`, `path`. Pipeline components: `libfuse`, `loopbackfs`. Authentication/config mode: `msi`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/config_msi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/config_sas.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/config_sas.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/config_sas.yaml`

## Purpose
Blobfuse2 test configuration selecting `loopback` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `account-name`, `container-name`, `auth`, `type`, `sas-token`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `ignore-open-flags`, `loopbackfs`, `path`. Pipeline components: `libfuse`, `loopbackfs`. Authentication/config mode: `sas`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/config_sas.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/config_spn.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/config_spn.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/config_spn.yaml`

## Purpose
Blobfuse2 test configuration selecting `loopback` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `account-name`, `container-name`, `auth`, `type`, `client-id`, `tenant-id`, `client-secret`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `ignore-open-flags`, `loopbackfs`, `path`. Pipeline components: `libfuse`, `loopbackfs`. Authentication/config mode: `spn`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/config_spn.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/scripts/generate-parquet-files.py -->
# sources/user-network-fs/blobfuse2/testdata/scripts/generate-parquet-files.py

Source path: `sources/user-network-fs/blobfuse2/testdata/scripts/generate-parquet-files.py`

## Purpose
Generates random Parquet data files for testdata workloads.

## Important APIs, Types, And Functions
Functions: `random_row_count`. Classes: none declared. Imports: `pandas`, `numpy`, `random`.

## Control Flow
Uses pandas, NumPy, and random row counts to build data frames and write Parquet files.

## State And Persistence
Persists generated Parquet files in the current working directory or configured output path.

## Dependencies And Integration Points
Integrates with Python runtime packages, benchmark datasets, mounted filesystem paths, and JSON/Parquet/report artifacts used by blobfuse2 performance experiments.

## Risks
Requires pandas/pyarrow-compatible parquet support; output volume depends on random row counts.

## Test Signals
Signals are successful script exit, valid generated JSON/Parquet/report files, timing metrics, and absence of unexpected read/classification/data-generation exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/scripts/generate-parquet-files.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/common/types.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/common/types.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/common/types.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: none declared. Types: `CacheEvent`, `CpuMemStat`. Imports: `path/filepath`.

## Control Flow
Defines monitor names, output file constants, global flag-backed runtime settings, default paths, version, and the JSON-facing `CacheEvent` and `CpuMemStat` structures.

## State And Persistence
Stores process-wide configuration in package globals populated by CLI flags or config integration.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Global mutable configuration couples all monitors and makes isolated tests or multiple monitor instances difficult.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/common/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/common/util.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/common/util.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/common/util.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `CheckProcessStatus`, `MonitorPid`. Types: none declared. Imports: `fmt`, `os/exec`, `strings`, `time`, `github.com/Azure/azure-storage-fuse/v2/common/log`.

## Control Flow
`CheckProcessStatus` shells out to `ps -ef | grep <pid>` and scans fields for the target pid; `MonitorPid` polls every second and allows monitor goroutines a short exit window after process loss.

## State And Persistence
No persisted state; it observes process tables and logs failures.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
String-based `ps|grep` matching is platform-specific and may mis-detect edge cases; command invocation every second adds overhead.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/common/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/factory.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/internal/factory.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/internal/factory.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetMonitor`, `AddMonitor`, `init`. Types: `NewMonitor`. Imports: `fmt`.

## Control Flow
Maintains a package-level registry from monitor name to constructor. Monitor packages register themselves in `init`; `GetMonitor` instantiates by name for main.

## State And Persistence
The registry map is process-global and mutable during package initialization.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
There is no locking around registration or lookup, so the design assumes single-threaded init-time registration.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/factory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/monitor.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/internal/monitor.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/internal/monitor.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: none declared. Types: `Monitor`. Imports: none declared.

## Control Flow
Declares the common `Monitor` interface implemented by every monitor plugin: naming, validation, monitoring loop, and export hook.

## State And Persistence
No state; this is the contract tying main, factory, and monitor implementations together.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
The interface has no context/cancellation parameter, so monitors rely on process death, pipe errors, or watcher closure to stop.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/stats_export.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/internal/stats_export.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/internal/stats_export.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `NewStatsExporter`, `Destroy`, `AddMonitorStats`, `StatsExporter`, `addToList`, `checkInList`, `addToOutputFile`, `checkOutputFile`, `getNewFile`, `CloseExporter`. Types: `ExportedStat`, `StatsExporter`, `Output`. Imports: `encoding/json`, `fmt`, `os`, `path/filepath`, `sync`, `sync/atomic`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/internal/stats_manager`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`.

## Control Flow
Creates a singleton exporter with a buffered channel and goroutine. Incoming timestamped stats are grouped into in-memory `Output` buckets, flushed to JSON arrays, and rotated once files reach the configured size/count limit.

## State And Persistence
Persists monitor JSON files under `OutputPath` named `monitor_<pid>.json` with numbered rotations. `pidStatus` prevents new channel writes during destroy, and `outputList` holds up to three recent timestamp buckets.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Type assertions depend on monitor names matching stat payload types. Dropping the oldest channel element on full buffer avoids blocking but can lose telemetry. JSON array formatting is hand-managed and vulnerable to abrupt process exit.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/stats_export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/main.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/main.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/main.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `getMonitors`, `main`, `init`. Types: none declared. Imports: `flag`, `fmt`, `os`, `strings`, `time`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor`.

## Control Flow
Parses flags, initializes syslog logging, validates the target pid, suffixes blobfuse stats pipe names with pid, builds enabled monitors, launches each monitor goroutine, waits while the pid is alive, and closes the exporter.

## State And Persistence
Reads CLI flags into `hmcommon` globals, creates log files, named pipes, and JSON output files.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Monitor goroutines are launched without join/error propagation. Missing pid is fatal, but individual monitor failures are logged asynchronously.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/blobfuse_stats/stats_reader.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/blobfuse_stats/stats_reader.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/blobfuse_stats/stats_reader.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetName`, `SetName`, `Monitor`, `ExportStats`, `Validate`, `statsReader`, `statsPoll`, `createPipe`, `NewBlobfuseStatsMonitor`, `init`. Types: `BlobfuseStats`. Imports: `bufio`, `encoding/json`, `fmt`, `os`, `syscall`, `time`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/internal/stats_manager`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`.

## Control Flow
Validates polling interval and pid, creates transfer and polling named pipes, reads newline-delimited JSON `stats_manager.PipeMsg` records from the transfer pipe, and periodically writes poll messages to the polling pipe.

## State And Persistence
Creates FIFO files using blobfuse common pipe names with pid suffixes and streams stats into the shared exporter.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Named pipe open/read behavior can block or fail if the blobfuse process does not cooperate. Malformed JSON records are skipped after logging.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/blobfuse_stats/stats_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetName`, `SetName`, `Monitor`, `ExportStats`, `Validate`, `getCpuMemoryUsage`, `getCpuMemIndex`, `NewCpuMemoryMonitor`, `init`. Types: `CpuMemProfiler`. Imports: `fmt`, `math`, `os/exec`, `strings`, `time`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`.

## Control Flow
On each process-monitor tick, executes `top`, parses header positions for `%CPU` and `VIRT`, normalizes units, then exports CPU and/or memory values depending on disabled flags.

## State And Persistence
No persisted state beyond exporter output; it observes process metrics through shell commands.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
`top` output parsing is locale/platform sensitive, and `ExportStats` assumes non-empty strings before checking the last character.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor_test.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor_test.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor_test.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `SetupTest`, `TestGetCpuMemoryUsage`, `TestGetCpuMemoryUsageFailure`, `TestCpuMemMonitor`. Types: `cpuMemMonitorTestSuite`. Imports: `fmt`, `os`, `testing`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/stretchr/testify/assert`, `github.com/stretchr/testify/suite`.

## Control Flow
Testify suite initializes logging and temp globals, tests successful and failed CPU/memory parsing, and exercises monitor construction/validation.

## State And Persistence
Mutates process-level health-monitor globals during setup.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Tests depend on local process/table behavior and may be brittle across operating systems or `top` variants.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/cache_monitor.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/cache_monitor.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/cache_monitor.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetName`, `SetName`, `Monitor`, `ExportStats`, `Validate`, `cacheWatcher`, `createEvent`, `removeEvent`, `chmodEvent`, `writeEvent`, `renameEvent`, `moveEvent`, `getCacheEventObj`, `NewFileCacheMonitor`, `init`. Types: `FileCache`, `CacheDir`. Imports: `fmt`, `math`, `strconv`, `strings`, `time`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`, `github.com/radovskyb/watcher`.

## Control Flow
Validates pid and cache path, sets a recursive watcher over the file-cache directory, converts CREATE/REMOVE/CHMOD/RENAME/MOVE events into `CacheEvent` payloads, updates size/eviction counters, and exports timestamped events.

## State And Persistence
Maintains in-memory maps of created and removed files plus aggregate cache bytes/percentage. The watcher observes the configured cache directory and emits JSON via the exporter.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Map updates happen in the watcher goroutine without explicit synchronization; cache-size accounting can be inaccurate if events are missed, reordered, or represent directories. `maxSizeMB` of zero risks divide-by-zero style output.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/cache_monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/types_cache.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/types_cache.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/types_cache.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: none declared. Types: none declared. Imports: none declared.

## Control Flow
Defines string constants used by the file-cache monitor for watcher operation names and JSON value keys.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Constants must match `watcher.Event.Op.String()` upper-case output; library changes can silently stop event classification.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/types_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/imports.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/imports.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/imports.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: none declared. Types: none declared. Imports: `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor/blobfuse_stats`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor/cpu_mem_profiler`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor/file_cache`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor/network_profiler`.

## Control Flow
Blank-imports every concrete monitor package so their `init` functions can self-register with the internal factory.

## State And Persistence
No direct state, but import side effects populate the monitor registry.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Removing or build-tagging this file can leave monitors unregistered even though their packages compile.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/imports.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/network_profiler/network_monitor.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/network_profiler/network_monitor.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/network_profiler/network_monitor.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetName`, `SetName`, `Monitor`, `ExportStats`, `Validate`, `NewNetworkMonitor`, `init`. Types: `NetworkProfiler`. Imports: `fmt`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`.

## Control Flow
Defines a monitor shell with validation and exporter plumbing, but its `init` registration is commented out and `Monitor` returns after validation.

## State And Persistence
No network stats are collected or persisted.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
The monitor is present in constants and disable flags but inactive; users may assume network telemetry exists when it does not.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/network_profiler/network_monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/install_fio.sh -->
# sources/user-network-fs/blobfuse2/tools/install_fio.sh

Source path: `sources/user-network-fs/blobfuse2/tools/install_fio.sh`

## Purpose
Installs a pinned fio version from source for performance testing.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `fio`, `git`, `make`, `apt`, `apt-get`.

## Control Flow
Installs build dependencies, clones `axboe/fio`, checks out `fio-3.36`, configures/builds/installs it, removes the clone, and prints the installed version.

## State And Persistence
Changes system packages and installs a binary into the host.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Requires sudo and network access; source build failures stop due to `set -e`.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/install_fio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/postinstall.sh -->
# sources/user-network-fs/blobfuse2/tools/postinstall.sh

Source path: `sources/user-network-fs/blobfuse2/tools/postinstall.sh`

## Purpose
Package post-install hook that generates blobfuse2 shell completions and restarts syslog when present.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `blobfuse2`.

## Control Flow
Runs `blobfuse2 completion` for bash globally and for zsh/fish user locations when shells are installed, then restarts rsyslog if `/etc/rsyslog.d` exists.

## State And Persistence
Writes completion files under `/etc` and user home directories and restarts a service.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Assumes plugin directories exist and uses sudo inside a package script; missing directories can fail completion generation.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/postinstall.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/preinstall.sh -->
# sources/user-network-fs/blobfuse2/tools/preinstall.sh

Source path: `sources/user-network-fs/blobfuse2/tools/preinstall.sh`

## Purpose
Package pre-install hook that recreates `/usr/share/blobfuse2`.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `blobfuse2`.

## Control Flow
Deletes the existing share directory and creates a fresh one.

## State And Persistence
Mutates system installation directory.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Unconditional removal can delete files placed there by other package versions or local administrators.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/preinstall.sh -->
