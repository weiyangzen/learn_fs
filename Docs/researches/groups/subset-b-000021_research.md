# Research Report: subset-b-000021

Grouped research for BuildKit frontend subrequests, development helper scripts, identity generation, and session auth/content/exporter/filesync/secrets plumbing. Each section is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/convertllb/convertllb.go -->
# sources/cloud-native/buildkit/frontend/subrequests/convertllb/convertllb.go

Purpose: defines the `frontend.convertllb` subrequest result format for converting a Dockerfile frontend invocation into an inspectable LLB graph. It packages protobuf solver operations, op metadata, and the root source into gateway result metadata.

Important APIs, types, and functions: `RequestConvertLLB` is the public request id. `SubrequestConvertLLBDefinition` declares version `0.1.0`, RPC type, description, and `result.json` metadata. `Result` carries `Def map[digest.Digest]*pb.Op`, `Metadata map[digest.Digest]llb.OpMetadata`, and `Source *pb.Source`. `(*Result).ToResult` creates a `client.Result`, adds formatted JSON under `result.json`, and records the request version. `(*Result).MarshalJSON` custom-marshals protobuf fields using `protojson`.

Control flow and state: the file is stateless apart from the request definition. Serialization iterates over digest-keyed ops, marshals each `pb.Op`, copies metadata directly, marshals `Source`, and then delegates to `encoding/json` for the final envelope.

Dependencies and integration: integrates with `frontend/gateway/client.Result` metadata, `client/llb` metadata, `solver/pb` protobuf types, and OCI digests. Dockerfile frontend code can expose this subrequest and buildctl-style callers can read `result.json`.

Risks and test signals: `MarshalJSON` assumes `Source` is non-nil and returns protobuf marshal errors directly. Digest-keyed JSON maps depend on digest string encoding. There are no direct tests in this file; coverage should come from frontend subrequest tests that assert valid `result.json` and version metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/convertllb/convertllb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/describe.go -->
# sources/cloud-native/buildkit/frontend/subrequests/describe.go

Purpose: implements the client-side `frontend.subrequests.describe` helper and text renderer for listing subrequests supported by a frontend.

Important APIs, types, and functions: `RequestSubrequestsDescribe` is the request id. `SubrequestsDescribeDefinition` advertises version `1.0.0`, RPC type, and both `result.json` and `result.txt`. `Describe(ctx, c)` verifies gateway caps, calls `c.Solve` with `requestid` and `frontend.caps`, extracts `result.json`, and unmarshals `[]Request`. `PrintDescribe(dt, w)` renders a tabular `NAME VERSION DESCRIPTION` list, trimming the `frontend.` prefix.

Control flow and state: `Describe` first checks `CapFrontendCaps`; lack of capability is normalized to an unsupported subrequest error. It then sends a Dockerfile frontend solve request and maps unsupported frontend-cap errors to unsupported subrequest errors for a stable caller contract. It has no persistent state.

Dependencies and integration: uses gateway client solve metadata, `frontend/gateway/pb` capabilities, `solver/errdefs` typed errors, and the local `Request` schema from `types.go`. The text printer is used when `result.txt` needs human-readable output.

Risks and test signals: missing `result.json` or malformed JSON fail hard. Error mapping is important for older daemons/frontends. Tests should exercise unsupported caps, unsupported subrequest propagation, JSON decoding, and tabwriter output.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/describe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/lint/lint.go -->
# sources/cloud-native/buildkit/frontend/subrequests/lint/lint.go

Purpose: defines the Dockerfile lint subrequest result model, JSON/text output generation, warning source mapping, and status-code metadata.

Important APIs, types, and functions: `RequestLint` and `SubrequestLintDefinition` expose `frontend.lint` version `1.0.0` with `result.json`, `result.txt`, and `result.statuscode`. `Warning` captures rule name, description, URL, detail, and protobuf location. `BuildError` records a build error and source location. `LintResults` contains warnings, source infos, and optional build error. `AddSource` deduplicates `llb.SourceMap` data into `pb.SourceInfo`. `AddWarning` converts parser ranges into `pb.Range` values. `ToResult` emits JSON, text, status code, and version. `PrintTo`, `PrintErrorTo`, `validateWarnings`, and `PrintLintViolations` render and validate warnings.

Control flow and state: lint collection is in-memory. Sources are appended only when filename, language, and raw data differ. Text output validates warning source indexes, sorts warnings by missing/known location, filename, line, then rule name, and renders BuildKit source snippets through `errdefs.Source.Print`.

Dependencies and integration: depends on Dockerfile parser ranges, LLB source maps, gateway result metadata, solver protobuf location/source types, and `errdefs.Source` formatting. It is a frontend subrequest result contract consumed by CLI and API clients.

Risks and test signals: `Warning.PrintTo` dereferences `Location` and `SourceIndex` without nil checks, so producers must always populate valid locations or validate before printing. `validateWarnings` checks out-of-range indexes but only checks nil sources when `SourceIndex > 0`, leaving index 0 nil as a possible panic path. Tests should cover sorting, source dedupe, status-code behavior, invalid source indexes, and build-error rendering.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/lint/lint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/outline/outline.go -->
# sources/cloud-native/buildkit/frontend/subrequests/outline/outline.go

Purpose: defines the `frontend.outline` subrequest response for documenting build target parameters such as build args, secrets, SSH mounts, cache mounts, and source snippets.

Important APIs, types, and functions: `RequestSubrequestsOutline` and `SubrequestsOutlineDefinition` publish version `1.0.0`, the optional `target` parameter, and `result.json`/`result.txt` outputs. `Outline` is the top-level JSON structure. `Arg`, `Secret`, `SSH`, and `CacheMount` represent discovered parameters with optional `pb.Location`. `Outline.ToResult` emits formatted JSON and rendered text. `PrintOutline` renders target metadata plus BUILD ARG, SECRET, and SSH tables.

Control flow and state: the file is stateless. Rendering conditionally writes sections only when the corresponding data exists. `Name` defaults to `(default)` in text when the target has a description but no explicit name.

Dependencies and integration: integrates with gateway result metadata and protobuf source locations. Dockerfile frontend parsers populate the model, while buildctl or other clients consume the text and JSON outputs.

Risks and test signals: cache mount data is present in JSON but not printed in the current text renderer, which can surprise human-output users. `Sources` contains raw bytes and can enlarge metadata. Tests should assert JSON stability and text rendering for each non-empty section, including default target naming.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/outline/outline.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/targets/targets.go -->
# sources/cloud-native/buildkit/frontend/subrequests/targets/targets.go

Purpose: defines the `frontend.targets` subrequest response for listing build targets/stages exposed by the current Dockerfile frontend.

Important APIs, types, and functions: `RequestTargets` and `SubrequestsTargetsDefinition` expose version `1.0.0` with `result.json` and `result.txt`. `List` contains `Targets []Target` and raw `Sources`. `Target` records name, default flag, description, base, platform, and optional source location. `List.ToResult` marshals JSON and text metadata. `PrintTargets` renders `TARGET DESCRIPTION`, labeling unnamed defaults as `(default)` and named defaults as `<name> (default)`.

Control flow and state: all work is pure serialization. Text rendering iterates target order as provided by the frontend and does not sort or filter.

Dependencies and integration: uses gateway client result metadata and solver protobuf locations. It is consumed by subrequest-aware clients that inspect Dockerfile stage inventories.

Risks and test signals: text output omits base, platform, source locations, and raw sources although JSON carries them. Tests should cover default label formatting and invalid JSON handling in `PrintTargets`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/targets/targets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/types.go -->
# sources/cloud-native/buildkit/frontend/subrequests/types.go

Purpose: provides shared metadata schemas for frontend subrequest discovery and documentation.

Important APIs, types, and functions: `Type` is a string alias with `TypeRPC = "rpc"`. `Named` captures a name, version, and description triple. `Request` describes a subrequest with name, version, type, description, option metadata, and output metadata.

Control flow and state: this file declares data-only structs with JSON tags and no behavior or persistence.

Dependencies and integration: consumed by describe, lint, outline, targets, convertllb, and other frontend subrequest packages. Its JSON field names form part of the external metadata contract returned by `frontend.subrequests.describe`.

Risks and test signals: schema changes are compatibility-sensitive because clients unmarshal these JSON objects. Tests should cover round-trip compatibility for existing fields and absence of required-field enforcement.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/buildkitd-entrypoint -->
# sources/cloud-native/buildkit/hack/buildkitd-entrypoint

Purpose: container entrypoint wrapper for `buildkitd` that attempts to create a cgroup namespace and remount `/sys/fs/cgroup` for cgroup v2 when running under an inherited cgroup path.

Important APIs, types, and functions: shell script with `set -e`. It checks `/sys/fs/cgroup/cgroup.controllers`, inspects `/proc/self/cgroup`, probes `/usr/bin/unshare --cgroup --mount /usr/bin/with-cgroupfs-remount true`, and on success `exec`s buildkitd through the same namespace/remount wrapper.

Control flow and state: no persistence. On cgroup v2 and non-root cgroup path, it tries an unshare/remount probe. If the probe succeeds it replaces the process with namespaced `buildkitd`; otherwise it logs a skip message and falls back to direct `buildkitd`.

Dependencies and integration: depends on Linux cgroup v2, `/usr/bin/unshare`, `/usr/bin/with-cgroupfs-remount`, and `/usr/bin/buildkitd`. It exists as a Kubernetes workaround until cgroup namespace control is available through the API.

Risks and test signals: failures intentionally degrade to direct execution, so deployments may silently lack the desired namespace behavior except for stderr. Tests are usually image/runtime tests that run under cgroup v2 and verify the fallback and successful exec paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/buildkitd-entrypoint -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/compose -->
# sources/cloud-native/buildkit/hack/compose

Purpose: thin development wrapper for running BuildKit's Docker Compose environment from the repository root.

Important APIs, types, and functions: bash script sources `hack/util`, enables `set -eu -o pipefail`, builds `args=(compose -f "$filesDir/compose.yaml")`, and invokes `dockerCmd "${args[@]}" "$@"`.

Control flow and state: no persistent state beyond Docker/Compose side effects. The script resolves `composefiles` relative to itself and forwards all user arguments.

Dependencies and integration: depends on `hack/util` for Docker CLI discovery and on `hack/composefiles/compose.yaml` plus profile-specific configs. Used by developers to start tracing/metrics/dev BuildKit services.

Risks and test signals: `$(dirname $0)` is unquoted, so paths with spaces are fragile. Compose behavior depends on Docker CLI availability. Test signal is successful `hack/compose config` or `hack/compose up` in a developer environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/compose -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/buildkitd.toml -->
# sources/cloud-native/buildkit/hack/composefiles/buildkitd.toml

Purpose: minimal development BuildKit daemon configuration used by the compose environment.

Important APIs, types, and functions: sets `[log].level = "debug"` and `[grpc].debugAddress = "0.0.0.0:6060"`.

Control flow and state: declarative config only. It affects daemon logging verbosity and exposes the debug endpoint inside the compose network and mapped localhost port.

Dependencies and integration: mounted into the `buildkit` service as `/etc/buildkit/buildkitd.toml` by `compose.yaml`.

Risks and test signals: debug logging and `0.0.0.0` binding are intended for local development and should not be reused unreviewed in production. Test with `buildkitd --config` through the compose service and debug endpoint reachability.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/buildkitd.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/compose.yaml -->
# sources/cloud-native/buildkit/hack/composefiles/compose.yaml

Purpose: Docker Compose definition for a local BuildKit development stack with optional tracing and metrics.

Important APIs, types, and functions: defines services `buildkit`, `otel-collector`, `jaeger`, `prometheus`, and `grafana`; volumes `buildkit`, `prometheus`, and `grafana`; and configs for BuildKit, OpenTelemetry collector, Prometheus, Grafana, and Grafana datasources. The BuildKit service builds from `../..`, tags `moby/buildkit:local`, runs privileged, maps localhost ports 5000 and 6060, sets OTEL environment, and runs `--save-cache-debug`.

Control flow and state: Compose manages container lifecycle and named volumes. Profiles gate `jaeger` under `tracing` and Prometheus/Grafana under `metrics`. BuildKit depends on the collector, Prometheus depends on BuildKit, and Grafana depends on Prometheus.

Dependencies and integration: consumed by `hack/compose`. It integrates BuildKit debug metrics, OTLP export to collector, Jaeger trace UI on 16686, Prometheus scraping, and Grafana UI on 3000.

Risks and test signals: privileged BuildKit and fixed localhost ports can conflict with existing services. `jaeger:latest` is intentionally fluid and may change behavior. Test with `hack/compose config` and selected `--profile tracing`/`--profile metrics` runs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/compose.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/datasources.yaml -->
# sources/cloud-native/buildkit/hack/composefiles/datasources.yaml

Purpose: Grafana provisioning file that registers Prometheus as the default datasource for the local development metrics stack.

Important APIs, types, and functions: `apiVersion: 1`, datasource named `Prometheus`, type `prometheus`, proxy access, URL `http://prometheus:9090`, default flag, POST method, alert management disabled, Prometheus version `2.48.1`, no cache, recording rules enabled, 10 minute overlap, and empty exemplar trace destinations.

Control flow and state: declarative provisioning consumed by Grafana at startup. State is stored by Grafana in its volume after provisioning.

Dependencies and integration: mounted by `compose.yaml` into Grafana provisioning. It assumes the Compose service name `prometheus` and matching Prometheus version.

Risks and test signals: cache disabled is appropriate for development but inefficient elsewhere. Version drift with the Prometheus image should be kept aligned. Test by starting the metrics profile and checking Grafana datasource health.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/datasources.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/extensions/buildx.yaml -->
# sources/cloud-native/buildkit/hack/composefiles/extensions/buildx.yaml

Purpose: optional Compose extension that adds a second OpenTelemetry collector config for filtering and debugging Buildx metrics.

Important APIs, types, and functions: extends `otel-collector` command with both the base config and `buildx.yaml`. Defines config `otelcol_buildx_config` inline with a `filter/buildx` processor that keeps metrics whose instrumentation scope is `github.com/docker/buildx`, debug exporter verbosity `detailed`, and a `metrics/buildx` pipeline from OTLP through the filter to debug output.

Control flow and state: declarative Compose override. No persistence except collector logs.

Dependencies and integration: used with the base compose stack to inspect Buildx OTLP metrics without changing the primary config files.

Risks and test signals: the YAML uses collector double-colon path expansion syntax, which depends on collector config support. Debug exporter can be noisy. Test with `docker compose -f compose.yaml -f extensions/buildx.yaml config` and by sending Buildx metrics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/extensions/buildx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/grafana.ini -->
# sources/cloud-native/buildkit/hack/composefiles/grafana.ini

Purpose: local Grafana security configuration for the development metrics profile.

Important APIs, types, and functions: under `[security]`, sets `admin_user = moby` and `admin_password = moby`.

Control flow and state: declarative config mounted into Grafana. The configured credentials affect the initial admin login.

Dependencies and integration: referenced by `compose.yaml` as `grafana_config` and mounted at `/etc/grafana/grafana.ini`.

Risks and test signals: hardcoded credentials are development-only. Test by starting the metrics profile and logging into Grafana with the configured values.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/grafana.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/otelcol.yaml -->
# sources/cloud-native/buildkit/hack/composefiles/otelcol.yaml

Purpose: OpenTelemetry collector config for local BuildKit tracing and metrics ingestion.

Important APIs, types, and functions: configures an OTLP receiver on `0.0.0.0:4317`, an OTLP exporter to `jaeger:4317` with insecure TLS and retry max elapsed time 1 minute, a `nop` exporter, trace pipeline `otlp -> otlp/jaeger`, metrics pipeline `otlp -> nop`, and low-noise collector telemetry.

Control flow and state: declarative collector routing. Traces are forwarded to Jaeger when the tracing profile runs; metrics are accepted but dropped unless an extension overrides behavior.

Dependencies and integration: mounted into `otel-collector` by `compose.yaml`. BuildKit points `OTEL_EXPORTER_OTLP_ENDPOINT` at this service.

Risks and test signals: collector starts even when Jaeger profile is not active but trace export will fail until Jaeger is reachable. Metrics are intentionally dropped by default. Test via collector startup logs and Jaeger trace visibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/otelcol.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/prometheus.yml -->
# sources/cloud-native/buildkit/hack/composefiles/prometheus.yml

Purpose: Prometheus scrape config for local BuildKit debug metrics.

Important APIs, types, and functions: defines one scrape job `buildkit`, scrape interval `1m`, target `buildkit:6060`.

Control flow and state: declarative scrape configuration. Prometheus stores scraped time series in its named volume.

Dependencies and integration: assumes BuildKit debug address is enabled on port 6060 by `buildkitd.toml` and service DNS name `buildkit` exists in Compose.

Risks and test signals: if debug address or service name changes, scraping silently fails except Prometheus target health. Test in Prometheus UI and Grafana datasource queries.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/prometheus.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/cni.json -->
# sources/cloud-native/buildkit/hack/fixtures/cni.json

Purpose: CNI bridge network fixture for BuildKit tests that need a deterministic CNI configuration.

Important APIs, types, and functions: CNI version `1.0.0`, network name `buildkit`, bridge plugin, bridge `buildkit0`, default gateway, IP masquerade, hairpin mode, and host-local IPAM range `10.10.0.0/16`.

Control flow and state: declarative CNI config. Runtime state is created by CNI plugins when tests use the fixture.

Dependencies and integration: depends on standard CNI bridge and host-local plugins. Used by test harnesses that point BuildKit worker networking at fixture config.

Risks and test signals: bridge name and subnet can conflict with host networking. Tests should verify setup and teardown under privileged CI environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/cni.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/gen_gpg_test_env.sh -->
# sources/cloud-native/buildkit/hack/fixtures/gen_gpg_test_env.sh

Purpose: generates GPG signing test fixtures under `BUILDKIT_TEST_SIGN_FIXTURES` for a requested username.

Important APIs, types, and functions: shell script validates `BUILDKIT_TEST_SIGN_FIXTURES` and username argument, sets shared `GNUPGHOME`, writes a no-protection RSA cert key config, substitutes username/email placeholders, runs `gpg --generate-key`, extracts the fingerprint, adds an RSA signing subkey, writes `git_gpg_sign.sh`, writes `<user>.gpg.gitconfig`, exports `<user>.gpg.pub`, and creates a detached signature fixture over `<user>.http.artifact`.

Control flow and state: persists generated GPG home, config, and key material in the fixture directory. It changes into the fixture root and runs with `set -e` plus `set -x` after validation.

Dependencies and integration: depends on `gpg`, shell utilities, and the signing test environment. Used to prepare test data for provenance/signing workflows.

Risks and test signals: generated keys are unprotected and must remain test-only. Existing fixture files may be overwritten depending on username. Test signal is successful key generation and later signing/verifier tests using the generated fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/gen_gpg_test_env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/gen_ssh_test_env.sh -->
# sources/cloud-native/buildkit/hack/fixtures/gen_ssh_test_env.sh

Purpose: generates SSH signing test fixtures for BuildKit signing-related tests.

Important APIs, types, and functions: shell script validates `BUILDKIT_TEST_SIGN_FIXTURES` and username argument, creates `.ssh/<user>.id_ed25519` when missing, reads the public key, writes a per-user `git_ssh_sign.sh` wrapper that runs `ssh-keygen -Y sign -n git`, substitutes the username into the wrapper, writes `<user>.ssh.gitconfig` with `gpg.format = ssh` and the public signing key, and exports `<user>.ssh.pub`.

Control flow and state: persists keys, wrapper, gitconfig, and public key under the fixture root. It is fail-fast and command-traced after validation. The wrapper unsets `SSH_AUTH_SOCK` so signing uses the fixture key directly.

Dependencies and integration: depends on OpenSSH `ssh-keygen` and fixture environment variables consumed by signing tests.

Risks and test signals: key material is test-only and should not escape fixture directories. The generated wrapper parses Git signing arguments narrowly and may need updates if Git changes its invocation shape. Test signal is successful fixture generation followed by Git SSH signing verification tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/gen_ssh_test_env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/shell -->
# sources/cloud-native/buildkit/hack/shell

Purpose: builds the BuildKit `dev-env` image target and opens an interactive privileged shell inside it.

Important APIs, types, and functions: shell script creates a temporary Docker iidfile, runs `DOCKER_BUILDKIT=1 docker build --target dev-env .`, traps cleanup to remove the image id, conditionally mounts `SSH_AUTH_SOCK`, the source tree, and a Docker config file, then runs the image with `--privileged`, `/tmp` volume, registry mirror cache env, and `ash`.

Control flow and state: state is Docker image/container state plus any mounted workspace writes. The script primarily resolves environment and delegates to Docker.

Dependencies and integration: integrates with BuildKit's hack scripts and Docker CLI detection in `hack/util`. It is a developer convenience for reproducing CI/build environment behavior.

Risks and test signals: unquoted variables make paths with spaces fragile, and cleanup depends on the iidfile remaining readable. Behavior depends on Docker availability, TTY support, and mount permissions. Validate with `hack/shell` startup and expected tools present inside the container.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/shell -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/test -->
# sources/cloud-native/buildkit/hack/test

Purpose: main BuildKit test runner wrapper that normalizes environment, tags, packages, integration modes, and helper services before invoking Go tests.

Important APIs, types, and functions: bash script sources `hack/util`, configures fail-fast shell options, interprets environment variables and arguments for test selection, prepares Docker/BuildKit integration settings, and runs `go test` with appropriate tags, package lists, and flags.

Control flow and state: mostly orchestration. It may start or depend on Docker resources, temporary directories, and fixture setup, then exits with the test command status.

Dependencies and integration: central integration point for CI and local testing. Depends on Go, Docker, BuildKit test fixtures, `hack/util`, and package-specific test expectations.

Risks and test signals: broad environment coupling makes failures sensitive to Docker daemon state, privileges, rootless mode, and test tags. The best signal is successful CI and targeted local invocations with representative package/tag combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/test -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/test-compatibility-releases -->
# sources/cloud-native/buildkit/hack/test-compatibility-releases

Purpose: runs compatibility integration tests against published BuildKit release images.

Important APIs, types, and functions: shell script defaults `TEST_IMAGE_NAME`, `TESTPKGS`, `TESTFLAGS`, and `TEST_IMAGE_BUILD`, defines a default `COMPATIBILITY_RELEASES` matrix from `v0.13.0` through `v0.29.0` with expected compatibility versions, pulls each `moby/buildkit:<release>` image, copies `/usr/bin/buildkitd` into `.tmp/compat-bin/<release>`, then invokes `./hack/test integration` with `TEST_BUILDKITD_BINARY`, report suffix, and expected version.

Control flow and state: downloads or references release artifacts, then runs tests comparing current behavior with release expectations. State is mostly temporary caches and Docker resources.

Dependencies and integration: depends on Docker, Go test tooling, release artifact availability, and the repository's test harness.

Risks and test signals: network/release availability, image architecture, and Docker daemon state can cause non-code failures. The script accumulates failures and exits non-zero after all releases, so logs must be checked per grouped release.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/test-compatibility-releases -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/util -->
# sources/cloud-native/buildkit/hack/util

Purpose: shared shell utility library for BuildKit hack scripts, especially Docker/buildx command wrapping and build context/cache flag preparation.

Important APIs, types, and functions: initializes defaults for `BUILDX_CMD`, `BUILDX_BUILDER`, GitHub Actions metadata, `CONTEXT`, `CACHE_FROM`, and `CACHE_TO`. `dockerCmd` traces and runs `docker`. `buildxCmd` traces and runs the configured buildx command with `BUILDX_NO_DEFAULT_LOAD=true`. `buildAttestFlags` emits SBOM/provenance attest flags when supported and adds a GitHub Actions builder id. The tail logic switches CI builds for `moby/buildkit` to a Git URL context and augments GHA cache specs with repository/token values.

Control flow and state: sourced by other scripts rather than executed directly. Its state is shell variables/functions in the caller process.

Dependencies and integration: used by `hack/compose`, `hack/test`, and other build/test scripts to avoid duplicating Docker/buildx invocation and CI cache handling.

Risks and test signals: because it is sourced, variable names and shell options can affect callers. Cache flag string concatenation is shell-sensitive. Tests are indirect: build/test scripts that source it should still produce expected Docker/buildx commands in local and GitHub Actions environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/util -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/with-cgroupfs-remount -->
# sources/cloud-native/buildkit/hack/with-cgroupfs-remount

Purpose: helper wrapper used after creating a mount namespace to remount `/sys/fs/cgroup` before executing a command.

Important APIs, types, and functions: shell script reads the existing `/sys/fs/cgroup` mount options from `/proc/self/mounts`, unmounts `/sys/fs/cgroup`, mounts `cgroup2` back with the same options, and `exec`s its arguments.

Control flow and state: changes mount namespace state for the running process tree, then replaces itself with the target command.

Dependencies and integration: called by `hack/buildkitd-entrypoint` during cgroup namespace setup. Depends on Linux mount permissions and cgroup filesystem layout.

Risks and test signals: incorrect remount behavior can break cgroup visibility for BuildKit workers. Test in cgroup v2 containerized environments by verifying BuildKit sees the intended cgroup namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/with-cgroupfs-remount -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/identity/randomid.go -->
# sources/cloud-native/buildkit/identity/randomid.go

Purpose: generates opaque random identifiers with low collision probability for BuildKit components.

Important APIs, types, and functions: `idReader` defaults to `crypto/rand.Reader` and is replaceable for tests. Constants define 17 bytes of entropy, base36 encoding, and fixed output length 25. `NewID()` reads random bytes, sets the high bit, converts to base36, and slices to 25 characters after dropping the leading extra-entropy character.

Control flow and state: no persistence. The only mutable package state is `idReader` for test injection. `NewID` panics if random bytes cannot be read.

Dependencies and integration: uses `crypto/rand`, `io.ReadFull`, and `math/big`. Callers should treat returned identifiers as opaque strings.

Risks and test signals: panic on entropy failure is deliberate but can crash callers in constrained environments. The string slicing depends on high-bit and entropy sizing invariants. Tests should inject deterministic readers and assert length/base36 properties.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/identity/randomid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.go -->
# sources/cloud-native/buildkit/session/auth/auth.go

Purpose: daemon-side helper functions for retrieving registry credentials and tokens from active BuildKit client sessions.

Important APIs, types, and functions: `sessionAuthTimeout` is 60 seconds. `getSalt` lazily creates a daemon-restart-local 32 byte salt. `CredentialsFunc` returns a callback that asks any session in a group for username/secret. `FetchToken` asks sessions for a registry token. `VerifyTokenAuthority` sends a random challenge and validates a NaCl signed response against a public key. `GetTokenAuthority` retrieves a public key for client-side token authority.

Control flow and state: each public helper wraps the caller context with a timeout cause, iterates sessions through `Manager.Any`, creates an `AuthClient`, and treats unimplemented methods as non-fatal where backward compatibility is needed. Salt is process-local and avoids stable token-authority keys across daemon restarts.

Dependencies and integration: integrates with `session.Manager`, generated Auth gRPC clients, BuildKit gRPC error helpers, and `golang.org/x/crypto/nacl/sign`. Registry resolver code uses these callbacks during image pulls and token requests.

Risks and test signals: `rand.Read` errors are ignored for salt and challenge generation, which is low-probability but security-sensitive. `GetTokenAuthority` error text uses `len(pubKey)` instead of response length when invalid. Tests should cover unimplemented-session fallback, timeout behavior, challenge validation, and invalid public key lengths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.pb.go -->
# sources/cloud-native/buildkit/session/auth/auth.pb.go

Purpose: generated Go protobuf message definitions and descriptors for the Auth session service schema.

Important APIs, types, and functions: defines messages `CredentialsRequest`, `CredentialsResponse`, `FetchTokenRequest`, `FetchTokenResponse`, `GetTokenAuthorityRequest`, `GetTokenAuthorityResponse`, `VerifyTokenAuthorityRequest`, and `VerifyTokenAuthorityResponse`. Generated methods include `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated descriptors, getters for each field, raw descriptor compression, and file initialization.

Control flow and state: generated descriptor state is initialized once at package init. Message instances carry protobuf runtime state, size cache, unknown fields, and schema fields such as host, username, secret, realm, service, scopes, token, expiry, salt, payload, public key, and signed response.

Dependencies and integration: generated from `auth.proto` with `google.golang.org/protobuf` runtime. Used by handwritten auth helpers and authprovider server implementation.

Risks and test signals: this file should not be manually edited. Compatibility depends on preserving protobuf field numbers. Tests should target behavior through `auth.go`, `authprovider`, and wire round trips rather than generated internals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.proto -->
# sources/cloud-native/buildkit/session/auth/auth.proto

Purpose: protobuf contract for BuildKit session registry authentication.

Important APIs, types, and functions: package `moby.filesync.v1` with Go package `github.com/moby/buildkit/session/auth`. Service `Auth` exposes unary RPCs `Credentials`, `FetchToken`, `GetTokenAuthority`, and `VerifyTokenAuthority`. Messages carry host credentials, token request realm/service/scopes, token response token/expiry/issued-at, token authority salt/public key, and challenge payload/signed response.

Control flow and state: schema only. State is carried in RPC messages and handled by generated code plus authprovider implementation.

Dependencies and integration: consumed by generated Go, vtprotobuf, and gRPC stubs. Registry pull code and session auth providers use this service across BuildKit sessions.

Risks and test signals: the declared proto package name says `moby.filesync.v1`, which is unusual for auth and must remain compatible if clients depend on it. Field-number changes would break wire compatibility. Test by regenerating stubs and running auth provider tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth_grpc.pb.go -->
# sources/cloud-native/buildkit/session/auth/auth_grpc.pb.go

Purpose: generated gRPC client/server bindings for the Auth service.

Important APIs, types, and functions: defines `AuthClient`, concrete `authClient`, client methods for all four unary RPCs, `AuthServer`, `UnimplementedAuthServer`, `UnsafeAuthServer`, `RegisterAuthServer`, service descriptors, and unary handlers for `Credentials`, `FetchToken`, `GetTokenAuthority`, and `VerifyTokenAuthority`.

Control flow and state: clients call `cc.Invoke` with full method names. Server handlers decode requests, invoke optional interceptors, and dispatch to registered implementations. No persistent state beyond registered server implementations.

Dependencies and integration: generated by `protoc-gen-go-grpc`, uses `google.golang.org/grpc`. Handwritten `auth.go` creates clients; `authprovider.Register` registers server implementations.

Risks and test signals: generated compatibility depends on service names and method paths. Manual edits are unsafe. Tests should exercise client/server behavior through session integration and authprovider tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth_vtproto.pb.go -->
# sources/cloud-native/buildkit/session/auth/auth_vtproto.pb.go

Purpose: vtprotobuf-generated optimized helpers for Auth protobuf messages.

Important APIs, types, and functions: for each Auth message it defines `CloneVT`, `CloneMessageVT`, `EqualVT`, `EqualMessageVT`, `MarshalVT`, `MarshalToVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT`.

Control flow and state: methods manually copy fields, compare slices/maps, encode protobuf wire format into caller-provided buffers, compute sizes, and parse wire data while preserving unknown fields. It mutates receiver slices during unmarshal for reuse.

Dependencies and integration: depends on vtprotobuf/proto helper packages and the standard protobuf `proto.Message` interface. Used wherever BuildKit opts into faster protobuf serialization.

Risks and test signals: generated code is dense and should be regenerated, not edited. Map and slice aliasing semantics matter for clone/unmarshal correctness. Test signal is protobuf round-trip, equality, clone independence, and generated-code compilation after schema changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authconfig.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/authconfig.go

Purpose: declares TLS configuration structures used by Docker auth providers when contacting registries.

Important APIs, types, and functions: `AuthTLSConfig` includes `RootCAs []string`, `Insecure bool`, and `KeyPairs []TLSKeyPair`. `TLSKeyPair` records certificate and key file paths.

Control flow and state: data declarations only.

Dependencies and integration: consumed by `authprovider.tlsConfig` to build `tls.Config` for token fetch HTTP clients.

Risks and test signals: path validation happens later when config is loaded. Tests should cover root CA loading, client certificate loading, insecure mode, and missing files through `tlsConfig`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authconfigprovider.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/authconfigprovider.go

Purpose: adapts Docker CLI config files into an `AuthConfigProvider` with simple per-host caching.

Important APIs, types, and functions: `LoadAuthConfig(config)` returns `acp.load`. `authConfigProvider` holds the Docker config, cache map, and mutex. `load(ctx, host, scopes, cacheExpireCheck)` returns a cached auth config unless expired, maps Docker Hub registry host to Docker's config-file key, loads credentials, and stores a timestamped cache entry. `authConfigCacheEntry` stores creation time and auth pointer.

Control flow and state: mutable cache is protected by a mutex. `scopes` are accepted for provider interface compatibility but not used by this config-file implementation.

Dependencies and integration: uses Docker CLI `configfile.ConfigFile` and `types.AuthConfig`. Used by `NewDockerAuthProvider` in client sessions.

Risks and test signals: cache key is only host, so scope-specific providers would need a different implementation. Docker Hub key translation is critical. Existing test `TestFetchTokenCaching` covers cache reuse and expiration through token fetch behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authconfigprovider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authprovider.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/authprovider.go

Purpose: implements the client-side session Auth service that shares Docker registry credentials, fetches bearer tokens, handles registry TLS overrides, and proves token authority.

Important APIs, types, and functions: constants define default token expiration and Docker Hub host/key names. `AuthConfigProvider`, `ExpireCachedAuthCheck`, and `DockerAuthProviderConfig` configure providers. `NewDockerAuthProvider` creates a session attachable with default 4m50s cache expiration. `authProvider` implements generated `AuthServer`, logger support, TLS config assembly, credential conversion, token fetching, credential sharing, token authority key derivation, and scope label trimming.

Control flow and state: provider state includes an auth config provider, token seed store, optional logger, logger cache, TLS configs, and a mutex protecting credential-helper access and logging. `FetchToken` loads auth config, returns static registry token when present, otherwise calls OAuth token endpoint when credentials exist and falls back to GET token for known POST failures, or fetches anonymous token. `Credentials` returns username/password or identity token and logs first share per host. Token authority derives an Ed25519 key from HMAC(salt, seed) only when a secret exists, unless disabled by `BUILDKIT_NO_CLIENT_TOKEN`.

Dependencies and integration: uses containerd Docker auth helpers, Docker CLI config types, tracing HTTP transport, BuildKit progress logging, generated auth server registration, and NaCl signing.

Risks and test signals: security-sensitive paths include client token seed persistence, salt handling, and TLS override loading. The `tracing.DefaultClient` assignment can share mutable HTTP client state. Existing tests cover token cache expiration. Additional tests should cover OAuth fallback statuses, TLS config loading, token authority disablement, identity-token credential conversion, and concurrent credential-helper access.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authprovider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authprovider_test.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/authprovider_test.go

Purpose: verifies Docker auth provider cache behavior for registry tokens loaded from Docker config.

Important APIs, types, and functions: `TestFetchTokenCaching` creates a Docker config with Docker Hub registry token `hunter2`, fetches it, mutates config to `hunter3`, verifies default provider returns cached `hunter2`, then repeats with `ExpireCachedAuth` always true and verifies refreshed `hunter3`.

Control flow and state: test exercises `LoadAuthConfig` cache through `NewDockerAuthProvider` and `FetchToken`. It also validates Docker Hub host to config key mapping.

Dependencies and integration: uses Docker CLI config structs, generated auth request types, and testify assertions.

Risks and test signals: only static `RegistryToken` path is covered. OAuth network paths, TLS config, logger behavior, and token authority remain untested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authprovider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/tokenseed.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/tokenseed.go

Purpose: persists per-registry random client token seeds used to derive token authority keys.

Important APIs, types, and functions: `tokenSeeds` stores a mutex, directory, and in-memory host-to-seed map. `seed` wraps seed bytes. `(*tokenSeeds).getSeed(host)` creates the config dir, locks `.token_seed.lock` when possible, reads `.token_seed`, unmarshals seeds, creates a new seed if missing, writes the map with mode 0600, and returns the host seed. `newSeed` returns 16 random bytes.

Control flow and state: state is both in memory and persisted as JSON under Docker config dir. File locking is best-effort: read-only or permission failures are tolerated for lock/write but most other errors fail.

Dependencies and integration: uses `gofrs/flock`, `crypto/rand`, JSON, and Docker config dir from auth provider. `authprovider.getAuthorityKey` consumes seeds for HMAC key derivation.

Risks and test signals: `rand.Read` error is ignored in `newSeed`. If write fails due to read-only or permission issues, new seeds are returned but may not persist, changing token authority across runs. Tests should cover lock failure tolerance, corrupt JSON recovery, permissions, and seed stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/tokenseed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/attachable.go -->
# sources/cloud-native/buildkit/session/content/attachable.go

Purpose: exposes one or more containerd content stores over a BuildKit session as an attachable gRPC content service.

Important APIs, types, and functions: `GRPCHeaderID` names the metadata key selecting a store. `attachableContentStore` implements content store methods by calling `choose(ctx)`. `choose` reads incoming metadata, validates store id, and returns the selected store. `NewAttachable(stores)` wraps the store selector in containerd's `contentserver.New`. `(*attachable).Register` registers the content server.

Control flow and state: persistent state is the in-memory map of store ids to `content.Store`. Every content API call chooses a store from request metadata and delegates.

Dependencies and integration: uses containerd content API/server, errdefs, BuildKit session attachables, gRPC metadata, OCI descriptors, and digest types. Paired with `content/caller.go`.

Risks and test signals: missing metadata returns invalid argument; unknown store returns not found. Store ids are trusted metadata over the authenticated session. `content_test.go` verifies two stores can be selected and read through a session.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/attachable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/caller.go -->
# sources/cloud-native/buildkit/session/content/caller.go

Purpose: creates a client-side `content.Store` proxy that routes operations over a BuildKit session to a selected attachable content store.

Important APIs, types, and functions: `callerContentStore` wraps a proxied content store, selected store id, and session caller. `choose(ctx)` merges caller context and outgoing metadata with `GRPCHeaderID`. All content store methods call `choose` and delegate, wrapping errors with stack context. `NewCallerStore(c, storeID)` builds a containerd content client over `c.Conn()` and returns a proxy store.

Control flow and state: state is the caller connection and target store id. Each operation injects metadata before making the proxied content request.

Dependencies and integration: integrates with containerd content proxy, generated containerd content service client, and session caller lifecycle.

Risks and test signals: outgoing metadata key overwrite order matters; the newest store id is intentionally first. Errors are stack-wrapped, which can affect equality tests. `content_test.go` validates read flow through a real session.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/caller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/content_test.go -->
# sources/cloud-native/buildkit/session/content/content_test.go

Purpose: integration test for attachable content stores over a BuildKit session.

Important APIs, types, and functions: `TestContentAttachable` creates two local content stores, writes distinct blobs, starts a session and manager connected via `testutil.TestStream`, attaches both stores, then reads each blob through `NewCallerStore`.

Control flow and state: uses `errgroup` to run session and caller concurrently. Test data lives in temporary directories and session closes after successful reads.

Dependencies and integration: exercises `session.NewSession`, `session.NewManager`, content attachable registration, content caller proxy, containerd local store, and test stream plumbing.

Risks and test signals: covers happy-path store selection but not missing metadata, unknown store ids, write/update/delete methods, or session cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/content_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/context.go -->
# sources/cloud-native/buildkit/session/context.go

Purpose: links request contexts to session caller contexts so requests cancel when the underlying session closes.

Important APIs, types, and functions: `contextWithCaller(ctx, callerCtx)` returns a context canceled either by the base request context or by `callerCtx` via `context.AfterFunc`, preserving the caller cancellation cause when present.

Control flow and state: no persistence. It creates a cancel-cause context and registers an AfterFunc on the caller context.

Dependencies and integration: used by `client.Context` in `manager.go`, affecting every session caller request.

Risks and test signals: AfterFunc is not explicitly stopped, relying on context lifecycle. `context_test.go` verifies caller cancellation and request cancellation causes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/context_test.go -->
# sources/cloud-native/buildkit/session/context_test.go

Purpose: tests cancellation behavior for contexts derived from session caller contexts.

Important APIs, types, and functions: `TestContextWithCaller` has subtests for caller close canceling the derived context with `context.DeadlineExceeded`, and base request close canceling with `context.Canceled`.

Control flow and state: uses `select` with a 5 second timeout to ensure cancellation occurs.

Dependencies and integration: validates the helper used by session callers in `manager.go`.

Risks and test signals: tests do not check cleanup of the registered AfterFunc or simultaneous cancellation ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/context_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter.pb.go -->
# sources/cloud-native/buildkit/session/exporter/exporter.pb.go

Purpose: generated protobuf message definitions for the session Exporter service.

Important APIs, types, and functions: defines `FindExportersRequest` with metadata map and refs, `FindExportersResponse` with repeated exporter requests, and `ExporterRequest` with type and attrs. Generated methods include standard protobuf reflection, getters, descriptor compression, and file initialization.

Control flow and state: generated descriptor state is initialized once. Message state is per-instance protobuf runtime data.

Dependencies and integration: generated from `exporter.proto`; used by exporterprovider and generated gRPC stubs.

Risks and test signals: field numbers are external wire contracts. Generated file should not be edited manually. Tests should operate through exporterprovider callback behavior and protobuf round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter.proto -->
# sources/cloud-native/buildkit/session/exporter/exporter.proto

Purpose: protobuf contract for discovering exporter requests through a BuildKit session.

Important APIs, types, and functions: package `moby.exporter.v1`, Go package `github.com/moby/buildkit/session/exporter`. Service `Exporter` exposes unary `FindExporters`. Request carries `map<string, bytes> metadata` and repeated refs. Response carries repeated `ExporterRequest`, each with string `Type` and string map `Attrs`.

Control flow and state: schema only. Runtime state is in request/response messages and provider callbacks.

Dependencies and integration: drives generated Go, gRPC, and vtproto code, and is implemented by `exporterprovider.Provider`.

Risks and test signals: map value bytes allow opaque metadata but require callers to agree on encoding. Field-name capitalization `Type` and `Attrs` is preserved in generated Go. Test by callback integration and wire compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter_grpc.pb.go -->
# sources/cloud-native/buildkit/session/exporter/exporter_grpc.pb.go

Purpose: generated gRPC bindings for the Exporter session service.

Important APIs, types, and functions: defines `ExporterClient`, `FindExporters` client call, `ExporterServer`, `UnimplementedExporterServer`, `UnsafeExporterServer`, `RegisterExporterServer`, service descriptor, and unary handler.

Control flow and state: client invokes `/moby.exporter.v1.Exporter/FindExporters`; server handler decodes request, applies optional interceptor, and dispatches to implementation.

Dependencies and integration: used by session exporter discovery providers and callers over gRPC.

Risks and test signals: service and method names are compatibility-sensitive. Generated code should be regenerated from proto. Test through provider registration and client calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter_vtproto.pb.go -->
# sources/cloud-native/buildkit/session/exporter/exporter_vtproto.pb.go

Purpose: vtprotobuf optimized clone, equality, marshal, size, and unmarshal helpers for exporter protobuf messages.

Important APIs, types, and functions: implements `CloneVT`, `EqualVT`, `MarshalVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT` for `FindExportersRequest`, `FindExportersResponse`, and `ExporterRequest`.

Control flow and state: generated code handles repeated exporter slices, string maps, byte maps, unknown fields, and protobuf wire parsing.

Dependencies and integration: used by protobuf fast paths in BuildKit session exporter code.

Risks and test signals: map ordering and deep-copy behavior matter for deterministic equality and clone independence. Regenerate after schema changes and run protobuf round-trip tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporterprovider/provider.go -->
# sources/cloud-native/buildkit/session/exporter/exporterprovider/provider.go

Purpose: small provider implementation for the session Exporter gRPC service backed by a callback.

Important APIs, types, and functions: `Callback` accepts context, metadata, and refs and returns exporter requests. `New(cb)` returns `*Exporter`. `Exporter.Register` registers the generated service. `FindExporters` calls the callback and wraps the result in `FindExportersResponse`, returning gRPC `Unavailable` when no callback is registered.

Control flow and state: state is only the callback. Each RPC delegates directly to it.

Dependencies and integration: depends on generated exporter gRPC code and standard gRPC status codes. Lets higher-level callers plug custom exporter discovery into a session.

Risks and test signals: nil callback is a runtime error. Callback errors are propagated directly. Tests should cover nil callback, metadata/ref propagation, and response wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporterprovider/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy.go -->
# sources/cloud-native/buildkit/session/filesync/diffcopy.go

Purpose: implements the diffcopy stream transport used by session filesync and local exporter copy operations.

Important APIs, types, and functions: `Stream` abstracts gRPC stream send/recv. `newStreamWriter` creates a buffered writer over a client stream. `streamWriterCloser.Write` chunks messages at 3 MiB to stay below gRPC defaults and handles EOF remote errors. `Close` closes send and waits for receiver EOF. `recvDiffCopy` receives fsutil changes into a destination and updates cache/progress. `syncTargetDiffCopy` receives into a directory root with merge or delete behavior. `writeTargetFile` writes streamed `BytesMessage` data to an output writer.

Control flow and state: streaming functions are stateful over gRPC streams and filesystem destinations. `recvDiffCopy` marks cache support and closes send on clean completion. `syncTargetDiffCopy` creates destination dirs, opens an `os.Root`, maps received file ownership to current uid/gid, and changes differ/merge settings for delete mode.

Dependencies and integration: depends on `tonistiigi/fsutil`, gRPC streams, filesystem APIs, and BuildKit logging. Called from `filesync.go` protocols and exporter copy helpers.

Risks and test signals: stream close semantics are subtle and EOF can mask remote errors. Delete mode replaces merge behavior and must be gated by daemon support. Tests cover delete-mode support gating in `filesync_test.go`; more coverage should include chunked writes, cache updater callbacks, and metadata-only receive.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy_unix.go -->
# sources/cloud-native/buildkit/session/filesync/diffcopy_unix.go

Purpose: Unix implementation of sending a diffcopy stream.

Important APIs, types, and functions: `sendDiffCopy(stream, fs, progress)` wraps `fsutil.Send(stream.Context(), stream, fs, progress)` with stack errors.

Control flow and state: no persistent state. It streams filesystem content and metadata through the provided stream.

Dependencies and integration: compiled on non-Windows platforms and called by the filesync protocol table.

Risks and test signals: behavior is primarily in fsutil. Test through session filesync integration, include/exclude filters, and exporter copy paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy_windows.go -->
# sources/cloud-native/buildkit/session/filesync/diffcopy_windows.go

Purpose: Windows implementation of sending a diffcopy stream with temporary backup privilege.

Important APIs, types, and functions: `sendDiffCopy` enables `winio.SeBackupPrivilege`, defers disabling it, and calls `fsutil.Send`.

Control flow and state: temporarily changes process privileges for the duration of send so fsutil goroutines can copy special Windows metadata files.

Dependencies and integration: compiled on Windows, depends on `github.com/Microsoft/go-winio` and fsutil. Called through the shared filesync protocol table.

Risks and test signals: privilege enablement is security-sensitive and has a TODO to review exploitability. Windows tests should cover copying metadata files and privilege cleanup after errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.go -->
# sources/cloud-native/buildkit/session/filesync/filesync.go

Purpose: main session file synchronization implementation for sending local sources to the daemon and copying daemon output back to callers.

Important APIs, types, and functions: constants define metadata keys for filters, dir names, exporter metadata, exporter ids, and multi-platform transfer support. `NewFSSyncProvider`, `DirSource`, `StaticDirSource`, and `fsSyncProvider` expose client local directories to sessions. `FSSync` requests a supported protocol, sends include/exclude/follow metadata, opens a stream, and receives into a destination. `WithFSSync`, `WithFSSyncDir`, `WithFSSyncDirDelete`, `NewFSSyncTarget`, and `SyncTarget` define local exporter receive targets. `CopyToCaller` streams an fsutil FS to the caller. `CopyFileWriter` returns a streaming writer. `encodeOpts` and `decodeOpts` preserve non-ASCII metadata values for gRPC headers.

Control flow and state: providers maintain local directory sources plus one-shot progress callback/done channel. SyncTarget maintains maps from exporter id to file callbacks or output directories. `FSSync` discovers supported methods through session method URLs, injects outgoing metadata, then delegates receive to the protocol. `SyncTarget.DiffCopy` chooses a target by metadata id, gates delete mode on multi-platform support metadata, and either receives into a directory or writes a single output stream.

Dependencies and integration: heavily integrates with BuildKit session callers, generated FileSync/FileSend gRPC services, `tonistiigi/fsutil`, gRPC metadata, and BuildKit logging. Used by local source transfer and local exporter transfer paths.

Risks and test signals: one-shot callback fields on `fsSyncProvider` are not protected by a mutex. Metadata overwrites are logged but still mutate caller-provided metadata. Non-ASCII header encoding only encodes non-ASCII characters, relying on gRPC header tolerance for other ASCII. Existing tests cover include patterns and delete-mode support gating. Additional tests should cover encoded metadata round trips, multiple exporter ids, callback races, and copy-to-caller error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.pb.go -->
# sources/cloud-native/buildkit/session/filesync/filesync.pb.go

Purpose: generated protobuf message and descriptor definitions for filesync's `BytesMessage`.

Important APIs, types, and functions: defines `BytesMessage` with `Data []byte`, standard protobuf methods/getters, raw descriptor state, and file initialization for `filesync.proto`.

Control flow and state: descriptor state is initialized once; message state is per stream message.

Dependencies and integration: generated from `filesync.proto`, imports fsutil wire proto descriptors because services stream fsutil packets. Used by FileSend streaming and `streamWriterCloser`.

Risks and test signals: generated file should not be edited manually. Message size and chunking behavior are handled in handwritten stream code. Test through filesync stream round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.proto -->
# sources/cloud-native/buildkit/session/filesync/filesync.proto

Purpose: protobuf contract for BuildKit session file synchronization.

Important APIs, types, and functions: package `moby.filesync.v1`, Go package `github.com/moby/buildkit/session/filesync`. Imports fsutil wire packet proto. Service `FileSync` has bidirectional streaming RPCs `DiffCopy` and `TarStream` over `fsutil.types.Packet`. Service `FileSend` has bidirectional `DiffCopy` over `BytesMessage`. `BytesMessage` contains `bytes data = 1`.

Control flow and state: schema only. Runtime behavior is implemented in generated gRPC stubs and handwritten filesync/diffcopy code.

Dependencies and integration: ties BuildKit sessions to fsutil's streaming diff protocol and local exporter byte streams.

Risks and test signals: `TarStream` exists in schema and provider method but is not listed in `supportedProtocols`, so callers currently negotiate diffcopy only. Test via generated-code compilation and filesync integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_grpc.pb.go -->
# sources/cloud-native/buildkit/session/filesync/filesync_grpc.pb.go

Purpose: generated gRPC client/server bindings for FileSync and FileSend streaming services.

Important APIs, types, and functions: defines `FileSyncClient` streams for `DiffCopy` and `TarStream`, `FileSyncServer` interfaces, stream wrapper types, `RegisterFileSyncServer`, plus `FileSendClient`, `FileSendServer`, and `RegisterFileSendServer` for `BytesMessage` diffcopy.

Control flow and state: stream clients create bidirectional gRPC streams and expose typed send/recv wrappers. Server descriptors route incoming streams to registered implementations.

Dependencies and integration: used by `filesync.go` providers and callers. It depends on fsutil packet generated types and gRPC.

Risks and test signals: service paths and stream message types are compatibility-sensitive. Test through end-to-end session file transfer and generated-code regeneration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_test.go -->
# sources/cloud-native/buildkit/session/filesync/filesync_test.go

Purpose: tests selected filesync behaviors.

Important APIs, types, and functions: `TestFileSyncIncludePatterns` creates a temp source with `foo` and `bar`, attaches a filesystem provider, runs a session, calls `FSSync` with include pattern `ba*`, and verifies only `bar` is copied. `TestLocalExporterModeDeleteRequiresDaemonSupport` creates a delete-mode sync target without support metadata, expects an error, and verifies stale file content remains. `testFileSendStream` is a minimal stream stub returning EOF.

Control flow and state: uses temp directories and errgroup-managed session/caller concurrency. Tests explicitly close the session after sync.

Dependencies and integration: exercises `session`, `testutil`, fsutil FS, gRPC metadata, and local exporter target code.

Risks and test signals: covers important gates but not exclude/follow path combinations, non-ASCII metadata encoding, successful delete mode, or CopyFileWriter streaming.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_vtproto.pb.go -->
# sources/cloud-native/buildkit/session/filesync/filesync_vtproto.pb.go

Purpose: vtprotobuf optimized helpers for filesync `BytesMessage`.

Important APIs, types, and functions: implements clone, equality, marshal, size, and unmarshal methods for `BytesMessage`.

Control flow and state: generated code deep-copies data on clone, compares data and unknown fields, writes protobuf wire format, and parses byte fields while preserving unknown fields.

Dependencies and integration: used by fast protobuf paths for FileSend byte streams.

Risks and test signals: generated code should be regenerated from proto. Test byte round trips, clone independence, and stream integration with large chunked writes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/group.go -->
# sources/cloud-native/buildkit/session/group.go

Purpose: defines session groups and iteration helpers for trying operations against one of several active sessions.

Important APIs, types, and functions: `ErrNoActiveSessions`, interfaces `Group` and `Iterator`, `NewGroup`, `group.NextSession`, `AllSessionIDs`, and `Manager.Any`. `Any` iterates session ids, waits up to 5 seconds for each session, invokes a callback with the caller, returns on first success, and otherwise returns the last error or `ErrNoActiveSessions`.

Control flow and state: group iteration consumes ids in order on iterator copies. `Any` uses `Manager.Get` and callback errors to advance to the next session.

Dependencies and integration: used by auth helpers and other session-scoped features that can use any active client session in a group.

Risks and test signals: `defer cancel` inside the loop defers all cancels until function return, which is bounded by group size but worth noting. Last-error behavior can hide earlier failures. Tests should cover nil groups, empty groups, session wait timeout, and fallback to later sessions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpc.go -->
# sources/cloud-native/buildkit/session/grpc.go

Purpose: provides low-level gRPC-over-hijacked-connection support and health monitoring for BuildKit sessions.

Important APIs, types, and functions: `healthCheckConfig`, `defaultHealthCheckConfig`, `headerSessionHealthCustomTimeout`, `healthCheckConfigFromHeaders`, `serve`, `grpcClientConn`, and `monitorHealth`. `grpcClientConn` builds a one-connection gRPC client over a provided `net.Conn`, applies max message sizes, error interceptors, optional tracing stats, and starts health monitoring.

Control flow and state: health monitoring ticks every configured interval, runs gRPC health checks with adaptive timeout, counts consecutive failures/successes, and closes/cancels the connection after fatal failures. Custom test timeout header lowers interval/timeout but clamps to at least 1 second.

Dependencies and integration: uses containerd default message sizes, BuildKit tracing/error helpers, http2 server, OpenTelemetry gRPC instrumentation, and gRPC health checking. Called by session manager connection handling.

Risks and test signals: health checks can falsely fail under low bandwidth or heavy concurrency, so thresholds are intentionally tolerant. Dialer rejects more than one connection. Tests should cover custom timeout parsing, single-connection enforcement, tracing option path, and fatal health close behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpchijack/dial.go -->
# sources/cloud-native/buildkit/session/grpchijack/dial.go

Purpose: adapts the BuildKit control service `Session` stream into a `net.Conn` suitable for session gRPC transport.

Important APIs, types, and functions: `Dialer(api)` returns a `session.Dialer` that lowercases headers, attaches them as outgoing metadata, opens `api.Session`, and wraps the stream with `streamToConn`. `conn` implements `net.Conn` over `SendMsg`/`RecvMsg`, buffering partial reads, serializing reads/writes with mutexes, and closing the client send side when possible.

Control flow and state: `Read` reuses leftover bytes before receiving a new `BytesMessage`. `Write` sends one message. `Close` calls `CloseSend` for client streams, drains received messages until EOF, appends leftovers, closes `closeCh`, and reports non-EOF receive errors. Deadline methods are no-ops.

Dependencies and integration: depends on BuildKit control API `BytesMessage`, gRPC metadata, and session dialer contract. Used when clients connect sessions through the control API instead of raw HTTP upgrade.

Risks and test signals: deadline no-ops can affect code expecting timeout semantics. `Close` appends `c.buf` after resetting it from message capacity, which deserves scrutiny for draining correctness. Tests should cover partial reads, concurrent read/write, close-drain behavior, and metadata lowercasing.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpchijack/dial.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpchijack/hijack.go -->
# sources/cloud-native/buildkit/session/grpchijack/hijack.go

Purpose: server-side helper for turning a control service session stream into a `net.Conn` plus incoming metadata.

Important APIs, types, and functions: `Hijack(stream)` reads incoming metadata from stream context, wraps the stream via `streamToConn`, and returns the connection, close channel, and metadata map.

Control flow and state: no persistence beyond stream connection state.

Dependencies and integration: paired with `grpchijack.Dialer` and used by control service session handling to feed session manager connections.

Risks and test signals: metadata is returned even if absent as the zero metadata map. Tests should verify metadata propagation and close channel behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpchijack/hijack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/manager.go -->
# sources/cloud-native/buildkit/session/manager.go

Purpose: tracks active BuildKit sessions and exposes callers for session-scoped services.

Important APIs, types, and functions: `Caller` interface exposes `Context`, `Supports`, `Conn`, and `SharedKey`. `Manager` stores session clients under a mutex/condition. `NewManager`, `HandleHTTPRequest`, `HandleConn`, internal `handleConn`, `Get`, `client.Context`, `SharedKey`, `Supports`, `Conn`, and `canonicalHeaders` implement session registration and lookup.

Control flow and state: incoming HTTP upgrade requests are hijacked, validated for `h2c`, acknowledged with 101, then passed to `handleConn`. `handleConn` canonicalizes headers, reads session id/shared key/methods, creates a gRPC client over the connection, stores the session, broadcasts waiters, waits for context cancellation, closes the connection, and removes the session. `Get` normalizes prefixed ids, waits on the condition unless `noWait`, and returns a caller or nil.

Dependencies and integration: used by BuildKit daemon session handling, auth/filesync/content/secrets callers, HTTP upgrade paths, and raw/grpchijack connection paths.

Risks and test signals: duplicate session ids are rejected. Missing session ids are not explicitly validated here. Condition waits rely on a cancellation goroutine broadcasting. Tests should cover HTTP upgrade validation, duplicate sessions, method support matching, noWait lookup, and cleanup on close.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.go -->
# sources/cloud-native/buildkit/session/secrets/secrets.go

Purpose: client helper for retrieving secret bytes from a BuildKit session.

Important APIs, types, and functions: `SecretStore` interface defines `GetSecret(context.Context, string)`. `ErrNotFound` is a package sentinel. `GetSecret(ctx, c, id)` derives caller context, creates a `SecretsClient`, calls `GetSecret`, maps unimplemented and not-found gRPC codes to wrapped `ErrNotFound`, and returns response data.

Control flow and state: no persistence. Each call is a unary session RPC.

Dependencies and integration: generated secrets gRPC client, session caller, BuildKit gRPC code helper, and secretsprovider server.

Risks and test signals: unimplemented is treated as not found for backward compatibility, which can hide client/server version mismatches. Tests should cover successful retrieval, not found mapping, unimplemented mapping, and other errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.pb.go -->
# sources/cloud-native/buildkit/session/secrets/secrets.pb.go

Purpose: generated protobuf message definitions for the Secrets session service.

Important APIs, types, and functions: defines `GetSecretRequest` with `ID` and `Annotations`, `GetSecretResponse` with `Data`, standard protobuf methods/getters, descriptor compression, map-entry metadata, and file initialization.

Control flow and state: generated descriptor initialization plus per-message protobuf state.

Dependencies and integration: generated from `secrets.proto`, used by handwritten secret client/provider code and gRPC stubs.

Risks and test signals: field numbers and map semantics are wire contracts. Generated file should not be edited. Test through secretsprovider behavior and protobuf round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.proto -->
# sources/cloud-native/buildkit/session/secrets/secrets.proto

Purpose: protobuf contract for retrieving secrets over a BuildKit session.

Important APIs, types, and functions: package `moby.buildkit.secrets.v1`, Go package `github.com/moby/buildkit/session/secrets`. Service `Secrets` exposes unary `GetSecret`. Request includes `ID` and annotations map. Response includes secret `data` bytes.

Control flow and state: schema only; runtime state lives in provider stores and RPC messages.

Dependencies and integration: drives generated Go, gRPC, and vtproto code. Used by Dockerfile secret mounts and secret providers.

Risks and test signals: annotations are in schema but not used by the simple provider. Compatibility requires stable field numbers. Test with generated code and provider integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets_grpc.pb.go -->
# sources/cloud-native/buildkit/session/secrets/secrets_grpc.pb.go

Purpose: generated gRPC bindings for the Secrets session service.

Important APIs, types, and functions: defines `SecretsClient`, `GetSecret` client method, `SecretsServer`, `UnimplementedSecretsServer`, `UnsafeSecretsServer`, `RegisterSecretsServer`, service descriptor, and unary handler.

Control flow and state: client invokes `/moby.buildkit.secrets.v1.Secrets/GetSecret`; server handler decodes request, applies optional interceptor, and dispatches to implementation.

Dependencies and integration: used by `secrets.GetSecret` and `secretsprovider.Register`.

Risks and test signals: service path changes would break compatibility. Generated code should be regenerated from proto. Test through session secret retrieval.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets_vtproto.pb.go -->
# sources/cloud-native/buildkit/session/secrets/secrets_vtproto.pb.go

Purpose: vtprotobuf optimized helpers for secret protobuf messages.

Important APIs, types, and functions: implements clone, equality, marshal, size, and unmarshal methods for `GetSecretRequest` and `GetSecretResponse`, including annotations map handling and data byte copying.

Control flow and state: generated code deep-copies maps/slices, preserves unknown fields, and parses protobuf wire format.

Dependencies and integration: used by fast protobuf paths for secrets session messages.

Risks and test signals: map clone/equality behavior is important for annotations. Regenerate after schema changes and test round trips plus clone independence.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secretsprovider/secretsprovider.go -->
# sources/cloud-native/buildkit/session/secrets/secretsprovider/secretsprovider.go

Purpose: implements a session attachable server for serving secrets from a `SecretStore`.

Important APIs, types, and functions: `MaxSecretSize` is 500 KiB. `NewSecretProvider(store)` returns a session attachable. `secretProvider.Register` registers generated server. `GetSecret` loads bytes from the store, maps `secrets.ErrNotFound` to gRPC NotFound, rejects oversized secrets, and returns data. `FromMap` creates a provider from an in-memory byte map. `mapStore.GetSecret` reads from the map.

Control flow and state: provider state is the backing store. Map provider state is in-memory bytes. Every RPC fetches from the store at request time.

Dependencies and integration: uses session attachables, generated secrets server, gRPC status codes, and `secrets.SecretStore`.

Risks and test signals: oversized map secrets are rejected only at request time, while file store validates file size at setup and reads env secrets at request time. Tests should cover max-size enforcement, not-found status, and FromMap behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secretsprovider/secretsprovider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secretsprovider/store.go -->
# sources/cloud-native/buildkit/session/secrets/secretsprovider/store.go

Purpose: builds a file/env-backed `SecretStore` from user-provided secret sources.

Important APIs, types, and functions: `Source` includes `ID`, `FilePath`, and `Env`. `NewStore(files)` validates ids, defaults an unspecified source to environment variable when present or file path otherwise, stats file-backed secrets, rejects files larger than `MaxSecretSize`, and stores sources by id. `fileStore.GetSecret` returns env value bytes or reads the configured file.

Control flow and state: store state is an in-memory id-to-source map. File content and environment values are read at request time, except file size is checked during construction.

Dependencies and integration: used by BuildKit secret CLI/session setup and `secretsprovider.NewSecretProvider`.

Risks and test signals: file size can change after `NewStore`, so provider-level max-size enforcement is still important. Env values are not size-checked until provider response path. Duplicate ids overwrite earlier sources. Tests should cover defaulting, missing ids, missing files, env reads, file reads, duplicate behavior, and size enforcement.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secretsprovider/store.go -->
