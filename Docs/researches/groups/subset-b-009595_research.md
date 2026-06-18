<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/vm_metrics.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/vm_metrics.py

Purpose: Python CLI/library for extracting Google Cloud Monitoring time-series metrics for gcsfuse VM performance runs and writing normalized rows to a Google Sheet. It targets CPU utilization, network bytes, gcsfuse custom read/error/latency metrics, and rename-specific memory/load/sent-byte metrics.

Important APIs, types, and functions: `MetricPoint` stores value plus interval timestamps. `Metric` describes metric type, unit conversion factor, aligner, optional Monitoring filter suffix, reducer, grouping fields, and populated `metric_point_list`. Global metric descriptors such as `CPU_UTI_PEAK`, `READ_BYTES_COUNT`, `OPS_ERROR_COUNT`, `MEMORY_USAGE_PEAK`, and `LOAD_AVG_OS_THREADS_MEAN` define the supported Monitoring requests. `VmMetrics._get_api_response` builds `monitoring_v3.MetricServiceClient.list_time_series` requests, `_get_metrics` converts responses to points, `_add_new_metric_using_test_type` selects read/write/rename metric sets, `fetch_metrics` builds spreadsheet rows, and `fetch_metrics_and_write_to_google_sheet` delegates persistence to `gsheet.write_to_google_sheet`.

Control flow: `main` validates six positional arguments, converts epoch/period values to integers, and calls `VmMetrics.fetch_metrics_and_write_to_google_sheet`. Fetching first validates that start time precedes end time, then builds a metric list from the test type. Each metric is fetched from Cloud Monitoring with a `TimeInterval`, `Aggregation`, aligner, reducer, and generated filter. Responses are parsed by `_create_metric_points_from_response`, reversed into chronological order, and then zipped by index into rows containing interval end time followed by each metric value.

State and persistence behavior: The module mutates shared global `Metric` instances by filling their `metric_point_list`; repeated calls reuse objects unless the caller receives copied lists. It contacts the GCE metadata server for instance ID, shells out to `ps` to find a gcsfuse PID for process RSS metrics, and writes final rows to Google Sheets through the sibling `gsheet` module. No local files are written by this module directly.

Dependencies and integration points: Depends on `google-cloud-monitoring`, `google.api_core`, GCE metadata, process table output, the `gcs-fuse-test-ml` project name, gcsfuse custom metrics, and a sibling `gsheet` package imported via `sys.path.insert(0, '..')`. Monitoring filters differ for compute metrics (`metric.label.instance_name`), custom metrics (`metadata.system_labels.name`), and agent metrics (`resource.labels.instance_id`).

Risks and test signals: Risks include global `Metric` mutation across calls, unsupported `test_type` values leaving `fs_op` unset, broad exception handling around API calls, shell parsing of `ps -aux | grep -i gcsfuse | head -1`, and filtering agent memory by PID only at request time. `OPS_ERROR_COUNT` uniquely tolerates empty data by synthesizing zero points; other empty series raise `NoValuesError`. Unit tests cover typed-value parsing, filter generation, empty-response handling, fixture response parsing, and metadata error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/vm_metrics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/vm_metrics_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/vm_metrics_test.py

Purpose: Unit test suite for `vm_metrics.py`, using Monitoring response JSON fixtures to validate parsing, filter construction, error behavior, metadata handling, and metric conversion.

Important APIs, types, and functions: `MetricsResponseObject` and `dict_to_obj` convert fixture dictionaries into attribute-style objects. `create_metrics_value_by_type` builds `monitoring_v3.TypedValue` instances for bool, int64, double, string, and distribution values. `get_response_from_filename` loads `testdata/*.json` and constructs a `monitoring_v3.TimeSeries`. `TestVmmetricsTest` contains tests for `_get_instance_id`, `_parse_metric_value_by_type`, `_get_metric_filter`, `_validate_start_end_times`, and `_get_metrics` across CPU, memory, network, read bytes, latency, load average, and error count.

Control flow: Tests instantiate `VmMetrics` in `setUp`. API-facing tests patch `VmMetrics._get_api_response` to return either empty mappings or fixture-backed `TimeSeries` objects, then assert `MetricPoint` lists or exceptions. Metadata tests patch `subprocess.check_output` or `_get_instance_id`. The fixture builder manually maps JSON point intervals and values to protobuf objects because TimeSeries JSON is not deserialized directly.

State and persistence behavior: Reads fixture files under `./testdata`; does not write persistent state. It patches process execution and Monitoring calls, so tests do not require live GCP. Some expected constants mirror production metric descriptors but include a memory metric type (`agent.googleapis.com/memory/percent_used`) that differs from the production `agent.googleapis.com/processes/rss_usage`, making test coverage partly historical.

Dependencies and integration points: Depends on `unittest`, `mock`/`unittest.mock`, `google.cloud.monitoring_v3`, `google.api.distribution_pb2`, fixture JSON, and the local `vm_metrics` module. It exercises the same Monitoring value-type codes as production.

Risks and test signals: Strong signals include empty response behavior for every metric class, distribution mean parsing, int64/double conversion, agent/custom/compute filter strings, and synthesized zero error-count series. Gaps include no direct test for `fetch_metrics` row zipping, no Google Sheets write assertion, no unsupported `test_type` handling, and limited coverage of `_get_gcsfuse_pid` shell parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/vm_metrics_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/checkpointing.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/checkpointing.yaml

Purpose: Example gcsfuse config for GPU checkpointing workloads that read and write model checkpoints through a mounted GCS bucket.

Important APIs, types, and functions: This is declarative YAML for gcsfuse configuration. It enables `implicit-dirs`, uses `/tmp` as `cache-dir`, configures `metadata-cache` with `negative-ttl-secs: 0`, `ttl-secs: -1`, and unlimited stat cache, enables unlimited `file-cache`, whole-file caching for range reads, parallel downloads, and `write.enable-streaming-writes`.

Control flow: At mount startup, gcsfuse reads these options and applies metadata caching, file caching, and streaming write behavior. There is no executable control flow in the file.

State and persistence behavior: File content cache is stored under `/tmp`; comments indicate GPU deployments expect local SSD backing. Metadata entries and file cache can grow without explicit size limit because both max sizes are `-1`. Streaming writes alter write path behavior for checkpoint output.

Dependencies and integration points: Intended for gcsfuse config-file consumption and to correspond to GKE CSI checkpointing PV mount options. It assumes workloads can tolerate indefinite metadata cache TTL and that `/tmp` has enough capacity for checkpoint cache pressure.

Risks and test signals: Unlimited metadata and file caches can consume local disk. `ttl-secs: -1` can expose stale metadata when other writers mutate the bucket. The checkpointing-specific signal is streaming writes enabled, unlike serving/training configs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/checkpointing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/serving.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/serving.yaml

Purpose: Example gcsfuse config for GPU serving workloads optimized for cached model artifact reads.

Important APIs, types, and functions: Declarative gcsfuse options enable `implicit-dirs`, `/tmp` cache directory, indefinite positive metadata cache, disabled negative lookup cache, unlimited stat cache, unlimited file cache, whole-file cache on range read, and parallel downloads.

Control flow: The serving mount reads these options at startup and serves later file reads through metadata and file caches. No write-specific section is present.

State and persistence behavior: File cache and metadata cache can persist for the mount lifetime with no configured size cap. Serving is read-heavy, so the config omits streaming writes and prioritizes parallel download/cache behavior.

Dependencies and integration points: Integrates with gcsfuse config-file mounting and GPU local SSD `/tmp` cache assumptions. It aligns with GKE serving PV options and serving pod examples that mount a cache volume.

Risks and test signals: Unlimited file cache can exhaust `/tmp`; indefinite metadata TTL can become stale if model objects change under the mount. Test signals should verify that read cache and parallel download behavior are effective for serving artifacts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/serving.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/training.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/training.yaml

Purpose: Example gcsfuse config for GPU training workloads where metadata caching is recommended and file content caching is optional depending on dataset size.

Important APIs, types, and functions: Active options enable `implicit-dirs` and metadata cache settings (`negative-ttl-secs: 0`, `ttl-secs: -1`, unlimited stat cache). File cache settings are commented out with a `<DATASET_SIZE>` placeholder.

Control flow: At mount time, gcsfuse applies only implicit directory and metadata cache options. File content cache is disabled unless the user uncommentes and sizes the `cache-dir`/`file-cache` block.

State and persistence behavior: Active state is limited to metadata cache, which may persist indefinitely for the mount lifetime. Optional file cache would store data under `/tmp` if enabled.

Dependencies and integration points: Intended for training jobs using gcsfuse config files and GPU local SSD `/tmp` when optional cache is enabled. It mirrors the training PV template where file cache mount options are commented out.

Risks and test signals: Indefinite metadata cache can hide external dataset changes. Commented file cache block avoids default disk blow-up but requires user sizing; bad substitution of `<DATASET_SIZE>` would break config if copied literally.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/training.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/checkpointing.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/checkpointing.yaml

Purpose: TPU checkpointing gcsfuse config equivalent to the GPU checkpointing profile, with comments noting `/tmp` is expected to be RAM disk backed on TPU.

Important APIs, types, and functions: Enables `implicit-dirs`, `/tmp` cache directory, metadata cache with disabled negative cache and indefinite positive cache, unlimited stat and file cache sizes, whole-file range-read caching, parallel downloads, and streaming writes.

Control flow: Declarative mount configuration is consumed by gcsfuse during startup; checkpoint writes use the streaming writes path.

State and persistence behavior: Uses `/tmp` for file cache, which may be RAM-backed on TPU. Unlimited cache sizing and indefinite metadata TTL persist until mount/cache cleanup.

Dependencies and integration points: Integrates with TPU workload deployments and matches the TPU checkpointing GKE CSI PV/POD examples that allocate RAM disk cache.

Risks and test signals: RAM disk exhaustion is a stronger risk for TPU than GPU local SSD. Streaming write behavior should be validated for checkpoint output; stale metadata remains a risk with `ttl-secs: -1`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/checkpointing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/serving.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/serving.yaml

Purpose: TPU serving gcsfuse config optimized for model artifact reads with RAM disk file cache.

Important APIs, types, and functions: Declarative options enable implicit directories, `/tmp` cache dir, indefinite metadata cache, disabled negative cache, unlimited stat cache, unlimited file cache, whole-file cache for range reads, and parallel downloads.

Control flow: gcsfuse applies cache and metadata options at mount time. There is no write path configuration.

State and persistence behavior: File cache is placed under `/tmp`, expected to be RAM disk backed on TPU samples, with no size limit. Metadata cache remains valid indefinitely.

Dependencies and integration points: Corresponds to TPU serving GKE CSI templates using `gke-gcsfuse-cache` as memory-backed `emptyDir`.

Risks and test signals: Unlimited RAM-backed cache may evict or OOM workloads. Indefinite metadata cache can serve stale metadata after model updates. Serving tests should validate full-file caching and parallel download performance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/serving.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/training.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/training.yaml

Purpose: TPU training gcsfuse config that enables metadata cache and leaves file cache as an opt-in block sized to the dataset.

Important APIs, types, and functions: Active YAML config contains `implicit-dirs: true` and metadata-cache settings for disabled negative cache, indefinite positive TTL, and unlimited stat cache. The optional `cache-dir` and `file-cache` lines are comments with `<DATASET_SIZE>`.

Control flow: Only active metadata and implicit-directory options are applied by gcsfuse unless the operator edits the commented file-cache block.

State and persistence behavior: Metadata cache persists for the mount lifetime. Optional file cache would use `/tmp` RAM disk on TPU, so it must be sized deliberately.

Dependencies and integration points: Aligns with TPU training GKE CSI samples. It is intended for workloads where the dataset may not fit safely in RAM-backed cache.

Risks and test signals: The commented `#file-cache:` line lacks a space after `#`, but remains a YAML comment. Risks include stale metadata and operator error when enabling a file cache with an unsized placeholder.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/training.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pod.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pod.yaml

Purpose: Kubernetes Pod template for GPU checkpointing workloads using the GKE gcsfuse CSI driver with a checkpoint bucket PVC.

Important APIs, types, and functions: Defines a `v1/Pod` with `gke-gcsfuse/volumes: "true"` annotation, placeholder namespace, workload container placeholder, `checkpoint-bucket-vol` mounted at `/checkpoint-data`, service account placeholder, and PVC-backed volume `checkpoint-bucket-pvc`. Optional metadata-prefetch resource annotations and RAM disk cache `emptyDir` are commented.

Control flow: Kubernetes schedules the pod; the GKE gcsfuse CSI integration sees the annotation, injects/uses the CSI volume, and mounts the checkpoint PVC into the workload container.

State and persistence behavior: Checkpoint data is persisted in the GCS bucket behind the PVC. Optional in-memory cache volume would be ephemeral and pod-scoped if uncommented.

Dependencies and integration points: Requires GKE gcsfuse CSI support, Workload Identity/service account wiring via `<YOUR_K8S_SA>`, and a matching `checkpoint-bucket-pvc` from the PV template.

Risks and test signals: The workload container is an ellipsis placeholder and is not valid as-is. Missing service account permissions or absent PVC prevents mounting. Optional metadata prefetch annotations require minimum GKE version `1.32.3-gke.1717000`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pv.yaml

Purpose: Kubernetes PersistentVolume and PersistentVolumeClaim template for GPU checkpointing buckets mounted through the GKE gcsfuse CSI driver.

Important APIs, types, and functions: Defines a `PersistentVolume` named `checkpoint-bucket-pv` with `ReadWriteMany`, `Retain`, dummy `gcsfuse-sc`, claimRef to `checkpoint-bucket-pvc`, gcsfuse mount options for implicit dirs, metadata cache, unlimited file cache, whole-file range caching, parallel downloads, kernel read-ahead, and streaming writes. CSI attributes set driver `gcsfuse.csi.storage.gke.io`, `volumeHandle: <checkpoint-bucket>`, `skipCSIBucketAccessCheck`, and `gcsfuseMetadataPrefetchOnMount`. The second YAML document defines the matching PVC.

Control flow: The statically bound PVC claims the named PV. During pod mount, CSI passes mountOptions and volumeAttributes to gcsfuse.

State and persistence behavior: The PV is retained after PVC deletion. Cached content is node/pod side, while checkpoint objects persist in GCS. Metadata prefetch populates metadata cache at mount time.

Dependencies and integration points: Must be paired with a pod mounting `checkpoint-bucket-pvc`. It depends on a real GCS bucket name replacing `<checkpoint-bucket>` and correct namespace substitution.

Risks and test signals: Unlimited cache and read-ahead can pressure local disk. `skipCSIBucketAccessCheck: "true"` defers access failure to runtime operations. Streaming writes are checkpoint-specific and should be validated with write-heavy tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/serving-pod.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/serving-pod.yaml

Purpose: Kubernetes Pod template for GPU serving workloads that mount a serving bucket and allocate RAM disk cache for gcsfuse file caching.

Important APIs, types, and functions: Defines a `v1/Pod` with gcsfuse CSI annotation, placeholder namespace/container, `serving-bucket-vol` mounted at `/serving-data`, service account placeholder, an active `gke-gcsfuse-cache` memory `emptyDir`, and PVC volume `serving-bucket-pvc`.

Control flow: GKE gcsfuse CSI uses the pod annotation and cache volume convention to mount the bucket PVC with cache backing before the workload starts.

State and persistence behavior: Serving data persists in GCS; the memory cache is ephemeral and tied to pod lifecycle. The mounted path is read-oriented.

Dependencies and integration points: Requires a matching serving PVC/PV, enough pod memory for RAM disk cache, and service account permissions to the model bucket.

Risks and test signals: Active RAM disk cache can compete with model server memory. Placeholder container YAML must be replaced. Metadata prefetch resource annotations are commented and version-gated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/serving-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/serving-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/serving-pv.yaml

Purpose: Static PV/PVC template for GPU serving bucket mounts using gcsfuse CSI with aggressive read cache options.

Important APIs, types, and functions: PV `serving-bucket-pv` uses `ReadWriteMany`, retained reclaim policy, dummy storage class, and `mountOptions` for implicit dirs, disabled negative metadata cache, indefinite metadata TTL, unlimited stat/file cache, range-read whole-file caching, parallel downloads, and `read_ahead_kb=1024`. CSI uses `volumeHandle: <serving-bucket>`, skips bucket access check, and enables metadata prefetch on mount. PVC `serving-bucket-pvc` binds to that PV.

Control flow: Kubernetes binds PVC to PV; the CSI driver uses the mount options when a pod consumes the PVC.

State and persistence behavior: GCS stores model artifacts; local cache state is external to this YAML and driven by pod/cache configuration. Metadata is prefetched and cached indefinitely by gcsfuse.

Dependencies and integration points: Must be consumed by serving pod template and parameterized with real bucket and namespace values.

Risks and test signals: Indefinite metadata and unlimited file cache favor performance over freshness/resource bounds. `skipCSIBucketAccessCheck` can hide configuration errors until pod I/O. Serving validation should measure cold and warm model reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/serving-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/training-pod.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/training-pod.yaml

Purpose: Kubernetes Pod template for GPU training workloads mounting a training data bucket through gcsfuse CSI.

Important APIs, types, and functions: Defines a `v1/Pod` annotated with `gke-gcsfuse/volumes: "true"`, a placeholder workload container, `training-bucket-vol` mounted at `/training-data`, service account placeholder, and PVC volume `training-bucket-pvc`. RAM disk cache and metadata prefetch resource annotations are commented.

Control flow: The pod consumes a precreated training PVC; the GKE gcsfuse CSI driver mounts it into the container.

State and persistence behavior: Training data persists in GCS. No active cache volume is allocated by default, avoiding unbounded pod memory use for large datasets.

Dependencies and integration points: Requires the matching training PV/PVC, bucket IAM via service account, and replacement of placeholder namespace/container fields.

Risks and test signals: YAML is a template, not directly valid due to `...`. File cache is optional; training jobs that need cache must add a cache volume and PV mount options consistently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/training-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/training-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/training-pv.yaml

Purpose: Static PV/PVC template for GPU training bucket mounts, optimized for metadata caching with optional file cache.

Important APIs, types, and functions: PV `training-bucket-pv` defines `ReadWriteMany`, `Retain`, dummy storage class, claimRef to `training-bucket-pvc`, active mount options for implicit dirs and metadata cache, and commented file-cache/read-ahead options. CSI uses `gcsfuse.csi.storage.gke.io`, `volumeHandle: <training-bucket>`, skips bucket access check, and enables metadata prefetch. Matching PVC binds to the PV.

Control flow: PVC binding is static via `volumeName`; pod mount causes CSI to pass active mount options to gcsfuse.

State and persistence behavior: Metadata cache can persist indefinitely for the mount. File content cache is disabled unless the user uncommentes file-cache options and provides cache backing.

Dependencies and integration points: Works with the GPU training pod template. Requires namespace and bucket placeholder replacement.

Risks and test signals: Active `ttl-secs:-1` can create stale training metadata. Commented cache options include unlimited max size if copied directly, which can exhaust local SSD. GKE integration should test both default metadata-only and cache-enabled modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/training-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/checkpointing-pod.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/checkpointing-pod.yaml

Purpose: Kubernetes Pod template for TPU checkpointing workloads with a GCS checkpoint bucket and memory-backed gcsfuse cache.

Important APIs, types, and functions: Defines `v1/Pod` with gcsfuse CSI annotation, placeholder namespace/container, `checkpoint-bucket-vol` mounted at `/checkpoint-data`, service account placeholder, active `gke-gcsfuse-cache` `emptyDir.medium: Memory`, and PVC `checkpoint-bucket-pvc`.

Control flow: GKE gcsfuse CSI recognizes the annotation and mounts the checkpoint PVC, using the memory cache volume for file cache behavior.

State and persistence behavior: GCS stores checkpoint data; RAM disk cache is ephemeral and pod-scoped. Checkpoint writes are configured by the paired PV to use streaming writes.

Dependencies and integration points: Requires TPU-compatible pod spec substitution, matching checkpoint PVC/PV, service account access, and enough memory for cache.

Risks and test signals: Active memory cache can consume TPU workload memory. Placeholder `...` must be replaced. Metadata prefetch resource annotations are commented and GKE-version gated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/checkpointing-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/checkpointing-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/checkpointing-pv.yaml

Purpose: Static PV/PVC template for TPU checkpointing buckets using the GKE gcsfuse CSI driver.

Important APIs, types, and functions: PV `checkpoint-bucket-pv` uses `ReadWriteMany`, `Retain`, dummy storage class, claimRef, mount options for implicit dirs, metadata cache, unlimited file cache, range-read whole-file caching, parallel downloads, read-ahead, and streaming writes. CSI attributes include driver `gcsfuse.csi.storage.gke.io`, `volumeHandle: <checkpoint-bucket>`, `skipCSIBucketAccessCheck`, and metadata prefetch. PVC `checkpoint-bucket-pvc` binds to the PV.

Control flow: Static PVC binding and CSI mount pass all mount options to gcsfuse when a TPU checkpoint pod consumes the PVC.

State and persistence behavior: Checkpoints persist in GCS; local file cache is usually RAM-backed by the TPU pod template. Metadata prefetch populates cache at mount time.

Dependencies and integration points: Designed to pair with TPU checkpointing pod YAML and TPU RAM disk cache. Requires bucket/namespace substitution.

Risks and test signals: Unlimited file cache on RAM disk can exhaust memory. `skipCSIBucketAccessCheck` can defer bucket misconfiguration errors. Streaming writes should be tested under checkpoint save/restore workloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/checkpointing-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pod.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pod.yaml

Purpose: Kubernetes Pod template for TPU serving workloads that mount serving data from GCS and use memory-backed gcsfuse cache.

Important APIs, types, and functions: Defines a `v1/Pod` with gcsfuse CSI annotation, placeholder namespace/container, `serving-bucket-vol` mounted at `/serving-data`, service account placeholder, active `gke-gcsfuse-cache` `emptyDir.medium: Memory`, and PVC `serving-bucket-pvc`.

Control flow: GKE injects/activates gcsfuse volume handling based on pod annotation and mounts the PVC before workload start.

State and persistence behavior: Model data persists in GCS; cache contents live in pod memory and are lost at pod termination.

Dependencies and integration points: Requires TPU serving workload spec, matching serving PV/PVC, bucket IAM, and sufficient memory allocation.

Risks and test signals: The RAM disk cache is active by default and can compete with serving memory. Placeholder container syntax must be replaced. Tests should verify cache-backed model reads and pod resource sizing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pv.yaml

Purpose: Static PV/PVC template for TPU serving buckets with gcsfuse CSI read-cache optimizations.

Important APIs, types, and functions: PV `serving-bucket-pv` includes implicit dirs, disabled negative metadata cache, indefinite metadata cache, unlimited stat/file caches, whole-file range-read caching, parallel downloads, and `read_ahead_kb=1024`. CSI points to `<serving-bucket>` and enables skipped bucket access check plus metadata prefetch. PVC `serving-bucket-pvc` binds to that PV.

Control flow: Kubernetes binds PVC to PV; CSI transforms mount options into gcsfuse command/config behavior for the consuming pod.

State and persistence behavior: GCS is persistent storage; local cache is pod/node-side and, in the paired TPU pod, RAM-backed.

Dependencies and integration points: Consumed by TPU serving pod template and requires bucket/namespace substitution.

Risks and test signals: Unlimited RAM-backed cache can overrun memory, and indefinite metadata can stale model artifact views. `skipCSIBucketAccessCheck` should be used only when IAM/bucket existence is validated elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pod.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pod.yaml

Purpose: Kubernetes Pod template for TPU training workloads mounting GCS training data through gcsfuse CSI.

Important APIs, types, and functions: Defines a gcsfuse-enabled `v1/Pod`, placeholder workload container, `training-bucket-vol` mounted at `/training-data`, service account placeholder, and PVC `training-bucket-pvc`. In-memory cache volume is commented and should be enabled only if the dataset fits.

Control flow: GKE CSI mounts the training PVC into the pod when the annotation is present.

State and persistence behavior: Training data remains in GCS. No active cache volume is created by default, limiting memory pressure for large datasets.

Dependencies and integration points: Requires matching TPU training PV/PVC and bucket IAM. Placeholder fields must be replaced for a valid pod.

Risks and test signals: Enabling RAM cache without dataset sizing can exhaust memory. Default metadata-only cache should be tested for data-loading performance and freshness assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pv.yaml

Purpose: Static PV/PVC template for TPU training data buckets with active metadata cache and optional file cache.

Important APIs, types, and functions: PV `training-bucket-pv` sets `ReadWriteMany`, `Retain`, dummy storage class, claimRef, active mount options for implicit dirs and metadata cache, and commented file cache/read-ahead options using `<DATASET_SIZE>`. CSI attributes point to `<training-bucket>`, skip access check, and enable metadata prefetch. PVC binds to this PV.

Control flow: CSI applies active mount options during pod mount. File cache is inactive until uncommented by an operator.

State and persistence behavior: Metadata cache can persist indefinitely during the mount. Optional file cache would likely be RAM-backed by the pod and must be sized to the dataset.

Dependencies and integration points: Paired with TPU training pod template. Requires GCS bucket, namespace, and IAM substitution.

Risks and test signals: Stale metadata risk is explicit with `ttl-secs:-1`. Optional cache comments are safer than unlimited defaults, but copying `<DATASET_SIZE>` literally would produce invalid configuration. Tests should include large dataset reads with and without cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main.go -->
# sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main.go

Purpose: Release/build helper that compiles gcsfuse and its mount helper into a target filesystem hierarchy suitable for packaging or installation.

Important APIs, types, and functions: `buildBinaries(dstDir, srcDir, version, arch, buildArgs)` creates `bin`/`sbin`, constructs temporary `GOPATH` and `GOCACHE`, symlinks source into GOPATH layout, runs `go build` for `github.com/googlecloudplatform/gcsfuse/v3` and `tools/mount_gcsfuse`, injects `common.gcsfuseVersion` via ldflags for the main binary, and creates Linux `mount.fuse.gcsfuse` symlink. `run` parses `--arch` via `pflag` and positional `src_dir dst_dir version [build args]`.

Control flow: `main` sets logging and exits nonzero on `run` error. `run` validates at least three positional args, then delegates to `buildBinaries`. `buildBinaries` prepares directories, environment, mount helper naming, build command arguments, environment variables (`GO111MODULE=auto`, `CGO_ENABLED=0`, `GOARCH`, GOPATH/GOCACHE), and then builds each target.

State and persistence behavior: Writes binaries and symlinks under `dstDir`. Temporary GOPATH/GOCACHE directories are removed by deferred cleanup. It reads `PATH`, source tree, Go toolchain, and runtime `GOROOT`.

Dependencies and integration points: Used by release scripts, package Dockerfiles, and local source installation paths. Depends on Go 1.20+ for `go build -C`, `spf13/pflag`, runtime OS/arch, and the gcsfuse module path.

Risks and test signals: Destination `bin`/`sbin` creation fails if directories already exist. The command forces `GO111MODULE=auto` and `CGO_ENABLED=0`, which may not match future build needs. Error wrapping detects unsupported `-C` to suggest Go upgrade. Tests verify version stamping by building and running `gcsfuse --version`/`-v`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main_test.go

Purpose: Integration-style Go test that verifies `buildBinaries` stamps the requested version into the built gcsfuse binary.

Important APIs, types, and functions: `TestVersion` creates a temp destination, calls `buildBinaries(dir, "../../", "99.88.77", runtime.GOARCH, nil)`, and runs the produced `bin/gcsfuse` with `--version` and `-v`, asserting output contains `gcsfuse version 99.88.77`.

Control flow: Temp dir is cleaned with `t.Cleanup`. Build failures fail the test immediately. Each version flag case runs as a subtest with `exec.Command(...).CombinedOutput`.

State and persistence behavior: Writes build outputs only under a temporary directory and deletes them after test. It compiles the local source tree and executes the resulting binary.

Dependencies and integration points: Depends on a working Go toolchain, repository-relative source path `../../`, host architecture, and `testify/assert`.

Risks and test signals: This is a high-signal test for release version injection but is slower and more environment-sensitive than a unit test. It does not inspect mount helper outputs or cross-architecture behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/e2e_test.sh -->
# sources/user-network-fs/gcsfuse/tools/cd_scripts/e2e_test.sh

Purpose: Legacy release VM startup script that installs prerequisites, installs or builds gcsfuse, runs integration test suites against flat/HNS/zonal/emulator buckets, gathers logs, and uploads results to a GCS release bucket.

Important APIs, types, and functions: Shell helpers include `create_user`, `grant_sudo`, `run_non_parallel_tests`, `run_parallel_tests`, `run_e2e_tests`, `gather_test_logs`, `log_based_on_exit_status`, and `run_e2e_tests_for_emulator_and_log`. It reads GCE metadata for zone and per-instance flags (`custom_bucket`, `run-on-zb-only`, `run-read-cache-only`, `run-light-test`), consumes `version-detail/details.txt`, and runs `go test` under `tools/integration_tests/*` with `--integrationTest`, `--testbucket`, `--testInstalledPackage`, timeout, and conditional `--zonal`.

Control flow: The outer root phase installs/updates gcloud, discovers metadata, creates a privileged local user, and enters a `sudo -u starterscriptuser` subshell. The user phase installs OS dependencies and Go, clones gcsfuse, checks out the release commit, optionally builds from source for custom bucket runs, assembles test package arrays, runs selected suites in parallel/non-parallel buckets, and uploads success/log artifacts in a trap on exit.

State and persistence behavior: Mutates the VM significantly: package installation, gcloud upgrade under `/usr/local`, sudoers file creation, user creation, repository clone, Go install, `/usr/bin`/`/usr/sbin` binary copy for source builds, local logs under home and `/tmp`, GCS uploads under `gs://<bucket>/v<version>/<vm>/`, and test buckets/objects via integration tests.

Dependencies and integration points: Requires GCE metadata server, gcloud, release bucket layout, apt/yum/dnf, Go downloads, GitHub, GCS permissions, integration test utilities, and OS-specific package managers. Integrates with release automation metadata and older gcsfuse versions by conditionally passing `-short` and `--zonal`.

Risks and test signals: Broad operational risk: root package changes, unpinned gcloud download, NOPASSWD sudo user, shell quoting complexity in nested script, and a bug-like variable mismatch in `run_e2e_tests_for_emulator_and_log` (`emulator_test_status` set but `e2e_tests_emulator_status` checked). Test signals are release-level: uploaded success markers per bucket type and consolidated logs for failed package suites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/e2e_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/improved_e2e_test.sh -->
# sources/user-network-fs/gcsfuse/tools/cd_scripts/improved_e2e_test.sh

Purpose: Newer wrapper for release E2E testing that validates command-line options, optionally selects a release package to install, and delegates actual test execution to `tools/integration_tests/improved_run_e2e_tests.sh`.

Important APIs, types, and functions: Defines `log_info`, `log_error`, `usage`, parses long options with `getopt`, and builds an `ARGS` array. Supported options are `--local-run`, `--release-package-bucket`, `--release-version`, `--zonal`, `--output-dir`, and `--help`.

Control flow: The script enables `set -euo pipefail`, parses options, enforces release bucket/version unless `--local-run` is set, detects Debian/Ubuntu vs RHEL/CentOS from `/etc/os-release`, appends `--install-package-from-path` for package mode, sets package-level parallelism to 4, adds zonal/regional choice, output directory, excludes `cloud_profiler`, sets flake attempts to 3, then invokes the improved runner.

State and persistence behavior: Creates the output directory and may cause the delegated runner to install packages, run tests, and write logs. This wrapper itself mostly constructs arguments and logs to stdout/stderr.

Dependencies and integration points: Depends on GNU `getopt`, OS release metadata, `dpkg` or `uname`, release package bucket naming conventions, and `improved_run_e2e_tests.sh`. It is intended to replace or simplify the legacy `e2e_test.sh` startup flow.

Risks and test signals: Release version regex only accepts plain `MAJOR.MINOR.PATCH`, so beta or build metadata versions are rejected. RHEL detection checks ID/ID_LIKE for `rhel` or `centos` but not `rocky`. Stronger shell settings reduce silent failure. Final signal comes from the delegated runner's exit code and output directory artifacts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/improved_e2e_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/install_test.sh -->
# sources/user-network-fs/gcsfuse/tools/cd_scripts/install_test.sh

Purpose: Release installation test script that verifies the to-be-released gcsfuse package installs, older version installation works, and package manager upgrade returns to the latest release.

Important APIs, types, and functions: Shell flow installs Python 3.11 locally for gcloud compatibility, upgrades gcloud, reads release details from `gs://gcsfuse-release-packages/version-detail/details.txt`, configures apt/yum repositories, installs exact gcsfuse version, checks `gcsfuse --version`, removes it, installs old version `1.2.0`, upgrades, compares versions with `sort -V`, and uploads logs/success marker.

Control flow: After dependency setup and gcloud upgrade, OS detection via `details.txt` and VM name selects Debian/Ubuntu or RHEL/CentOS package manager logic. Debian path handles apt-key vs signed-by behavior based on VM name; RHEL path writes a yum repo file. Any logged "Failure" suppresses success marker upload.

State and persistence behavior: Installs build dependencies and Python under `$HOME/.local`, modifies package repositories, installs/removes/upgrades system `gcsfuse`, writes logs in home, and uploads artifacts to the release bucket.

Dependencies and integration points: Depends on gcloud, GCE metadata, release bucket details format, package repositories, apt/yum, Python source download, and package availability for version `1.2.0`.

Risks and test signals: String comparisons on VM names for apt-key policy are fragile. Python source build is slow and network-dependent. Some package install output redirection precedence may only redirect fallback commands. Test signal is `success.txt` plus logs uploaded under `installation-test/<vm>`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/install_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/package_gcsfuse.sh -->
# sources/user-network-fs/gcsfuse/tools/cd_scripts/package_gcsfuse.sh

Purpose: Release packaging VM script that builds gcsfuse Debian/RPM artifacts for supported architectures in Docker and uploads packages/logs to a GCS bucket.

Important APIs, types, and functions: `fetch_meta_data_value` reads GCE instance attributes. The script reads `RELEASE_VERSION`, `UPLOAD_BUCKET`, and `COMMIT_HASH`, normalizes `~` to `_` for Docker tag use, installs Docker/git/qemu support, clones gcsfuse, builds `tools/package_gcsfuse_docker` with build args `GCSFUSE_VERSION`, `ARCHITECTURE`, and `BRANCH_NAME`, runs the image to copy `/packages`, and uploads release files.

Control flow: Metadata fetch precedes package dependency installation. Docker Buildx creates a local image tagged by architecture/version. Container output is mounted into `$HOME/gcsfuse/release`, then recursively copied to `gs://$UPLOAD_BUCKET/v$RELEASE_VERSION`.

State and persistence behavior: Installs Docker and related packages on the VM, clones source, creates Docker images/containers, writes build logs, creates release package files locally, and uploads them to GCS.

Dependencies and integration points: Requires Ubuntu/Debian-style `apt`, Docker repository availability, GCE metadata attributes, gcloud auth, package Dockerfile, and release bucket permissions. Integrates with release package consumers such as E2E and install tests.

Risks and test signals: Assumes `dpkg --print-architecture` and Ubuntu Docker repo `focal` regardless of host release. Running privileged Docker/package setup is invasive. Build log upload provides diagnostic signal; package existence in the release bucket is the primary output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/package_gcsfuse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/requirements.in -->
# sources/user-network-fs/gcsfuse/tools/cd_scripts/requirements.in

Purpose: pip-compile input for Python dependencies needed by release CD scripts on platforms where crcmod is installed through pip.

Important APIs, types, and functions: Contains the single top-level requirement `crcmod`.

Control flow: No executable flow. Tooling such as `pip-compile` or direct pip install consumes it to produce/install hashed requirements.

State and persistence behavior: No runtime state. It influences generated `requirements.txt` and pip-installed user packages.

Dependencies and integration points: Used by `e2e_test.sh` on RHEL/CentOS paths via `pip3 install --require-hashes -r tools/cd_scripts/requirements.txt --user`; `crcmod` supports gsutil CRC32C validation for composite object downloads.

Risks and test signals: The `.in` file itself has no hash pin; hash enforcement occurs in generated `requirements.txt`. Missing or stale compiled requirements would break the release script pip install.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/requirements.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/flag_template_data_gen.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/flag_template_data_gen.go

Purpose: Converts parsed configuration parameter metadata into template data for generating pflag/viper flag declarations and config field bindings.

Important APIs, types, and functions: `flagTemplateData` embeds `Param` and adds `Fn`, `GoPath`, and `GoType`. `computeFlagTemplateData` maps every `Param` through `computeFlagTemplateDataForParam`. `capitalize` converts hyphen-separated names to exported Go identifier segments. `computeFlagTemplateDataForParam` normalizes default values, chooses pflag function names, escapes usage text, computes dotted Go config paths, and maps types through `getGoDataType`.

Control flow: For each parameter, a type switch handles scalar, duration, custom string-like, and slice types. Duration defaults are parsed with `time.ParseDuration` and emitted as nanosecond expressions. Config paths are split by `.`, each segment is capitalized by `-`, and joined back with dots for generated selector paths.

State and persistence behavior: Pure transformation of `Param` values; no file I/O. It mutates only the local copy of `Param` embedded into returned template data.

Dependencies and integration points: Consumed by `main.go` template execution. Depends on type names accepted by `parser.go` and `getGoDataType` from `type_template_data_gen.go`. Integrates with generated `config.go` and `config_test.go` templates.

Risks and test signals: Incorrect default formatting can produce invalid generated Go. `[]int`/`[]string` defaults are inserted inside literal braces without parsing. Duration parse errors are propagated. Test coverage is indirect through config generation tests rather than a dedicated file in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/flag_template_data_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/main.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/main.go

Purpose: Entry point for generating gcsfuse config Go source and tests from a params YAML file plus text templates.

Important APIs, types, and functions: Flags `-outDir`, `-paramsFile`, and `-templateDir` configure generation. `templateData` carries type template data, flag template data, machine type maps/groups, and a `Backticks` string for templates. `validateFlags`, `write`, `invertMachineTypeGroups`, `formatValue`, and `main` orchestrate parsing and rendering.

Control flow: `main` parses flags, validates required paths, parses params YAML, constructs type and flag template data, sorts both deterministically, inverts machine group mappings, and renders `config.tpl` and `config_test.tpl` to `config.go` and `config_test.go`. `write` creates output files and executes templates with `formatValue` and title-casing helpers.

State and persistence behavior: Writes generated files directly with `os.Create`, truncating existing outputs. It panics on validation, parse, or generation errors. No atomic write is used.

Dependencies and integration points: Depends on local parser/type/flag helpers, `cfg/shared` optimization types, Go `text/template`, `golang.org/x/text/cases`, and template files. Generated outputs are part of the gcsfuse config package contract.

Risks and test signals: `invertMachineTypeGroups` panics on duplicate machine mapping; parser validation also rejects duplicates, so panic is a defensive layer. `formatValue` treats exported strings ending in `()` as function calls, which is powerful but could misclassify values. Tests cover machine group inversion and duplicate panic behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/main_test.go

Purpose: Unit tests for `invertMachineTypeGroups`, verifying machine type to group mapping and duplicate detection.

Important APIs, types, and functions: `TestInvertMachineTypeGroups` defines table cases for empty maps, one-to-one, one-to-many, and duplicate machine membership across groups. It uses deferred `recover` to assert expected panics.

Control flow: Each subtest defers a panic checker, calls `invertMachineTypeGroups`, and compares the returned map when no panic is expected.

State and persistence behavior: No file or external state. All data is in-memory maps.

Dependencies and integration points: Depends on `testify/assert` and the generator main package. It validates a helper used before template rendering.

Risks and test signals: Good signal for duplicate group membership, but it does not exercise flag parsing, template execution, or `formatValue`. Panic-based error behavior is intentionally tested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/parser.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/parser.go

Purpose: YAML parser and validator for config generator params, including flag metadata, config paths, data types, deprecation settings, optimization rules, and machine type groups.

Important APIs, types, and functions: `Param` models individual params; `ParamsYAML` models top-level YAML. `parseParamsYAMLStr` uses `yaml.Decoder.KnownFields(true)`, then validates params and machine groups. Validation helpers include `checkFlagName`, `validateParam`, `isSorted`, `validateParams`, `validateForDuplicates`, `validateMachineTypeGroups`, and `validateForDuplicatesInSortedSlice`.

Control flow: YAML decoding rejects unknown fields. Param validation enforces sorted order, unique flag names/config paths, valid flag naming, deprecation warnings, required usage/type/config-path for non-deprecated params, supported data types, and valid bucket optimization types. Machine type group validation enforces kebab-case group names, non-empty sorted unique machine lists, and cross-group machine uniqueness.

State and persistence behavior: `parseParamsYAML` reads the file path held in global flag `paramsFile`; `parseParamsYAMLStr` is pure. No output files are written here.

Dependencies and integration points: Depends on `gopkg.in/yaml.v3`, `cfg/shared.OptimizationRules`, and generator code that consumes `ParamsYAML`. It is the schema gate for generated config source.

Risks and test signals: Sorting logic treats params with empty config paths specially for deprecated flags and can reject valid-looking reorderings. `checkFlagName` allows underscores despite comments saying hyphen-separated lower-case. Machine group map key order cannot be sorted-validated because Go maps lose order. Tests cover positive parsing, malformed YAML, duplicate fields, group validation, and invalid bucket types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/parser_test.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/parser_test.go

Purpose: Unit tests for params YAML parsing and validation in the config generator.

Important APIs, types, and functions: Tests cover `checkFlagName`, `validateMachineTypeGroups`, `validateForDuplicatesInSortedSlice`, and `parseParamsYAMLStr`. Positive parsing asserts machine groups and optimization rules for bucket-based, machine-based, profile, mixed, and absent optimization cases. Negative parsing checks malformed YAML, duplicate flag names, invalid group name, unsorted/duplicate/empty machine groups, and unsupported bucket type.

Control flow: Table-driven tests call validation helpers and assert errors or substrings. The success YAML fixture includes sorted config paths and machine groups, then subtests inspect parsed `Param.Optimizations`.

State and persistence behavior: No file I/O; YAML content is embedded strings. Tests do not mutate global flags.

Dependencies and integration points: Depends on `cfg/shared`, `testify/assert`, and `testify/require`. It provides schema-safety signal for generator input consumed by `main.go`.

Risks and test signals: Strong coverage of machine group validation and optimization parsing. Gaps include no test for param sorting failures in the visible subset, no duplicate config-path case, and no unknown-field assertion despite `KnownFields(true)`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/type_template_data_gen.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/type_template_data_gen.go

Purpose: Builds template data for generated nested Go config structs from dotted config paths in params YAML.

Important APIs, types, and functions: `fieldInfo` describes generated struct fields. `typeTemplateData` groups fields under a generated type. `capitalizeIdentifier` validates and exports config path segments, `getGoDataType` maps params YAML types to Go types, `computeFields` expands a single config path into parent/child field entries, and `constructTypeTemplateData` merges/sorts/compacts fields across params.

Control flow: Each non-deprecated param config path is split on dots. Starting from `Config`, each segment becomes an exported field; non-leaf segments become nested type names like `MetadataCacheConfig`, while leaf segments use mapped data types. Fields are grouped by containing type, sorted by field name, compacted, then type groups are sorted by type name.

State and persistence behavior: Pure in-memory transformation with no I/O. Deprecated params with empty config path are skipped.

Dependencies and integration points: Used by `main.go` before template rendering. It must stay consistent with parser-supported types and flag template Go paths.

Risks and test signals: `cfgSegmentRegex` uses `MatchString` without anchors, so a partially matching invalid string could pass validation. `slices.Compact` only removes adjacent equal `fieldInfo`, so prior sorting by field name is important but may not deduplicate fields that differ in non-key metadata. Test coverage is indirect unless other generator tests exercise emitted structs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/type_template_data_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/containerize_gcsfuse_docker/Dockerfile -->
# sources/user-network-fs/gcsfuse/tools/containerize_gcsfuse_docker/Dockerfile

Purpose: Multi-stage Dockerfile for building container images with gcsfuse installed, including a distroless runtime target and an Ubuntu/Debian runtime target.

Important APIs, types, and functions: Build args include `GO_VERSION`, `OS_VERSION`, `OS_NAME`, `GCSFUSE_VERSION`, `GCSFUSE_REPO`, and `BRANCH_NAME`. Stage `gcsfuse-package` clones gcsfuse, checks out a branch/tag, installs fpm via bundler, builds gcsfuse using `build_gcsfuse`, and packages a `.deb`. The `distroless` stage copies gcsfuse, mount helper, fusermount, and shell. The final OS stage installs the generated deb and fuse.

Control flow: Docker builds the package stage first. Consumers can target `distroless` explicitly or build the final Ubuntu/Debian image by supplying OS args. Both runtime targets define `CMD gcsfuse --key-file /key.json ... $BUCKET_NAME /gcs`.

State and persistence behavior: Build-time state includes cloned source, generated binaries, and package files. Runtime mounts a bucket into `/gcs` and expects host/container mount propagation and privileged FUSE access.

Dependencies and integration points: Depends on golang base image, Debian apt, Ruby/fpm packaging, GitHub source, gke distroless libc image, FUSE, and host Docker run options described in comments. Integrates with release/container samples rather than the Go test suite.

Risks and test signals: Requires privileged containers and key file mount. Final OS stage copies `*amd64.deb`, so non-amd64 builds may not work there. Distroless includes `/bin/sh` copied from build stage, which may be surprising. Runtime command uses environment variable expansion in shell form only if interpreted as shell; Dockerfile `CMD` shell form is used, so variable expansion is expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/containerize_gcsfuse_docker/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main.go -->
# sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main.go

Purpose: Standalone shared chunk cache garbage collector for gcsfuse, expiring least-recently-used `.bin` cache chunks, deleting previous `.bak` expirations, removing stale `.tmp` files, and cleaning empty directories.

Important APIs, types, and functions: CLI flags are `--cache-dir`, `--target-size-mb`, `--concurrency`, `--dry-run`, and `--debug`. `FileInfo` records path, atime, mtime, and size. `Manifest` stores `.bin`, `.bak`, `.tmp`, directories, total size, and scan duration. Core functions are `scanCache`, `removeBakFiles`, `removeOldTmpFiles`, `findLRUFiles`, `expireFiles`, `cleanupEmptyDirs`, and `printFileInfo`.

Control flow: `main` configures slog, requires `cache-dir`, scans the cache, deletes previous `.bak` files, compares total `.bin` size against target, selects oldest chunks by max(atime, mtime), renames selected `.bin` files to `.bin.bak`, removes `.tmp` files older than one hour, cleans empty directories, and logs completion. Dry run logs intended work without mutation.

State and persistence behavior: Mutates filesystem cache under `cache-dir` or `cache-dir/gcsfuse-shared-chunk-cache` if present. Expiration is a rename to `.bak` so existing file handles continue working until next run deletes the `.bak`. Parallel workers delete/rename files, using atomics for counters.

Dependencies and integration points: Linux/Unix filesystem stat access via `syscall.Stat_t` for atime/mtime, shared chunk cache file naming (`.bin`, `.tmp`, `.bak`), and external scheduling by users or services. It does not interact with GCS directly.

Risks and test signals: `cleanupEmptyDirs` uses `filepath.SplitList` to estimate depth, which is path-list separator based and likely not actual directory depth; cleanup order may be wrong. Atime availability depends on mount options such as noatime/relatime; mtime fallback mitigates new files. Concurrency flag values of zero or negative could deadlock or skip workers. Unit tests cover LRU selection, .bak deletion, tmp age threshold, extension filtering, and atime/mtime ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main_test.go

Purpose: Unit tests for the shared chunk cache garbage collector's scan, LRU selection, expiration, and cleanup behavior.

Important APIs, types, and functions: Tests include `TestLRUEviction`, `TestNoEvictionWhenBelowTarget`, `TestBakFileCleanup`, `TestTmpFileCleanup`, `TestOnlyBinFilesProcessed`, `TestMultipleFilesExpiredToReachTarget`, `TestLRUWithIdenticalAtimes`, `TestAtimeFallbackToMtime`, `TestTmpFileAtOneHourBoundary`, `TestEmptyTmpFileList`, and `TestLRUSortingOrderVerification`.

Control flow: Each test creates a temp cache directory and object-like subdirectory structure, writes files with controlled sizes and times via `os.Chtimes`, calls `scanCache`, `findLRUFiles`, `expireFiles`, `removeBakFiles`, or `removeOldTmpFiles`, and asserts filesystem outcomes.

State and persistence behavior: All state is temporary filesystem content under `t.TempDir`. Tests rename files to `.bak`, remove `.bak` and old `.tmp`, and validate recent temp files remain.

Dependencies and integration points: Depends on `testify/assert`/`require` and OS support for file timestamps. It validates behavior expected by external scheduled GC runs.

Risks and test signals: Strong signal for core eviction ordering and cleanup. Gaps include no dry-run CLI test, no `gcsfuse-shared-chunk-cache` subdirectory detection test, no concurrency edge cases, and no empty-directory cleanup depth verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_delete_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_delete_test.go

Purpose: Benchmark integration test that measures average gcsfuse file deletion latency and fails when it exceeds an expected threshold.

Important APIs, types, and functions: `benchmarkDeleteTest` implements `SetupB`, `TeardownB`, and `Benchmark_Delete`. Top-level `Benchmark_Delete` builds compatible flag sets and runs the benchmark via `benchmark_setup.RunBenchmarks`. `expectedDeleteLatency` is 1800 ms.

Control flow: Setup mounts gcsfuse and creates a test directory. The benchmark precreates `b.N` files, resets/stops the timer, and for each iteration times only `os.Remove` with the benchmark timer while also tracking wall-clock max latency. Average latency is `b.Elapsed()/b.N`; exceeding the threshold reports errors.

State and persistence behavior: Creates and deletes objects through the mounted filesystem. Teardown unmounts gcsfuse and saves logs on failure.

Dependencies and integration points: Depends on benchmark setup utilities, configured test bucket/mount, gcsfuse flags built from config, and Go benchmark runner semantics. It is skipped for presubmit via `setup.IgnoreTestIfPresubmitFlagIsSet`.

Risks and test signals: Threshold is environment-sensitive and set as anomaly detection rather than precise performance target. Precreating `b.N` files can be expensive for high benchtime. Provides direct signal on delete performance for flat/HNS/zonal-compatible configs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_rename_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_rename_test.go

Purpose: Benchmark integration test for gcsfuse rename latency.

Important APIs, types, and functions: `benchmarkRenameTest` provides `SetupB`, `TeardownB`, and `Benchmark_Rename`. Top-level `Benchmark_Rename` iterates flag sets and delegates to `benchmark_setup.RunBenchmarks`. `expectedRenameLatency` is 1900 ms.

Control flow: Setup mounts gcsfuse and creates a test directory. The benchmark creates `aN.txt` files, then renames each to `bN.txt`, timing only `os.Rename` in the benchmark timer and tracking maximum wall-clock iteration.

State and persistence behavior: Creates and renames files in the mounted bucket. Teardown unmounts and saves logs on failure.

Dependencies and integration points: Uses `setup.BuildFlagSets`, benchmark utilities, and test config from `setup_test.go`. Default configs include `--enable-atomic-rename-object=true`.

Risks and test signals: Rename behavior may differ by bucket type, atomic rename support, and client protocol. Threshold failures indicate regressions or infrastructure anomalies; detailed max iteration logging helps diagnose tail latency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_rename_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_stat_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_stat_test.go

Purpose: Benchmark integration test for stat latency on a mounted gcsfuse file.

Important APIs, types, and functions: `benchmarkStatTest` implements benchmark setup/teardown and `Benchmark_Stat`. Helper `createFilesToStat` creates `benchmarking/a.txt`. `expectedStatLatency` is 1100 ms.

Control flow: The benchmark creates one file, then repeatedly calls `operations.StatFile` on it. Only the stat call is measured by the benchmark timer; max wall-clock latency is tracked separately. Average above threshold is reported as benchmark error.

State and persistence behavior: Creates one test object and repeatedly reads metadata through the mount. Teardown unmounts and preserves logs on failure.

Dependencies and integration points: Depends on integration test operations helpers, benchmark runner, and default configs that disable stat cache (`--stat-cache-ttl=0`) to measure backend/stat path behavior.

Risks and test signals: Threshold is sensitive to network and bucket state. Because stat cache is disabled in defaults, this is more backend/metadata path signal than cache-hit signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/benchmark_stat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/setup_test.go

Purpose: TestMain and shared helpers for benchmarking integration tests.

Important APIs, types, and functions: Defines package globals `testEnv`, `mountFunc`, `mountDir`, and `rootDir`; `env` stores storage client, context, test directory, config, and bucket type. Helpers include `mountGCSFuseAndSetupTestDir` and `createFiles`. `TestMain` parses flags/config and initializes environment.

Control flow: `TestMain` reads config; if absent, it synthesizes benchmarking configs for stat, rename, and delete with flat/grpc variants. It creates a storage client, handles mounted-directory mode, sets up test bucket mount directories, selects static mounting, runs benchmarks, then cleans the GCS test directory.

State and persistence behavior: Creates a test directory in the bucket, mounts/unmounts gcsfuse via benchmark tests, and deletes GCS test data on completion. Global test environment is shared by benchmark files.

Dependencies and integration points: Depends on Cloud Storage client, integration setup/client/operations utilities, static mounting, and test suite config schema.

Risks and test signals: Benchmark files rely on shared global state initialized here. If cleanup fails, benchmark objects may remain. Fallback default config makes the package runnable without YAML but may drift from release config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/benchmarking/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/fallback_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/fallback_test.go

Purpose: Integration suites validating buffered-read fallback behavior when reader creation fails due to block pool limits or access pattern becomes random.

Important APIs, types, and functions: `fallbackSuiteBase` provides suite setup/teardown. `InsufficientPoolCreationSuite` tests no reader creation with insufficient global pool. `RandomReadFallbackSuite` tests random read fallback, small-file no fallback, and random-then-sequential restart. Top-level `TestInsufficientPoolCreationSuite` and `TestRandomReadFallbackSuite` run suites for configured flag sets.

Control flow: Suite setup configures log file, mounts gcsfuse, and sets mount directory. Tests truncate logs, create GCS-backed files, read with `O_DIRECT`, validate read contents against GCS, parse buffered-read logs, and assert fallback/restart/random seek fields.

State and persistence behavior: Creates test files in the mounted bucket, writes/truncates gcsfuse logs, and unmounts after suite. Log parsing is central test state.

Dependencies and integration points: Depends on setup/client/operations utilities, JSON read log parser, `testEnv` initialized by `setup_test.go`, and gcsfuse buffered read flags such as `--read-global-max-blocks`, block sizes, and kernel reader disabling.

Risks and test signals: Tests assert internal log messages/fields, so logging schema changes can fail tests even if behavior is correct. `O_DIRECT` may have platform/filesystem constraints. Strong signals include no log entry when reader creation fails, fallback flag after random reads, and restart after sequential pattern resumes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/fallback_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/helpers_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/helpers_test.go

Purpose: Shared helpers for buffered-read integration tests, covering file setup, direct reads, GCS validation, and buffered-read log parsing.

Important APIs, types, and functions: `Expected` captures expected log attributes. `readFileAndValidate` performs full or chunk reads and validates CRC32C or object chunk content. `validate` checks log entry timestamps, bucket/object names, and fallback flag. `setupFileInTestDir`, `parseBufferedReadLogs`, `parseAndValidateSingleBufferedReadLog`, `readAndValidateChunk`, and `induceRandomReadFallback` support the suites.

Control flow: Read helpers create expected metadata before the read, perform mounted filesystem reads using `O_DIRECT`, compare data with Cloud Storage, then record end timestamps. Log helpers open the configured log file and parse buffered read entries, expecting one entry for single-handle tests.

State and persistence behavior: Reads mounted files, creates test files via GCS client, opens log files, and depends on global `testEnv` and setup flags. It does not clean up itself.

Dependencies and integration points: Integrates Cloud Storage object validation, gcsfuse log parser `read_logs`, operations helpers, setup bucket selection including dynamic bucket mounts, and the buffered read test suites.

Risks and test signals: Timestamp assertions use seconds and only check start lower bound; delayed log flushing can affect parsing. CRC32C full-file validation gives strong data integrity signal. Random fallback induction assumes threshold and block-size behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/sequential_read_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/sequential_read_test.go

Purpose: Integration suite validating buffered reader behavior for sequential reads, mixed header/footer/body reads, and reads spanning buffer blocks.

Important APIs, types, and functions: `SequentialReadSuite` provides setup/teardown and test cases `TestSequentialRead`, `TestReadHeaderFooterAndBody`, and `TestReadSpanningTwoBlocks`. Top-level `TestSequentialReadSuite` runs the suite for mounted directory or configured flag sets.

Control flow: Suite setup configures logging and mounts gcsfuse. Tests truncate logs, create files of specific sizes, perform direct reads with specific chunk sizes/offsets, validate contents against GCS, parse exactly one buffered-read log entry, and assert no fallback/random seeks for sequential patterns.

State and persistence behavior: Creates bucket objects and reads through mounted files. Logs are truncated per case and parsed after closing handles where needed. Suite unmounts after completion and saves logs on failure.

Dependencies and integration points: Depends on helpers in `helpers_test.go`, `testEnv` from setup, gcsfuse buffered read flags, and integration setup utilities.

Risks and test signals: `O_DIRECT` and block alignment can be environment-sensitive. Header/footer/body test intentionally mixes random-looking reads on one handle but expects no fallback, making it a high-signal regression test for classifier behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/sequential_read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/setup_test.go

Purpose: Package-level TestMain and environment setup for buffered-read integration tests.

Important APIs, types, and functions: Defines constants `testDirName`, `testFileName`, `blockSizeInBytes`, and `GKETempDir`, globals `mountFunc`, `mountDir`, `rootDir`, and `testEnv`, plus `env` structure. `TestMain` builds default buffered-read configs when config file lacks them.

Control flow: Parses setup flags, reads config or synthesizes three config items for sequential reads, insufficient pool creation, and random fallback. It initializes context/storage client, handles mounted-directory mode, sets up test bucket directory, rewrites GKE-specific log paths for GCE, selects static mounting, runs tests, then cleans up GCS test directory.

State and persistence behavior: Creates Cloud Storage client and test directory, modifies config flag paths, and cleans test bucket directory after suite. Mount state is managed in individual suites.

Dependencies and integration points: Depends on `internal/util` for MiB, integration setup/client/static mounting/test suite utilities, and Cloud Storage.

Risks and test signals: Defaults hard-code trace log paths under `/gcsfuse-tmp`, which must be overridden or available. Shared globals couple all buffered-read test files. Cleanup at package end may leave objects if process exits early.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/cloud_profiler_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/cloud_profiler_test.go

Purpose: TestMain for Cloud Profiler integration tests, configuring unique service/version labels and mounting gcsfuse with profiler flags.

Important APIs, types, and functions: Constants define test directory, suffix, retry timings, and lexicographic ID alphabet. `getDecreasingString` generates a fixed-length string that sorts newer test identifiers earlier. `TestMain` prepares `testServiceName`, `testVersionName`, config flags, storage client, test environment, and static mount execution.

Control flow: `TestMain` parses setup flags, generates unique profiler service/version names, loads config or creates a default profiler config, substitutes `${PROFILE_LABEL}` and `${PROFILE_SERVICE_NAME}` placeholders when present, initializes Cloud Storage, handles mounted-directory mode, builds flag sets, sets up test dir, runs tests with static mounting, and cleans up the GCS directory.

State and persistence behavior: Creates global service/version identifiers, mounts gcsfuse with profiler enabled, creates a test bucket directory, and deletes it after tests. Cloud Profiler profiles are external GCP state and are queried by companion tests.

Dependencies and integration points: Depends on Cloud Storage, gcsfuse integration setup, static mounting, Cloud Profiler flags, and logger. It sets up globals consumed by `with_gcp_profiler_service_test.go`.

Risks and test signals: Cloud Profiler availability is eventual and external. The decreasing string is designed to reduce API pagination work by making newer deployments sort earlier. Default config enables multiple profiler types and is excluded from release wrapper due to stability TODO.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/cloud_profiler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/with_gcp_profiler_service_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/with_gcp_profiler_service_test.go

Purpose: Integration test that verifies a real Cloud Profiler profile appears for the gcsfuse service/version configured by the package TestMain.

Important APIs, types, and functions: `CloudProfilerSuite` defines `writeSingleRandomFile` to generate write load, `getGCPProjectID` to resolve project from metadata or environment, `checkIfProfileExistForServiceAndVersion` to page through Cloud Profiler API profiles, and `TestValidateProfilerWithActualService` to retry until a matching profile exists. `TestCloudProfilerSuite` runs the suite.

Control flow: The test obtains a project ID, creates a Cloud Profiler API client, then calls `operations.RetryUntil` for up to 10 minutes. Each retry writes a 100 MiB random file through the mount to stimulate profiling and scans profile pages for deployment target equal to `testServiceName` and version label equal to `testVersionName`.

State and persistence behavior: Writes large random files into the mounted bucket and relies on Cloud Profiler backend state. It does not delete individual load files directly; package cleanup removes the test directory.

Dependencies and integration points: Depends on GCE metadata or `GOOGLE_CLOUD_PROJECT`, Cloud Profiler v2 API, gcsfuse mount from TestMain, and service/version globals. Requires profiler API permissions and eventual profile ingestion.

Risks and test signals: `getGCPProjectID` shadows `projectID` inside the error branch and may return an empty outer variable if metadata fails but env is set, which is a correctness risk. Pagination uses errors for early exit, including a sentinel success break. The strong signal is a matching profile from the real API; failures may be infrastructure, permission, or eventual-consistency related.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/with_gcp_profiler_service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/concurrent_listing_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/concurrent_listing_test.go

Purpose: Integration suite stressing concurrent directory listing, lookup/stat, file mutations, directory mutations, and move operations to detect gcsfuse deadlocks and race conditions.

Important APIs, types, and functions: Constants set iteration counts for heavy, medium, and light operations. `concurrentListingTest` embeds `suite.Suite` and carries flags, client, context, and base test name. `createDirectoryStructureForTestCase` creates an explicit directory with two files. Test cases include `Test_OpenDirAndLookUp`, `Test_Parallel_ReadDirAndLookUp`, `Test_MultipleConcurrentReadDir`, `Test_Parallel_ReadDirAndFileOperations`, `Test_Parallel_ReadDirAndDirOperations`, `Test_Parallel_ReadDirAndFileEdit`, `Test_MultipleConcurrentOperations`, `Test_ListWithMoveFile`, `Test_ListWithMoveDir`, and `Test_StatWithNewFileWrite`. `TestConcurrentListing` mounts per flag set and runs the suite.

Control flow: Each test creates its own case directory under the mounted test root, starts goroutines for repeated operations, waits through a `sync.WaitGroup`, and fails on timeout as a possible deadlock/race. The top-level runner handles mounted-directory mode specially; otherwise it iterates built flag sets, configures log file, mounts, runs the suite inside `t.Run` to allow parallel subtests to complete, then unmounts.

State and persistence behavior: Creates, renames, edits, moves, stats, opens, and deletes files/directories through the gcsfuse mount. Saves logs on failure and relies on package-level setup/cleanup outside this file for bucket lifecycle.

Dependencies and integration points: Depends on package globals from the concurrent operations setup file, integration `operations` and `setup` utilities, Cloud Storage client, and testify suite/assert/require. It is sensitive to gcsfuse directory cache, list, lookup, and rename/move internals.

Risks and test signals: Calling `require` assertions inside goroutines can be problematic because failures are reported from non-test goroutines; however timeouts and error assertions still expose many failures. Long timeouts reflect slow listing without kernel list cache. Strong signal is absence of deadlock under parallel listings and mutations across multiple flag sets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/concurrent_listing_test.go -->
