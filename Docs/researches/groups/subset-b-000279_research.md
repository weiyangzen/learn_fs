# Research Report: subset-b-000279

Grouped report for source-tree-aligned research outputs. Each section is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/converter.go -->
# sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/converter.go

Purpose: Implements native image-layer conversion that stores each eStargz layer's TOC in a separate OCI image instead of only embedding it in the layer. The public conversion constructors wrap normal eStargz conversion and return a finalize callback that writes an external TOC manifest under the original reference plus `-esgztoc`.
Important APIs/types/functions: `LayerConvertFunc`, `LayerConvertWithLayerAndCommonOptsFunc`, `LayerConvertLossLessConfig`, `LayerConvertLossLessFunc`, `layerConvert`, `layerLossLessConvertFunc`, `calcUncompression`, `writeTOCTo`, `createManifest`, and `writeJSON`. The code depends on containerd `converter.ConvertFunc`, `content.Store`, OCI descriptors/manifests, eStargz compressors, and containerd GC labels.
Control flow: each layer conversion allocates an external-TOC gzip compressor, delegates actual layer conversion to the selected eStargz converter, records the converted layer digest, writes the TOC blob to the content store, and later `finalize` emits a sorted manifest whose layers are TOC blobs annotated with their target layer digests. The lossless path reads the original layer, appends tar content through `AppendTarLossLess`, computes original and converted uncompressed digests in parallel, rejects diffID/size drift, commits the converted blob, and annotates the descriptor.
State and persistence: converted layer blobs, TOC blobs, config JSON, and manifest JSON are written into containerd content with refs such as `convert-estargz-from-*`, `external-toc*`, and `write-json-ref*`. The in-memory `esgzDigest2TOC` map accumulates layer-to-TOC state until `finalize`; manifest labels preserve content-store GC reachability.
Dependencies and integration points: used by `ctr-remote image optimize/convert` style flows, must be paired with Docker-to-OCI conversion so layer annotations survive, and is consumed by the external TOC fetcher. It integrates with containerd image conversion, OCI media types, eStargz annotations, and registry references.
Risks: the shared `esgzDigest2TOC` map is not concurrency-protected if a caller invokes one converter instance concurrently. `calcUncompression` closes its info channel on decompression errors, so a receive can produce a zero-value digest without a direct error path. TOC refs use wall-clock string data, and all platforms are combined into one TOC image. Tests should cover repeated layers, concurrent conversion, and decompression failure handling.
Test signals: covered by unit tests in `converter_test.go` for normal external TOC emission and lossless diffID preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/converter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/converter_test.go -->
# sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/converter_test.go

Purpose: Unit-tests external TOC eStargz conversion without requiring a daemon. It validates both standard eStargz conversion and keep-diff-id lossless conversion on the shared hello image fixture.
Important APIs/types/functions: `TestLayerConvertFunc`, `TestLayerConvertLossLessFunc`, and helper `rootFS`. Tests use containerd `converter.DefaultIndexConvertFunc`, `images.Walk`, `images.Config`, `images.RootFS`, gzip readers, OCI manifests, and the eStargz TOC digest annotation.
Control flow: each test prepares a sample image, converts it with Docker-to-OCI enabled, calls the returned finalize callback, confirms the generated TOC image reference has the `-esgztoc` suffix, walks the converted image to collect layers and TOC annotations, reads the external TOC manifest from content, and verifies every converted layer has a corresponding external TOC layer annotation. The lossless test additionally compares rootfs diffIDs and recomputes layer diffIDs by gzip-decompressing converted layers.
State and persistence: all content is stored in the fixture content store. Tests mutate only in-memory maps of layer digests, wanted diffIDs, and discovered TOC digests.
Dependencies and integration points: exercises the converter package through containerd's index converter rather than calling lower-level helpers directly, which gives coverage for multi-descriptor traversal and annotation propagation.
Risks: assertions confirm presence and mapping but do not fetch/decode TOC blobs, test error paths, or cover duplicate layer digests/platform-specific TOC manifests. The gzip-only diffID check assumes converted lossless layers are gzip.
Test signals: strong signal that the public converter constructors produce a usable external TOC image and preserve rootfs diffIDs in lossless mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/converter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/fetcher.go -->
# sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/fetcher.go

Purpose: Provides a remote eStargz decompressor hook that fetches an external TOC blob from a companion TOC image in a registry.
Important APIs/types/functions: `NewRemoteDecompressor`, `fetchTOCBlob`, and `fetchTOCBlobFromManifest`. It uses containerd remote resolvers/fetchers, Docker registry hosts, platform manifest fetching, OCI descriptors, and the shared `getTOCReference` suffix convention.
Control flow: the decompressor lazily constructs a Docker resolver constrained to the expected host, resolves `<image>-esgztoc`, fetches the platform manifest, scans manifest layers for the `containerd.io/snapshot/stargz/layer.digest` annotation that matches the requested layer digest, and returns the fetched TOC bytes.
State and persistence: no local persistence or cache is implemented; each lazy decompressor invocation can resolve and fetch the manifest/blob again.
Dependencies and integration points: pairs directly with `converter.go`'s external TOC image layout and integrates with stargz snapshotter source registry hosts plus containerd remote fetch APIs.
Risks: only supports the hard-coded `-esgztoc` location and default platform manifest lookup. Host mismatch is treated as an error, which is good for safety but limits unusual resolver setups. Missing annotations return a generic `TOC not found`, and manifest caching is noted as a TODO.
Test signals: no direct tests in this subset; integration coverage is implied by external TOC integration tests that pull `--estargz-external-toc` images.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/externaltoc/fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/nativeconverter.go -->
# sources/cloud-native/stargz-snapshotter/nativeconverter/nativeconverter.go

Purpose: Empty package anchor for `nativeconverter`; it exists so the package directory passes Go linting even though implementation lives in subpackages.
Important APIs/types/functions: no exported APIs, types, or functions. The only effective declaration is `package nativeconverter`.
Control flow: none.
State and persistence: none.
Dependencies and integration points: establishes the package namespace for tooling and import path stability.
Risks: behavioral risk is negligible; deleting it could break lint or package discovery if the directory otherwise has no Go source.
Test signals: no direct tests required beyond package/lint checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/nativeconverter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/zstdchunked/zstdchunked.go -->
# sources/cloud-native/stargz-snapshotter/nativeconverter/zstdchunked/zstdchunked.go

Purpose: Converts image layers into zstd:chunked eStargz-compatible blobs so the snapshotter can lazy-pull zstd compressed random-access layers.
Important APIs/types/functions: `zstdCompression`, `LayerConvertFunc`, `LayerConvertWithLayerOptsFunc`, `LayerConvertFuncWithCompressionLevel`, `LayerConvertWithLayerOptsFuncWithCompressionLevel`, and `convertMediaTypeToZstd`. It uses eStargz build options, `zstdchunked.Compressor/Decompressor`, containerd content writers, uncompress conversion, and OCI media types.
Control flow: conversion skips non-layer descriptors, uncompresses compressed inputs if needed, copies labels from the original content record, builds an eStargz blob with a zstd:chunked compressor and metadata map, writes the new blob to containerd content, commits it with the uncompressed digest label, converts media type to OCI zstd, and annotates TOC digest, uncompressed size, manifest checksum, and manifest position. Per-layer options are selected by original descriptor digest.
State and persistence: writes converted blobs to the content store under `convert-zstdchunked-from-*`, persists labels and layer annotations, and captures zstd chunk metadata through the compressor metadata map.
Dependencies and integration points: intended for containerd image converter pipelines with Docker-to-OCI conversion enabled. It bridges eStargz chunk layout, klauspost zstd encoder levels, OCI layer media types, and stargz snapshotter metadata annotations.
Risks: `opts = append(opts, ...)` mutates the local slice and may alias caller-provided backing arrays. Per-layer selection by digest cannot distinguish duplicate layers with identical digests but different intended options. Conversion depends on content-store labels from the original descriptor even after uncompressing.
Test signals: unit coverage verifies that conversion produces OCI zstd layers and required annotations, but does not validate decompression equivalence or error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/zstdchunked/zstdchunked.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/zstdchunked/zstdchunked_test.go -->
# sources/cloud-native/stargz-snapshotter/nativeconverter/zstdchunked/zstdchunked_test.go

Purpose: Unit-tests zstd:chunked layer conversion through containerd's index conversion path.
Important APIs/types/functions: `TestLayerConvertFunc` invokes `LayerConvertFunc` with prioritized files, `converter.DefaultIndexConvertFunc`, `images.Walk`, and metadata constants from eStargz and zstdchunked.
Control flow: the test prepares a hello fixture, converts it with Docker-to-OCI enabled, walks the converted image tree, records media types and layer annotations, then asserts the zstd media type and TOC/manifest annotations exist.
State and persistence: all image content lives in the fixture content store; the test only accumulates observed media types and annotations in maps.
Dependencies and integration points: validates the public converter in the same shape used by higher-level image conversion commands.
Risks: the test checks metadata presence but not chunk manifest correctness, rootfs equivalence, selected zstd level, duplicate layer behavior, or actual lazy-read compatibility.
Test signals: good smoke coverage for conversion plumbing and annotation propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/zstdchunked/zstdchunked_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/recorder/recorder.go -->
# sources/cloud-native/stargz-snapshotter/recorder/recorder.go

Purpose: Provides a small thread-safe JSON log recorder for recording file/layer access entries.
Important APIs/types/functions: `Entry` with `Path`, optional `ManifestDigest`, and optional `LayerIndex`; `New(io.Writer)`; and `(*Recorder).Record`.
Control flow: `New` wraps an output writer in `json.Encoder`; `Record` serializes access through a mutex and emits one JSON object per call.
State and persistence: state is the encoder and mutex. Persistence is delegated to the caller-provided writer, so durability, buffering, and close semantics are external.
Dependencies and integration points: useful for optimizer/access tracing flows that need newline-delimited JSON access records. It only depends on Go standard library `encoding/json`, `io`, and `sync`.
Risks: no nil checks for recorder, writer, or entry; writer errors are returned from `Encode`. Because entries are written immediately and locked, high-frequency recording can become serialized on one mutex.
Test signals: no direct tests in this subset; behavior is simple enough for targeted unit tests around concurrent `Record` calls and JSON shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/recorder/recorder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/config-containerd/etc/containerd-stargz-grpc/config.toml -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/config-containerd/etc/containerd-stargz-grpc/config.toml

Purpose: Benchmark snapshotter config toggling prefetch and exposing a debug socket.
Important APIs/types/functions: declarative configuration keys include `noprefetch` and `debug_address`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Used by `hello-bench/reboot_containerd.sh`, which rewrites `noprefetch` before starting `containerd-stargz-grpc`.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/config-containerd/etc/containerd-stargz-grpc/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/config-containerd/etc/containerd/config.toml -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/config-containerd/etc/containerd/config.toml

Purpose: Containerd benchmark config registering the stargz proxy snapshotter.
Important APIs/types/functions: declarative configuration keys include `version = 2`, `[proxy_plugins.stargz]`, socket `address`, and exported `root`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Containerd loads it during benchmark node startup so `ctr-remote` can use the remote snapshotter.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/config-containerd/etc/containerd/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/config-podman/etc/containers/policy.json -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/config-podman/etc/containers/policy.json

Purpose: Podman benchmark signature policy accepting test images without signature enforcement.
Important APIs/types/functions: declarative configuration keys include JSON `default` policy with `insecureAcceptAnything`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Consumed by containers/image inside the Podman benchmark container.
Risks: Intentionally insecure and suitable only for benchmark/test environments.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/config-podman/etc/containers/policy.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/config-podman/etc/stargz-store/config.toml -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/config-podman/etc/stargz-store/config.toml

Purpose: Podman benchmark stargz-store config with a prefetch toggle.
Important APIs/types/functions: declarative configuration keys include `noprefetch`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Rewritten by `hello-bench/reboot_store.sh` before starting `stargz-store`.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/config-podman/etc/stargz-store/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/prepare.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/prepare.sh

Purpose: Prepares benchmark image variants in a target repository before timing runs.
Important APIs/types/functions: environment variables `DISABLE_ESTARGZ`, paths to `hello.py` and `reboot_containerd.sh`; no reusable shell functions.
Control flow: validates arguments, starts plain containerd without stargz, then runs `hello.py --op=prepare` for selected images.
State and persistence: pushes legacy, eStargz, no-optimize, and zstdchunked image tags to the requested registry via `hello.py`.
Dependencies and integration points: depends on containerd/ctr-remote/nerdctl/crane availability inside the benchmark container.
Risks: argument expansion uses unquoted image lists; registry side effects are persistent and require credentials/environment to be correct.
Test signals: used as a setup step for benchmark runs; failures surface as missing target images.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/prepare.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/reboot_containerd.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/reboot_containerd.sh

Purpose: Resets and restarts the containerd benchmark environment with or without stargz lazy pulling.
Important APIs/types/functions: `retry`, `kill_all`, and `cleanup`; env flags `DISABLE_PREFETCH`, `DISABLE_ESTARGZ`, `LOG_FILE`.
Control flow: kills existing daemons, removes containerd and snapshotter state, rewrites `noprefetch`, optionally starts `containerd-stargz-grpc`, then starts containerd and waits for `ctr`/`ctr-remote version`.
State and persistence: destructively clears `/var/lib/containerd` and `/var/lib/containerd-stargz-grpc`; may append snapshotter logs to a provided file.
Dependencies and integration points: integrates benchmark configs, system daemons, FUSE mounts, and `ctr-remote` fallback to `ctr`.
Risks: uses broad `ps|grep|kill -9` matching and `rm -rf` on daemon roots, so it must only run in disposable benchmark nodes.
Test signals: benchmark modes rely on it to isolate each workload and validate daemon readiness.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/reboot_containerd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/reboot_store.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/reboot_store.sh

Purpose: Resets and starts Podman plus stargz-store benchmark storage.
Important APIs/types/functions: `retry`, `kill_all`, `cleanup`; env flags `DISABLE_PREFETCH`, `DISABLE_ESTARGZ`, and `LOG_FILE`.
Control flow: kills store processes, unmounts/removes store data, resets Podman, rewrites store config, writes Podman `storage.conf`, optionally starts `stargz-store`, and waits for the pool link.
State and persistence: clears `/var/lib/stargz-store`, rewrites `/etc/containers/storage.conf`, and resets Podman state.
Dependencies and integration points: integrates Podman overlay storage `additionallayerstores` with stargz-store's mounted reference store.
Risks: destructive cleanup and broad process killing require isolated containers; failed unmounts can leave state behind.
Test signals: exercised by benchmark mode `BENCHMARK_RUNTIME_MODE=podman`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/reboot_store.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/run.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/run.sh

Purpose: Runs randomized benchmark samples across legacy, eStargz no-prefetch, eStargz, and zstdchunked modes.
Important APIs/types/functions: mode constants, `cleanup`, `output`, and `measure`; env `BENCHMARK_RUNTIME_MODE`, `BENCHMARK_SAMPLES_NUM`, `BENCHMARK_PROFILE`.
Control flow: selects containerd or Podman reboot script, prints host specs, randomizes image/mode workload order per sample, reboots runtime per workload, runs `hello.py --op=run`, checks remote snapshot logs for lazy modes, and emits JSON array fragments prefixed by `BENCHMARK_OUTPUT:`.
State and persistence: creates temporary workload/log files and `/tmp/hello-bench-output`; repeatedly clears runtime state through reboot scripts.
Dependencies and integration points: depends on `script/util/utils.sh` for `check_remote_snapshots`, the `hello.py` runner, and benchmark configs.
Risks: `sort -R` creates nondeterministic order by design; shell word splitting of image lists requires simple image names; one bad workload exits the entire run.
Test signals: consumed by `script/benchmark/test.sh`, which captures and formats its output.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/elasticsearch/elasticsearch.yml -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/elasticsearch/elasticsearch.yml

Purpose: Minimal Elasticsearch benchmark override forcing a single-node cluster.
Important APIs/types/functions: declarative configuration keys include `discovery.type: single-node`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Bind-mounted by `hello.py` when benchmarking `elasticsearch:8.1.1`.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/elasticsearch/elasticsearch.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/gcc/main.c -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/gcc/main.c

Purpose: Tiny C workload used by the GCC benchmark image.
Important APIs/types/functions: `main` prints `hello` with `printf`.
Control flow: compiled and run inside the `gcc:11.2.0` container by `hello.py` stdin commands.
State and persistence: no persistent state.
Dependencies and integration points: depends on a C compiler in the benchmark image and bind-mounted source directory.
Risks: only validates startup and simple compilation, not meaningful application behavior.
Test signals: benchmark succeeds when compile/run exits zero and prints output.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/gcc/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/go/main.go -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/go/main.go

Purpose: Tiny Go workload used by the Go benchmark image.
Important APIs/types/functions: `main` prints `hello` with `fmt.Println`.
Control flow: run by `go run main.go` from `hello.py` inside the `golang:1.18` container.
State and persistence: no persistent state.
Dependencies and integration points: depends on bind-mounted source and Go toolchain in the image.
Risks: only measures toolchain/container startup, not application complexity.
Test signals: benchmark succeeds when `go run` exits zero.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/go/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/hello.py -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/hello.py

Purpose: Core benchmark driver for preparing optimized image variants and timing pull/create/start for a catalog of workloads.
Important APIs/types/functions: classes `RunArgs`, `Bench`, `BenchRunner`, `ContainerdController`, `PodmanController`; helpers `format_repo`, `genargs_for_optimization`, `tmp_copy`, and CLI `main`.
Control flow: parses CLI flags, chooses runtime controller, prepares images by copying/or optimizing to mode-specific tags, or runs benchmark iterations by pulling images, creating containers with command/stdio/wait-line strategies, starting them, recording elapsed times, cleaning up, and printing JSON rows with `BENCHMARK_OUTPUT:`.
State and persistence: uses a temporary directory for copied mounts, creates/pushes images in external registries, creates/removes runtime containers and images, and can write pprof output under `/tmp/hello-bench-output`.
Dependencies and integration points: integrates ctr/ctr-remote, nerdctl, crane, Podman, optimizer command flags, benchmark fixture files, and specific image command expectations.
Risks: many commands are shell-formatted strings with limited quoting; assertions abort on nonzero commands; wait-line loops can hang if stdout stalls; benchmark catalog versions are fixed and may age.
Test signals: covered by benchmark scripts rather than unit tests; output is post-processed by tools under `script/benchmark/tools`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/hello.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/test.sh

Purpose: Builds an isolated Docker Compose benchmark node, runs hello-bench, and formats result artifacts.
Important APIs/types/functions: uses env `BENCHMARK_TARGETS`, `BENCHMARK_RUNTIME_MODE`, `BENCHMARK_RESULT_DIR`, `BENCHMARK_LOG_DIR`; defines `cleanup`.
Control flow: builds the base and node images, copies runtime-specific configs, starts a privileged compose service, executes `hello-bench/run.sh` inside it, collects `/tmp/hello-bench-output`, archives logs, runs format/plot/percentile/table/csv tools, then tears down compose volumes.
State and persistence: creates temporary Dockerfile/context/compose file, Docker images, volumes, output directory, and archived log artifacts.
Dependencies and integration points: depends on Docker BuildKit, docker compose, benchmark configs, jq/wget/crane in the node image, and all benchmark tools.
Risks: requires privileged containers and host Docker access; formatting failures are separated from run failures but still mark failure; compose cleanup is destructive to benchmark volumes.
Test signals: primary benchmark entrypoint; success produces `result.json`, graphs, percentile data, markdown table, CSV, and logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/csv.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/csv.sh

Purpose: Converts benchmark JSON rows into a compact CSV table by image, operation, and mode.
Important APIs/types/functions: sources `util.sh`; uses `min_samples` and `percentile`; env `TARGET_MODES`, `TARGET_IMAGES`.
Control flow: reads JSON from stdin into a temp file, determines modes/images, computes the common minimum sample count across mode/image combinations, then emits pull/create/run rows with percentile values.
State and persistence: stores stdin in a temp file and uses `util.sh`'s shared percentile temp file.
Dependencies and integration points: depends on `jq`, Python/numpy through `util.sh`, and well-formed benchmark JSON.
Risks: `min_samples` in `util.sh` references global `IMGNAME`, so callers must preserve that variable name; empty sample sets can break numpy percentile.
Test signals: indirectly exercised by `benchmark/test.sh` formatting stage.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/csv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/format.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/format.sh

Purpose: Extracts the JSON benchmark payload from noisy run logs.
Important APIs/types/functions: constant `OUTPUT_MARK=BENCHMARK_OUTPUT:` plus a grep/sed pipeline.
Control flow: filters stdin for marked lines, strips the prefix, and repairs trailing comma/newline combinations to produce a JSON array.
State and persistence: no persistent state.
Dependencies and integration points: consumed by `benchmark/test.sh` before plot/table/CSV generation.
Risks: fragile to changed output marker or JSON formatting; grep exits nonzero if no rows exist under `set -e`.
Test signals: validated when downstream `jq`-based tools accept the formatted JSON.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/format.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/percentiles.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/percentiles.sh

Purpose: Creates per-image percentile CSV/data/gnuplot outputs for benchmark timings.
Important APIs/types/functions: sources `util.sh`; defines gnuplot `template`; env `TARGET_MODES`, `TARGET_IMAGES`, `BENCHMARK_PERCENTILES_GRANULARITY`.
Control flow: reads JSON from stdin, chooses modes/images and common sample count, writes raw data, plot files, PNG graphs, and CSV files for pull/create/run percentiles across a configured granularity.
State and persistence: creates `raw`, `plt`, `png`, and `csv` subdirectories under the output directory.
Dependencies and integration points: depends on jq, Python/numpy, gnuplot, and benchmark JSON fields.
Risks: uses `mkdir` without `-p`; rerunning into an existing directory with those subdirs fails. Random sample selection in `percentile` means outputs can vary.
Test signals: run by `benchmark/test.sh` after successful benchmark execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/percentiles.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/plot.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/plot.sh

Purpose: Generates a stacked histogram PNG comparing pull/create/run time per image and mode.
Important APIs/types/functions: sources `util.sh`; writes `result.plt`, `result.png`, and per-image `.dat` files.
Control flow: reads JSON, computes common sample count, writes a gnuplot script with one histogram per image, writes data rows for each mode, and invokes gnuplot.
State and persistence: persists plot/data files in the specified output directory.
Dependencies and integration points: depends on jq, Python/numpy, and gnuplot.
Risks: image names are sanitized only for `/` and `:`, and gnuplot labels may still be awkward; percentile randomness can make plots non-reproducible.
Test signals: called by `benchmark/test.sh` formatting stage.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/plot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/table.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/table.sh

Purpose: Renders benchmark JSON as a markdown table grouped by image.
Important APIs/types/functions: sources `util.sh`; env `TARGET_MODES`, `TARGET_IMAGES`.
Control flow: reads JSON from stdin, computes common sample count, prints a markdown report header, then emits pull/create/run percentile rows per mode for each image.
State and persistence: no persistent state beyond temporary JSON/stdin file.
Dependencies and integration points: depends on jq and Python/numpy through `util.sh`.
Risks: header text is hard-coded to a GitHub Actions Ubuntu runner; table separator is minimal markdown and assumes downstream renderer tolerance.
Test signals: used by `benchmark/test.sh` to create `result.md`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/table.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/util.sh -->
# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/util.sh

Purpose: Shared percentile/sample helpers for benchmark post-processing.
Important APIs/types/functions: global `PERCENTILE`, `CALCTEMP`; functions `samples_num`, `min_samples`, and `percentile`.
Control flow: functions filter benchmark JSON with jq, compute sample counts, randomly select equal sample counts, sort values, and call Python/numpy percentile calculation.
State and persistence: creates one temp file for percentile inputs but never removes it in this script.
Dependencies and integration points: sourced by csv/plot/table/percentiles tools; requires jq and Python with numpy.
Risks: `min_samples` uses `IMGNAME` instead of its `IMAGE` parameter, coupling it to caller loop variable names. Numpy `interpolation` argument may warn or change under newer numpy versions.
Test signals: indirectly tested by every benchmark formatting path.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/benchmark/tools/util.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/policy.json -->
# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/policy.json

Purpose: CRI-O test image policy accepting unsigned images.
Important APIs/types/functions: declarative configuration keys include JSON default policy `insecureAcceptAnything`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Installed into CRI-O test images for controlled local registry pulls.
Risks: Intentionally insecure outside isolated tests.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/policy.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/registries.conf -->
# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/registries.conf

Purpose: CRI-O containers/image registry config enabling stargz-store auth helper.
Important APIs/types/functions: declarative configuration keys include `unqualified-search-registries` and `additional-layer-store-auth-helper`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Works with CRI-O, containers/image, and stargz-store helper for additional layer store access.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/registries.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/storage.conf -->
# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/storage.conf

Purpose: CRI-O storage config using overlay plus stargz-store as an additional layer store.
Important APIs/types/functions: declarative configuration keys include `driver`, `graphroot`, `runroot`, and `additionallayerstores`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Mounted into CRI-O test nodes so lazy layers can be served from `/var/lib/stargz-store/store:ref`.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/storage.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/stargz-store/config.toml -->
# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/stargz-store/config.toml

Purpose: Placeholder stargz-store config for CRI-O test images.
Important APIs/types/functions: declarative configuration keys include empty/comment-only config. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Scripts append resolver and metadata settings as needed before starting stargz-store.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/stargz-store/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/systemd/system/stargz-store.service -->
# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/systemd/system/stargz-store.service

Purpose: Systemd unit that starts stargz-store before CRI-O.
Important APIs/types/functions: declarative configuration keys include `After`, `Before`, `Type=notify`, `ExecStart`, `ExecStopPost`, and restart policy. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Ensures the additional layer store is mounted before `crio.service` starts.
Risks: Stop cleanup runs a direct `umount`; failures or busy mounts can leave state for later tests.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/systemd/system/stargz-store.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/usr/local/bin/entrypoint -->
# sources/cloud-native/stargz-snapshotter/script/config-cri-o/usr/local/bin/entrypoint

Purpose: Entrypoint for privileged CRI-O test containers using systemd.
Important APIs/types/functions: cgroup-v2 setup block, sysctl/iptables host tweaks, and generated `demo.target`.
Control flow: enables nested cgroups, configures loopback NAT needed by CRI-O tests, writes a systemd target wanting stargz-store and CRI-O, then execs `/sbin/init` for that target.
State and persistence: writes `/lib/systemd/system/demo.target` and mutates sysctl/iptables inside the privileged container.
Dependencies and integration points: integrates Docker-in-Docker style cgroup setup, CRI-O, systemd, and stargz-store service.
Risks: requires privileged container permissions; iptables/sysctl changes are test-environment-specific.
Test signals: used by CRI-O test images built in `script/cri-o/test.sh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config-cri-o/usr/local/bin/entrypoint -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config/etc/containerd-stargz-grpc/config.toml -->
# sources/cloud-native/stargz-snapshotter/script/config/etc/containerd-stargz-grpc/config.toml

Purpose: Kind/containerd snapshotter config enabling CRI-based keychain forwarding.
Important APIs/types/functions: declarative configuration keys include `[cri_keychain] enable_keychain` and `image_service_path`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Requires kubelet to use the snapshotter image-service endpoint so credentials can be proxied to containerd.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config/etc/containerd-stargz-grpc/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config/etc/containerd/config.toml -->
# sources/cloud-native/stargz-snapshotter/script/config/etc/containerd/config.toml

Purpose: Containerd config for kind nodes using stargz snapshotter by default.
Important APIs/types/functions: declarative configuration keys include CRI containerd `snapshotter=stargz`, `disable_snapshot_annotations=false`, runc runtimes, and stargz proxy plugin. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Loaded by kind-style node images to route CRI image/layer operations through stargz snapshotter.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config/etc/containerd/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config/etc/systemd/system/stargz-snapshotter.service -->
# sources/cloud-native/stargz-snapshotter/script/config/etc/systemd/system/stargz-snapshotter.service

Purpose: Systemd unit for standalone `containerd-stargz-grpc`.
Important APIs/types/functions: declarative configuration keys include `Before=containerd.service`, notify type, `ExecStart`, restart policy. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Ensures the snapshotter socket is ready before containerd starts.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config/etc/systemd/system/stargz-snapshotter.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config/usr/local/bin/kind-entrypoint.sh -->
# sources/cloud-native/stargz-snapshotter/script/config/usr/local/bin/kind-entrypoint.sh

Purpose: Kind node entrypoint wrapper that enables cgroup-v2 nesting before running the requested command.
Important APIs/types/functions: cgroup-v2 controller setup block and final `exec $@`.
Control flow: moves existing root cgroup processes into `/init`, enables subtree controllers, then delegates to the original entrypoint command.
State and persistence: mutates cgroup files inside privileged kind node containers.
Dependencies and integration points: copied from Docker-in-Docker patterns and used by kind-compatible node images.
Risks: requires privileges and cgroup v2; `$@` is intentionally unquoted in source and could split unusual arguments.
Test signals: validated indirectly by kind/CRI tests that boot nodes successfully.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/config/usr/local/bin/kind-entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/config.containerd.transfer.toml -->
# sources/cloud-native/stargz-snapshotter/script/cri-containerd/config.containerd.transfer.toml

Purpose: Containerd CRI config enabling stargz both as snapshotter and transfer-service unpack target.
Important APIs/types/functions: declarative configuration keys include CRI snapshotter, transfer `unpack_config` entries, and stargz proxy plugin export `enable_remote_snapshot_annotations`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Used when `TRANSFER_SERVICE=true` in CRI containerd tests to cover containerd transfer service paths.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/config.containerd.transfer.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/const.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-containerd/const.sh

Purpose: Defines shared Docker image names for CRI containerd tests.
Important APIs/types/functions: variables `NODE_BASE_IMAGE_NAME`, `NODE_TEST_IMAGE_NAME`, and `PREPARE_NODE_IMAGE`.
Control flow: sourced by sibling scripts before building/running test containers.
State and persistence: no persistence by itself.
Dependencies and integration points: coordinates naming between test, legacy, stargz, and mirror scripts.
Risks: changing names can orphan old Docker images or break compose references.
Test signals: covered by CRI containerd test scripts.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/const.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/mirror.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-containerd/mirror.sh

Purpose: Mirrors and optimizes CRI test images into a local registry for stargz validation.
Important APIs/types/functions: `retry`; inputs `TOOLS_DIR/list` and `TOOLS_DIR/host`.
Control flow: builds `ctr-remote`, starts containerd, waits for readiness, then for each unique image pulls it, optimizes it with `--oci --period=1`, and pushes to the mirror over plain HTTP.
State and persistence: writes `/bin/ctr-remote` and populates the target registry with optimized image tags.
Dependencies and integration points: runs in the prepare node from `test-stargz.sh`; depends on make, containerd, ctr-remote, and registry connectivity.
Risks: uses simple URL rewriting that strips original host and digest; assumes mirror registry accepts plain HTTP and unique path mapping.
Test signals: stargz CRI tests fail if mirrored images are missing or invalid.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/mirror.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/test-legacy.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-containerd/test-legacy.sh

Purpose: Runs baseline CRI validation against containerd before stargz mirroring.
Important APIs/types/functions: cleanup temp files, readiness loop, and image-list extraction from journald.
Control flow: starts a privileged test node, waits for containerd, runs `critest` against runtime and image endpoints, extracts all pulled image names from containerd logs plus pause images, writes them to the provided list file, then kills the node.
State and persistence: creates a disposable Docker container and temporary log/list files; output is the image list consumed by stargz tests.
Dependencies and integration points: depends on Docker, critest, runc/containerd, optional FUSE manager endpoint, and `utils.sh` version helpers.
Risks: log scraping is format-sensitive; cleanup trap is defined but not installed in the file, so early failures can leak temp files until process exit cleanup by OS.
Test signals: serves as the first phase of `cri-containerd/test.sh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/test-legacy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/test-stargz.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-containerd/test-stargz.sh

Purpose: Runs CRI validation against containerd using stargz lazy-pulled mirrored images.
Important APIs/types/functions: `cleanup` trap, registry/mirror setup, config generation, digest replacement, critest, snapshot/log checks.
Control flow: starts a compose stack with test node, prepare node, and registry; mirrors/optimizes images; configures containerd and snapshotter registry mirrors; rewrites digest references in cri-tools to optimized digests; rebuilds critest; restarts services; runs critest; verifies stargz snapshots and remote snapshot log records.
State and persistence: creates compose resources, temp configs, mirrored registry content, modified cri-tools files inside the node, and log extracts.
Dependencies and integration points: depends on Docker Compose, registry:2, ctr-remote, critest, containerd/stargz services, and `check_remote_snapshots`.
Risks: highly environment-sensitive and mutates test tool source in-container; digest extraction with grep/sed can fail if image listing format changes.
Test signals: second phase of `cri-containerd/test.sh`; success proves CRI lazy-pull integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/test-stargz.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-containerd/test.sh

Purpose: Builds CRI containerd test images and orchestrates legacy plus stargz CRI validation.
Important APIs/types/functions: uses Dockerfile version extraction, env toggles `BUILTIN_SNAPSHOTTER`, `FUSE_MANAGER`, `FUSE_PASSTHROUGH`, `TRANSFER_SERVICE`, `METADATA_STORE`; generates CNI and optional containerd configs.
Control flow: builds base/prepare images, creates a temp Dockerfile installing Go, ginkgo, cri-tools, and CNI plugins, appends snapshotter/fuse configs, builds the node image, runs legacy collection, then stargz validation.
State and persistence: creates temporary build context and image-list file; builds Docker images used by sibling scripts.
Dependencies and integration points: integrates Docker build stages, containerd configs, CRI tools, CNI plugins, and snapshotter runtime variants.
Risks: large network-dependent build; unsupported builtin+FUSE passthrough combination exits early; duplicate `DOCKER_BUILD_ARGS` usage can be noisy but harmless.
Test signals: top-level CRI containerd CI entrypoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-containerd/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/const.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-o/const.sh

Purpose: Defines shared Docker image names for CRI-O tests.
Important APIs/types/functions: variables `NODE_BASE_IMAGE_NAME`, `NODE_TEST_IMAGE_NAME`, and `PREPARE_NODE_IMAGE`.
Control flow: sourced by CRI-O mirror and test scripts.
State and persistence: no persistent state.
Dependencies and integration points: coordinates Docker image naming across the CRI-O test workflow.
Risks: name changes must be synchronized with all CRI-O scripts.
Test signals: covered by `script/cri-o/test.sh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/const.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/mirror.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-o/mirror.sh

Purpose: Mirrors and optimizes CRI-O test images into a local registry.
Important APIs/types/functions: same structure as CRI containerd `mirror.sh`: `retry`, `TOOLS_DIR/list`, `TOOLS_DIR/host`.
Control flow: builds `ctr-remote`, starts containerd, pulls each unique source image, optimizes to eStargz, and pushes to the mirror over plain HTTP.
State and persistence: writes `/bin/ctr-remote` and registry content.
Dependencies and integration points: used by CRI-O stargz tests from a prepare node with repository mounted read-only.
Risks: inherits URL rewriting/plain-HTTP assumptions from the containerd mirror script.
Test signals: failures surface during CRI-O stargz validation when pulls cannot resolve optimized images.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/mirror.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/test-legacy.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-o/test-legacy.sh

Purpose: Runs baseline CRI validation against CRI-O and records images used by tests.
Important APIs/types/functions: `retry`, `cleanup` temp cleanup, CRI-O socket constants, pause image path.
Control flow: starts a privileged CRI-O node, waits for `crictl stats`, runs `critest`, scrapes CRI-O journal for pulled images, appends the pause image, writes the unique image list, and kills the node.
State and persistence: creates a disposable Docker node and temp log/list files; outputs the image list for stargz mirroring.
Dependencies and integration points: depends on Docker, CRI-O, crictl/critest, and the test node image.
Risks: journal parsing is brittle; privileged runtime and tmpfs storage are required.
Test signals: first phase of `cri-o/test.sh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/test-legacy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/test-stargz.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-o/test-stargz.sh

Purpose: Runs CRI-O validation with stargz-store additional layer store and mirrored optimized images.
Important APIs/types/functions: `retry`, `cleanup`, auth registry setup, mirror config append, digest rewriting, auth pull check, critest, remote snapshot log validation.
Control flow: creates compose stack with CRI-O node, prepare node, public and auth registries; prepares TLS/auth creds; mirrors images; configures containers/image and stargz-store mirrors; rewrites digest references; rebuilds critest; restarts services; pulls an auth-protected eStargz image; runs critest; checks stargz-store logs.
State and persistence: creates temp auth certs, compose resources, registry content, CRI-O/store configs, and log extracts.
Dependencies and integration points: integrates CRI-O, containers/image, stargz-store, registry auth/TLS, ctr-remote mirror preparation, and `check_remote_snapshots`.
Risks: network, TLS, and sed-based digest rewriting are fragile; requires privileged containers and systemd.
Test signals: second phase of CRI-O CI; success covers auth and lazy layer store behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/test-stargz.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/cri-o/test.sh

Purpose: Builds CRI-O stargz-store test images and runs legacy plus stargz CRI validation.
Important APIs/types/functions: env `CRI_NO_RECREATE`, `METADATA_STORE`; generated `crio.conf`; Dockerfile installing Go/ginkgo/cri-tools.
Control flow: builds base and prepare images, generates a test node Dockerfile with CRI tools and metadata store config, builds it, then invokes `test-legacy.sh` and `test-stargz.sh` with a shared image-list file.
State and persistence: creates temp build context and image list; produces Docker test images.
Dependencies and integration points: depends on Docker build stages, CRI-O base image, Go toolchain, cri-tools, and utility version parsing.
Risks: network-heavy build; metadata store config is appended rather than replacing prior conflicting entries.
Test signals: top-level CRI-O CI entrypoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/cri-o/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/criauth/create-pod.sh -->
# sources/cloud-native/stargz-snapshotter/script/criauth/create-pod.sh

Purpose: Creates a Kubernetes pod that pulls a private image and verifies every committed layer is a remote stargz snapshot.
Important APIs/types/functions: random pod/container names, `REMOTE_SNAPSHOT_LABEL`, kubectl apply/wait loop, ctr-remote snapshot traversal.
Control flow: applies a pod in namespace `ns1` using `testsecret`, waits for container running state, finds the container in the kind node, walks snapshot parents from the active snapshot, and requires every parent layer to have the remote snapshot label.
State and persistence: creates a pod and leaves it running unless caller cleans cluster; reads snapshot metadata from the node.
Dependencies and integration points: used by CRI auth kind tests; depends on kubectl, docker exec, ctr-remote, jq, and Kubernetes secrets.
Risks: status parsing is odd (`cut -d '$'`) because jsonpath output has no delimiter; snapshot traversal assumes stargz snapshotter naming and a max of 100 layers.
Test signals: test fails if private image pull does not use lazy remote snapshots.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/criauth/create-pod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/criauth/mirror.sh -->
# sources/cloud-native/stargz-snapshotter/script/criauth/mirror.sh

Purpose: Optimizes and pushes one source image into an authenticated registry for CRI auth tests.
Important APIs/types/functions: `retry`; positional `SRC` and `DST`; env `REGISTRY_CREDS`.
Control flow: updates CA certificates, builds `ctr-remote`, starts containerd, pulls source, optimizes to OCI eStargz destination, and pushes with credentials.
State and persistence: writes build output under `/out` and populates the private registry.
Dependencies and integration points: called inside the prepare service from `criauth/test.sh`.
Risks: requires valid mounted CA and credentials; no cleanup of containerd state.
Test signals: failure prevents private registry test setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/criauth/mirror.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/criauth/run-kind.sh -->
# sources/cloud-native/stargz-snapshotter/script/criauth/run-kind.sh

Purpose: Builds a kind node image with CRI keychain support and creates a single-node kind cluster wired to a private registry.
Important APIs/types/functions: kind node image variables, generated containerd config snippets, builtin snapshotter hack config, namespace/secret creation.
Control flow: optionally builds base image, writes TLS and CRI keychain containerd config, builds node image, creates kind cluster, connects node to registry network, prints versions, and installs namespace plus imagePullSecret.
State and persistence: creates Docker images, a kind cluster, temporary configs, kubeconfig, and Kubernetes secret state.
Dependencies and integration points: integrates kind, containerd CRI registry TLS, standalone or builtin stargz snapshotter, Docker network, and Kubernetes secret auth.
Risks: cluster creation is heavyweight; builtin and standalone config paths differ and can drift; typo in log text is harmless.
Test signals: used by `criauth/test.sh` before `create-pod.sh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/criauth/run-kind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/criauth/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/criauth/test.sh

Purpose: End-to-end test for CRI image-pull secret auth with stargz snapshotter in kind.
Important APIs/types/functions: registry/auth constants, `prepare_creds`, compose setup, `run-kind.sh`, `create-pod.sh`.
Control flow: builds prepare image, creates htpasswd/TLS registry and prepare service on a dedicated Docker network, mirrors an optimized test image into the registry, creates a kind cluster with keychain support, waits, creates a private-image pod, then tears down compose, cluster, and network.
State and persistence: creates temp auth data, Docker config JSON, compose file, kind kubeconfig, registry content, Docker network, and cluster.
Dependencies and integration points: depends on Docker Compose, kind, kubectl, registry:2, mounted repo, and utility credential helper.
Risks: cleanup is manual after the main test block; failures during early registry prep perform explicit partial cleanup but abrupt host failures can leave networks/clusters.
Test signals: success proves CRI credentials reach stargz snapshotter for lazy pulls.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/criauth/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/docker-compose.yml -->
# sources/cloud-native/stargz-snapshotter/script/demo-store/docker-compose.yml

Purpose: Docker Compose environment for interactive Podman/stargz-store demo.
Important APIs/types/functions: declarative configuration keys include service build target `podman-base`, privileged mode, FUSE mount, repo/storage volumes, and local `registry2`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Used with `demo-store/run.sh` to demonstrate Podman additional layer store behavior.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/policy.json -->
# sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/policy.json

Purpose: Demo-store containers/image policy accepting test images.
Important APIs/types/functions: declarative configuration keys include JSON default `insecureAcceptAnything`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Copied into the demo container by `demo-store/run.sh`.
Risks: Intentionally insecure and demo-only.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/policy.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/registries.conf -->
# sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/registries.conf

Purpose: Demo-store registry config marking local registry insecure.
Important APIs/types/functions: declarative configuration keys include `[registries.insecure] registries=['registry2-store:5000']`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Used by Podman/containers-image inside the demo-store container.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/registries.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/storage.conf -->
# sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/storage.conf

Purpose: Demo-store Podman storage config with stargz additional layer store.
Important APIs/types/functions: declarative configuration keys include overlay storage roots and `additionallayerstores`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Allows Podman to consume layers mounted by stargz-store.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/storage.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/etc/stargz-store/config.toml -->
# sources/cloud-native/stargz-snapshotter/script/demo-store/etc/stargz-store/config.toml

Purpose: Demo-store stargz-store config exposing metrics and local registry mirror.
Important APIs/types/functions: declarative configuration keys include `metrics_address` and resolver mirror for `registry2-store:5000`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Loaded by `stargz-store` in the demo container.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/etc/stargz-store/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/run.sh -->
# sources/cloud-native/stargz-snapshotter/script/demo-store/run.sh

Purpose: Builds and starts stargz-store inside the Podman demo container.
Important APIs/types/functions: `retry`, `kill_all`, `cleanup`; constants for repo, config, root, and mountpoint.
Control flow: resets Podman/store state, copies demo configs into `/etc`, builds and installs project binaries, starts `stargz-store`, and waits for the pool directory.
State and persistence: clears `/var/lib/stargz-store`, resets Podman, copies configs, installs binaries under `PREFIX=/tmp/out` target paths.
Dependencies and integration points: used with `demo-store/docker-compose.yml`; depends on make, podman, FUSE, and stargz-store.
Risks: destructive state cleanup and broad process kill make it demo-container only.
Test signals: manual/demo validation when pool link appears and Podman can use store.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo-store/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/config.containerd.toml -->
# sources/cloud-native/stargz-snapshotter/script/demo/config.containerd.toml

Purpose: Containerd demo config registering stargz as a proxy snapshotter.
Important APIs/types/functions: declarative configuration keys include `version=2` and `[proxy_plugins.stargz]` socket/root settings. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Copied by `demo/run.sh` before starting containerd.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/config.containerd.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/config.stargz.toml -->
# sources/cloud-native/stargz-snapshotter/script/demo/config.stargz.toml

Purpose: Standalone snapshotter demo config enabling metrics, IPFS, direct directory cache, and relaxed restart handling.
Important APIs/types/functions: declarative configuration keys include `metrics_address`, `disable_verification`, `ipfs`, resolver mirror, `[directory_cache] direct`, and `[snapshotter] allow_invalid_mounts_on_restart`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Loaded by `containerd-stargz-grpc` in the demo environment.
Risks: Disables verification, so it is suitable for demo experimentation only.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/config.stargz.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/docker-compose.yml -->
# sources/cloud-native/stargz-snapshotter/script/demo/docker-compose.yml

Purpose: Docker Compose stack for interactive containerd/stargz snapshotter demo.
Important APIs/types/functions: declarative configuration keys include privileged `containerd_demo`, FUSE mount, repo and data volumes, local registry service. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Pairs with `demo/init.sh` and `demo/run.sh` to run containerd plus snapshotter in a disposable container.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/init.sh -->
# sources/cloud-native/stargz-snapshotter/script/demo/init.sh

Purpose: Initializes cgroup-v2 nesting for the demo container and keeps it alive.
Important APIs/types/functions: cgroup setup block and final `exec sleep infinity`.
Control flow: moves cgroup processes, enables controllers, then sleeps forever for interactive use.
State and persistence: mutates cgroup files but no app data.
Dependencies and integration points: entrypoint for `script/demo/docker-compose.yml`.
Risks: requires privileged container and cgroup v2; does not start daemons by itself.
Test signals: demo user runs `demo/run.sh` after container startup.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/init.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/run.sh -->
# sources/cloud-native/stargz-snapshotter/script/demo/run.sh

Purpose: Builds, installs, and starts containerd plus stargz snapshotter in the demo container.
Important APIs/types/functions: `retry`, `kill_all`, `cleanup`; daemon root/socket constants.
Control flow: copies demo configs, kills old daemons, unmounts/clears roots, builds and installs binaries, starts `containerd-stargz-grpc`, waits for socket, and starts containerd with optional extra args.
State and persistence: clears `/var/lib/containerd` and `/var/lib/containerd-stargz-grpc`; installs binaries from local build output.
Dependencies and integration points: depends on demo compose environment, make, FUSE, containerd, and CNI config file outside this subset.
Risks: destructive cleanup; missing `config.cni.conflist` would fail copy; broad process matching can kill unrelated processes in non-isolated environments.
Test signals: manual demo signal is running containerd and snapshotter socket readiness.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/demo/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/generated-files/generate.sh -->
# sources/cloud-native/stargz-snapshotter/script/generated-files/generate.sh

Purpose: BuildKit-based generator/validator for protobuf-generated Go files.
Important APIs/types/functions: commands `update` and `validate`; generated Dockerfile stages `golang-base`, `generate`, `update`, `validate`.
Control flow: derives Go base version, builds a tool image with protoc and protoc-gen-gogo, runs `go generate ./...`, then either exports changed `*.pb.go` files back to the repo or fails if validation sees diffs.
State and persistence: creates temporary build context/output dirs and may copy generated files into the repository on `update`.
Dependencies and integration points: depends on Docker BuildKit, Go, protoc, gogo protobuf, and `utils.sh` version parsing.
Risks: network-dependent tool downloads; only tracks `*.pb.go`; update copies generated output over existing files.
Test signals: CI can run `validate`; developers use `update` when generated files are stale.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/generated-files/generate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/integration/containerd/config.containerd.toml -->
# sources/cloud-native/stargz-snapshotter/script/integration/containerd/config.containerd.toml

Purpose: Integration-test config for builtin containerd stargz snapshotter and transfer service.
Important APIs/types/functions: declarative configuration keys include stargz snapshotter root, verification, metadata store, blob checking, registry mirror, and transfer unpack configs. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Used by integration test images, especially builtin snapshotter and transfer-service modes.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/integration/containerd/config.containerd.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/integration/containerd/config.stargz.toml -->
# sources/cloud-native/stargz-snapshotter/script/integration/containerd/config.stargz.toml

Purpose: Integration-test config for standalone stargz snapshotter.
Important APIs/types/functions: declarative configuration keys include metadata store, IPFS enablement, FUSE passthrough, blob retries/checking, and registry mirror. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Copied into integration test image and modified by `integration/test.sh` for metadata/fuse variants.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/integration/containerd/config.stargz.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/integration/containerd/entrypoint.sh -->
# sources/cloud-native/stargz-snapshotter/script/integration/containerd/entrypoint.sh

Purpose: Large end-to-end integration entrypoint covering registry auth, optimized image formats, lazy pulls, IPFS, mirror fallback, filesystem equivalence, external TOC, and graceful restart.
Important APIs/types/functions: helpers `retry`, `kill_all`, `wait_all`, `reboot_containerd`, `optimize`, `convert`, `copy`, `copy_out_dir`, `dump_dir`, `run_and_check_remote_snapshots`, and `check_cache_empty`.
Control flow: sets up cgroups, logs into TLS registry, boots containerd/snapshotter, verifies plugin health, prepares original/eStargz/zstd/external-TOC images, optionally tests IPFS pulls, verifies mirror/refresh behavior with iptables blocks, compares root filesystems from overlayfs and stargz for multiple formats, tests namespace pulls, missing-config startup, and graceful SIGINT/SIGTERM restarts.
State and persistence: creates many temporary rootfs directories, registry images, IPFS repo, daemon state, logs, iptables rules, and content-store/snapshotter data; cleanup removes temp dirs/logs.
Dependencies and integration points: depends on containerd, ctr-remote, stargzify, IPFS, authenticated registries, `utils.sh`, FUSE, iptables, jq/tar/diff, and optional builtin snapshotter config.
Risks: very environment-sensitive; failed iptables cleanup can affect later steps; several tests depend on exact log messages and registry hostnames. It is intentionally broad and should run in disposable privileged containers.
Test signals: primary integration signal for lazy-pull correctness across formats and operational restart behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/integration/containerd/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/integration/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/integration/test.sh

Purpose: Builds and runs the integration Docker Compose environment.
Important APIs/types/functions: env toggles `BUILTIN_SNAPSHOTTER`, `METADATA_STORE`, `FUSE_MANAGER`, `FUSE_PASSTHROUGH`, `TRANSFER_SERVICE`; helper `prepare_creds`.
Control flow: builds a base image, generates a test Dockerfile with IPFS/stargzify/configs/entrypoint, adjusts snapshotter config for selected variants, creates TLS registry credentials, writes a compose stack with test node plus registries, runs compose until the test container exits, then tears down volumes.
State and persistence: creates temp compose/auth/root/context dirs, Docker images, registry auth files, and compose volumes.
Dependencies and integration points: depends on Docker Compose, registry:2, Go tools, IPFS download, FUSE, and integration container scripts.
Risks: network-heavy and privileged; builtin+FUSE passthrough is explicitly unsupported; duplicate build args are passed in one docker build command.
Test signals: top-level integration CI entrypoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/integration/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/ipfs/entrypoint.sh -->
# sources/cloud-native/stargz-snapshotter/script/ipfs/entrypoint.sh

Purpose: Starts an offline IPFS daemon before running a supplied command.
Important APIs/types/functions: IPFS init/daemon startup and curl readiness probe; final `$@` execution.
Control flow: initializes IPFS, runs daemon offline in background, waits for API `/version`, then executes the container command.
State and persistence: creates IPFS repository under default IPFS path inside the container.
Dependencies and integration points: used by `ipfs/test.sh` to run Go IPFS client tests.
Risks: does not clean up daemon explicitly; `$@` is unquoted in source and can split unusual arguments.
Test signals: readiness is validated by curl before tests start.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/ipfs/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/ipfs/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/ipfs/test.sh

Purpose: Builds a temporary IPFS-enabled Go test container and runs IPFS client tests.
Important APIs/types/functions: uses `go_base_version`, `IPFS_VERSION`, temp Dockerfile, and cleanup trap.
Control flow: builds an image with Go, fuse3, and go-ipfs, mounts the repo read-only, starts the entrypoint, and runs `go test -v -run TestIPFSClient ./client/... --ipfs-api=http://localhost:5001`.
State and persistence: creates temporary Docker build context and Docker image `testipfs`.
Dependencies and integration points: depends on Docker, Go base image, IPFS download, FUSE device, and repository IPFS client tests.
Risks: hard-codes amd64 IPFS tarball; read-only repo means tests must not need writes under source tree.
Test signals: direct CI signal for IPFS client package integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/ipfs/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s-argo-workflow/run.sh -->
# sources/cloud-native/stargz-snapshotter/script/k3s-argo-workflow/run.sh

Purpose: Benchmarks Argo workflow runtime on custom k3s images with overlayfs versus stargz snapshotter.
Important APIs/types/functions: helpers `argo_yaml`, `replace_image`, `go_ci_yaml`, and `run`; constants for k3s, containerd, Argo versions.
Control flow: downloads Argo manifest, clones k3s, vendors current stargz snapshotter via git archive, patches go.mod, builds a local k3s node image, then repeatedly creates k3d clusters, installs Argo, submits a Go workflow, records elapsed time, and deletes the cluster.
State and persistence: creates temp cloned repos, generated YAMLs, k3d clusters, local k3s images, and an output JSON-lines result file.
Dependencies and integration points: depends on git, Go, k3s build tooling, k3d, kubectl, argo CLI, envsubst, jq, and current repo commit state.
Risks: very heavyweight and tracks `main` branches by default; local uncommitted changes are excluded because it uses `git archive HEAD`.
Test signals: result file contains elapsed comparisons for overlayfs and stargz workflow runs.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s-argo-workflow/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s/create-pod.sh -->
# sources/cloud-native/stargz-snapshotter/script/k3s/create-pod.sh

Purpose: Creates a k3s pod from a private image and verifies all parent layers are remote stargz snapshots.
Important APIs/types/functions: same structure as kind create-pod but uses `ctr` inside k3s node.
Control flow: applies pod/secret usage, waits for running, locates container by Kubernetes label, walks snapshot parents with `ctr --namespace=k8s.io`, and checks `containerd.io/snapshot/remote` labels.
State and persistence: creates a pod in namespace `ns1`; reads node snapshot metadata.
Dependencies and integration points: used by `k3s/test.sh`; depends on k3d node container, kubectl, ctr, jq, and imagePullSecret.
Risks: status parsing and snapshot traversal assumptions match the kind script; max layer count is fixed at 100.
Test signals: success demonstrates k3s private-image lazy pulling.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s/create-pod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s/mirror.sh -->
# sources/cloud-native/stargz-snapshotter/script/k3s/mirror.sh

Purpose: Optimizes and pushes a test image into the k3s private registry.
Important APIs/types/functions: `retry`; positional `SRC`/`DST`; env `REGISTRY_CREDS`.
Control flow: updates certs, builds `ctr-remote`, starts containerd, pulls source, optimizes to OCI eStargz, and pushes with credentials.
State and persistence: writes `/out/ctr-remote` and registry content.
Dependencies and integration points: called from the k3s prepare container in `k3s/test.sh`.
Risks: requires trusted registry CA and credentials; no explicit cleanup of containerd data.
Test signals: failure blocks k3s private registry test setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s/mirror.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s/run-k3s.sh -->
# sources/cloud-native/stargz-snapshotter/script/k3s/run-k3s.sh

Purpose: Builds a custom k3s node image with current stargz snapshotter and creates a k3d cluster configured for stargz.
Important APIs/types/functions: clone/build workflow, generated registry config YAML, namespace/secret creation.
Control flow: clones k3s, vendors current repo from `HEAD`, patches go.mod replacements, builds local k3s image, writes registry mirror/TLS config, creates k3d cluster with `--snapshotter=stargz`, connects node to private registry network, exports kubeconfig, and installs imagePullSecret.
State and persistence: creates temp repos/context/configs, local k3s image, k3d cluster, and Kubernetes namespace/secret.
Dependencies and integration points: depends on git archive, Go toolchain, k3s build scripts, k3d, kubectl, Docker network, and private registry CA.
Risks: uses `git archive HEAD`, so uncommitted code changes are not tested; tracking k3s `main` can introduce moving failures.
Test signals: used by `k3s/test.sh` before pod remote-snapshot validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s/run-k3s.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/k3s/test.sh

Purpose: End-to-end k3s private registry lazy-pull test.
Important APIs/types/functions: uses `prepare_creds`, compose registry/prepare services, `run-k3s.sh`, and `create-pod.sh`.
Control flow: builds prepare image, starts authenticated TLS registry and prepare node on a dedicated network, mirrors optimized test image, creates custom k3s cluster, waits for secret sync, creates a pod, validates remote snapshots, and cleans up compose, cluster, and network.
State and persistence: creates temp auth/dockerconfig/compose/kubeconfig dirs, registry data, Docker network, and k3d cluster.
Dependencies and integration points: depends on Docker Compose, k3d, kubectl, k3s build, registry auth/TLS, and stargz mirror script.
Risks: heavyweight and network-dependent; cleanup occurs after test block and may leave artifacts on abrupt termination.
Test signals: success proves k3s can pull private optimized images lazily via stargz.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/k3s/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/kind/create-pod.sh -->
# sources/cloud-native/stargz-snapshotter/script/kind/create-pod.sh

Purpose: Creates a kind pod from a private image, verifies remote snapshot labels, and checks standalone snapshotter restart when applicable.
Important APIs/types/functions: random names, `REMOTE_SNAPSHOT_LABEL`, kubectl wait loop, ctr-remote snapshot traversal, optional systemd restart.
Control flow: applies pod, waits for running, finds container in kind node, walks stargz snapshot parents and requires remote labels, then for standalone snapshotter deletes the pod and restarts `stargz-snapshotter.service`.
State and persistence: creates/deletes Kubernetes pod and reads node snapshot state; may restart snapshotter service.
Dependencies and integration points: used by `kind/test.sh`; depends on kubectl, docker exec, ctr-remote, jq, systemd inside node.
Risks: same status parsing/layer traversal fragility as related scripts; service restart check only applies to standalone mode.
Test signals: validates both lazy pull and restart health in kind.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/kind/create-pod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/kind/mirror.sh -->
# sources/cloud-native/stargz-snapshotter/script/kind/mirror.sh

Purpose: Optimizes and pushes one source image into the kind private registry.
Important APIs/types/functions: `retry`; positional `SRC` and `DST`; env `REGISTRY_CREDS`.
Control flow: updates CAs, builds `ctr-remote`, starts containerd, pulls source, optimizes to OCI eStargz, and pushes with credentials.
State and persistence: writes `/out/ctr-remote` and registry content.
Dependencies and integration points: called by the prepare service in `kind/test.sh`.
Risks: requires registry credentials and mounted CA; no daemon state cleanup.
Test signals: failure prevents kind private registry test from running.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/kind/mirror.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/kind/run-kind.sh -->
# sources/cloud-native/stargz-snapshotter/script/kind/run-kind.sh

Purpose: Builds a kind node image with kubeconfig keychain support and creates a single-node kind cluster.
Important APIs/types/functions: generated stargz/containerd configs, builtin snapshotter hack, Kubernetes RBAC/secret setup, `wait_for_data`.
Control flow: optionally builds base image, writes snapshotter kubeconfig-keychain config and registry TLS config, builds node image, creates kind cluster, connects it to registry network, installs namespace/imagePullSecret/RBAC/service-account token secret, waits for CA/token data, builds a kubeconfig for the snapshotter, and copies it into the node.
State and persistence: creates Docker images, cluster, Kubernetes secrets/RBAC, and a kubeconfig copied into the node filesystem.
Dependencies and integration points: integrates kind, Kubernetes service-account credentials, stargz snapshotter kubeconfig keychain, registry TLS, and standalone/builtin modes.
Risks: secret name typo `sercret` is consistent but easy to misread; depends on legacy service-account token secret behavior and API server port parsing from process args.
Test signals: used by `kind/test.sh` before pod validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/kind/run-kind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/kind/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/kind/test.sh

Purpose: End-to-end kind private registry lazy-pull and keychain test.
Important APIs/types/functions: uses `prepare_creds`, compose registry/prepare node, `run-kind.sh`, and `create-pod.sh`.
Control flow: builds prepare image, creates auth/TLS registry on a dedicated network, mirrors optimized Ubuntu image, creates configured kind cluster, waits for secret sync, creates pod and validates remote snapshots, then tears down compose, cluster, and network.
State and persistence: creates temp auth/dockerconfig/compose/kubeconfig dirs, Docker network, registry content, and kind cluster.
Dependencies and integration points: depends on Docker Compose, kind, kubectl, registry:2, keychain-enabled node image, and mirror script.
Risks: heavy integration test with many external tools; early failures can leave artifacts if cleanup commands fail.
Test signals: success proves kind/Kubernetes secret credentials work with stargz lazy pulls.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/kind/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/optimize/optimize/entrypoint.sh -->
# sources/cloud-native/stargz-snapshotter/script/optimize/optimize/entrypoint.sh

Purpose: Container entrypoint that validates image optimization output, TOC annotations, uncompressed-size annotations, and optimizer networking/mount support.
Important APIs/types/functions: helpers `retry`, `prepare_context`, `validate_toc_json`, `check_uncompressed_size`, `check_optimization`, and `append_toc`.
Control flow: logs into a TLS registry, starts buildkitd/containerd, builds a scratch sample image with files and an accessor binary, builds race-enabled `ctr-remote`, optimizes and no-optimizes images with supplied commands, saves/pulls them to inspect layer tar order and annotations, then runs optimizer with CNI, add-hosts, bind mount, and curl checks against a test server.
State and persistence: creates registry images, build context, Go binary, working dirs, BuildKit/containerd state, and bind-mount output files.
Dependencies and integration points: parameterized by `OPTIMIZE_COMMAND`, `NO_OPTIMIZE_COMMAND`, `GETTOCDIGEST_COMMAND`, `DECOMPRESS_COMMAND`, and `INVISIBLE_TOC` from `optimize/test.sh`.
Risks: assumes specific tar listing order and annotation names; uses privileged network setup and iptables legacy mode; `nerdctl push || true` can hide push failures before later checks catch them.
Test signals: run twice by `optimize/test.sh` for zstdchunked and gzip/eStargz modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/optimize/optimize/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/optimize/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/optimize/test.sh

Purpose: Builds and runs optimizer integration tests for zstdchunked and gzip eStargz modes.
Important APIs/types/functions: `test_optimize` writes compose YAML with command parameters; uses version helpers for CNI and nerdctl.
Control flow: builds a race-enabled base image, creates a test image with jq/iptables/zstd/dns/crane/CNI/buildkit tools, prepares TLS registry creds, then runs compose twice with different optimizer/get-TOC/decompress command sets.
State and persistence: creates temp compose/auth/context files, Docker images, registry and buildkit/containerd volumes.
Dependencies and integration points: depends on Docker Compose, registry:2, httpd test server, BuildKit, nerdctl, CNI plugins, and `entrypoint.sh`.
Risks: privileged and network-heavy; test output depends on exact optimizer layer layout.
Test signals: top-level optimizer CI entrypoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/optimize/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/config/containers.conf -->
# sources/cloud-native/stargz-snapshotter/script/podman/config/containers.conf

Purpose: Rootless Podman config selecting slirp4netns for networking.
Important APIs/types/functions: declarative configuration keys include `[network] default_rootless_network_cmd`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Installed in the podman-rootless test image so rootless containers can run with expected networking.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/config/containers.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/config/podman-rootless-stargz-store.service -->
# sources/cloud-native/stargz-snapshotter/script/podman/config/podman-rootless-stargz-store.service

Purpose: User systemd unit for rootless stargz-store under Podman.
Important APIs/types/functions: declarative configuration keys include `ExecStart` via `podman unshare stargz-store`, root/address/store paths under `%h`, `ExecStopPost`, restart policy. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Started by `test-podman-rootless.sh` before rootless Podman lazy-pull tests.
Risks: Pipes through `cat` as a workaround; rootless mount cleanup can fail if store is busy.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/config/podman-rootless-stargz-store.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/config/storage.conf -->
# sources/cloud-native/stargz-snapshotter/script/podman/config/storage.conf

Purpose: Rootless Podman storage config adding stargz-store as an additional layer store.
Important APIs/types/functions: declarative configuration keys include overlay driver and `additionallayerstores` path under `/home/rootless`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Used by Podman rootless test image with the user systemd stargz-store service.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/config/storage.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/config/test-podman-rootless.sh -->
# sources/cloud-native/stargz-snapshotter/script/podman/config/test-podman-rootless.sh

Purpose: Wrapper that switches from root to the rootless user and starts the user stargz-store service before running a command.
Important APIs/types/functions: root/user branch, `systemctl start ssh`, `ssh rootless@localhost`, `systemctl --user start podman-rootless-stargz-store`.
Control flow: if running as root, starts SSH and re-execs itself through rootless SSH; otherwise starts the user service and execs the provided command.
State and persistence: starts system/user services; no file persistence itself.
Dependencies and integration points: used inside podman-rootless test image to mimic rootless execution patterns from nerdctl CI.
Risks: requires SSH daemon and password/keyless rootless access configured in image; strict host checking disabled for test convenience.
Test signals: indirectly exercised by Podman rootless test image startup.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/config/test-podman-rootless.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/run_test.sh -->
# sources/cloud-native/stargz-snapshotter/script/podman/run_test.sh

Purpose: Runs rootless Podman lazy-pull smoke tests against stargz-store.
Important APIs/types/functions: `retry`; service name `podman-rootless-stargz-store`; remote snapshot log marker.
Control flow: waits until `podman unshare mount` shows stargzstore, pulls/runs eStargz images, runs another eStargz image to include lazy pulling, prints store journal remote snapshot lines, runs a non-lazy original image, then stops the user service.
State and persistence: creates `/tmp/test1.sh`, pulls Podman images, and reads/stops user systemd service state.
Dependencies and integration points: depends on rootless Podman, stargz-store service, journalctl, and public ghcr.io test images.
Risks: public image availability and journal log format are external dependencies; smoke test is small but catches gross integration failures.
Test signals: `podman/test.sh` parses its log and validates remote snapshot records.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/run_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/test.sh -->
# sources/cloud-native/stargz-snapshotter/script/podman/test.sh

Purpose: Builds and runs the rootless Podman stargz-store test image.
Important APIs/types/functions: uses `check_remote_snapshots`, temp logs, and generated Dockerfile that runs `run_test.sh`.
Control flow: builds base podman-rootless image if needed, builds a node image containing `run_test.sh`, runs it privileged, captures logs, extracts remote snapshot JSON lines, and validates them.
State and persistence: creates temp context/log files and Docker images; pulls/runs public images inside the test container.
Dependencies and integration points: depends on Docker, podman-rootless Dockerfile stage, stargz-store service config, and utility log checker.
Risks: requires privileged Docker run even though testing rootless behavior; public registry availability is needed.
Test signals: top-level Podman rootless CI signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/podman/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/util/make.sh -->
# sources/cloud-native/stargz-snapshotter/script/util/make.sh

Purpose: Runs repository `make` targets inside a minimal privileged Go container.
Important APIs/types/functions: uses `go_base_version`, generated Dockerfile, `MAKECMD=make ... PREFIX=/tmp/out/`.
Control flow: builds a `golang:<version>` image with fuse3/gzip/pigz, then runs the requested make target with the repo mounted read-only and git safe.directory configured.
State and persistence: creates a temp Docker build context and local image `minienv`; build outputs stay inside the container unless target writes elsewhere.
Dependencies and integration points: depends on Docker, Go base image, FUSE device, and repository Makefile.
Risks: repo is mounted read-only, so make targets that write to source will fail; command arguments are interpolated into `/bin/sh -c`.
Test signals: useful for reproducible build/test invocations in CI or developer scripts.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/util/make.sh -->
