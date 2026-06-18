# subset-b-009269 Research

Grouped research report for the files assigned to `subset-b-009269`. Each section is bounded by source-path markers so it can be split into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.0.json -->
# sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.0.json

## Purpose
This file is a stored pynfs NFSv4.0 baseline result in JSON form. It is not executable logic; it captures the expected result envelope for an `all` pynfs run so kdevops can compare future test output against a known baseline. The top-level schema is junit-like: `name`, `tests`, `failures`, `errors`, `skipped`, `time`, `timestamp`, and a `testcase` array.

## Important Data Shape
The baseline records `tests: 679`, `failures: 1`, `errors: 0`, `skipped: 98`, and a total runtime near 1782.75 seconds with timestamp `2023-03-20 16:13:01.857565`. Each testcase object carries at least `classname`, `name`, and `time`; skipped cases include `skipped: 1`, and failed cases include a nested `failure` object with `err` and `message`.

The only recorded failure is `st_lock.testOpenUpgradeLock`, where `OP_LOCK` returned `NFS4ERR_BAD_SEQID` instead of `NFS4_OK`. High-volume classes include `st_setattr`, `st_getattr`, `st_rename`, `st_nverify`, `st_verify`, `st_lock`, and `st_open`.

## Control Flow and Integration
The file is produced by the pynfs runner, specifically the NFSv4.0 leg in `run_pynfs.sh`, which writes `${PYNFS_DATA}/pynfs-4.0-results.json` after running `./testserver.py ... "${EXPORT_BASE}-4.0" all`. Downstream playbooks or result checkers can use this baseline to decide whether a current run differs materially from the accepted state.

## State, Persistence, and Dependencies
Persistence is the JSON artifact itself. The external dependency is the pynfs testserver output format; any schema drift in pynfs will affect consumers. Since this file stores timestamps and duration, consumers should compare semantic fields such as test names, failure messages, and skip counts rather than expecting byte-for-byte stability.

## Risks and Test Signals
The failure count is intentionally nonzero, so tooling must not treat any failure as automatically fatal without consulting the baseline. The `status_counts` inferred from the data are not explicit because passing cases omit `status`; readers must interpret missing failure/error/skipped fields as pass. The key regression signals are changes in the single `st_lock` failure, the 98 skipped tests, and the total testcase count of 679.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.0.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.1.json -->
# sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.1.json

## Purpose
This file is the stored pynfs NFSv4.1 baseline result. Like the v4.0 baseline, it is a data artifact rather than code, and it anchors expected behavior for a kdevops pynfs run against an NFSv4.1 export.

## Important Data Shape
The top-level object contains `name: all`, `tests: 262`, `failures: 0`, `errors: 0`, `skipped: 91`, `time: 546.1761648654938`, `timestamp: 2023-03-20 16:22:10.506308`, and an array of 262 testcase objects. Testcases include `classname`, `name`, and `time`; skipped cases use `skipped: 1`. Passing cases do not carry an explicit status field.

Prominent classes include `st_rename`, `st_create_session`, `st_exchange_id`, `st_flex`, `st_sequence`, `st_reboot`, `st_xattr`, `st_current_stateid`, and `st_delegation`. All `st_flex`, `st_reboot`, `st_xattr`, and `st_delegation` cases visible in the class summaries are skipped, so the baseline includes substantial unsupported or intentionally omitted coverage.

## Control Flow and Integration
`run_pynfs.sh` runs the NFSv4.1 leg by changing into `${PYNFS_DATA}/nfs4.1` and invoking `testserver.py` with JSON output at `${PYNFS_DATA}/pynfs-4.1-results.json`. The flags for this leg are `all deleg xattr`, making the baseline sensitive to delegation and extended attribute coverage even when many of those tests are skipped.

## State, Persistence, and Dependencies
The file persists a historical expected result for comparison. It depends on pynfs JSON formatting and test class naming. Because runtime fields are environmental, robust consumers should focus on testcase identity, skip/failure/error fields, and aggregate counts.

## Risks and Test Signals
This baseline expects no failures or errors but many skips. A new failure is a strong regression signal; a skipped-to-passed transition may be improvement but still changes baseline accounting. The 262 testcase count and 91 skipped tests are the key checks. Since this is v4.1-specific, consumers must not compare it directly with the v4.0 baseline, which has a different testcase universe and one accepted failure.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/current-v4.1.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs.sh -->
# sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs.sh

## Purpose
This shell script runs pynfs server tests for both NFSv4.0 and NFSv4.1 in parallel and writes JSON result files under `$PYNFS_DATA`. It is the workflow runner that generates the current result artifacts consumed by baseline comparison.

## Important APIs and Variables
The script depends on environment variables `PYNFS_DATA` and `EXPORT_BASE`. It defines two parallel arrays: `vers=("4.0" "4.1")` and `flags=("all" "all deleg xattr")`. For each version it changes directory to `${PYNFS_DATA}/nfs${version}` and runs `./testserver.py` with `--json`, `--maketree`, `--uid=0`, `--gid=0`, the export path, and the per-version flags.

## Control Flow
The first loop starts both pynfs invocations in the background. It increments an array index so v4.0 receives `all` and v4.1 receives `all deleg xattr`. The second loop calls `fg || true` once per version to wait for background jobs through shell job control.

## State, Persistence, and Dependencies
Persistent outputs are `${PYNFS_DATA}/pynfs-4.0-results.json` and `${PYNFS_DATA}/pynfs-4.1-results.json`. The script assumes job control is available (`set -m`), `testserver.py` exists in each pynfs checkout, exports are mounted or reachable at `${EXPORT_BASE}-${version}`, and the shell can foreground background jobs.

## Risks and Test Signals
The use of `fg || true` suppresses failures while waiting, so a failing pynfs run may not fail the script directly. Missing quotes around environment-expanded paths can break on spaces. Because both runs execute concurrently, shared server/export resources can introduce cross-test interference. Test signal comes from the JSON result files rather than the script exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs_block.sh -->
# sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs_block.sh

## Purpose
This script runs the pynfs NFSv4.1 pNFS block test set and writes a dedicated JSON result file. It complements the general v4.0/v4.1 runner with coverage for the block layout export.

## Important APIs and Variables
The script fixes `version="4.1"`, changes to `${PYNFS_DATA}/nfs4.1`, and invokes `./testserver.py`. Its output is `${PYNFS_DATA}/pynfs-block-results.json`; the export path is `"${EXPORT_BASE}-pnfs"`; the test selector is `block`.

## Control Flow
There is no loop or concurrency. The script performs a single directory change and a single testserver execution. The exit code is therefore controlled by `testserver.py` unless the `cd` command fails and the shell continues, because the script does not use `set -e`.

## State, Persistence, and Dependencies
The persistent state is the block-layout JSON result file. The script depends on the v4.1 pynfs checkout, the pNFS export name, root uid/gid test execution, and the server supporting the block test group.

## Risks and Test Signals
The unguarded `cd` means a missing pynfs directory can still lead to executing `./testserver.py` from the wrong directory if such a file exists. The script does not quote `PYNFS_DATA` in the `cd`. The primary test signal is whether the generated block result matches accepted pNFS behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs_block.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Cargo.toml -->
# sources/test-tools/kdevops/workflows/rcloud/Cargo.toml

## Purpose
This manifest defines the `rcloud` Rust package, a kdevops private-cloud REST API server that exposes VM lifecycle operations over libvirt. It builds a single binary named `rcloud` from `src/main.rs`.

## Important Dependencies
Core runtime dependencies are `actix-web` and `actix-rt` for HTTP service, `tokio` with full features for async runtime support, `serde`, `serde_json`, and `serde_yaml` for API and kdevops configuration data, `virt` for libvirt bindings, `tera` for XML templating support, `tracing` plus `tracing-subscriber` and `tracing-actix-web` for logs, `prometheus-client` for metrics, `anyhow` and `thiserror` for error handling, `uuid` for VM IDs, and `chrono` for time support. `clap` is optional behind the `cli` feature.

## Control Flow and Integration
The package metadata sets edition 2021, minimum Rust 1.70, and points repository/license metadata back to kdevops. The `Makefile` in the same workflow calls `cargo build --release` in this directory, and the generated binary is installed by the kdevops rcloud Ansible workflow.

## State and Persistence
The manifest itself does not persist runtime state, but it controls the dependency lock and binary build graph. Persistent VM state is delegated to libvirt and disk files in the Rust code.

## Risks and Test Signals
The `virt` crate requires system libvirt headers and libraries, which the workflow Makefile checks with `pkg-config`. `config`, `thiserror`, `tera`, and `chrono` are not heavily used in the current code, which may indicate planned features or dependency drift. Test signals are `cargo test`, health endpoint integration tests, and successful release builds under the kdevops Makefile target.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Kconfig -->
# sources/test-tools/kdevops/workflows/rcloud/Kconfig

## Purpose
This Kconfig file adds an optional `RCLOUD` workflow to kdevops. It lets users enable the Rust REST API server and configure its bind address, worker count, and Terraform provider build.

## Important Symbols
`RCLOUD` is a top-level bool defaulting to `n`. When enabled, `RCLOUD_SERVER_BIND` is emitted to YAML with default `127.0.0.1:8765`, `RCLOUD_WORKERS` is emitted to YAML with default `4`, and `RCLOUD_ENABLE_TERRAFORM_PROVIDER` defaults to `y`.

## Control Flow and Integration
The `if RCLOUD` block scopes all runtime configuration to enabled deployments. The workflow `Makefile` checks `CONFIG_RCLOUD` and adds `rcloud-build` to `DEFAULT_DEPS`, then uses `CONFIG_RCLOUD_SERVER_BIND` and `CONFIG_RCLOUD_ENABLE_TERRAFORM_PROVIDER` for build/install behavior. Values marked `output yaml` become part of `extra_vars.yaml`, which `src/config/kdevops.rs` later reads.

## State, Persistence, and Dependencies
Kconfig persists deployment intent through generated kdevops configuration. The comments intentionally recommend localhost binding unless authentication is provided. The Terraform provider option assumes a separate `terraform-provider-rcloud` tree and a Go toolchain when enabled.

## Risks and Test Signals
The default Terraform provider build being enabled can make `make` fail on systems without Go even when users only need the API server. Exposing `0.0.0.0:8765` has an explicit security risk because the current API handlers do not enforce authentication. Validation signals are generated YAML values and Makefile behavior under both enabled and disabled `RCLOUD`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Makefile -->
# sources/test-tools/kdevops/workflows/rcloud/Makefile

## Purpose
This Makefile integrates rcloud into the kdevops build and operations surface. When `CONFIG_RCLOUD=y`, it builds the Rust server, optionally builds and installs the Terraform provider, prepares guestfs base images, installs the service via Ansible, starts systemd, and provides status/help targets.

## Important Targets and Variables
`RCLOUD_WORKFLOW := workflows/rcloud`. `RCLOUD_PORT` is extracted from `CONFIG_RCLOUD_SERVER_BIND`. `rcloud-check-deps` verifies `cargo`, `rustc`, `pkg-config`, and libvirt development libraries. The release binary target runs `cargo build --release`. `rcloud-check-go-deps` and `terraform-provider-rcloud/terraform-provider-rcloud` are active when `CONFIG_RCLOUD_ENABLE_TERRAFORM_PROVIDER=y`. Operational targets include `rcloud-build`, `rcloud-base-images`, `rcloud`, `rcloud-status`, provider installation targets, and help text.

## Control Flow
Enabling rcloud appends `rcloud-build` to `DEFAULT_DEPS`. The install path first builds dependencies, then runs `playbooks/guestfs.yml` for base images, then `playbooks/rcloud.yml`, optionally copies the Terraform provider into `~/.terraform.d/plugins`, starts `rcloud` with systemd, and invokes `scripts/check-health.py`.

## State, Persistence, and Dependencies
Build state lives under `workflows/rcloud/target/release`. Provider state is copied into the user's Terraform plugin directory. Runtime state is managed by systemd, libvirt, guestfs image directories, and Ansible inventory. The Makefile depends on cargo/rustc/pkg-config/libvirt, optionally Go, Ansible, sudo/systemd, and the rcloud health script.

## Risks and Test Signals
The Makefile shell-extracts the port with `sed`, which assumes a simple `host:port` bind string. The install target starts a system service and copies files into the user's home, so dry-run separation matters. Health-check success after systemd start is the strongest integration signal; build-only validation is `rcloud-build`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/scripts/check-health.py -->
# sources/test-tools/kdevops/workflows/rcloud/scripts/check-health.py

## Purpose
This Python script checks the rcloud service health endpoint and prints raw JSON, human-readable interpretation, troubleshooting steps, and suggested follow-up API calls. It is used by the Makefile after service installation and by the `rcloud-status` target.

## Important APIs and Functions
`check_health(endpoint)` constructs `<endpoint>/api/v1/health`, performs a `urllib.request.urlopen` with a five-second timeout, parses JSON, and returns `(success, data, message)`. `explain_health_status(data)` maps the `status` field to explanatory text and includes the server version. `main()` parses an optional endpoint argument, prints diagnostics, calls the checker, and returns exit status `0` or `1`.

## Control Flow
The script defaults to `http://localhost:8765`. On failure it prints service, socket, and journalctl troubleshooting hints. On success it prints the raw response, explanation, and curl examples for `/api/v1/vms`, `/api/v1/images`, `/api/v1/status`, and `/metrics`.

## State, Persistence, and Dependencies
There is no persistent local state. It uses only Python standard library modules: `json`, `sys`, `urllib.request`, and `urllib.error`. It depends on the rcloud server returning JSON with at least `status` and `version`.

## Risks and Test Signals
The script currently includes non-ASCII symbols in output, which can be awkward in constrained logs. `urllib.error.HTTPError` is a subclass of `URLError`, but the code catches `URLError` first, so HTTP-specific handling may be bypassed. The test signal is process exit status plus the parsed health JSON.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/scripts/check-health.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/health.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/health.rs

## Purpose
This module implements rcloud health and status HTTP handlers. It provides a minimal liveness check and a configuration status endpoint.

## Important Types and Functions
`HealthResponse` serializes `status` and `version`. `SystemStatusResponse` serializes operational metadata: status, version, kdevops root, libvirt URI, storage pool path, base images directory, and network bridge. `health_check()` returns `{"status":"healthy","version":CARGO_PKG_VERSION}`. `system_status(config)` reads `AppConfig` from Actix shared data and exposes selected fields.

## Control Flow
Both handlers log a request, construct response structs, and return `HttpResponse::Ok().json(...)`. They do not query libvirt, disk paths, or the VM manager, so they report service process health rather than full dependency health.

## State, Persistence, and Dependencies
State comes from compile-time package version and injected `web::Data<AppConfig>`. Dependencies are Actix Web, Serde, tracing, and the rcloud configuration module.

## Risks and Test Signals
The status endpoint exposes filesystem paths and libvirt URI, which is useful operationally but may be sensitive if the server is network-exposed. The health endpoint can return healthy even if libvirt or storage is broken. The existing integration test exercises `health_check` and validates `status == healthy`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/health.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/images.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/images.rs

## Purpose
This module exposes the image catalog endpoint for rcloud. It lists files in the configured base image directory and returns them as API model objects.

## Important APIs and Functions
`list_images(config)` receives Actix `web::Data<AppConfig>`, constructs `VmManager`, calls `manager.list_base_images()`, maps each image name into `ImageInfo`, and returns `ListImagesResponse`.

## Control Flow
The handler logs the request, performs a synchronous filesystem scan through `VmManager`, then branches on `Result`. Success returns HTTP 200 JSON. Failure logs the error and returns HTTP 500 with a JSON `error` string.

## State, Persistence, and Dependencies
The endpoint reads persistent base image files from `config.base_images_dir`; it does not mutate them. It depends on the VM manager implementation, Actix Web response types, Serde JSON, and tracing.

## Risks and Test Signals
The handler runs blocking filesystem work in an async handler, which is acceptable for small directories but can block Actix workers on slow storage. It exposes raw filenames rather than validated image metadata. Test signals should include a temporary base image directory and a missing-directory error path.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/images.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/metrics.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/metrics.rs

## Purpose
This module implements the Prometheus scrape endpoint for rcloud.

## Important APIs and Functions
`metrics_handler(metrics)` receives `web::Data<Metrics>`, calls `metrics.encode()`, and returns a text response with content type `text/plain; version=0.0.4`.

## Control Flow
The handler logs access, encodes the registry, and returns HTTP 200. It does not update metrics itself.

## State, Persistence, and Dependencies
The state is the in-memory `Metrics` registry shared through Actix app data. There is no persistent metrics storage in this module. It depends on the local `metrics.rs` wrapper and Actix Web.

## Risks and Test Signals
Because most metric recording methods are currently unused in handlers, the scrape may show registered metrics but not meaningful request or VM operation counters. Tests should verify content type and that known metric names are present after `Metrics::new()`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/mod.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/mod.rs

## Purpose
This module is the handler namespace aggregator for rcloud's API layer.

## Important APIs
It publicly declares `health`, `images`, `metrics`, and `vms` submodules. This makes the handlers available to route configuration and tests through `crate::api::handlers::*`.

## Control Flow and Integration
There is no runtime control flow. The integration point is `src/api/routes.rs`, which imports `super::handlers::{health, images, metrics, vms}` and binds functions from each module to URL paths.

## State, Persistence, and Dependencies
No state is stored here. Its dependency surface is only the module tree.

## Risks and Test Signals
The risk is namespace drift: adding a handler file without exporting it here makes it unavailable to route configuration. Compile-time tests catch missing modules. The existing health test indirectly validates this export path.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/vms.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/vms.rs

## Purpose
This module implements VM lifecycle REST handlers for create, list, get, start, stop, and destroy operations. It is the HTTP bridge between API models and `VmManager`.

## Important APIs and Functions
`create_vm(config, req)` maps `CreateVmRequest` into `VmSpec` and returns `CreateVmResponse`. `list_vms(config)` maps `VmInfo` values into `VmResponse` objects inside `ListVmsResponse`. `get_vm(config, vm_id)`, `start_vm`, `stop_vm`, and `destroy_vm` delegate by id or name through `VmManager` and return JSON status or errors.

## Control Flow
Every handler constructs a new `VmManager` from a cloned `AppConfig`. Operations are synchronous inside async handlers. Success paths return 201 for create and 200 for the other operations. `get_vm` converts manager errors to 404; other lifecycle errors become 500.

## State, Persistence, and Dependencies
State changes are delegated to libvirt and disk operations in `VmManager`. The handlers themselves only transform request and response shapes. Dependencies include Actix Web extractors, API model structs, `AppConfig`, `VmManager`, `VmSpec`, tracing, and `serde_json` for error/status objects.

## Risks and Test Signals
There is no input validation for VM name, CPU count, memory, disk size, base image name, SSH username, or SSH key content before reaching the manager. Blocking libvirt and process work in async handlers can occupy Actix workers. Error mapping is coarse and may expose internal messages. Tests should cover serialization, validation failures, not-found behavior, and manager integration with mocked or isolated libvirt.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/vms.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/mod.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/mod.rs

## Purpose
This is the public module root for rcloud's API layer.

## Important APIs
It declares `handlers`, `models`, and `routes` as public modules. That gives both the binary and library consumers access to route registration, request/response structs, and handler implementations.

## Control Flow and Integration
There is no runtime flow. `src/main.rs` imports `crate::api::routes::configure_routes`, and tests import `rcloud::api::handlers::health` through this module path.

## State, Persistence, and Dependencies
No state is stored here. It organizes compile-time module visibility.

## Risks and Test Signals
The main risk is public API stability: moving or renaming modules changes downstream import paths. Compile-time integration through `main.rs` and `tests/api_tests.rs` is the primary signal.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/models.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/models.rs

## Purpose
This module defines the JSON contract for rcloud API requests and responses.

## Important Types
`CreateVmRequest` includes `name`, `vcpus`, `memory_mb`, `base_image`, `root_disk_gb`, optional `ssh_user`, and optional `ssh_public_key`. `CreateVmResponse` returns `id`, `name`, and `state`. `VmResponse` returns VM identity, lifecycle state, sizing, and optional `ip_address`. `ListVmsResponse` wraps VM responses. `ImageInfo` and `ListImagesResponse` model available base images.

## Control Flow and Integration
These are passive Serde structs used by Actix extractors and JSON responses in `handlers/vms.rs` and `handlers/images.rs`. Optional fields are skipped when serializing if absent.

## State, Persistence, and Dependencies
The module does not persist state; it defines wire-level data shape. Dependencies are Serde derive traits. Persistent VM data is provided by libvirt through `VmManager` and adapted into these response types.

## Risks and Test Signals
There are no validation attributes, so invalid values are syntactically accepted if they deserialize. Optional SSH public key content can be large and sensitive. API compatibility depends on these field names remaining stable. Tests should cover JSON round trips and invalid payload handling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/models.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/routes.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/routes.rs

## Purpose
This module registers all HTTP routes for the rcloud service.

## Important APIs
`configure_routes(cfg)` installs an `/api/v1` scope with health, status, VM lifecycle, and image endpoints, plus a top-level `/metrics` route outside the versioned API scope.

## Control Flow
The function mutates Actix `ServiceConfig`. It binds `/api/v1/health`, `/api/v1/status`, `/api/v1/vms` for POST and GET, `/api/v1/vms/{id}` for GET and DELETE, `/api/v1/vms/{id}/start`, `/api/v1/vms/{id}/stop`, `/api/v1/images`, and `/metrics`.

## State, Persistence, and Dependencies
No state is stored here. It depends on handler module exports and Actix Web's routing DSL. Request state comes from `AppConfig` and `Metrics` app data inserted by `main.rs`.

## Risks and Test Signals
There is no authentication or authorization middleware on any route. Route order is straightforward and unlikely to conflict, but `/metrics` being unversioned and unauthenticated may expose operational data. Tests should initialize an Actix app with `configure_routes` and verify route availability and method handling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/routes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/config/kdevops.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/config/kdevops.rs

## Purpose
This module parses kdevops `extra_vars.yaml` and environment overrides into a typed `KdevopsConfig` used by rcloud.

## Important Types and Functions
`KdevopsConfig` stores libvirt URI, storage pool path, base images directory, optional network bridge, optional server bind, optional worker count, optional SSH user and public key path, plus flattened extra YAML. `load(kdevops_root)` reads `extra_vars.yaml`, parses it with Serde YAML, resolves required storage and image paths, applies selected `RCLOUD_*` environment overrides, and returns the config. `get_string` and `get_usize` extract simple YAML values.

## Control Flow
The loader prioritizes environment variables for libvirt URI, storage pool, base images, network bridge, server bind, and workers. It falls back to kdevops YAML keys such as `kdevops_storage_pool_path`, `libvirt_storage_pool_path`, `guestfs_base_image_dir`, and `libvirt_bridge_name`. Missing storage pool or base image directory is fatal.

## State, Persistence, and Dependencies
Persistent state is read from `extra_vars.yaml`; no writes occur. Dependencies include `anyhow`, `serde`, `serde_yaml`, filesystem reads, and environment variables.

## Risks and Test Signals
SSH user and key file are read only from YAML, not environment variables. `extra` stores the whole YAML after values are already inspected. String-only extraction ignores YAML scalar types that are not strings. The included unit test creates a temporary `extra_vars.yaml` and validates core path and bridge parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/config/kdevops.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/config/mod.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/config/mod.rs

## Purpose
This module defines the application-level configuration consumed by the rcloud server, VM manager, and health/status endpoints.

## Important Types and Functions
`AppConfig` contains `ServerConfig`, `kdevops_root`, libvirt URI, storage pool path, base images directory, network bridge, SSH user, SSH public key file, and `VmDefaults`. `ServerConfig` defaults to `127.0.0.1:8765` and 4 workers. `VmDefaults` defaults to `raw` format and `virtio` driver. `AppConfig::load()` determines `KDEVOPS_ROOT` or current directory, loads `KdevopsConfig`, maps values into path types, and applies defaults. `xml_template_path()` points at the guestfs Q35 XML template in kdevops.

## Control Flow
Configuration loading is synchronous at process startup in `main.rs`. Errors are propagated with context but `main.rs` currently panics via `expect` if loading fails.

## State, Persistence, and Dependencies
The module reads persistent kdevops config through `config/kdevops.rs` and environment variables. It stores configuration in memory and clones it into handlers and the VM manager.

## Risks and Test Signals
`VmDefaults` is not yet used by disk/XML generation, so the configured defaults may not affect runtime behavior. The network bridge fallback is `default` if `KdevopsConfig.network_bridge` is absent, while the lower-level kdevops config defaults to `virbr0`, so behavior depends on where absence is resolved. Tests should cover missing files, environment overrides, and default propagation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/config/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/lib.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/lib.rs

## Purpose
This is the library entry point for rcloud. It exposes the main internal modules for integration tests and potential external reuse.

## Important APIs
The file publicly exports `api`, `config`, `metrics`, and `vm`.

## Control Flow and Integration
There is no runtime logic. `tests/api_tests.rs` imports `rcloud::api::handlers::health` through this library entry point, while `src/main.rs` declares its own modules for the binary.

## State, Persistence, and Dependencies
No state is stored here. The dependency surface is the public module graph.

## Risks and Test Signals
The library exports broad internal modules, which is convenient for tests but makes future refactors more visible to downstream users. Compile-time testing is the main signal; if any public module fails to compile, both library and tests fail.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/main.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/main.rs

## Purpose
This file is the rcloud binary entry point. It configures logging, loads kdevops-derived configuration, constructs shared Actix application state, registers routes, and starts the HTTP server.

## Important APIs and Functions
`main()` uses `#[actix_web::main]`. It builds a JSON `tracing_subscriber` with INFO level, target disabled, thread IDs and file/line enabled. It calls `AppConfig::load()`, creates `web::Data<AppConfig>` and `web::Data<Metrics>`, and starts an `HttpServer` with logger, compression, tracing middleware, and `configure_routes`.

## Control Flow
Startup is linear: initialize tracing, load config, log key paths, clone bind address and worker count, build shared state, initialize metrics, then bind and run the server. Each Actix worker gets an app instance with cloned data handles.

## State, Persistence, and Dependencies
The process stores config and metrics in memory. Persistent VM state remains outside this file in libvirt and disk storage. Dependencies include Actix Web, tracing, the local API/config/metrics/vm modules, and the OS socket bind.

## Risks and Test Signals
`AppConfig::load().expect(...)` makes configuration errors fatal panics rather than formatted startup errors. The service starts successfully even if libvirt/storage are unavailable until a VM endpoint is used. Test signals include successful bind in deployment, `check-health.py`, and Actix route integration tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/metrics.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/metrics.rs

## Purpose
This module owns rcloud's Prometheus metrics registry and helper methods for request and VM operation counters.

## Important Types and Functions
`ApiLabels` is an encoded label set with `method`, `endpoint`, and `status`. `Metrics` stores an `Arc<Mutex<Registry>>`, a `Family<ApiLabels, Counter>` for HTTP requests, a `Gauge` for VM count, and a `Family<ApiLabels, Counter>` for VM operations. `new()` registers `rcloud_http_requests_total`, `rcloud_vm_count`, and `rcloud_vm_operations_total`. `record_request`, `set_vm_count`, `record_vm_operation`, and `encode` update or serialize metrics.

## Control Flow
Metrics are initialized once in `main.rs` and shared through Actix app data. `/metrics` calls `encode()`, which locks the registry and encodes Prometheus text into a buffer.

## State, Persistence, and Dependencies
Metrics are in-memory only and reset when the service restarts. The module depends on `prometheus-client`, `Arc`, and `Mutex`.

## Risks and Test Signals
The recording helpers are marked dead code and are not wired into request handlers, so counters may stay at zero. Lock failure in `encode()` silently returns an empty buffer. Tests should verify registration output and add integration coverage once handlers record metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/disk.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/vm/disk.rs

## Purpose
This module provides disk helpers for rcloud VM creation and deletion.

## Important APIs and Functions
`create_cow_disk(base_image, target_disk, size_gb)` creates parent directories and invokes `qemu-img create -f qcow2 -b <base> -F raw <target> <size>G`. `delete_disk(disk_path)` removes a disk file if it exists. `get_vm_disk_dir(storage_pool, vm_name)` returns `<storage_pool>/<vm_name>`. `get_root_disk_path(storage_pool, vm_name)` returns `<storage_pool>/<vm_name>/root.qcow2`.

## Control Flow
Disk creation logs intent, creates the directory, runs `qemu-img`, checks the exit status, and bails with stderr on failure. Deletion is idempotent for missing files.

## State, Persistence, and Dependencies
Persistent state is VM disk directories and qcow2 root disks under the configured storage pool. The module depends on filesystem access, `qemu-img`, and assumptions that base images are raw format.

## Risks and Test Signals
The backing format is hard-coded as raw even though filenames may vary. VM names directly shape filesystem paths, so name validation is needed upstream to avoid path traversal or collisions. Tests should cover path helpers, failed `qemu-img`, existing directories, and cleanup after partial creation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/disk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/manager.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/vm/manager.rs

## Purpose
`VmManager` is the core rcloud lifecycle implementation. It connects HTTP requests to libvirt domains, qcow2 disks, guest customization, XML generation, and image discovery.

## Important Types and Functions
`VmSpec` describes create inputs: name, vcpus, memory, base image, root disk size, optional SSH user, and optional public key content. `VmManager::new(config)` stores `AppConfig`. `connect()` opens libvirt. Lifecycle methods are `create_vm`, `list_vms`, `get_vm`, `start_vm`, `stop_vm`, and `destroy_vm`. Supporting methods include `customize_vm_disk`, `get_vm_info_from_domain`, `get_domain_ip_address`, `parse_domifaddr_output`, and `list_base_images`. `VmInfo` is the internal response shape.

## Control Flow
`create_vm` generates a UUID, validates base image existence, computes disk paths, creates a COW disk, customizes it with `virt-customize` if SSH data is available, infers UEFI needs from the image name, generates simple libvirt XML, defines the domain, starts it, and returns the libvirt UUID. It cleans up disks, directories, and domains on customization, define, or start failures. Other lifecycle methods look up domains by UUID or name and call libvirt operations.

## State, Persistence, and Dependencies
VM state is persisted in libvirt domain definitions, running QEMU instances, NVRAM for UEFI guests, and qcow2 disk files under the storage pool. The manager depends on libvirt Rust bindings, `qemu-img`, `virt-customize`, `sudo virsh domifaddr`, filesystem paths, UUID generation, and XML generation.

## Risks and Test Signals
Blocking process and libvirt calls run synchronously under async HTTP handlers. User-controlled names and SSH usernames are interpolated into filesystem paths and shell commands passed to `virt-customize --run-command`, so validation is important. IP lookup requires sudo virsh permissions and guest/network support. `domain.shutdown()` is graceful and may not stop immediately. Strong tests need isolated path helper tests, XML tests, mocked command execution, and real integration tests behind a libvirt-capable environment.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/mod.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/vm/mod.rs

## Purpose
This module is the VM subsystem root for rcloud.

## Important APIs
It declares `disk`, `manager`, and `xml` submodules and re-exports `VmManager` and `VmSpec` from `manager`.

## Control Flow and Integration
There is no runtime control flow. API handlers import `crate::vm::{VmManager, VmSpec}` through this re-export, while the manager imports sibling `disk` and `xml` modules.

## State, Persistence, and Dependencies
No state is stored here. It defines module boundaries for disk persistence, libvirt lifecycle, and XML rendering.

## Risks and Test Signals
The re-export makes handler code independent of the manager file path but exposes the manager API as the VM module's public contract. Compile-time tests catch missing modules and changed exported names.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/xml.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/vm/xml.rs

## Purpose
This module renders libvirt domain XML for rcloud VMs. It supports both a Tera-template path and a currently used simple string generator.

## Important Types and Functions
`VmXmlContext` holds fields expected by guestfs/kdevops XML templates, including hostname, memory, vcpu count, storage paths, network device, QEMU binary path, UEFI flag, host passthrough, and GDB toggle. `VmXmlContext::new` builds default context values. `render_vm_xml(template_path, context)` loads a template, registers it with Tera, inserts all context fields, and renders XML. `generate_simple_vm_xml` directly formats a libvirt `<domain type='kvm'>` using q35 machine, qcow2 virtio disk, network interface, serial console, balloon, rng, and optional EFI/SMM settings.

## Control Flow
`VmManager::create_vm` calls `generate_simple_vm_xml`, not the Tera renderer. UEFI mode changes the `<os>` section and adds `<smm state='on'/>`.

## State, Persistence, and Dependencies
The XML string becomes persistent only after libvirt `define_xml` stores the domain. The template renderer reads template files from disk. Dependencies include Tera, Serde, tracing, and path formatting.

## Risks and Test Signals
Direct string interpolation can produce invalid XML if VM names, paths, or network names contain special characters. The `network_name` argument is used as a libvirt network source, while surrounding config names it a bridge, which can cause deployment mismatch. Tests should parse generated XML for BIOS and UEFI cases and validate escaping or input restrictions.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/xml.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/tests/api_tests.rs -->
# sources/test-tools/kdevops/workflows/rcloud/tests/api_tests.rs

## Purpose
This integration test validates the rcloud health endpoint through Actix's test harness.

## Important APIs and Functions
`test_health_check` initializes an `App` with `/api/v1/health` routed to `health::health_check`, sends a GET request, asserts the response status is successful, parses the body as JSON, and asserts `body["status"] == "healthy"`.

## Control Flow
The test is asynchronous under `#[actix_rt::test]`. It does not start a TCP listener; it exercises the service in memory.

## State, Persistence, and Dependencies
No persistent state is used. Dependencies include Actix Web test utilities, `web`, `App`, and the public library export `rcloud::api::handlers::health`.

## Risks and Test Signals
Coverage is intentionally narrow. It does not validate route registration through `configure_routes`, system status, metrics, images, or VM lifecycle endpoints. It is still a useful smoke test that the library module graph and health JSON contract compile and behave.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/tests/api_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/selftests/Kconfig -->
# sources/test-tools/kdevops/workflows/selftests/Kconfig

## Purpose
This Kconfig file configures Linux kernel selftests coverage for kdevops. It controls whether specific selftest subsystems are selected manually or as a vetted default set.

## Important Symbols
`SELFTESTS_KMOD_TIMEOUT_SET_BY_CLI` detects `KMOD_TIMEOUT` from the command line. Build helper flags include `SELFTESTS_BUILD_RADIX_TREE` and `SELFTESTS_BUILD_SELFTESTS_DIR`. `SELFTESTS_MANUAL_COVERAGE` defaults to `y` and exposes manual selections. Manual options include `SELFTESTS_TEST_BUNDLE_RADIX_TREE`, `SELFTESTS_SECTION_FIRMWARE`, `KMOD`, `MODULE`, `MAPLE`, `SYSCTL`, `XARRAY`, and `VMA`. When manual coverage is disabled, several sections default to enabled. `SELFTESTS_SECTION_KMOD_TIMEOUT` configures the kmod timeout and can be set from CLI.

## Control Flow and Integration
Selections use `select` to enable required build paths. The Makefile includes per-section test Makefiles and shows specific help only when manual coverage is enabled. Values marked `output yaml` feed Ansible variables for `playbooks/selftests.yml`.

## State, Persistence, and Dependencies
The generated configuration persists selected coverage and timeout values. It depends on kdevops Kconfig helpers such as `scripts/check-cli-set-var.sh` and `scripts/append-makefile-vars-int.sh`.

## Risks and Test Signals
Some help strings contain typos, but the symbol graph is clear. Defaults differ significantly between manual and automatic modes, so result comparisons should include the config. The kmod timeout is runner-specific and may need tuning. Test signals are generated YAML and successful selftests targets.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/selftests/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/selftests/Makefile -->
# sources/test-tools/kdevops/workflows/selftests/Makefile

## Purpose
This Makefile wires the selftests workflow into kdevops targets, dynamic runtime variables, per-section helpers, and help output.

## Important Targets and Variables
`SELFTESTS_DYNAMIC_RUNTIME_VARS` starts with `"kdevops_run_selftests": True` and conditionally appends `selftests_skip_run` and `selftests_skip_reboot` based on `SKIP_RUN` and `SKIP_REBOOT`. It includes section Makefiles for firmware, module, kmod, maple, sysctl, and xarray. Targets are `selftests`, `selftests-baseline`, `selftests-results`, `selftests-check-results`, `selftests-help-main`, `selftests-help-menu`, and `selftests-help-menu-targets`.

## Control Flow
`selftests` runs `playbooks/selftests.yml` while skipping run/copy/check tags, so it prepares/builds. `selftests-baseline` limits to `baseline`, passes runtime vars, and runs vars, test execution, result copy, and result check tags. Result-only and check-only targets narrow tag sets.

## State, Persistence, and Dependencies
State flows through Ansible, inventory groups, generated YAML, copied test results, and per-section Makefile variables. It depends on `LIMIT_HOSTS`, `TOPDIR`, and included test Makefiles.

## Risks and Test Signals
Only some section Makefiles are included directly; a VMA section exists in Kconfig but is not visibly included here unless pulled indirectly elsewhere. Runtime variable construction is string-based JSON/YAML, so quoting errors can break Ansible. Test signals are successful Ansible runs and check_results output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/selftests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/steady_state/Kconfig -->
# sources/test-tools/kdevops/workflows/steady_state/Kconfig

## Purpose
This Kconfig file defines tunables for SSD steady-state preconditioning and fio steady-state verification. It captures target device selection, prefill workload shape, runtime, and steady-state pass criteria.

## Important Symbols
`SSD_STEADY_STATE_DEVICE` selects a default block device based on provider and storage type. Prefill controls include blocksize, iodepth, numjobs, loop count, verbose mode, maximum size, physical block size override, ioengine, direct I/O, allocation size, and extra fio arguments. Verification controls include runtime and IOPS/BW mean and slope limits plus required durations.

## Control Flow and Integration
All symbols are emitted to YAML for Ansible consumption. The Makefile targets call `playbooks/steady_state.yml` with tags for setup, prefill, and steady-state phases. Runtime logic in Ansible or helper scripts computes an effective blocksize when the config value is empty.

## State, Persistence, and Dependencies
Persistent configuration lands in generated kdevops vars. Runtime state is destructive or performance-sensitive because the selected device is prefilled. Dependencies include provider-specific device naming, fio, and the steady-state playbook.

## Risks and Test Signals
The workflow can overwrite the configured device, so defaults and user overrides require care. Device names vary by cloud and libvirt bus. Very long defaults such as `6h` runtime and multi-hour steady-state durations make test cycles expensive. Strong signals are generated fio commands, prefill logs, and steady-state criteria results.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/steady_state/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/steady_state/Makefile -->
# sources/test-tools/kdevops/workflows/steady_state/Makefile

## Purpose
This Makefile exposes kdevops targets for the SSD steady-state workflow.

## Important Targets and Variables
It adds phony targets `steady-state`, `steady-state-files`, `steady-state-prefill`, `steady-state-run`, and `steady-state-help-menu`. `SSD_STEADY_STATE_DYNAMIC_RUNTIME_VARS` sets `"kdevops_run_ssd_steady_state": True`.

## Control Flow
`steady-state-files` runs `playbooks/steady_state.yml` with tags `vars,setup`. `steady-state-prefill` runs `vars,prefill`. `steady-state-run` runs `vars,steady_state`. `steady-state` passes the runtime variable and runs the broader playbook. Help text is appended to `HELP_TARGETS`.

## State, Persistence, and Dependencies
State flows through Ansible vars, generated template files, prefilled storage devices, fio results, and any copied logs. Dependencies are `extra_vars.yaml`, `LIMIT_HOSTS`, and the steady-state playbook.

## Risks and Test Signals
Because prefill can be destructive, separating files, prefill, and run targets is operationally important. The all-in target hides phase boundaries and should be used only when the configured device is confirmed. Test signals are playbook completion and the produced fio steady-state output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/steady_state/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/sysbench/Kconfig -->
# sources/test-tools/kdevops/workflows/sysbench/Kconfig

## Purpose
This Kconfig file configures sysbench database workload testing in kdevops. It selects Docker/MySQL or native/PostgreSQL modes, imports filesystem and mode-specific config, and defines common workload parameters.

## Important Symbols
Hidden type flags `SYSBENCH_DB_TYPE_MYSQL` and `SYSBENCH_DB_TYPE_POSTGRESQL` feed `SYSBENCH_DB_TYPE`. The main choice defaults to `SYSBENCH_DOCKER`, selecting `SYSBENCH_TYPE_MYSQL_DOCKER`; `SYSBENCH_NATIVE` selects `SYSBENCH_TYPE_POSTGRESQL_NATIVE`. It sources `Kconfig.fs`, `Kconfig.docker`, and `Kconfig.native` conditionally. Common values include database name/user/passwords, report interval, OLTP table size/count, thread selection, test duration, and telemetry path. MySQL-specific tunables include table engine, redo log capacity, and buffer pool size.

## Control Flow and Integration
Selected Kconfig values are emitted to YAML and consumed by `playbooks/sysbench.yml`. Conditional source files expand the configuration surface depending on Docker/native mode and filesystem choices.

## State, Persistence, and Dependencies
Persistent configuration is generated into kdevops vars. Runtime state includes database data, telemetry under `/data/sysbench-telemetry` by default, logs, and plotted results. Dependencies include sysbench, Docker/MySQL or native PostgreSQL, filesystem setup, and monitoring roles.

## Risks and Test Signals
Defaults are example-oriented and may under-size or over-size database buffers for real hardware. Passwords default to `kdevops`, so exposure matters. `SYSBENCH_THREADS` uses duplicate symbol names in mutually exclusive blocks, which is legal but must remain scoped correctly. Test signals are populated tables, sysbench run results, telemetry, and plots.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/sysbench/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/sysbench/Makefile -->
# sources/test-tools/kdevops/workflows/sysbench/Makefile

## Purpose
This Makefile defines sysbench setup, execution, telemetry, result collection, cleanup, plotting, monitoring, and help targets for kdevops.

## Important Targets and Variables
`TAGS_SYSBENCH_RUN` aggregates db start, connection test, post entrypoint, population, run, telemetry, logs, results, and plot tags. `TAGS_SYSBENCH_TEST`, `TAGS_SYSBENCH_TELEMETRY`, and `TAGS_SYSBENCH_RESULTS` prepend `vars` as needed. Targets include `sysbench`, `sysbench-test`, `sysbench-telemetry`, `sysbench-results`, `monitor-results`, `sysbench-clean`, `sysbench-plot`, and `sysbench-help-menu`.

## Control Flow
`sysbench` runs `playbooks/sysbench.yml` while skipping the run tag set, so it performs setup. `sysbench-test` runs the full tagged workload. Telemetry and results targets run narrower tag groups. Cleanup runs `vars,clean`; plotting runs `vars,plot`. `monitor-results` invokes `playbooks/monitor-results.yml` with `extra_vars.yaml` and, in the second definition, `LIMIT_HOSTS`.

## State, Persistence, and Dependencies
State is managed by Ansible: database containers or native services, populated tables, telemetry, logs, results, and plots. The Makefile depends on kdevops variables such as `space`, `comma`, `Q`, and `LIMIT_HOSTS`.

## Risks and Test Signals
`monitor-results` is defined twice, which can lead to make override warnings or the latter recipe replacing the former. Tag composition is central; missing tags silently skip phases. Test signals include playbook tag execution, result files, telemetry collection, and generated plots.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/sysbench/Makefile -->
