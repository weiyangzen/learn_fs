# Research Group: subset-b-009263

This grouped report covers the requested kdevops PyNFS visualization, rcloud Terraform provider, and Terraform cloud-provider Kconfig generation files. Each source file has its own bounded section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/pynfs/visualize_results.py -->
# sources/test-tools/kdevops/scripts/workflows/pynfs/visualize_results.py

## Purpose
This Python CLI turns PyNFS JSON result files into an HTML dashboard and, when `matplotlib` is importable, companion PNG charts. It is oriented around a single kernel version and searches a results directory for files named like `<kernel>-v4.0.json`, `<kernel>-v4.1.json`, or `<kernel>-vblock.json`. The output is intended for human inspection of NFS protocol test pass/fail/error/skip counts, per-class test details, and version-to-version comparisons.

## Important APIs, Types, And Functions
`load_json_results()` wraps JSON parsing with stderr-style console errors and returns `None` on failure. `categorize_tests()` groups `testcase` entries by `classname` and classifies them by presence of `skipped`, `failure`, or `error` fields. `generate_chart_data()` converts suite counters into normalized chart dictionaries with total, passed, failed, errors, skipped, and pass rate. `generate_png_charts()` uses `matplotlib` with the `Agg` backend to render per-version pie/bar charts plus a multi-version comparison chart. `generate_html_report()` is the main renderer: it discovers JSON files, creates `results_dir/html`, calls chart generation, embeds CSS/JavaScript, and returns HTML text plus generated PNG names. `main()` parses `results_dir`, `kernel_version`, and optional `--output`.

## Control Flow
At import time the script attempts to import matplotlib, sets `MATPLOTLIB_AVAILABLE`, and prints a warning if unavailable. Runtime starts in `main()`, calls `generate_html_report()`, exits with status 1 if no matching result data exists, chooses either the requested output path or `html/index.html`, and writes the report. HTML rendering loads all matching JSON files for the kernel, builds chart summaries, optionally writes PNGs, categorizes detailed test cases, then concatenates one large HTML document with tabs, cards, progress bars, PNG previews, and Chart.js fallback code.

## State And Persistence
Persistent inputs are JSON files in the supplied results directory. Outputs are `index.html` or the requested output file, a created `html/` directory, and optional PNG chart files named `pynfs-<version>-results.png` and `pynfs-comparison.png`. The script has no cache and no durable state beyond these artifacts. Runtime state is in dictionaries/lists of result data and chart descriptors.

## Dependencies And Integration Points
It depends on Python standard modules `json`, `argparse`, `pathlib`, `datetime`, and `re`, optional `matplotlib`, and runtime browser access to Chart.js from jsDelivr for non-PNG fallback charts. It integrates with kdevops PyNFS result production, expecting junit-like JSON counters plus optional `testcase` arrays with `classname`, `name`, `code`, `skipped`, `failure`, and `error` fields.

## Risks And Test Signals
The generated HTML directly interpolates JSON-derived names and codes without HTML escaping, so malformed or adversarial test data can break markup or inject script. Empty chart slices can make `matplotlib` pie chart creation fragile when all counters are zero. The JSON discovery regex is strict and ignores unexpected file naming. External Chart.js makes fallback charts network-dependent. Useful tests include JSON loading failures, no-match behavior, zero-test suites, all result categories, missing `testcase`, matplotlib-present and matplotlib-absent runs, custom output paths, and generated HTML inspection for correct tabs and links.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/workflows/pynfs/visualize_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/client.go -->
# sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/client.go

## Purpose
This Go file implements the minimal HTTP client used by the custom `rcloud` Terraform provider. It models VM create/read/delete/start/stop operations against an rcloud REST API under `/api/v1/vms`.

## Important APIs, Types, And Functions
`APIClient` carries endpoint, bearer token, default SSH user/public-key file metadata, and an optional `*http.Client` injection point for tests. `VM` models API read responses with ID, name, state, vCPU count, memory in MB, and optional IP address. `CreateVMRequest` is the JSON payload for VM creation, including optional SSH user and public key contents. `CreateVMResponse` carries the create response ID/name/state. `newHTTPClient()` returns the injected client or a 30-second timeout client. `CreateVM()`, `GetVM()`, `DeleteVM()`, `StartVM()`, and `StopVM()` construct HTTP requests, attach JSON or authorization headers, check expected status codes, and decode or discard response bodies.

## Control Flow
Each client method builds a URL by concatenating `Endpoint` with a fixed API path. Create marshals the request body, posts JSON, requires HTTP 201, and decodes the creation response. Read performs GET, maps 404 to a generic "VM not found" error, requires 200, and decodes `VM`. Delete, start, and stop call DELETE or POST action endpoints and require HTTP 200.

## State And Persistence
The client itself is stateless besides configuration fields. State lives in the remote rcloud API. The code persists no local files, but operations mutate remote VM lifecycle state. Request timeouts are per-operation through the HTTP client.

## Dependencies And Integration Points
It depends only on Go standard library packages `bytes`, `encoding/json`, `fmt`, `io`, `net/http`, and `time`. It is consumed by `provider.go` for Terraform provider configuration and by `resource_vm.go` for resource CRUD. The REST API contract is implicit: status codes, JSON field names, and action routes must match the rcloud service.

## Risks And Test Signals
URL concatenation does not normalize trailing slashes, so `Endpoint` values ending in `/` can produce double slashes. Not-found is a plain error string, which the resource currently treats as a diagnostic instead of removing Terraform state. Delete expects only 200 and may reject common 204 delete responses. Error bodies are surfaced verbatim and may include sensitive server output. Unit tests can inject `HTTPClient` with a fake transport or `httptest.Server` to cover headers, JSON payloads, expected status handling, timeout use, and malformed JSON responses.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/provider.go -->
# sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/provider.go

## Purpose
This file defines the Terraform Plugin Framework provider for rcloud. It exposes provider-level endpoint, token, and SSH defaults, constructs an `APIClient`, and registers the VM resource.

## Important APIs, Types, And Functions
`RcloudProvider` implements `provider.Provider` and stores the build/version string. `RcloudProviderModel` maps Terraform provider configuration attributes `endpoint`, `token`, `ssh_user`, and `ssh_public_key_file`. `Metadata()` sets provider type name `rcloud` and version. `Schema()` declares optional/sensitive configuration attributes. `Configure()` reads config, falls back to `RCLOUD_ENDPOINT` and `RCLOUD_TOKEN`, defaults the endpoint to `http://localhost:8765`, builds `APIClient`, and publishes it through `resp.DataSourceData` and `resp.ResourceData`. `Resources()` returns `NewVMResource`; `DataSources()` currently returns an empty list; `New(version)` is the provider factory used by `main.go`.

## Control Flow
Terraform calls schema and configure during provider setup. Configure decodes config into framework `types.String` fields, short-circuits on diagnostics, resolves environment/config/default precedence, then passes the client to resources and future data sources. Resource discovery is static and currently includes only `rcloud_vm`.

## State And Persistence
The provider persists no data itself. Sensitive token values are held in the in-memory client and provider config state through Terraform. SSH defaults are provider-level state that resources inherit during create.

## Dependencies And Integration Points
It depends on Terraform Plugin Framework provider, resource, datasource, schema, and types packages. It integrates with environment variables `RCLOUD_ENDPOINT` and `RCLOUD_TOKEN`, with `resource_vm.go` through `ResourceData`, and with the provider server in `main.go`.

## Risks And Test Signals
Optional string attributes are checked only for null, not unknown values, which can matter during planning in Terraform Framework providers. There is no validation for endpoint URL format or SSH key path. `DataSourceData` is populated despite no data sources. Acceptance tests should verify configuration precedence, sensitive token schema marking, default endpoint behavior, provider metadata, and resource registration. Framework unit tests can use provider schema/configure harnesses without contacting rcloud.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/resource_vm.go -->
# sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/resource_vm.go

## Purpose
This file implements the `rcloud_vm` Terraform resource. It maps Terraform desired VM properties into rcloud create requests, waits for a usable IP address, updates Terraform state, deletes VMs, and supports import by ID.

## Important APIs, Types, And Functions
`VMResource` implements `resource.Resource` and `resource.ResourceWithImportState` and stores the configured `*APIClient`. `VMResourceModel` maps state attributes: `id`, `name`, `vcpus`, `memory_gb`, `base_image`, `root_disk_gb`, `ssh_user`, `ssh_public_key_file`, `state`, and `ip_address`. `Schema()` marks most creation inputs as `Required` or `Optional` with `RequiresReplace()` plan modifiers, while computed fields use `UseStateForUnknown()` for ID and computed-only schema for state/IP. `Configure()` type-checks provider data. `Create()` resolves SSH settings, reads public key file contents, calls `CreateVM()`, polls `GetVM()` for an IP address, cleans up on timeout, and sets state. `Read()`, `Update()`, `Delete()`, and `ImportState()` implement the rest of the resource lifecycle.

## Control Flow
Create reads planned values, picks resource SSH settings over provider defaults, reads the SSH public key file if configured, sends a create request with memory converted from GB to MB, and stores the returned ID. It then polls once per second for up to 300 seconds until `vm.IPAddress` is non-empty. If no IP arrives, it reports a diagnostic and attempts to delete the VM. Read fetches the remote VM and refreshes state/IP. Update is effectively a no-op because replace-required plan modifiers should handle mutable inputs. Delete calls remote delete and leaves state removal to Terraform.

## State And Persistence
Terraform state stores the VM ID, desired immutable inputs, remote state, and IP address. The remote rcloud API owns actual VM lifecycle state. Create reads the SSH public key file from disk and sends its contents to the API but does not persist it locally. Failed IP acquisition can leave a remote VM if cleanup delete fails.

## Dependencies And Integration Points
It depends on Terraform Plugin Framework resource/schema/planmodifier packages, `terraform-plugin-log/tflog`, Go `os` for key reads, and the local `APIClient`. It integrates with kdevops bringup assumptions by refusing successful create without an IP address, because later SSH configuration needs that IP.

## Risks And Test Signals
The 5-minute polling loop uses `time.Sleep()` directly and does not honor context cancellation, which can make Terraform interrupts slow. A 404 on read is reported as an error rather than removing state, so out-of-band deletion is not gracefully reconciled. Update can write planned data without reading remote truth if any future mutable field is added. SSH key file contents are logged only by length, but diagnostics include the key path. Tests should cover resource/provider config type errors, create payload conversion, provider-vs-resource SSH precedence, key read failures, IP timeout cleanup, read IP nulling, delete errors, import state, and context cancellation expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/resource_vm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform-provider-rcloud/main.go -->
# sources/test-tools/kdevops/terraform-provider-rcloud/main.go

## Purpose
This is the executable entrypoint for the rcloud Terraform provider plugin. It starts the Terraform Plugin Framework provider server with the registry address `registry.terraform.io/kdevops/rcloud`.

## Important APIs, Types, And Functions
The package-level `version` variable defaults to `dev` and is intended to be overridden by release tooling. `main()` declares a `-debug` flag, parses CLI flags, constructs `providerserver.ServeOpts` with provider address and debug mode, and calls `providerserver.Serve(context.Background(), provider.New(version), opts)`.

## Control Flow
Execution is linear: parse flags, build serve options, start the provider server, and fatal-log any startup/runtime error returned by the framework server. `go:generate` comments document optional Terraform formatting and plugin docs generation.

## State And Persistence
There is no persistent state in this file. Runtime state is the provider server process and its debug setting. Version metadata flows into provider metadata.

## Dependencies And Integration Points
It depends on Go `flag`, `log`, `context`, HashiCorp `providerserver`, and the internal provider package. Terraform discovers and runs this binary as a provider plugin; the address must match provider source names used by Terraform configurations.

## Risks And Test Signals
The server uses a background context, so shutdown relies on framework/server process handling rather than caller-provided cancellation. Debug mode is only opt-in through `-debug`. Tests are usually limited to build tests and provider smoke tests; release checks should verify the injected version, provider address, and generated docs examples.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform-provider-rcloud/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/Kconfig -->
# sources/test-tools/kdevops/terraform/Kconfig

## Purpose
This Kconfig fragment is the top-level Terraform configuration menu for kdevops when `TERRAFORM` is enabled. It wires provider-specific, SSH, private-network, and Terraform-vs-OpenTofu settings into generated YAML output.

## Important APIs, Types, And Functions
It sources `terraform/Kconfig.providers` and `terraform/Kconfig.ssh`, defines `TERRAFORM_PRIVATE_NET`, `TERRAFORM_PRIVATE_NET_PREFIX`, `TERRAFORM_PRIVATE_NET_MASK`, a choice between `TERRAFORM_USE_TERRAFORM` and `TERRAFORM_USE_OPENTOFU`, and `TERRAFORM_BINARY_PATH`. Several symbols use `output yaml` so generated configuration can feed automation.

## Control Flow
The whole file is guarded by `if TERRAFORM`. Provider and SSH menus are displayed first. Azure-only private network options follow, then a mutually exclusive IaC binary choice with Terraform as the default. The binary path default depends on the selected choice.

## State And Persistence
Kconfig choices persist in `.config` and downstream generated YAML. The binary path becomes a runtime dependency for Make/Terraform orchestration. Private-network prefix and mask persist as user-selected infrastructure configuration.

## Dependencies And Integration Points
It integrates with the broader kdevops Kconfig tree, provider-specific Terraform modules, YAML generation, and Make targets that invoke the configured Terraform/OpenTofu binary. `TERRAFORM_PRIVATE_NET` currently depends on Azure only.

## Risks And Test Signals
The default OpenTofu path `/usr/local/bin/tofu` may not match distro packaging. Private-network defaults can conflict with user networks. The Azure-only dependency should be retested if private networking becomes available for other providers. Test signals include `make menuconfig`, defconfig generation for Terraform and OpenTofu, YAML output inspection, and Make targets using the selected binary path.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/Kconfig -->
# sources/test-tools/kdevops/terraform/aws/Kconfig

## Purpose
This Kconfig fragment assembles AWS-specific Terraform configuration menus when `TERRAFORM_AWS` is selected.

## Important APIs, Types, And Functions
It creates menus for resource location, compute, storage, and identity/access. It sources wrapper/generated Kconfig files: `terraform/aws/kconfigs/Kconfig.location`, `Kconfig.instance`, `Kconfig.ami`, `Kconfig.storage`, and `Kconfig.identity`.

## Control Flow
The file is a declarative menu wrapper guarded by `if TERRAFORM_AWS`. Location is shown first, compute combines instance and AMI selection, then storage and identity menus are loaded.

## State And Persistence
The file itself has no runtime state. Selected symbols from sourced files persist in Kconfig `.config` and generated YAML/Terraform variable files.

## Dependencies And Integration Points
It depends on dynamic Kconfig generation targets such as `make cloud-config-aws` to populate current AWS location, instance, and AMI choices. It integrates with AWS Terraform modules and scripts under `terraform/aws/scripts`.

## Risks And Test Signals
Missing generated files can break menuconfig or hide choices. AWS resource availability changes frequently, so stale generated fragments can present unavailable AMIs, regions, or instance types. Tests should run menuconfig/olddefconfig before and after `make cloud-config-aws`, and validate that generated symbols match Terraform variable consumption.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/scripts/aws_common.py -->
# sources/test-tools/kdevops/terraform/aws/scripts/aws_common.py

## Purpose
This module provides shared AWS helper functions for scripts that generate AWS Kconfig menus for regions, availability zones, instance types, and AMIs.

## Important APIs, Types, And Functions
`AwsNotConfiguredError` signals optional missing credentials. `get_default_region()` reads `~/.aws/config` and falls back to `us-east-1`. `get_jinja2_environment()` creates a trimmed/lstripped Jinja2 environment rooted at the caller script directory. `create_ec2_client()` builds a boto3 EC2 client. `handle_aws_client_error()` and `handle_aws_credentials_error()` provide common stderr messages. `require_aws_credentials()` validates credentials using STS caller identity. `get_all_regions()` calls `describe_regions(AllRegions=True)`. `get_region_availability_zones()` calls `describe_availability_zones()` for availability-zone types. `get_all_instance_types()` pages through `describe_instance_types()`. `get_region_kconfig_name()` converts region names to Kconfig symbol suffixes.

## Control Flow
Generator scripts call `require_aws_credentials()` early when live AWS data is needed, then use the list/query helpers and Jinja environment. Query helpers catch credential and client errors and return empty lists or `None` rather than throwing, allowing callers to choose whether to exit or skip optional generation.

## State And Persistence
The module reads `~/.aws/config` but writes no state. AWS credential/session state is managed by boto3. Returned data structures are in-memory lists and dictionaries consumed by Kconfig renderers.

## Dependencies And Integration Points
It depends on `boto3`, `botocore`, `jinja2`, and Python `ConfigParser`. It is imported by AWS `gen_kconfig_location`, `gen_kconfig_instance`, and `gen_kconfig_ami`. It integrates with local AWS CLI/profile conventions without shelling out to `aws`.

## Risks And Test Signals
`require_aws_credentials()` uses STS without explicitly passing the default region, so unusual profiles may fail differently from EC2 calls. `get_default_region()` supports common default profile names but not all AWS config inheritance features. Client helpers return empty results on broad exceptions, which can hide transient API failures. Tests should mock boto3 clients/paginators for success/error paths, parse sample config files, verify Kconfig name conversion, and ensure generators skip cleanly when credentials are absent.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/scripts/aws_common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_ami -->
# sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_ami

## Purpose
This executable Python script discovers Linux AMI publishers and AMI name patterns and renders AWS AMI-related Kconfig or raw/Terraform reference output.

## Important APIs, Types, And Functions
`get_known_ami_owners()` defines trusted owner IDs and regex search patterns for AlmaLinux, Amazon, CentOS, Debian, Fedora, Oracle, PyTorch, Red Hat, Rocky, SUSE, and Ubuntu. `discover_ami_patterns()` queries `describe_images`, filters by owner/pattern/state/type, groups AMIs, and emits latest/sample data plus Terraform filter examples. `classify_ami_name()` maps AMI names into OS/version groups. `generate_terraform_pattern()` and helpers derive wildcard filters from sample names. `generate_terraform_example()` emits complete `aws_ami` data-source snippets. Output functions render owners, per-owner distro menus, raw tables, or Terraform examples. `parse_arguments()` supports owner selection, `--owners`, `--format`, `--quiet`, and `--region`.

## Control Flow
`main()` can list known owners without credentials. For discovery it validates AWS credentials, picks an explicit or default region, and either processes one owner or all owners. Full Kconfig mode prints an owners menu, then uses a 10-worker thread pool to discover each owner and renders `distro.j2` sections in deterministic owner order.

## State And Persistence
No local files are written by the script itself; stdout is redirected by Make targets into generated Kconfig files. It reads AWS credentials/config through boto3 and current AMI state from EC2. AMI owner metadata is static in code.

## Dependencies And Integration Points
It depends on `aws_common.py`, `botocore`, `jinja2` templates `owners.j2` and `distro.j2`, and live EC2 AMI APIs. It integrates with `terraform/aws/Kconfig` through generated `Kconfig.ami` content and with Terraform users through example output.

## Risks And Test Signals
The `recent_amis` fallback is computed but grouping still iterates over `matching_amis`, so the time-window filtering currently does not constrain generated patterns. Regex classifications are heuristic and can become stale as publishers rename images. Owner IDs can change, especially marketplace-style publishers. Parallel AWS calls can hit rate limits. Tests should mock `describe_images` pages, exercise classification for every owner, verify pattern generation, confirm no-credentials exit status 0, and render Jinja templates with stable fixture data.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_ami -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_instance -->
# sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_instance

## Purpose
This script queries AWS EC2 instance-type metadata and renders Kconfig menus or raw tables for EC2 instance families and specific instance types.

## Important APIs, Types, And Functions
`parse_all_instance_families()` groups `describe_instance_types` records by prefix before the dot and tracks counts, GPU presence, and architectures. `get_gpu_info()` formats GPU names/counts/memory from `GpuInfo`. `get_instance_family_info()` filters instances in a family and extracts vCPUs, memory, CPU ISA, GPU, network performance, storage, bare-metal, free-tier, and placeholder pricing. Output functions render Jinja templates `families.j2` and `family.j2` or raw tables. `parse_arguments()` supports family selection, `--families`, `--format`, `--quiet`, and `--region`.

## Control Flow
`main()` validates AWS credentials but exits 0 if absent so dynamic config can be optional. It chooses region, fetches all instance types once, then either lists families, renders one family, or renders all families and their instance choices. Kconfig full output first prints the family selector then one section per family.

## State And Persistence
The script writes only stdout. AWS instance metadata is live remote state. In-memory state is the instance-type list and derived family dictionaries.

## Dependencies And Integration Points
It imports shared helpers from `aws_common.py`, depends on boto3 EC2 `describe_instance_types`, and renders Jinja templates from the script directory. It feeds generated AWS compute Kconfig fragments consumed by `terraform/aws/Kconfig`.

## Risks And Test Signals
Family parsing assumes the dot-delimited EC2 naming convention. Pricing is always "Not available", so raw output can look more complete than it is. Architecture and GPU detection depend on fields present in AWS responses. Tests should mock instance-type pages with GPU, local storage, ARM, bare-metal, free-tier, and missing optional fields; verify family sorting; and validate no-credential skip behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_instance -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_location -->
# sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_location

## Purpose
This script discovers AWS regions and availability zones and renders Kconfig or raw output for selecting Terraform AWS resource locations.

## Important APIs, Types, And Functions
`get_region_info()` combines a region record with its availability zones, skips not-opted-in regions, and returns endpoint, opt-in status, and zone metadata. `output_region_kconfig()` renders `zone.j2` for one region. `output_regions_kconfig()` renders `regions.j2` with the default region. `output_locations_kconfig()` renders all regions plus zone sections, using a 20-worker thread pool for per-region zone discovery. Raw output functions print tables. `parse_arguments()` supports region lookup, `--regions`, `--format`, and `--quiet`.

## Control Flow
`main()` validates credentials with optional skip-on-absent behavior, fetches all regions, then either lists regions, details a specific region, or emits the complete locations menu. Full Kconfig output is deterministic: the top-level regions menu follows sorted region order, and zone sections are printed in the original region list order after parallel discovery completes.

## State And Persistence
The script writes generated content to stdout only. It reads AWS config/credentials and live EC2 region/AZ state. No cache is maintained.

## Dependencies And Integration Points
It depends on `aws_common.py`, boto3 EC2 `describe_regions`/`describe_availability_zones`, Jinja templates `regions.j2` and `zone.j2`, and the AWS Kconfig wrapper. Generated symbols are later consumed by Terraform variable generation.

## Risks And Test Signals
All-region availability-zone discovery can be slow or rate-limited. Opt-in statuses differ by account, so generated menus are account-specific. The zone query currently only includes `availability-zone`, not local/wavelength zones. Tests should mock opted-in and not-opted-in regions, empty zone lists, API errors, default-region conversion, template rendering, and no-credential exit 0.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_location -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/templates/config.yaml -->
# sources/test-tools/kdevops/terraform/aws/templates/config.yaml

## Purpose
This small cloud-init YAML template configures hostname behavior and the default SSH user for AWS guests launched by kdevops Terraform.

## Important APIs, Types, And Functions
The file is declarative YAML. It sets `preserve_hostname: false`, `manage_etc_hosts: false`, `hostname: ${new_hostname}`, and `system_info.default_user.name: ${ssh_config_user}`. The `${...}` placeholders are intended for Terraform/template substitution.

## Control Flow
There is no executable control flow. A provisioning layer renders the template with a target hostname and SSH username, then passes it as cloud-init user-data or merged cloud configuration.

## State And Persistence
The rendered configuration affects guest-local persistent state: hostname and default user configuration. The template itself stores no secrets.

## Dependencies And Integration Points
It depends on cloud-init semantics and the surrounding Terraform/template engine that supplies `new_hostname` and `ssh_config_user`. It integrates with AWS instance provisioning and kdevops SSH access setup.

## Risks And Test Signals
If placeholders are not substituted, guests may receive literal `${...}` values. Disabling `manage_etc_hosts` may interact with distro defaults. Tests should render the template with representative values, validate YAML syntax, boot a cloud image, and verify hostname/default user behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/aws/templates/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/Kconfig -->
# sources/test-tools/kdevops/terraform/azure/Kconfig

## Purpose
This Kconfig wrapper exposes Azure Terraform menus for location, compute size, OS image, storage, and identity/access when `TERRAFORM_AZURE` is enabled.

## Important APIs, Types, And Functions
It sources generated files `Kconfig.location.generated`, `Kconfig.size.generated`, and `Kconfig.image.generated`, plus static `Kconfig.storage` and `Kconfig.identity`. It uses comments to separate VM size and OS image selection under the compute menu.

## Control Flow
The file is guarded by `if TERRAFORM_AZURE`. Menu ordering is location, compute, storage, and identity/access.

## State And Persistence
Selected Azure symbols persist through Kconfig `.config` and generated YAML/Terraform variables. The wrapper has no state beyond the sourced menu tree.

## Dependencies And Integration Points
It depends on Azure dynamic generator scripts to populate generated Kconfig files and on Terraform Azure modules that consume those selections.

## Risks And Test Signals
Missing or stale generated files can break menu generation or offer invalid Azure choices. Tests should run Azure cloud-config generation with and without credentials, then run `olddefconfig`/menuconfig and verify selected symbols propagate into Terraform variables.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/azure_common.py -->
# sources/test-tools/kdevops/terraform/azure/scripts/azure_common.py

## Purpose
This module centralizes Azure SDK, authentication, region, VM-size, image-offer, Jinja, and error-handling helpers for Azure Kconfig generator scripts.

## Important APIs, Types, And Functions
`AzureNotConfiguredError` marks optional auth absence. `get_default_region()` uses Azure CLI profile validation, `AZURE_DEFAULTS_LOCATION`, `~/.azure/config`, and fallback `westus`. `get_all_regions()` uses `SubscriptionClient.list_locations()` and skips logical regions. `get_compute_client()` builds `ComputeManagementClient` from CLI credentials. `get_vm_sizes_and_skus()` queries resource SKUs once per region and derives size records plus capability dictionaries. `get_all_offers_and_skus()` lists image offers and fetches SKUs in parallel. `exit_on_empty_result()` exits with diagnostics. `require_azure_credentials()` validates CLI credentials and distinguishes auth-like failures from other exceptions.

## Control Flow
Generator scripts call `require_azure_credentials()` first when live Azure data is required. Region, size, and image helpers authenticate via Azure CLI profile, call SDK list operations, convert SDK objects to plain dictionaries, and return empty structures on query failures while printing optional diagnostics.

## State And Persistence
It reads Azure CLI auth/config state and environment variables but writes no files. Returned metadata is transient and consumed by renderers. Azure SDK token/session state is managed by the Azure libraries.

## Dependencies And Integration Points
It depends on `azure.common.credentials`, `azure.mgmt.resource`, `azure.mgmt.compute`, `jinja2`, and Python config/json/os modules. It is imported by Azure location, size, and image generators and shares templates from caller directories.

## Risks And Test Signals
The Azure SDK import path `azure.common.credentials` is from older Azure SDK conventions and may not be installed in newer environments. Broad exception handling can turn service failures into empty generated menus. SKU capability parsing assumes numeric capability names are present and parseable. Tests should mock CLI profiles and SDK clients, cover missing SDK/auth, region config precedence, SKU parsing failures, offer filtering, and generated structures for logical vs physical locations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/azure_common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_image -->
# sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_image

## Purpose
This executable Python script discovers Azure Linux VM image offers/SKUs for known publishers and renders image-selection Kconfig or raw publisher/image tables.

## Important APIs, Types, And Functions
`load_yaml_config()` loads YAML from the script directory. `get_known_publishers()` reads `publisher_definitions.yml` with fallback to Debian/Red Hat. `score_sku_quality()` prefers Gen2 and LVM variants while avoiding CI/legacy variants. `supports_cloud_init()` filters Oracle/RHEL versions older than 7.7. `classify_offer_sku()` maps publisher offer/SKU names into version keys, friendly names, architectures, offers, and SKUs across Debian, RHEL, Oracle, Ubuntu, openSUSE, SLE Micro, SLES/SLE-HPC, and generic patterns. `organize_images_by_publisher()` queries Azure offers/SKUs and selects the best SKU per version. `output_images_kconfig()` renders `image_distributions.j2` and `image_publisher.j2`.

## Control Flow
`main()` can list publishers without credentials. Otherwise it validates Azure credentials, optionally filters to one publisher, chooses a region, organizes images, and emits raw or Kconfig output. Single-publisher Kconfig output is intentionally rejected; raw output is supported for inspection. Full Kconfig output sorts publishers by priority and versions numerically.

## State And Persistence
The script writes only stdout. It reads static publisher definitions and live Azure image metadata. In-memory state is a nested publisher/version mapping; `_score` is retained internally for selection but not intended as user-facing output.

## Dependencies And Integration Points
It imports `azure_common.py`, requires PyYAML for configured publisher definitions, uses Azure Compute image APIs through shared helpers, and renders Jinja templates. Generated output feeds `terraform/azure/Kconfig` image menus.

## Risks And Test Signals
Classification is heavily regex-based and provider naming changes can silently hide images. Marketplace publisher IDs for AlmaLinux/Rocky can change. The script assumes cloud-init requirements based on version heuristics. Missing PyYAML falls back to a minimal publisher list, which can reduce coverage without failing. Tests should use fixture offer/SKU maps for every publisher path, validate best-SKU scoring, ensure unsupported old Oracle/RHEL versions are filtered, cover missing YAML, and assert no-credential exit 0.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_image -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_location -->
# sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_location

## Purpose
This script discovers Azure regions and renders Azure location Kconfig choices or raw region details.

## Important APIs, Types, And Functions
`get_region_friendly_name()` combines display name and physical location when available. `get_region_info()` finds one region in an already fetched region list. `output_region_kconfig()` prints one `config TERRAFORM_AZURE_REGION_<NAME>` stanza and optional paired-region help. `output_regions_kconfig()` renders all regions via `regions.j2` after adding friendly names. Raw output functions print region tables and metadata. `parse_arguments()` supports optional region name, `--regions`, `--format`, and `--quiet`.

## Control Flow
`main()` validates credentials with optional skip-on-absent behavior, fetches regions, then either lists all regions, emits one region, or renders the complete regions Kconfig. The default region is converted to a Kconfig-safe symbol for template defaults.

## State And Persistence
The script writes stdout only. It reads Azure authentication/config state through `azure_common.py` and live subscription location metadata. No cache is maintained.

## Dependencies And Integration Points
It depends on `azure_common.py`, Azure SDK region discovery, and the `regions.j2` template. Generated content is sourced by `terraform/azure/Kconfig`.

## Risks And Test Signals
Account/subscription permissions can affect visible locations. The raw output assumes `displayName` is present. Kconfig output is only as good as the template and naming conversion. Tests should mock region lists with physical and paired metadata, missing metadata, unknown region lookup, no-credential skip behavior, and template rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_location -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_size -->
# sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_size

## Purpose
This script discovers Azure VM sizes and capabilities, groups them into families, and renders a hierarchical Kconfig menu for family and size selection.

## Important APIs, Types, And Functions
`get_all_vm_sizes_and_capabilities()` queries one or more regions, deduplicates size names, and filters Gen1-only sizes using `HyperVGenerations`. `extract_vm_size_family()` parses family prefixes from names like `Standard_D2s_v3`. `parse_vm_size_families()` computes per-family counts and min/max CPU/memory. `get_vm_size_family_info()` returns detailed raw records for one family. `determine_architecture()` identifies ARM64 Dp/Dpds families. `natural_sort_key()` sorts VM names numerically. `load_family_metadata()` reads `vm_family_metadata.yml`. `output_families_kconfig()` builds family metadata, per-size capability data, defaults, and renders `families.j2`. CLI parsing supports family query, `--families`, `--all-regions`, `--region`, `--format`, and `--quiet`.

## Control Flow
`main()` validates Azure credentials with optional skip, chooses either an explicit region, all regions, or the default region, fetches sizes/capabilities, then lists families, details a family, or emits Kconfig. Full Kconfig output groups sizes by family and chooses the default family containing `Standard_DS3_v2` when available.

## State And Persistence
The script writes stdout only. It reads `vm_family_metadata.yml`, Azure CLI auth/config, and live SKU metadata. In-memory state includes deduplicated sizes and capabilities keyed by size name.

## Dependencies And Integration Points
It depends on `azure_common.py`, PyYAML, Azure resource SKU APIs, and Jinja template `families.j2` or older `sizes.j2`. Generated size menus are sourced by Azure Kconfig and later consumed by Terraform variable generation.

## Risks And Test Signals
Family extraction is regex-based and may group new Azure families poorly. Filtering `HyperVGenerations == "V1"` assumes capability strings are present and exact. ARM detection only covers Dp/Dpds patterns. Loading metadata is best-effort, so missing descriptions do not fail generation. Tests should use fixture SKUs with Gen1/Gen2, ARM, accelerated networking, new-family names, default-size absent/present, all-regions deduplication, and missing metadata file.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_size -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/publisher_definitions.yml -->
# sources/test-tools/kdevops/terraform/azure/scripts/publisher_definitions.yml

## Purpose
This YAML file is the policy/configuration source for Azure image publishers supported by `gen_kconfig_image`. It records Azure publisher IDs, display names, descriptions, priorities, and optional offer regex filters.

## Important APIs, Types, And Functions
Top-level keys are publisher identifiers such as `debian`, `redhat`, `canonical`, `oracle`, `suse`, `almalinux`, and `rockylinux`. Required fields are `publisher_id`, `publisher_name`, `description`, and `priority`. Some entries include `offer_patterns`, which are regex strings matched against Azure offer names before SKU classification.

## Control Flow
There is no executable flow. `gen_kconfig_image` loads this file with PyYAML, sorts publishers by priority, queries each `publisher_id`, and applies `offer_patterns` to filter relevant offers.

## State And Persistence
The file persists curated publisher metadata in the repository. It does not include secrets. Updating it changes future generated Azure image Kconfig output.

## Dependencies And Integration Points
It integrates directly with Azure image discovery and indirectly with menuconfig and Terraform image variables. Comments document using `az vm image list-publishers --location westus` to find publisher IDs.

## Risks And Test Signals
Marketplace publisher IDs for AlmaLinux and Rocky Linux are timestamp-like and may become stale. Regex filters can be too broad or too narrow, hiding useful images or including unsupported variants. Tests should load the YAML, validate required fields and priority uniqueness/order, compile all regexes, and run fixture offers through expected filters.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/publisher_definitions.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/vm_family_metadata.yml -->
# sources/test-tools/kdevops/terraform/azure/scripts/vm_family_metadata.yml

## Purpose
This YAML file provides human-readable Azure VM family descriptions, help text, and workload examples for hierarchical VM-size Kconfig generation.

## Important APIs, Types, And Functions
Top-level keys are family prefixes such as `Standard_A`, `Standard_B`, `Standard_D`, `Standard_DS`, `Standard_E`, `Standard_ES`, `Standard_M`, `Standard_F`, `Standard_FS`, `Standard_L`, `Standard_LS`, `Standard_N`, `Standard_NC`, `Standard_ND`, `Standard_NV`, `Standard_H`, and `Standard_Dp`. Each entry can contain `description`, block `help_text`, and `workloads`.

## Control Flow
There is no code execution. `gen_kconfig_size` loads the file, looks up metadata by parsed family prefix, and falls back to generic descriptions if a family is missing.

## State And Persistence
The file persists curated documentation and policy text in the repo. Updating descriptions changes generated menu help but not cloud state.

## Dependencies And Integration Points
It depends on PyYAML parsing and the family-prefix parser in `gen_kconfig_size`. It integrates with `families.j2` output so menuconfig users see useful family descriptions.

## Risks And Test Signals
The "Last Updated" comment can become stale as Azure adds families. Missing families degrade help text quality but do not fail generation. YAML formatting or indentation errors can disable all metadata. Tests should parse the file, verify required fields for each family, compare discovered family prefixes against metadata coverage, and render a sample Kconfig menu.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/azure/scripts/vm_family_metadata.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/Kconfig -->
# sources/test-tools/kdevops/terraform/datacrunch/Kconfig

## Purpose
This Kconfig fragment exposes DataCrunch Terraform menus and configuration for compute, OS image, identity/access, API credential file, and optional OS-NVMe volume preservation.

## Important APIs, Types, And Functions
It sources `terraform/datacrunch/kconfigs/Kconfig.compute`, `Kconfig.images`, and `Kconfig.identity`. `TERRAFORM_DATACRUNCH_KEEP_VOLUMES` controls whether OS-NVMe volumes are preserved and cached; its default is driven by whether the `KEEP` make variable is set. `TERRAFORM_DATACRUNCH_API_KEY_FILE` stores the credentials file path, defaulting to `~/.datacrunch/credentials`.

## Control Flow
The file is guarded by `if TERRAFORM_DATACRUNCH`. Menus are shown first, followed by volume-cache and credential path options. Help text documents cost tradeoffs and cache location.

## State And Persistence
Selections persist in `.config` and generated outputs. Volume cache behavior maps to files under `~/.cache/kdevops/datacrunch/$KDEVOPS_HOSTS_PREFIX.yml` via wrapper scripts. Credential file path points to external secret material but does not store the secret in Kconfig.

## Dependencies And Integration Points
It integrates with DataCrunch Terraform modules, apply/destroy wrapper scripts, `volume_cache.py`, and `extract_api_key.py`. It also uses Kconfig `$(shell, ...)` to reflect Make variable state.

## Risks And Test Signals
The `KEEP`-derived default is environment-dependent and can surprise users if stale cache files incur charges. The help text describes a legacy `datacrunch_api_key` key while extractor also requires `client_id`. Tests should verify defconfig behavior with and without `KEEP`, generated YAML values, wrapper interpretation of `.config`, and credential-file path expansion.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/extract_api_key.py -->
# sources/test-tools/kdevops/terraform/datacrunch/extract_api_key.py

## Purpose
This Python helper reads DataCrunch credentials from an INI file and emits JSON suitable for Terraform's external data source.

## Important APIs, Types, And Functions
`extract_credentials(creds_file)` expands the path, validates existence, parses it with `configparser`, chooses `[default]` or `DEFAULT`, extracts `client_id`, and extracts `client_secret` from `client_secret`, `datacrunch_api_key`, or `api_key`. The CLI defaults to `~/.datacrunch/credentials` and prints `{"client_id": "...", "client_secret": "..."}`.

## Control Flow
The script validates the file and required keys, writes error messages to stderr, and exits 1 on any failure. On success it prints JSON to stdout.

## State And Persistence
It reads credential files but writes no state. Secret values are transiently held in memory and printed to stdout for Terraform consumption.

## Dependencies And Integration Points
It depends on Python standard `configparser`, `json`, `sys`, and `pathlib`. It integrates with Terraform `external` data sources and DataCrunch provider authentication.

## Risks And Test Signals
Printing secrets to stdout is required by Terraform external data flow but means logs must not capture it. `ConfigParser` default-section handling is subtle: `DEFAULT` is always present but may not represent an explicit section. Errors are broad and exit immediately, which is fine for CLI use but harder for library reuse. Tests should cover missing file, missing section, legacy key names, whitespace trimming, explicit path argument, and JSON shape.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/extract_api_key.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/scripts/apply_wrapper.sh -->
# sources/test-tools/kdevops/terraform/datacrunch/scripts/apply_wrapper.sh

## Purpose
This Bash wrapper runs `terraform apply` for DataCrunch and, when volume preservation is enabled, records OS volume IDs from Terraform output into the kdevops DataCrunch volume cache.

## Important APIs, Types, And Functions
The script computes `SCRIPT_DIR`, `TERRAFORM_DIR`, `VOLUME_CACHE`, and `KDEVOPS_ROOT`; sources `$KDEVOPS_ROOT/.config`; derives `KEEP_VOLUMES` from `CONFIG_TERRAFORM_DATACRUNCH_KEEP_VOLUMES`; and reads `CONFIG_KDEVOPS_HOSTS_PREFIX`. It invokes `terraform apply "$@"`, then on success calls `terraform output -json` and an inline Python JSON parser to extract `instance_details.value[hostname].os_volume_id`, saving each mapping with `volume_cache.py save`.

## Control Flow
With `set -e`, missing config or failed commands abort. The script validates host prefix, prints summary information, changes to the Terraform directory, runs apply, captures status, and only performs cache update when apply succeeded and keep-volumes is yes. It preserves Terraform's exit status.

## State And Persistence
It mutates remote infrastructure through Terraform apply and writes local cache mappings under `~/.cache/kdevops/datacrunch/<prefix>.yml` through `volume_cache.py`. It reads `.config` and Terraform state/output.

## Dependencies And Integration Points
It depends on Bash, Terraform on PATH, Python 3, the DataCrunch Terraform output contract `instance_details`, and `volume_cache.py`. It integrates with kdevops Make targets that should call this wrapper instead of raw Terraform when DataCrunch caching is desired.

## Risks And Test Signals
`set -e` plus command substitution around `terraform output` is handled with an `if`, but other unexpected failures abort. The wrapper hardcodes `terraform` rather than honoring a configured Terraform/OpenTofu binary. Cache update depends on output field shape and silently does nothing when no volume IDs are present. Tests should run with fixture `.config`, fake Terraform script outputs, KEEP on/off, host prefix missing, malformed JSON output, and volume cache save failures.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/scripts/apply_wrapper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/scripts/destroy_wrapper.sh -->
# sources/test-tools/kdevops/terraform/datacrunch/scripts/destroy_wrapper.sh

## Purpose
This Bash wrapper runs `terraform destroy` for DataCrunch and keeps or clears local OS-volume cache records according to the configured keep-volumes setting.

## Important APIs, Types, And Functions
It computes the same paths as `apply_wrapper.sh`, sources `.config`, derives `KEEP_VOLUMES`, validates `CONFIG_KDEVOPS_HOSTS_PREFIX`, optionally gathers instance hostnames from `terraform output -json`, runs `terraform destroy "$@"`, and then either lists preserved cache entries or deletes mappings for destroyed instances with `volume_cache.py delete`.

## Control Flow
The wrapper prints warnings when keep-volumes is disabled, captures existing instance names before destruction when Terraform output is available, runs destroy, and post-processes cache state only if destroy exits 0. KEEP=yes preserves cache and displays it; KEEP=no deletes cache mappings for known instance names.

## State And Persistence
It mutates remote infrastructure via Terraform destroy. Local persistent side effects are deletion or preservation of cache mappings under `~/.cache/kdevops/datacrunch/<prefix>.yml`. It reads `.config`, Terraform output/state, and cache files.

## Dependencies And Integration Points
It depends on Bash, Terraform, Python 3, the `instance_details` Terraform output contract, and `volume_cache.py`. It integrates with DataCrunch lifecycle automation and the `TERRAFORM_DATACRUNCH_KEEP_VOLUMES` Kconfig option.

## Risks And Test Signals
The comments note DataCrunch may automatically delete OS-NVMe volumes unless detached, so preserving only the cache may not guarantee actual volume reuse. Like apply, it hardcodes `terraform`. If `terraform output` fails, `instance_list` may be unset and cache clearing becomes incomplete. Tests should cover KEEP yes/no, absent output, destroy failure preserving cache, malformed output, multiple hostnames, and fake `volume_cache.py` calls.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/scripts/destroy_wrapper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/scripts/volume_cache.py -->
# sources/test-tools/kdevops/terraform/datacrunch/scripts/volume_cache.py

## Purpose
This Python CLI manages DataCrunch OS-NVMe volume ID mappings for faster reprovisioning. It stores per-host mappings keyed by kdevops host prefix.

## Important APIs, Types, And Functions
`get_cache_dir()` creates `~/.cache/kdevops/datacrunch`. `get_cache_file(prefix)` returns `<prefix>.yml`. `load_cache()` reads YAML and returns `{}` on missing file or read/parse error. `save_cache()` writes YAML. Command handlers `cmd_save`, `cmd_load`, `cmd_delete`, `cmd_list`, and `cmd_clear` implement the CLI subcommands. `main()` builds an argparse subcommand parser requiring `command`.

## Control Flow
Each subcommand loads or modifies one prefix file. `save` upserts a hostname-volume mapping. `load` prints the volume ID or exits 1. `delete` removes a hostname if present. `list` prints all mappings. `clear` unlinks the entire prefix file. The process exits with the handler's status.

## State And Persistence
Persistent state is YAML files under the user's home cache directory. Writes are direct and not atomic. There is no locking, so concurrent apply/destroy/cache operations can race.

## Dependencies And Integration Points
It depends on PyYAML and Python standard `argparse`, `pathlib`, `os`, and `sys`. It is invoked by DataCrunch apply/destroy wrappers and can be used manually for troubleshooting cache state.

## Risks And Test Signals
Direct YAML writes can corrupt cache files if interrupted. Prefix and hostname are accepted without validation, so unusual strings can create surprising filenames or mappings. Load errors are swallowed into empty cache, which can overwrite bad data on the next save. Tests should use a temporary HOME, exercise all subcommands, simulate invalid YAML, verify exit codes, and test concurrent write behavior if wrappers can run in parallel.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/datacrunch/scripts/volume_cache.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/Kconfig -->
# sources/test-tools/kdevops/terraform/gce/Kconfig

## Purpose
This Kconfig wrapper exposes GCE Terraform menus for resource location, machine type, OS image, storage, and identity/access when `TERRAFORM_GCE` is enabled.

## Important APIs, Types, And Functions
It sources generated files `Kconfig.location.generated`, `Kconfig.machine.generated`, and `Kconfig.image.generated`, plus static `Kconfig.storage` and `Kconfig.identity`. Compute is split into machine and OS image selection comments.

## Control Flow
The file is declarative and guarded by `if TERRAFORM_GCE`. Menu order is location, compute, storage, then identity/access.

## State And Persistence
Selected GCE symbols persist in Kconfig `.config` and generated Terraform/YAML configuration. The wrapper itself has no runtime state.

## Dependencies And Integration Points
It depends on GCE dynamic generation scripts to populate generated menus and on Terraform GCE modules consuming those symbols.

## Risks And Test Signals
Missing generated fragments can break menu rendering. GCE resource availability varies by project/zone, so stale machine/image menus can mislead users. Tests should run generator targets, menuconfig/olddefconfig, and Terraform variable generation for representative GCE configs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/gce_common.py -->
# sources/test-tools/kdevops/terraform/gce/scripts/gce_common.py

## Purpose
This module provides shared GCE helpers for Kconfig generators using direct Compute REST API calls with `google-auth` authorized sessions rather than the heavier `google-cloud-compute` SDK.

## Important APIs, Types, And Functions
`GceNotConfiguredError` marks optional auth absence. Constants define `GCE_COMPUTE_API` and `GCE_API_TIMEOUT`. `get_authenticated_session()` creates an OAuth-scoped `AuthorizedSession` and resolves project ID. `get_default_project()`, `get_default_region()`, and `get_default_zone()` read google-auth, environment variables, and gcloud config properties. `get_jinja2_environment()` enables Jinja loop controls. `load_yaml_config()` loads script-local YAML. Name helpers convert regions, zones, and machine types into Kconfig suffixes. REST list helpers include `list_regions()`, `list_zones()`, `list_machine_types()`, `list_machine_types_aggregated()`, `list_images()`, and `get_image_families()`. `require_gce_credentials()` wraps auth failures into `GceNotConfiguredError`.

## Control Flow
Generator scripts authenticate once, then pass the session and project to REST helpers. REST calls request limited fields, enforce a 30-second timeout, raise for most HTTP errors, and handle image-project 403/404 as empty lists. Pagination is handled for aggregated machine types and image lists. `get_image_families()` groups images by family, preferring non-deprecated and then newer images.

## State And Persistence
The module reads gcloud config, environment variables, and application-default credentials. It writes no files and maintains no cache. Remote GCE data is live state returned as plain dictionaries.

## Dependencies And Integration Points
It depends on `google-auth`, `requests`, `yaml`, `jinja2`, and Python typing/path/configparser modules. It is imported by GCE location, machine, and image generators. Generated outputs are sourced by `terraform/gce/Kconfig`.

## Risks And Test Signals
Project resolution can fail if application-default credentials lack a project and environment variables are unset. Direct REST calls require careful field selection and pagination; new API shapes can break assumptions. Image family selection compares ISO timestamp strings, which is acceptable for GCE timestamps but should be fixture-tested. Tests should mock authorized sessions for HTTP success, pagination, 403/404 image projects, auth failures, gcloud config reading, and Kconfig name conversion.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/gce_common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_image -->
# sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_image

## Purpose
This executable Python script discovers GCE public Linux image families for known publishers and renders OS-image Kconfig menus or raw publisher/image tables.

## Important APIs, Types, And Functions
`get_known_publishers()` loads `publisher_definitions.yml` with fallback to Debian and CentOS. `classify_family()` converts GCE image family names into version keys and friendly labels for Debian, CentOS/Stream, Ubuntu/minimal/LTS, Red Hat, Rocky, AlmaLinux, Fedora, openSUSE, SUSE/SLES, and Oracle while preserving architecture suffixes. `organize_images_by_publisher()` queries each publisher project in parallel, filters family names through configured regexes, classifies families, and returns nested publisher/version dictionaries. `output_images_kconfig()` renders `image_distributions.j2` and `image_publisher.j2`, sorts publishers by priority and versions numerically, and notes whether ARM64 images exist. Raw output functions list publishers or versions.

## Control Flow
`main()` can list publishers without credentials. Otherwise it filters publishers if requested, validates GCE credentials with optional skip-on-absent behavior, logs the project, organizes image families, exits 1 if none are found, and emits either Kconfig or raw output. For single-publisher Kconfig mode it still renders Kconfig for that subset.

## State And Persistence
The script writes generated output to stdout only. It reads publisher YAML definitions and live GCE image project data. Runtime state is an in-memory organized image mapping.

## Dependencies And Integration Points
It imports `gce_common.py`, uses REST API helpers through `requests` sessions, and renders Jinja templates from the GCE scripts directory. Its generated file is sourced by the GCE Kconfig wrapper.

## Risks And Test Signals
Classification is naming-convention dependent and can miss new image families. Publisher YAML absence reduces coverage to a fallback list. Parallel project queries may hide per-publisher failures behind warnings. Some families lack architecture metadata and default to x86. Tests should mock image families for every classification branch, verify regex filtering, check deprecated/newer selection via `gce_common`, assert no-credential exit 0, and render templates with ARM64 and x86 variants.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_image -->
