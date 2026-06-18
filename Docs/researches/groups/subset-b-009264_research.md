# subset-b-009264 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_location -->
# sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_location

Purpose: Python generator for GCE location Kconfig. It queries Compute Engine regions and zones through helpers in `gce_common.py`, joins that live API data with `region_friendly_names.yml`, and renders `regions.j2` and `zone.j2` menus.

Important functions include `load_region_friendly_names()`, `get_region_friendly_name()`, `get_all_regions()`, `get_all_zones_by_region()`, `get_region_zones()`, `get_region_info()`, and output helpers for raw tables or Kconfig. The CLI supports full generation, `--regions`, a single region argument, `--format`, and `--quiet`.

Control flow starts by parsing arguments, requiring optional GCE credentials, then either parallel-fetches regions/zones for full Kconfig generation or fetches only region data for narrower commands. Missing GCE config exits 0 so `make dynconfig` can continue when GCE is not configured.

State is external: credentials, project, live GCE API responses, YAML friendly names, and generated stdout. Risks include stale friendly-name YAML, API schema/status drift, default region selection that may not exist, and duplicated zone queries for single-region inspection. Test signals should mock `gce_common` API helpers and validate empty-result exits, fallback friendly names, and rendered Kconfig symbols.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_location -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_machine -->
# sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_machine

Purpose: Python generator for GCE machine-type Kconfig. It discovers GCE machine types by zone or aggregated all-zone API, groups them into machine series, annotates those series with curated metadata, and renders series and per-type menus.

Important data and APIs include `SERIES_METADATA`, boot-disk constants for Persistent Disk versus Hyperdisk, `extract_machine_series()`, `extract_machine_family()`, `parse_all_machine_series()`, `get_machine_series_info()`, `natural_sort_key()`, `get_all_machine_types()`, and Kconfig/raw output helpers. It relies on `gce_common` for credentials, default zone, Jinja environment, machine type symbol naming, and REST calls.

Control flow validates optional GCE credentials, chooses the default zone unless `--all-zones` is set, loads machine types, and then emits all machine choices, only series choices, or a single series. Custom machine types are intentionally filtered out.

State is mostly derived from live GCE API results plus the static metadata table. Risks include metadata lag for new series, heuristic parsing of names like GPU/local-SSD/bare-metal variants, and boot-disk type assumptions for C4/C4A/N4. Tests should cover parser edge cases, natural ordering, duplicate suppression, metadata fallback, and render variables passed to `series.j2` and `machine_type.j2`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_machine -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/publisher_definitions.yml -->
# sources/test-tools/kdevops/terraform/gce/scripts/publisher_definitions.yml

Purpose: YAML catalog of Linux image publishers for GCE image Kconfig generation. Each top-level key names a distribution family such as `debian`, `ubuntu`, `redhat`, or `rocky`.

The schema provides `project_id`, `publisher_name`, `description`, `priority`, `default_disk_size`, and `family_patterns`. Generator scripts can use this to enumerate public image projects, match image families by regex, order menus, and choose sensible boot disk defaults.

There is no executable control flow or persistence in this file; it is read as configuration by provider scripts. Its integration points are GCE public image projects and generated Kconfig image menus. The comments document update workflow through `gcloud compute images list` and regeneration of `Kconfig.image`.

Risks are data freshness and regex breadth. Broad patterns such as `ubuntu-.*` or `centos-.*` are convenient but can match deprecated or unexpected families unless the consuming script filters further. Test signals should validate YAML parsing, required keys for every publisher, unique priorities or deterministic ordering, and that family regexes match representative live or fixture image-family names.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/publisher_definitions.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/region_friendly_names.yml -->
# sources/test-tools/kdevops/terraform/gce/scripts/region_friendly_names.yml

Purpose: YAML mapping from GCE region identifiers to human-readable labels used in generated Kconfig menus. It covers Africa, Asia Pacific, Australia, Europe, Middle East, North America, and South America entries.

The file has a simple `region: "Friendly Name"` schema. `gen_kconfig_location` reads it through `load_yaml_config()` and falls back to title-cased region identifiers when a live region is absent from this mapping.

There is no runtime control flow beyond YAML loading. Persistence is static repository content with a `Last Verified` comment and instructions for update via `gcloud compute regions list`, Google documentation, and regenerating `Kconfig.location`.

Integration is directly user-facing: labels appear in kdevops GCE region selection menus while the real GCE region IDs remain the deployable values. Risks include new regions missing from the map, renamed locations, or documentation drift. Test signals should parse the YAML, compare keys against a mocked or captured `list_regions()` result, and ensure missing keys produce readable fallback names rather than generator failures.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/region_friendly_names.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/globals.mk -->
# sources/test-tools/kdevops/terraform/globals.mk

Purpose: shared Make variable definitions for Terraform support. It currently defines host OS prefix and the download coordinates for the external YAML Terraform provider plugin.

Important variables are `UNAME_PREFIX`, `YAML_PLUGIN_URL_DOWNLOAD`, `YAML_PLUGIN_NAME`, `YAML_PLUGIN_VERSION`, `YAML_PLUGIN_ARCH`, `YAML_PLUGIN_FILE`, and `YAML_PLUGIN_URL`. `UNAME_PREFIX` shells out to `uname -s` and lowercases the result, then the URL is assembled for `ashald/terraform-provider-yaml` release artifacts.

There is no branching control flow. State is Make-expanded environment plus the host OS name. Integration points are Terraform provider installation targets elsewhere in the kdevops make graph.

Risks include hardcoded `amd64`, pinned provider version `v2.0.2`, and assumptions that the release artifact naming convention matches `$(name)_$(version)-$(os)-$(arch)`. On non-amd64 systems this variable set likely points at the wrong binary. Test signals should inspect Make expansion on Linux and Darwin, verify URL construction, and ensure downstream installation rules fail clearly when the artifact is missing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/globals.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/lambdalabs/Kconfig -->
# sources/test-tools/kdevops/terraform/lambdalabs/Kconfig

Purpose: top-level Lambda Labs Terraform Kconfig entrypoint, gated by `TERRAFORM_LAMBDALABS`. It wires provider-supported menus into kdevops configuration and documents provider limitations.

It sources `terraform/lambdalabs/kconfigs/Kconfig.location`, `Kconfig.compute`, and `Kconfig.identity` under Resource Location, Compute, and Identity & Access menus. Storage and OS menus are intentionally absent because the `elct9620/lambdalabs` Terraform provider lacks OS selection, volume management, custom user creation, and cloud-init/user-data support.

Control flow is Kconfig conditional inclusion only. State persists through selected symbols emitted to yaml by included files. Integration points are the Lambda Labs Terraform provider and kdevops-generated extra vars.

Risks include provider feature drift: if the provider gains storage or image selection, this Kconfig will hide available capabilities until updated. The comment also has a minor typo in the provider name line but not functional impact. Test signals should include Kconfig parsing, confirming menus appear only when `TERRAFORM_LAMBDALABS=y`, and verifying unsupported storage/OS symbols are not referenced by Lambda Labs Terraform templates.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/lambdalabs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/lambdalabs/SET_API_KEY.sh -->
# sources/test-tools/kdevops/terraform/lambdalabs/SET_API_KEY.sh

Purpose: operator-facing shell helper that prints instructions for configuring Lambda Labs API credentials. It does not mutate files; it only emits setup guidance.

There are no functions or complex APIs. The script prints a prominent warning, points users to `https://cloud.lambdalabs.com`, and instructs them to create `~/.lambdalabs/credentials` with mode `600`, then run `make bringup`.

Control flow is linear `echo` output. There is no persistence performed by the script, but the documented state is a credentials file in the user home directory. Integration points are any Terraform external data source or provider configuration that later reads `~/.lambdalabs/credentials`.

Risks include format mismatch with `extract_api_key.py`: this helper suggests writing only the raw API key, while the Python extractor expects INI-style sections containing `lambdalabs_api_key`. That inconsistency can cause setup failures. Test signals should execute the script and compare its instructions against the actual parser contract, then add an integration fixture for accepted credential formats.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/lambdalabs/SET_API_KEY.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/lambdalabs/extract_api_key.py -->
# sources/test-tools/kdevops/terraform/lambdalabs/extract_api_key.py

Purpose: Terraform external-data helper that extracts a Lambda Labs API key from a credentials file and prints JSON as `{"api_key": "..."}`.

The main API is `extract_api_key(creds_file="~/.lambdalabs/credentials")`. It expands the path, requires the file to exist, parses it with `configparser.ConfigParser`, and looks for `lambdalabs_api_key` in either a `default` section or the parser `DEFAULT` section. On errors or missing keys it writes to stderr and exits with status 1.

Control flow is simple: choose CLI path or default path, call extractor, print JSON. State read is user-local credentials; output is stdout JSON for Terraform. Dependencies are `configparser`, `json`, `sys`, and `pathlib`.

Risks include the credential format mismatch with `SET_API_KEY.sh`, broad exception handling that may hide parse details, and no permission check despite the shell guidance recommending `600`. Test signals should include missing file, malformed INI, `default` section, `DEFAULT` values, custom path argument, JSON output shape, and absence of secret leakage to stderr.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/lambdalabs/extract_api_key.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/Kconfig -->
# sources/test-tools/kdevops/terraform/oci/Kconfig

Purpose: top-level OCI Terraform Kconfig entrypoint, gated by `TERRAFORM_OCI`. It composes generated and static OCI provider menus used by kdevops.

The file sources generated location, shape, and image menus from `terraform/oci/kconfigs/Kconfig.location.generated`, `Kconfig.shape.generated`, and `Kconfig.image.generated`. It also sources static storage, network, and identity menus. Comments direct users to `make cloud-config-oci` to populate current OCI resource information.

Control flow is Kconfig conditional inclusion and menu grouping. Persistent state is the generated Kconfig files and selected symbols emitted to yaml. Integration points are the OCI generator scripts in `terraform/oci/scripts`, Terraform OCI provider modules, and the broader kdevops configuration flow.

Risks include missing generated files before `make cloud-config-oci`, stale generated choices after OCI resources change, and inconsistent file naming if scripts emit `Kconfig.images` or `Kconfig.shapes` while this file expects singular generated names. Test signals should run Kconfig parsing with generated fixtures and verify provider-specific generated files are created before menu evaluation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/catalog_shapes.yml -->
# sources/test-tools/kdevops/terraform/oci/scripts/catalog_shapes.yml

Purpose: YAML catalog of well-known OCI compute shapes that may not appear in `list_shapes()` for the current tenancy. It supports the `--include-catalog` mode in `gen_kconfig_shape`.

The schema maps shape names to `architectures`, optional `is_flex`, optional `is_bare_metal`, optional `has_gpu`, and `description`. Current entries cover DenseIO and GPU shapes including VM and bare-metal variants.

There is no executable control flow. The shape generator reads this file, fabricates minimal shape-like objects for missing catalog entries, and marks them as catalog shapes in raw output or Kconfig help. Persistence is static YAML plus comments tracking update date and total count.

Integration is intentionally advisory: catalog entries may require limits or regional availability not present in the user's tenancy. Risks include overpromising deployability, stale shape counts, and incomplete synthetic object properties such as memory/OCPU ranges. Test signals should validate schema, compare count comments to actual entries, ensure catalog merges do not override API-discovered shapes, and verify catalog-only shapes are marked distinctly.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/catalog_shapes.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_image -->
# sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_image

Purpose: Python generator for OCI platform image Kconfig. It discovers Linux platform images across one or more OCI regions, classifies them by publisher/version/architecture, and renders Kconfig menus with region-specific OCID mappings.

Important functions include `discover_publishers_from_images()`, `get_known_publishers()`, `get_all_images()`, `is_recognized_image()`, `get_image_architecture()`, `classify_image()`, `organize_images_by_publisher()`, `get_release_notes_url()`, and `output_images_kconfig()`. It depends on `oci_common` for config, compartment, subscribed regions, Compute clients, region keys, YAML loading, and Jinja setup.

Control flow supports `--publishers`, a single publisher key, raw or Kconfig output, and `--region`. Normal generation requires OCI config, derives compartment from tenancy, loads region-key mappings, queries subscribed regions, merges static publisher definitions with dynamic Linux publisher discovery, keeps the newest release per version key, and renders distribution/publisher templates.

State is live OCI image data, user OCI config, static publisher YAML, and generated stdout. Risks include regex-based classification, architecture inference from names, release-date comparison by display-name string, no pagination handling, and HTML in generated reports if names were unsafe. Test signals should mock OCI images, publisher YAML, region key fallbacks, duplicate version replacement, and no-credentials exit behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_image -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_location -->
# sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_location

Purpose: Python generator for OCI location Kconfig. It lists OCI regions, subscription status, home region, and availability domains, then renders region and AD selection menus.

Key functions include `load_region_friendly_names()`, `get_region_code()`, `get_region_friendly_name()`, `get_all_regions()`, `get_region_info()`, output helpers for region/raw/full Kconfig, and `parse_arguments()`. It uses OCI Identity clients and helpers from `oci_common` for default region, Jinja, config loading, and credential checks.

Control flow allows `--regions`, a specific region, `--include-unsubscribed`, raw output, or full Kconfig. Full output filters to subscribed regions by default because AD queries and deployments are not valid for unsubscribed regions. It appends a `TERRAFORM_OCI_COMPARTMENT_NAME` string config after region/AD menus.

State comes from `~/.oci/config`, tenancy region subscriptions, region list API, AD API, and static friendly-name YAML. Missing OCI config exits 0 for optional dynconfig. Risks include default region absent from filtered region list, fallback AD for unsubscribed regions being deployability-confusing, no pagination assumptions, and API errors returning partial data. Tests should mock Identity clients for subscribed/unsubscribed/home regions and AD sorting.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_location -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_shape -->
# sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_shape

Purpose: Python generator for OCI compute shape Kconfig. It queries shapes across subscribed or selected regions, optionally merges catalog-only shapes, groups shapes by flex/fixed/bare-metal categories, and renders Kconfig menus or raw tables.

Important functions include `get_all_shapes()`, `get_catalog_shapes()`, `merge_catalog_shapes()`, `parse_all_shape_families()`, `get_gpu_info()`, `extract_cpu_architecture()`, `extract_memory_info()`, `extract_ocpu_info()`, `extract_network_info()`, `extract_storage_info()`, `extract_shape_info()`, `get_shape_family_info()`, and rendering helpers. It depends on OCI Compute clients, compartment discovery, subscribed-region discovery, YAML loading, and Jinja templates from `oci_common`.

Control flow requires optional OCI config, determines region scope, lists shapes, merges catalog entries when requested, and then emits families, a single family, or full grouped shape menus. Catalog entries are represented by `SimpleNamespace` with minimal properties and `is_catalog_shape=True`.

State is live shape data, static catalog YAML, and stdout. Risks include duplicate shape-extraction logic diverging between `extract_shape_info()` and `get_shape_family_info()`, heuristic family parsing, minimal catalog properties producing "Flexible" placeholders, and no explicit region availability map after aggregation. Tests should cover flex option extraction, architecture heuristics, catalog merge dedupe, family parsing, and rendering of catalog markers.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_shape -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/oci_common.py -->
# sources/test-tools/kdevops/terraform/oci/scripts/oci_common.py

Purpose: shared utility module for OCI Kconfig generator scripts. It centralizes OCI config access, client creation, YAML loading, Jinja environment setup, subscribed-region discovery, and region-key conversion.

Important APIs are `OciNotConfiguredError`, `get_default_region()`, `get_default_compartment()`, `get_subscribed_regions()`, `get_jinja2_environment()`, `load_yaml_config()`, `get_oci_config()`, `require_oci_config()`, `create_identity_client()`, `create_compute_client()`, `get_all_region_keys()`, and `get_region_kconfig_name()`.

Control flow is defensive: imports of the OCI SDK are lazy, missing config is converted to `OciNotConfiguredError` for optional generators, YAML failures return defaults, and region-key API failures fall back to generated three-letter names. Persistent state read includes `~/.oci/config` and script-local YAML files.

Integration points are all OCI generator scripts and their Jinja templates. Risks include type annotations that reference `oci.*` names while `oci` is only imported inside functions, which can fail without postponed annotation evaluation; region-key fallback can collide for similarly named regions; and broad YAML defaults can hide broken config. Tests should import the module in an environment without OCI installed, mock config parsing, verify YAML default behavior, and validate region key fallback/collision handling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/oci_common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/publisher_definitions.yml -->
# sources/test-tools/kdevops/terraform/oci/scripts/publisher_definitions.yml

Purpose: YAML catalog of known OCI Linux image publishers and display-name regexes for `gen_kconfig_image`.

The schema maps publisher keys such as `oracle`, `ubuntu`, `centos`, and `fedora` to `publisher_name`, `description`, `display_name_patterns`, and `priority`. Patterns are Python regexes evaluated case-insensitively by the generator.

There is no executable control flow or dynamic state in this file. It is static input for image classification, menu ordering, and help text. The comments document update steps using `oci compute image list`, pattern selection, verification with `--publishers`, and regeneration of `Kconfig.images`.

Risks include stale patterns when OCI changes image naming, overlapping patterns where priority and dictionary order determine classification, and excluding distributions whose names lack `Linux`-style conventions until dynamic discovery catches them. Test signals should parse the YAML, enforce required keys, compile each regex, match representative image names, and verify static and dynamically discovered publishers merge without overwriting intended definitions.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/publisher_definitions.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/region_friendly_names.yml -->
# sources/test-tools/kdevops/terraform/oci/scripts/region_friendly_names.yml

Purpose: YAML map from OCI region identifiers to friendly labels used in generated Kconfig menus. It contains 41 entries ordered to match Oracle documentation.

The schema is `region-identifier: "Friendly Display Name"`. `gen_kconfig_location` loads it through `load_yaml_config()` and generates fallback labels from region names when keys are missing.

There is no executable control flow. Persistence is static source content with a verification date, total-region count, ordering requirement, and update instructions. Integration is with OCI region menu generation and user-visible Kconfig labels; actual deployable values remain OCI region IDs and region keys.

Risks include stale verification metadata, new OCI regions missing from the map, order drift versus documentation, and documentation being HTML rather than a stable API. The file correctly points maintainers toward CLI/API sources for programmatic access. Test signals should parse YAML, compare comment count to actual entries, compare keys to mocked `list_regions()` output, and ensure missing friendly names fall back gracefully.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/oci/scripts/region_friendly_names.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/rcloud/Kconfig -->
# sources/test-tools/kdevops/terraform/rcloud/Kconfig

Purpose: rcloud Terraform provider Kconfig fragment, gated by `TERRAFORM_RCLOUD`. It exposes the minimal configuration needed to talk to an rcloud REST API and select a base image.

The two symbols are `TERRAFORM_RCLOUD_API_URL`, defaulting to `http://localhost:8765`, and `TERRAFORM_RCLOUD_BASE_IMAGE`, defaulting to `debian-13-generic-amd64-daily`. Help text explains local versus remote API URLs and the expected base image directory on the rcloud server.

Control flow is just Kconfig conditional inclusion. State persists as selected string values that downstream Terraform or Ansible code consumes. Integration points are the rcloud REST server, guestfs-created base images, and kdevops defconfig-rcloud setup.

Risks include no validation of URL syntax, no authentication/TLS settings, and a hardcoded default base image that may not exist on a given server. Test signals should parse the Kconfig fragment, verify yaml/export behavior where expected by downstream code, and run a configuration fixture with non-default API URL and image name.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/rcloud/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/scripts/cloud-init.sh -->
# sources/test-tools/kdevops/terraform/scripts/cloud-init.sh

Purpose: Terraform-rendered cloud-init shell script for kdevops hosts. It currently gates user-data execution and optionally reconfigures SSH to a non-default port.

Important variables are Terraform-substituted `user_data_log_dir`, `user_data_enabled`, `new_hostname`, and `ssh_config_port`. The helper `run_cmd_admin()` executes commands, logs success or failure with timestamps to `admin.txt`, and propagates failures under `set -e`.

Control flow creates the log directory, exits early unless user data is enabled, then checks whether the SSH port differs from 22. For alternate ports it edits `sshd_config`, adjusts SELinux port context when possible, opens firewalld or ufw rules when active, and restarts `sshd`.

State mutations are significant: filesystem logs, SSH daemon config, SELinux policy ports, firewall rules, and service restart. Integration points are Terraform template interpolation, distro package managers, systemd, SELinux tools, and cloud-init execution. Risks include unquoted variables, command logging through `$@`, package-manager assumptions, `sshd` service naming variance, and unused `NEW_HOSTNAME`. Tests should run shellcheck/template checks and containerized dry runs for RHEL-like and Ubuntu-like hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/scripts/cloud-init.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/tests/__init__.py -->
# sources/test-tools/kdevops/tests/__init__.py

Purpose: empty Python package marker for the kdevops test tree. It allows test modules under `tests` to be imported as part of a package when discovery or tooling requires package semantics.

There are no functions, classes, APIs, control flow, or local state. Dependencies are none. Its integration point is Python unittest discovery and any relative import expectations under the test suite.

Risk is minimal. Removing it could alter import behavior for older tooling or package-based discovery, while keeping it has no runtime cost. Test signal is indirect: `python3 -m unittest discover -s tests -v` should still discover and run the test suite. Because the file is empty, coverage expectations should be limited to package/import behavior rather than executable behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/tests/callback_plugins/__init__.py -->
# sources/test-tools/kdevops/tests/callback_plugins/__init__.py

Purpose: empty Python package marker for callback plugin tests. It marks `tests/callback_plugins` as importable package space for unittest discovery and tooling.

There are no functions, classes, control paths, mutable state, or dependencies. The only integration behavior is Python package recognition around `test_lucid.py`.

Risks are limited to test discovery/import semantics. If removed, direct `unittest discover` may still work in modern Python, but package-aware tools or relative imports could behave differently. Test signals are indirect: callback plugin tests should still be discoverable and import their target plugin after path setup in `test_lucid.py`. No standalone unit tests are meaningful for this empty marker.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/tests/callback_plugins/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/tests/callback_plugins/test_lucid.py -->
# sources/test-tools/kdevops/tests/callback_plugins/test_lucid.py

Purpose: unittest suite for the `lucid` Ansible stdout callback plugin. It tests plugin metadata, documentation YAML, terminal interactivity detection, formatting helpers, result cleaning, task state transitions, failed item tracking, argspec filtering, and background update-thread cleanup.

Important helpers and fixtures include `_make_callback()`, `ANSIBLE_REQUIRED`, mocked Display objects, lightweight MagicMock task/result objects, and `patch.dict()` environment manipulation. The suite imports `callback_plugins/lucid.py` by prepending the callback directory to `sys.path`.

Control flow skips all tests if the callback or Ansible dependencies cannot be imported. Individual tests then isolate one plugin behavior at a time, avoiding full Ansible runner setup. Some tests seed `running_tasks` directly to simulate `v2_runner_on_start`.

State under test includes callback fields such as `running_tasks`, `completed_tasks`, `failed_items`, `current_task_name`, and dynamic update-thread stop events. Risks include reliance on private plugin methods, timing sensitivity in thread cleanup, and test expectations coupled to exact formatting strings. Test signal is strong for regressions in callback UI helpers and lifecycle transitions; it should run with `python3 -m unittest discover -s tests -v`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/tests/callback_plugins/test_lucid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/Makefile -->
# sources/test-tools/kdevops/workflows/Makefile

Purpose: central workflow Makefile that conditionally includes individual kdevops workflow Makefiles and accumulates Ansible extra variables.

Important variables are `WORKFLOW_ARGS`, `WORKFLOW_ARGS_SEPARATED`, `BOOTLINUX_ARGS`, `ANSIBLE_EXTRA_ARGS`, `ANSIBLE_EXTRA_ARGS_SEPARATED`, and `ANSIBLE_EXTRA_ARGS_DIRECT`. It includes `workflows/common/Makefile` unconditionally, then includes workflow-specific Makefiles when their `CONFIG_KDEVOPS_WORKFLOW_ENABLE_*` or related config symbols are `y`.

Control flow is GNU Make `ifeq` based on generated config. Bootlinux additionally writes `kdevops_bootlinux='True'` or `'False'`. The one unconditional target is `nfstests-results-visualize`, which runs the nfstest visualization script independent of enabling the full workflow.

State is Make variable accumulation and included target definitions. Integration points are Kconfig-generated `.config`, Ansible playbooks, and each workflow subdirectory. Risks include missing included files when config enables a workflow, ordering effects in `WORKFLOW_ARGS`, and `WORKFLOW_ARGS_DIRECT` being appended without initialization in this file. Test signals should run `make -n` with representative configs and verify expected targets/extra vars are present.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/Kconfig -->
# sources/test-tools/kdevops/workflows/ai/Kconfig

Purpose: Kconfig configuration for the AI workflow, currently centered on Milvus vector database performance testing.

Important symbols include `AI_TESTS_VECTOR_DATABASE`, `AI_VECTOR_DB_MILVUS`, `AI_VECTOR_DB_MILVUS_QUICK_TEST`, Docker-only Milvus settings, version/port/collection/dimension/dataset/batch/query counts, `AI_BENCHMARK_RESULTS_DIR`, graphing enablement, `AI_BENCHMARK_ITERATIONS`, Docker storage inclusion, and optional `AI_MULTIFS_ENABLE`.

Control flow is nested Kconfig choices and conditionals under `KDEVOPS_WORKFLOW_ENABLE_AI`. Selecting vector database tests also selects baseline/dev comparison. Quick-test mode can be forced by CLI detection through `scripts/check-cli-set-var.sh`; it reduces dataset size and iteration count for CI/demo runs. Docker, docker-storage, native, and multifs fragments are sourced based on symbols.

State persists as yaml output consumed by Ansible and Make. Risks include `AI_VECTOR_DB_MILVUS_NATIVE` being referenced without definition in this file, typo in help text, storage consumption defaults near 100 GiB, and Docker-only assumptions. Test signals should parse Kconfig, test quick-mode defaults, and verify generated yaml drives `workflows/ai/Makefile` correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/Makefile -->
# sources/test-tools/kdevops/workflows/ai/Makefile

Purpose: Make target layer for the AI workflow. It translates Kconfig symbols into Ansible extra vars and defines setup, benchmark, results, uninstall, destroy, and help targets.

Important variables include `AI_DATA_TARGET`, `AI_ARGS`, `AI_MANUAL_ARGS`, and `AI_ARGS_SEPARATED`. Important targets include `ai`, `ai-baseline`, `ai-dev`, `ai-tests`, `ai-tests-baseline`, `ai-tests-dev`, `ai-tests-results`, `ai-results`, `ai-results-baseline`, `ai-results-dev`, `monitor-results`, `ai-setup`, `ai-uninstall`, `ai-destroy`, and `ai-help-menu`.

Control flow builds `AI_ARGS` from `CONFIG_AI_BENCHMARK_RESULTS_DIR`, `CONFIG_AI_TESTS_VECTOR_DATABASE`, and `CONFIG_AI_VECTOR_DB_MILVUS`. Targets invoke Ansible playbooks with `--extra-vars=@$(KDEVOPS_EXTRA_VARS)` plus inline AI arguments and optional host limits. Benchmark targets run result collection after tests.

State is Make variable expansion, Ansible inventory, extra-vars files, and generated result artifacts. Integration points are playbooks under `playbooks/ai*.yml` and global workflow Make aggregation. Risks include inconsistent host limiting via `HOSTS` versus `LIMIT_HOSTS`, hardcoding Milvus Docker true when Milvus enabled, and shell quoting of inline extra vars. Test signals should use `make -n` for baseline/dev/all targets and assert expected playbooks and vars.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/scripts/analysis_config.json -->
# sources/test-tools/kdevops/workflows/ai/scripts/analysis_config.json

Purpose: default JSON configuration for AI benchmark result analysis and graph generation.

The schema contains `enable_graphing`, `graph_format`, `graph_dpi`, and `graph_theme`. `analyze_results.py` loads this file when passed via `--config` and overlays it onto its built-in defaults.

There is no control flow or persistence beyond static JSON. Integration points are Ansible result-analysis tasks or manual invocations of `workflows/ai/scripts/analyze_results.py`.

Risks are low, but the configured DPI of 150 differs from the script's built-in default of 300, so output quality depends on whether the config file is supplied. Unsupported `graph_format` or invalid matplotlib style names are not validated here. Test signals should parse JSON, verify keys and types, run analyzer with this config on a small fixture, and confirm graph filenames use the configured extension and DPI path without errors.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/scripts/analysis_config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/scripts/analyze_results.py -->
# sources/test-tools/kdevops/workflows/ai/scripts/analyze_results.py

Purpose: AI benchmark post-processing tool. It loads `results_*.json` files, summarizes Milvus vector insert/index/query performance, captures local DUT information, writes text/HTML/consolidated JSON reports, and optionally generates matplotlib/seaborn graphs.

The main type is `ResultsAnalyzer`. Important methods include `_collect_system_info()`, `_get_storage_info()`, `_get_nvme_info()`, `_detect_virtualization()`, `_get_filesystem_info()`, `_extract_filesystem_config()`, `_extract_node_info()`, `load_results()`, `generate_summary_report()`, `generate_html_report()`, `generate_graphs()`, plotting helpers for insert/query/index/matrix/filesystem comparison, and `analyze()`. CLI requires `--results-dir` and `--output-dir`, with optional JSON `--config`.

Control flow loads optional graph libraries at import time, creates the output directory, reads all result JSON files, writes `benchmark_summary.txt`, `benchmark_report.html`, optional PNGs, and `consolidated_results.json`. Multi-node baseline/dev comparisons are inferred from hostnames ending in `-dev`; filesystem/block-size labels are primarily inferred from filenames.

State includes result files, local `/proc`, `lsblk`, `nvme`, `df`, `dmesg`, output reports, and graph files. Risks include unescaped HTML from result data, broad bare `except`, filename heuristics overriding JSON, missing graph libraries causing summary-only output, and local analyzer host info being mixed with DUT result info. Tests should use fixture JSONs for single-node and baseline/dev cases, mock subprocesses, validate generated reports, and exercise graph-disabled and graph-missing paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/scripts/analyze_results.py -->
