# subset-b-009258 research

Grouped research report for selected kdevops Ansible playbooks, roles, and helper scripts. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/steady_state/tasks/main.yaml -->
# sources/test-tools/kdevops/playbooks/roles/steady_state/tasks/main.yaml

Purpose: Ansible task list that prepares and runs an SSD steady-state workflow with `fio`, including optional whole-device prefill and IOPS/bandwidth steady-state jobs.

Important APIs/types/functions: uses `include_vars`, role `create_data_partition`, package install, `template` for `ss_iops.ini`/`ss_bw.ini`, `realpath`, `stat`, `/sys/block/*/queue/*`, `blockdev --getsize64`, arithmetic `set_fact` stages, `fio`, local `file`, and `fetch`.

Control flow: imports optional extra vars, creates the data partition and config directory, renders fio configs, resolves and validates `ssd_steady_state_device`, reads device geometry and capacity, computes effective block size and job distribution, validates alignment, runs aligned and remainder prefill jobs, runs the two steady-state jobs, then fetches results to `workflows/steady_state/results/<host>/`.

State/persistence behavior: installs `fio`, creates `steady_state_data`, may overwrite the target block device through prefill writes, produces JSON fio outputs on the target, and copies those artifacts to the controller. Facts such as `effective_blocksize`, `aligned_jobs`, and byte counts are transient Ansible state.

Dependencies/integration: depends on generated kdevops variables such as `kdevops_run_ssd_steady_state`, `ssd_steady_state_*`, `data_device`, and `topdir_path`, plus Linux sysfs/blockdev, root privileges, and the `create_data_partition` role.

Risks/test signals: destructive device writes are gated only by variable correctness and block-device validation. Alignment math and remainder handling are the main correctness risks. Test signals are Ansible syntax success, correct device geometry discovery, fio exit success, and non-empty `ss_iops.json`/`ss_bw.json` fetched to the controller.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/steady_state/tasks/main.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/sysbench/defaults/main.yml

Purpose: default variable set for the sysbench role, covering MySQL Docker mode, PostgreSQL native mode, filesystem formatting, benchmark sizing, telemetry paths, and durability toggles.

Important APIs/types/functions: exports Ansible defaults such as `sysbench_type_mysql_docker`, `sysbench_type_postgresql_native`, `sysbench_device`, `sysbench_fstype`, `sysbench_oltp_table_size`, `sysbench_threads`, container names/images, PostgreSQL source/PGDATA paths, and full-page-write/doublewrite controls.

Control flow: no executable flow; these defaults are consumed by `tasks/main.yaml`, database-specific task files, filesystem creation roles, templates, and plotting commands.

State/persistence behavior: defaults point persistent state at `/db`, `/data`, PostgreSQL source under `data_path`, telemetry under `/data/sysbench-telemetry`, and controller results under workflow paths created by task files.

Dependencies/integration: integrates Kconfig-generated overrides, inventory host naming for baseline/dev comparisons, Docker, MySQL, PostgreSQL, sysbench, and kdevops data partition roles.

Risks/test signals: unsafe defaults like `sysbench_device: /dev/null` prevent accidental device writes but must be overridden for real tests. Test signals are effective variable dumps in task output, generated database config files, and expected telemetry/result files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/debian/main.yml

Purpose: Debian-family package installation for sysbench workflows.

Important APIs/types/functions: uses optional `include_vars`, `apt update_cache`, and multiple `apt` package lists for Docker/MySQL, PostgreSQL build/runtime, sysbench, and Python plotting packages.

Control flow: loads optional extra vars, refreshes apt metadata, installs common Docker/sysbench dependencies when MySQL Docker mode is enabled, and installs PostgreSQL build/runtime/sysbench/plotting dependencies when PostgreSQL native mode is enabled.

State/persistence behavior: mutates system package state and apt cache. It does not create benchmark data directly.

Dependencies/integration: selected by `install-deps/main.yml` when `ansible_facts.os_family` is Debian. Depends on `sysbench_type_mysql_docker` and `sysbench_type_postgresql_native`.

Risks/test signals: package names are distro-version sensitive, especially PostgreSQL build libraries and Docker packages. Test signals are successful apt completion and later ability to build PostgreSQL, run Docker, run sysbench, and import plotting libraries.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/main.yml

Purpose: dispatcher for OS-specific sysbench dependency installation.

Important APIs/types/functions: includes role `pkg`, then conditionally includes `debian/main.yml`, `suse/main.yml`, or `redhat/main.yml` based on `ansible_facts.os_family`.

Control flow: runs generic package role first, then branches by normalized OS family.

State/persistence behavior: direct persistent changes are delegated to included package tasks.

Dependencies/integration: depends on gathered facts and role-relative task paths. It is included by sysbench role setup before database deployment.

Risks/test signals: unsupported or differently named OS families silently skip all OS-specific setup. Test signals are Ansible include selection and successful package availability after the branch.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/redhat/main.yml

Purpose: Red Hat-family dependency setup for sysbench, mainly enabling repositories and installing Docker/sysbench packages.

Important APIs/types/functions: includes `codereadyrepo`, installs `epel-release` when appropriate, and installs a `packages` list through `dnf`.

Control flow: enables CodeReady, optionally enables EPEL, then installs Docker and sysbench dependency packages.

State/persistence behavior: changes repository availability and system package state.

Dependencies/integration: selected by `install-deps/main.yml` for RedHat OS family. Depends on distro-specific repository roles/tasks and package manager metadata.

Risks/test signals: repository enabling can vary across RHEL, CentOS Stream, and clones. Test signals are dnf success and later Docker/sysbench command availability.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/suse/main.yml

Purpose: SUSE-family dependency setup for sysbench, including distribution facts and Docker tooling.

Important APIs/types/functions: sets SUSE/SLE facts, flags repository capability assumptions, and installs Docker tools through `zypper`.

Control flow: derives generic and SLE-specific release facts, decides whether repo-dependent features are available, then installs Docker-related packages when supported.

State/persistence behavior: changes Ansible facts and package state; no benchmark data is created.

Dependencies/integration: selected by sysbench dependency dispatcher for SUSE OS family. Feeds later MySQL Docker sysbench tasks.

Risks/test signals: SLE version detection and repository presence are fragile across SUSE variants. Test signals are successful zypper install and Docker runtime availability.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/main.yaml -->
# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/main.yaml

Purpose: top-level sysbench role dispatcher that prepares directories, dependencies, storage, and selects MySQL Docker or PostgreSQL native execution.

Important APIs/types/functions: optional `include_vars`, `file` directory creation, `include_tasks` for `install-deps`, role `create_data_partition`, and includes for `mysql-docker/main.yaml` and `postgresql-native/main.yaml`.

Control flow: imports extra vars, creates sysbench directories, installs dependencies, optionally creates the data partition, then branches into the selected database backend. A final debug/fail style guard handles unsupported configuration.

State/persistence behavior: creates local/remote directories and delegates package, filesystem, database, telemetry, and result persistence to included tasks.

Dependencies/integration: consumes defaults and Kconfig variables, uses `data_device`, `kdevops_baseline_and_dev`, and backend booleans. Integrates with `create_data_partition`.

Risks/test signals: conflicting backend booleans or missing storage variables can dispatch the wrong backend or skip required setup. Test signals are include selection, created directories, and backend-specific results.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/main.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/mysql-docker/main.yaml -->
# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/mysql-docker/main.yaml

Purpose: end-to-end MySQL-in-Docker sysbench workflow that formats a target device, starts MySQL and sysbench containers, populates and runs OLTP workload, gathers telemetry, and plots results.

Important APIs/types/functions: uses `set_fact` for A/B device and filesystem selection, Docker modules `community.docker.docker_container` and `docker_container_exec`, role `create_partition`, templates for MySQL client/server config, git clone of telemetry plugin, async sysbench execution, `async_status`, `fetch`, `journalctl`, debugfs extfrag files, and local Python plotting scripts.

Control flow: resolves per-host device, creates telemetry/root directories, derives filesystem command/page size/sector size, removes stale containers, unmounts and wipes target device, creates filesystem, toggles InnoDB doublewrite for baseline/dev modes, writes MySQL config, starts MySQL, verifies socket/client access, creates database user/grants, installs telemetry Python dependencies inside the container, starts a reusable sysbench container, populates the database, runs sysbench asynchronously while telemetry collection runs, waits for completion, collects logs and host kernel/memory signals, optionally cleans results, and generates per-node/A-vs-B/variance plots.

State/persistence behavior: destructive on `sysbench_device`; creates/mounts `sysbench_mnt`, Docker containers, `/data` MySQL/config/telemetry paths, controller result directories, and plot artifacts. It also writes config and metadata such as kernel version, doublewrite setting, and page size.

Dependencies/integration: depends on Docker, MySQL image/client, `severalnines/sysbench`, kdevops filesystem command variables, `create_partition`, `sysbench_db_*` credentials, and Python plotting scripts under `playbooks/python/workflows/sysbench`.

Risks/test signals: primary risks are destructive wipefs on the wrong device, fragile container readiness checks, credential exposure in task output, telemetry plugin/network dependency, and async polling duration. Test signals include successful MySQL socket checks, sysbench populate/run logs, `sysbench_tps.txt`, copied telemetry, dmesg/extfrag captures, and generated plots.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/mysql-docker/main.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/postgresql-native/main.yaml -->
# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/postgresql-native/main.yaml

Purpose: end-to-end native PostgreSQL sysbench workflow that builds PostgreSQL from source, formats a target device, initializes a database cluster, runs OLTP workload, gathers telemetry, and plots results.

Important APIs/types/functions: uses shell/git to resolve PostgreSQL ref, `ansible.builtin.git`, `nproc`, `community.general.make`, `user`, `stat`, `pg_ctl`, `initdb`, `psql`, role `create_partition`, PostgreSQL config template, sysbench command-line driver, `pg_controldata`, `fetch`, `journalctl`, debugfs extfrag files, and local sysbench plotting scripts.

Control flow: selects baseline/dev device, resolves and clones PostgreSQL, configures/builds/installs with requested block sizes, ensures PostgreSQL user and telemetry directory, stops existing server, derives filesystem options, wipes and recreates target filesystem, initializes PGDATA, toggles `full_page_writes`, renders config, records kernel/settings, starts PostgreSQL, creates user/database/grants, verifies write permission, populates with sysbench, runs benchmark, escalates PostgreSQL stop from smart to fast/immediate if needed, writes run and control data logs, gathers telemetry and kernel/memory signals, optionally cleans results, and generates plots.

State/persistence behavior: installs PostgreSQL under `/usr/local/pgsql`, creates or replaces `sysbench_mnt` data, writes PGDATA and logs, creates database users/databases, produces telemetry under `/data/sysbench-telemetry`, and copies outputs to controller result paths.

Dependencies/integration: depends on PostgreSQL build deps, sysbench PostgreSQL driver, generated filesystem variables, `create_partition`, `sysbench_postgresql_*` defaults, and A/B host naming conventions.

Risks/test signals: destructive device formatting, source build nondeterminism, changed_when expressions that compare result objects incorrectly, SQL grant mistakes, and stop escalation are key risks. Test signals are build/install success, `pg_ctl` start, permission test, populated tables, sysbench output, `pg_controldata`, copied telemetry, and plots.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/postgresql-native/main.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/defaults/main.yml

Purpose: default variable file for Terraform orchestration.

Important APIs/types/functions: defines `ssh_config_kexalgorithms` and `terraform_binary_path`.

Control flow: no executable flow; values are consumed by Terraform task files and SSH config templates/modules.

State/persistence behavior: no direct state. Defaults influence which Terraform binary is invoked and SSH template content.

Dependencies/integration: integrates with `cloud.terraform` modules, role task shell commands, and generated extra vars.

Risks/test signals: incorrect `terraform_binary_path` breaks every lifecycle task. Test signals are successful module calls and shell `terraform` invocations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/datacrunch.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/datacrunch.yml

Purpose: DataCrunch-specific Terraform bringup, including external provider installation, capacity-aware GPU instance selection, dev-overrides initialization, and apply with tier fallback.

Important APIs/types/functions: uses `set_fact`, `stat`, shell download/unzip of `terraform-provider-datacrunch`, helper scripts `datacrunch_select_tier.py` and `datacrunch_check_capacity.py`, `lineinfile` edits to `terraform.tfvars`, `terraform state list`, temporary Terraform provider config generation, and shell `terraform apply`.

Control flow: normalizes architecture, installs provider if missing, optionally resolves wildcard tier to instance/location, validates capacity, auto-selects location for explicit instance types, updates tfvars, skips apply when state already contains resources, initializes external provider around dev overrides by hiding real `.tf` files, then applies. For wildcard tiers the apply loop retries with lower-tier selections when capacity/provisioning fails.

State/persistence behavior: writes provider binaries under `~/.terraform.d/plugins`, mutates `terraform/<provider>/terraform.tfvars`, creates `.terraform` and `.terraform.lock.hcl`, and provisions cloud resources recorded in Terraform state.

Dependencies/integration: depends on GitHub releases, DataCrunch helper scripts/API credentials, Terraform CLI, provider-specific tfvars, `topdir_path`, and generated `terraform_datacrunch_*` variables.

Risks/test signals: high-risk mutations include editing tfvars in place, hiding/restoring Terraform files, and retrying cloud provisioning. Capacity checks are time-sensitive. Test signals are provider binary existence, successful state list/init, selected instance/location messages, Terraform apply success, and non-empty Terraform state.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/datacrunch.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/generic.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/generic.yml

Purpose: generic Terraform bringup for providers that do not need custom preflight logic.

Important APIs/types/functions: uses `cloud.terraform.terraform` with `terraform_binary_path`, `state: present`, and provider project path.

Control flow: one module invocation initializes/applies the provider directory.

State/persistence behavior: creates Terraform working directory metadata, state, and provider cloud resources.

Dependencies/integration: called by `bringup/main.yml` when provider is not Lambda Labs or DataCrunch. Depends on `cloud.terraform` collection and `topdir_path`.

Risks/test signals: generic path lacks provider-specific capacity or credential validation. Test signals are module success and active resources in Terraform state.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/generic.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/lambdalabs.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/lambdalabs.yml

Purpose: Lambda Labs-specific Terraform bringup with API key checks, wildcard tier selection, capacity probing, tfvars updates, and Terraform apply.

Important APIs/types/functions: `set_fact`, shell `scripts/lambdalabs_credentials.py check`, `lambdalabs_select_tier.py`, `lambdalabs_check_capacity.py`, inline Python for capacity response parsing, `fail`, `lineinfile`, and `cloud.terraform.terraform`.

Control flow: defines wildcard tiers, validates API key configuration, selects instance/region for wildcard tiers, validates output shape, writes selected instance and region to `terraform.tfvars`, computes resolved instance type, runs a capacity check for explicit selections, reports capacity failures, then invokes Terraform state-present apply.

State/persistence behavior: mutates `terraform/lambdalabs/terraform.tfvars`, reads local credential storage, and creates Terraform state/cloud instances.

Dependencies/integration: depends on Lambda Labs credentials helper, capacity/selection scripts, Terraform provider configuration, and generated variables such as `terraform_lambdalabs_instance_type` and `terraform_lambdalabs_region`.

Risks/test signals: API capacity is volatile; scripts must return exactly expected stdout formats. Test signals are credential check success, two-token tier selection output, tfvars update, and successful Terraform apply.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/lambdalabs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/main.yml

Purpose: provider dispatcher for Terraform bringup.

Important APIs/types/functions: conditional `include_tasks` for `lambdalabs.yml`, `datacrunch.yml`, or `generic.yml`.

Control flow: selects Lambda Labs tasks for `kdevops_terraform_provider == 'lambdalabs'`, DataCrunch tasks for `datacrunch`, and generic tasks otherwise.

State/persistence behavior: no direct state except delegated provider bringup side effects.

Dependencies/integration: driven by generated `kdevops_terraform_provider`.

Risks/test signals: provider string drift routes to generic path and bypasses required custom validation. Test signals are correct include path and provider-specific status output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/common/ssh-config.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/common/ssh-config.yml

Purpose: generates controller SSH config entries for Terraform-provisioned nodes.

Important APIs/types/functions: uses `cloud.terraform.terraform_output` for `controller_ip_map`, `blockinfile` with `ssh_config.j2`, and a second `blockinfile` to add `Include {{ kdevops_ssh_config_prefix }}*` to `~/.ssh/config`.

Control flow: retrieves the Terraform output map, loops over host/IP entries to write managed SSH host blocks into `kdevops_ssh_config`, then ensures the user's main SSH config includes the generated files.

State/persistence behavior: mutates SSH config files on the controller and depends on Terraform output state.

Dependencies/integration: depends on Terraform output `controller_ip_map`, template `ssh_config.j2`, variables `kdevops_ssh_config`, `kdevops_ssh_config_prefix`, and OpenSSH include semantics.

Risks/test signals: malformed Terraform output or template variables can write unusable SSH entries. Test signals are generated host blocks, include directive presence, and successful SSH to provisioned nodes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/common/ssh-config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/common/status.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/common/status.yml

Purpose: reports current Terraform resource and controller IP status.

Important APIs/types/functions: block with `cloud.terraform.terraform_output`, `meta: end_play`, shell `terraform state list`, and debug output.

Control flow: reads `controller_ip_map`; if Terraform state is empty or missing it ends the play; otherwise counts resources via `terraform state list` and displays resource count plus IP map.

State/persistence behavior: read-only against Terraform state.

Dependencies/integration: included after bringup/status operation by Terraform role; depends on Terraform CLI and output state.

Risks/test signals: warning-based empty-state detection can miss some failure modes. Test signals are displayed active resource count and controller IP map.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/common/status.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/datacrunch.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/datacrunch.yml

Purpose: DataCrunch-specific Terraform destroy that works around dev-overrides provider initialization.

Important APIs/types/functions: shell block hides DataCrunch resource `.tf` files, creates minimal provider config, runs `terraform init`, restores files/lockfile, runs `terraform destroy -auto-approve -no-color`, and removes `.terraform.lock.hcl`.

Control flow: initializes external provider with the workaround, destroys resources, then deletes the lock file.

State/persistence behavior: destroys cloud resources, mutates Terraform working files temporarily, rewrites lock file, and removes the final lock file.

Dependencies/integration: depends on DataCrunch Terraform provider behavior and `topdir_path` provider directory.

Risks/test signals: temporary file hiding/restoration is fragile if interrupted; auto-approve is intentionally destructive. Test signals are successful destroy exit, empty Terraform state, and restored `.tf` files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/datacrunch.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/generic.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/generic.yml

Purpose: generic Terraform destroy for providers without custom teardown.

Important APIs/types/functions: `cloud.terraform.terraform` with `state: absent`.

Control flow: one module invocation destroys resources in the provider project path.

State/persistence behavior: destroys cloud infrastructure and updates Terraform state.

Dependencies/integration: called by destroy dispatcher for non-DataCrunch providers.

Risks/test signals: destructive action depends entirely on correct provider directory and state. Test signals are module success and empty state.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/generic.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/main.yml

Purpose: top-level Terraform teardown dispatcher.

Important APIs/types/functions: removes ephemeral SSH config file with `file`, then includes DataCrunch or generic destroy tasks based on provider.

Control flow: deletes `kdevops_ssh_config`, dispatches DataCrunch-specific destroy for DataCrunch, otherwise generic destroy.

State/persistence behavior: removes controller SSH config and destroys cloud resources via included tasks.

Dependencies/integration: depends on `kdevops_ssh_config` and `kdevops_terraform_provider`.

Risks/test signals: removes SSH config before destroy, which can complicate manual access if destroy fails. Test signals are missing generated SSH config and empty Terraform state.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/main.yml

Purpose: Terraform role action dispatcher for bringup, SSH configuration, status, and destroy.

Important APIs/types/functions: conditionally includes `bringup/main.yml`, `common/ssh-config.yml`, `common/status.yml`, and `destroy/main.yml`.

Control flow: chooses an include based on lifecycle booleans such as bringup/status/destroy variables generated by kdevops configuration.

State/persistence behavior: no direct state; included files provision, destroy, or report Terraform resources and mutate SSH config.

Dependencies/integration: invoked by `playbooks/terraform.yml` on localhost and depends on generated lifecycle variables.

Risks/test signals: mutually conflicting lifecycle booleans can run unexpected includes. Test signals are only the selected lifecycle task side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/terraform/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/update_etc_hosts/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/update_etc_hosts/defaults/main.yml

Purpose: default booleans for host-file update behavior.

Important APIs/types/functions: defines `terraform_private_net_enabled: false` and `kdevops_enable_guestfs: false`.

Control flow: no executable flow; these defaults control conditionals in the role tasks.

State/persistence behavior: no direct state.

Dependencies/integration: consumed by `tasks/main.yml` and overridden by generated config for Terraform private networks or guestfs.

Risks/test signals: wrong defaults/overrides select public vs private IP handling. Test signal is resulting `/etc/hosts` line content.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/update_etc_hosts/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/update_etc_hosts/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/update_etc_hosts/tasks/main.yml

Purpose: updates each target node's `/etc/hosts` with peer hosts and disables cloud-init host management when present.

Important APIs/types/functions: optional `include_vars`, `wait_for_connection`, `setup` network subset, `set_fact`, `stat`, `lineinfile`, `ansible.utils.ipaddr`, `hostvars`, and `ansible_play_hosts_all`.

Control flow: imports extra vars, waits for connectivity, gathers network facts, builds private network CIDR when enabled, builds peer-host list excluding current host, disables cloud-init management, writes peer host entries using private-network-filtered IPs or first IPv4 address, and fixes Debian guestfs unassigned-hostname line.

State/persistence behavior: mutates `/etc/cloud/cloud.cfg.d/99-kdevops-manage-net-disable` and `/etc/hosts` on target nodes.

Dependencies/integration: depends on inventory hostvars, network facts, `terraform_private_net_prefix/mask`, `ansible.utils` collection, NixOS/guestfs flags, and sudo.

Risks/test signals: `first` IP selection can pick the wrong interface; private-network filtering can fail if addresses are missing. Test signals are idempotent lineinfile output and resolvable peer hostnames.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/update_etc_hosts/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/update_ssh_config_guestfs/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/update_ssh_config_guestfs/tasks/main.yml

Purpose: manages the controller user's OpenSSH config include directive for guestfs-generated kdevops SSH configs.

Important APIs/types/functions: `stat`, `lineinfile` in check mode, `meta: end_play`, `replace`, `blockinfile`, and `file`.

Control flow: checks for `~/.ssh/config`, detects whether the current include and `kdevops_version` comment already exist, exits early when fixed, removes stale include/comment/blank lines otherwise, inserts a managed include block at the beginning, and ensures permissions.

State/persistence behavior: mutates `~/.ssh/config` on localhost and can remove broad lines matching kdevops comments/includes.

Dependencies/integration: depends on `kdevops_version` and OpenSSH include behavior.

Risks/test signals: regex removal may delete user comments containing `kdevops`; replacing all blank lines can compact user formatting. Test signals are a single managed include block and mode `0600`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/update_ssh_config_guestfs/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/defaults/main.yml

Purpose: default vLLM role values for production-stack source, local paths, results directory, and image selections.

Important APIs/types/functions: defines `vllm_production_stack_repo`, `vllm_production_stack_version`, `vllm_local_path`, `vllm_results_dir`, CPU/GPU-aware `vllm_engine_image_repo/tag`, and router image defaults.

Control flow: no executable flow; defaults drive Docker, Kubernetes, Helm, and bare-metal task files.

State/persistence behavior: path defaults direct state to `/data/vllm` and `/data/vllm-benchmark`.

Dependencies/integration: consumed by vLLM deployment templates and tasks; image defaults assume vLLM CPU image for CPU inference and upstream GPU image otherwise.

Risks/test signals: `latest` tags and image compatibility can drift. Test signals are resolved image names in deployment output and successful pod/container startup.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/cleanup-bare-metal.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/cleanup-bare-metal.yml

Purpose: cleanup routine for vLLM bare-metal and related local runtime artifacts.

Important APIs/types/functions: `systemd`, `file`, shell Docker commands, minikube stop/delete commands, and cleanup flags `vllm_cleanup_remove_binaries`/`vllm_cleanup_remove_data`.

Control flow: stops/removes the vLLM service and unit file, reloads systemd, stops/removes vLLM containers and images, stops/deletes minikube, optionally removes kubectl/minikube/helm binaries, optionally removes data directories, then reports completion.

State/persistence behavior: deletes systemd unit, containers/images, Kubernetes local cluster state, binaries, and data directories depending on flags.

Dependencies/integration: used by vLLM cleanup/teardown paths; depends on Docker, minikube, systemd, and root privileges for system paths.

Risks/test signals: shell Docker filters can remove more than intended if names/images match broadly; data cleanup is destructive. Test signals are absent service/container/image/minikube resources and idempotent rerun success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/cleanup-bare-metal.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/configure-docker-data.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/configure-docker-data.yml

Purpose: configures Docker to use `/data/docker`, optionally adds a registry mirror, migrates existing Docker data, and prepares vLLM/minikube data directories.

Important APIs/types/functions: `file`, `stat`, `slurp`, `from_json`, `set_fact`, mirror auto-detection through `/mirror/docker/registry` and IP curl, `copy` to `/etc/docker/daemon.json`, `systemd`, shell `mv`, and directory creation.

Control flow: creates `/data/docker`, reads or initializes `daemon.json`, detects Docker mirror path or HTTP endpoint, merges `data-root` and optional `registry-mirrors`, writes daemon config, stops Docker if changed, moves existing `/var/lib/docker` content to `/data/docker`, removes empty old directory, restarts/enables Docker, and creates minikube/vLLM directories.

State/persistence behavior: mutates `/etc/docker/daemon.json`, Docker service state, Docker data root, `/var/lib/docker`, `/data/docker`, `/data/minikube`, and vLLM data directories.

Dependencies/integration: included for Docker and production-stack vLLM deployments. Depends on Docker service, mirror variables, and systemd.

Risks/test signals: Docker data migration can fail or leave split state if interrupted; JSON merge must preserve existing daemon options. Test signals are valid daemon JSON, Docker restart success, `docker info` data root, and created `/data` directories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/configure-docker-data.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-bare-metal.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-bare-metal.yml

Purpose: deploys vLLM as a systemd-managed bare-metal service, either containerized or directly installed in a Python virtual environment.

Important APIs/types/functions: Ansible block, `file`, `command`/`uri`, GPU detection via `nvidia-smi`, `set_fact`, Docker service/user/group tasks, `nvidia-container-toolkit`, `nvidia-ctk`, image pull with mirror fallback, service templates, Python venv/pip/git source install, systemd reload/restart/start, health check, and model listing.

Control flow: creates directories, detects GPU availability, branches to container runtime or direct install, configures Docker/GPU runtime if needed, selects and pulls image, writes container service unit or direct service unit, optionally writes config file, reloads systemd, restarts if unit/config changed, starts/enables service, waits for `/health`, queries `/v1/models`, and displays endpoint info.

State/persistence behavior: creates `/opt`/data directories, installs packages or Python env, pulls images, writes systemd unit/config files, and runs persistent service.

Dependencies/integration: depends on templates, vLLM image/source variables, Docker or Python/pip/git, NVIDIA tooling when GPU is present, and `vllm_bare_metal_*` variables.

Risks/test signals: GPU runtime setup and image mirror fallback are fragile; direct pip/source install may drift. Test signals are systemd active state, health endpoint response, model API response, and successful image/venv installation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-bare-metal.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-docker.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-docker.yml

Purpose: deploys a basic vLLM Kubernetes manifest using Docker/minikube or an existing Kubernetes environment.

Important APIs/types/functions: Docker service/group/permission tasks, `include_tasks: setup-kubernetes.yml`, `file`, image mirror `set_fact`, manifest `template`, `kubectl apply`, `kubernetes.core.k8s_info`, and service endpoint reporting.

Control flow: ensures Docker is running and current user can access it, sets up Kubernetes when requested, creates local/results directories, resolves image path with optional mirror, renders deployment manifest, applies it with kubectl, waits for pods by label, reads `vllm-service`, and displays endpoint information.

State/persistence behavior: mutates Docker group/socket permissions, creates Kubernetes resources, writes manifest under local vLLM path, and creates result directories.

Dependencies/integration: depends on Docker, kubectl, Kubernetes/minikube setup, templates, `kubernetes.core`, and image variables.

Risks/test signals: chmodding Docker socket is broad; Kubernetes namespace/context assumptions can misdeploy. Test signals are `kubectl apply` changed/created output, ready pods, and service info.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-docker.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-production-stack.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-production-stack.yml

Purpose: deploys vLLM Production Stack through Helm on minikube or an existing Kubernetes cluster, with optional monitoring and autoscaling.

Important APIs/types/functions: includes Kubernetes and Helm setup, `kubernetes.core.helm_repository`, `helm`, `k8s` namespace/HPA resources, template/copy of Helm values, `kubectl cluster-info`, `k8s_info` waits for pods/deployments/services, and monitoring/autoscaling conditionals.

Control flow: sets up Kubernetes and Helm, sets default engine/router images, adds and updates Helm repo, verifies cluster connectivity, optionally switches context, creates local directory and namespace, writes values file, deploys Helm release, waits for engine/router readiness, checks/sets up monitoring components, gathers service endpoints, and optionally creates HPA.

State/persistence behavior: creates namespace, Helm repo cache/release, Kubernetes deployments/services/pods, optional Prometheus/Grafana resources, local values files, and HPA.

Dependencies/integration: depends on vLLM Production Stack chart, Helm, kubectl, `kubernetes.core`, image variables, namespace/release variables, and GPU/CPU inference settings.

Risks/test signals: chart values and image tags may drift; become handling differs for minikube vs existing clusters. Test signals are Helm release success, ready engine/router pods, service list, and monitoring/HPA resources when enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-production-stack.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/debian/main.yml

Purpose: installs Debian-family dependencies for vLLM Docker/Kubernetes benchmarking.

Important APIs/types/functions: `apt` update, `dpkg-query` for docker-ce detection, package installs with or without `docker.io`, Python development/benchmark/Kubernetes packages, and user group modification.

Control flow: refreshes apt, checks whether Docker CE is already installed, installs system dependencies with Docker only if needed, installs Python build and benchmarking packages, installs Python Kubernetes client, and adds current user to Docker group.

State/persistence behavior: changes apt package state and user group membership.

Dependencies/integration: selected by vLLM install dispatcher for Debian OS family.

Risks/test signals: mixing Docker CE and distro Docker packages can conflict; group membership needs reconnect. Test signals are package install success, Docker command availability, and Python imports.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/main.yml

Purpose: vLLM OS-specific dependency dispatcher.

Important APIs/types/functions: includes role `pkg`, then includes Debian, SUSE, or RedHat task files based on `ansible_facts.os_family`.

Control flow: generic package setup first, then distro branch.

State/persistence behavior: delegated to package tasks.

Dependencies/integration: used early in vLLM role main flow.

Risks/test signals: unsupported OS family means no dependencies installed. Test signals are selected include and later deployment prerequisites.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/redhat/main.yml

Purpose: installs Red Hat-family vLLM dependencies with yum/dnf split for old vs newer releases.

Important APIs/types/functions: `yum`/`dnf` package installs for Docker/system tools, Python development packages, benchmarking libraries, and Python Kubernetes client.

Control flow: branches on `ansible_distribution_major_version <= 7` for yum package sets and `>= 8` for dnf package sets across system, development, benchmarking, and Kubernetes client packages.

State/persistence behavior: changes system package state.

Dependencies/integration: selected by vLLM install dispatcher for RedHat OS family.

Risks/test signals: package names differ across RHEL clones and EPEL availability. Test signals are package install success, Docker availability, Python venv/pip and Kubernetes client imports.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/suse/main.yml

Purpose: installs SUSE-family dependencies for vLLM.

Important APIs/types/functions: zypper/package installs for Docker/system tools, Python development, benchmark packages, and Kubernetes Python client.

Control flow: sequential package groups are installed without further branching.

State/persistence behavior: changes package state.

Dependencies/integration: selected by vLLM install dispatcher for SUSE OS family.

Risks/test signals: package naming/repo availability is the key SUSE risk. Test signals are successful package installation and later Docker/Python/Kubernetes operations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/main.yml

Purpose: top-level vLLM workflow dispatcher for setup, deployment, benchmarking, monitoring, cleanup, results collection, and visualization.

Important APIs/types/functions: roles `create_data_partition` and `docker_mirror_9p`, `set_fact`, includes for install deps, Docker data config, Docker/production-stack/bare-metal deployments, benchmark script template, async port forwarding, benchmark command, `k8s`/`helm` cleanup, `fetch`, and visualization template/command.

Control flow: prepares data/mirror roles, sets workflow variables, installs dependencies, configures Docker data root for Docker-like deployments, branches to selected deployment type, optionally runs benchmarks with port-forwarding when needed, reports monitoring endpoints, performs cleanup/teardown when requested, collects result and system-info files, and optionally generates HTML visualization.

State/persistence behavior: delegates deployment state to Docker/Kubernetes/systemd tasks, creates benchmark scripts/results under vLLM paths, may delete Kubernetes resources or bare-metal services, and fetches results to the controller.

Dependencies/integration: depends on vLLM defaults, deployment type variables, templates, Kubernetes/Helm/Docker/systemd tasks, and generated kdevops workflow flags.

Risks/test signals: many flags share one task file, so conflicting deploy/cleanup/result modes can produce surprising behavior. Test signals are selected include output, benchmark JSON/results, service endpoints, fetched artifacts, and visualization HTML.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/setup-helm.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/setup-helm.yml

Purpose: installs Helm if missing and verifies it.

Important APIs/types/functions: `stat`, `get_url` for installer script, command execution of installer, `helm version`, and debug output.

Control flow: checks for `/usr/local/bin/helm`, downloads and runs installer only when absent, verifies version, and displays it.

State/persistence behavior: writes Helm binary and temporary installer script.

Dependencies/integration: included by production-stack deployment; depends on network access to Helm installer and root privileges to install.

Risks/test signals: remote installer execution and version drift are risks. Test signals are `helm version` success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/setup-helm.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/setup-kubernetes.yml -->
# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/setup-kubernetes.yml

Purpose: installs kubectl/minikube/crictl as needed and prepares either minikube or an existing Kubernetes cluster for vLLM.

Important APIs/types/functions: `stat`, shell/curl version discovery, downloads/install commands, veth kernel config/module checks, Docker socket permission, user/group tasks, file/sysctl setup, `minikube start/status/addons`, `kubectl cluster-info`, and GPU resource checks.

Control flow: installs kubectl if missing; for minikube, installs minikube and crictl, validates Docker/veth support, cleans stopped minikube containers, fixes permissions and sysctl, ensures kdevops Docker group and `/data/minikube`, starts minikube with configured resources, waits ready, and enables addons. For existing clusters, verifies connectivity and optionally checks GPU resources.

State/persistence behavior: writes binaries under `/usr/local/bin`, changes Docker socket permissions/group membership, writes `/data/minikube`, sets sysctl, creates or modifies minikube cluster, and changes Kubernetes context/state.

Dependencies/integration: included by Docker and production-stack vLLM deployments. Depends on Docker, kernel veth support, minikube/kubectl networks, and kdevops user assumptions.

Risks/test signals: broad Docker socket permissions, kernel-module assumptions, and remote latest-version downloads are risks. Test signals are `kubectl cluster-info`, minikube ready state, enabled addons, and detected GPU resources when required.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/vllm/tasks/setup-kubernetes.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/volume_group/defaults/main.yml

Purpose: defaults for LVM volume group provisioning.

Important APIs/types/functions: defines guestfs/Terraform booleans, `physical_volumes`, `ebs_volume_ids`, and `tmp_device`.

Control flow: no executable flow; values seed provider-specific enumeration and final LVM creation.

State/persistence behavior: no direct state.

Dependencies/integration: consumed by `tasks/main.yml` and provider/guestfs task files.

Risks/test signals: empty `physical_volumes` is expected initially but must be populated before LVM creation. Test signal is final list content.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/guestfs.yml -->
# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/guestfs.yml

Purpose: discovers extra guestfs/libvirt block devices to use as LVM physical volumes while excluding root and `/data`.

Important APIs/types/functions: `set_fact` for device ID patterns, `fail`, `debug`, `find` under `/dev/disk/by-id`, and looped `set_fact` appending to `physical_volumes`.

Control flow: selects a by-id pattern based on configured bus type, fails if unsupported, reports reserved data device, finds matching symlinks excluding partitions and the data device, and appends found paths.

State/persistence behavior: only updates Ansible `physical_volumes`; LVM mutation happens later.

Dependencies/integration: included by volume group main when `kdevops_enable_guestfs` is true. Depends on libvirt extra storage variables and stable `/dev/disk/by-id` naming.

Risks/test signals: wrong pattern/exclusion can select the wrong disk. Test signals are discovered symlink list and final LVM creation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/guestfs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/main.yml

Purpose: creates an LVM volume group from provider-discovered extra block devices.

Important APIs/types/functions: `gather_facts` hardware subset, package install `lvm2`, conditional includes for guestfs or Terraform provider tasks, `fail`, and `community.general.lvg`.

Control flow: gathers hardware facts, installs LVM support, enumerates devices through guestfs or Terraform provider-specific tasks, fails if no candidates remain, and creates the requested volume group.

State/persistence behavior: installs `lvm2` and writes LVM metadata to selected physical volumes and volume group.

Dependencies/integration: depends on `volume_group_name`, `physical_volumes`, provider variables, root privileges, and `community.general`.

Risks/test signals: destructive LVM metadata on wrong devices is the primary risk. Test signals are non-empty `physical_volumes` and successful `vgs`/`lvs` visibility.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/aws.yml -->
# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/aws.yml

Purpose: discovers AWS EBS devices attached for kdevops as LVM candidates.

Important APIs/types/functions: `find` under `/dev/disk/kdevops` and `set_fact` extracting link paths.

Control flow: finds symlinks excluding the data device basename, then sets `physical_volumes` to those paths.

State/persistence behavior: only Ansible fact mutation; no disk writes here.

Dependencies/integration: relies on a udev rule creating stable `/dev/disk/kdevops` links for EBS volumes.

Risks/test signals: missing udev links or incorrect data-device exclusion can select wrong volumes. Test signal is stable repeatable `physical_volumes` list.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/aws.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/azure.yml -->
# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/azure.yml

Purpose: discovers Azure managed disks to use as LVM physical volumes.

Important APIs/types/functions: `find` under `/dev/disk/azure/scsi1` and looped `set_fact`.

Control flow: enumerates managed disk symlinks and appends all paths except `data_device` to `physical_volumes`.

State/persistence behavior: Ansible fact mutation only.

Dependencies/integration: relies on Azure disk symlink layout and `data_device` being comparable to found paths.

Risks/test signals: path mismatch between `data_device` and Azure symlink can fail exclusion. Test signal is expected device list before LVM creation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/azure.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/gce.yml -->
# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/gce.yml

Purpose: discovers Google Compute Engine persistent disks to use as LVM physical volumes.

Important APIs/types/functions: regex `find` under `/dev/disk/by-id` and looped `set_fact`.

Control flow: finds `google-persistent-disk-N` symlinks, excludes the data device and root disk `google-persistent-disk-0`, and appends the rest.

State/persistence behavior: Ansible fact mutation only.

Dependencies/integration: relies on GCE persistent disk naming conventions and `data_device`.

Risks/test signals: hard-coded root/data assumptions can fail if disk numbering changes. Test signal is deterministic candidate list.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/gce.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/oci.yml -->
# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/oci.yml

Purpose: discovers Oracle Cloud block volumes to use as LVM candidates while excluding root and data devices.

Important APIs/types/functions: `stat` of `/dev/oracleoci/oraclevda` and `data_device`, `set_fact` parsing `lnk_source`, and iteration over `ansible_devices`.

Control flow: resolves root device name, resolves data device name, then appends `/dev/<device>` for `ansible_devices` entries whose model is `BlockVolume` and not root/data.

State/persistence behavior: Ansible fact mutation only.

Dependencies/integration: depends on OCI device symlinks and gathered hardware facts.

Risks/test signals: `lnk_source.split('/dev/').1` is brittle if stat output shape changes. Test signals are correct root/data exclusion and non-empty extra volume list.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/oci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/rxe.yml -->
# sources/test-tools/kdevops/playbooks/rxe.yml

Purpose: wrapper playbook for configuring software-emulated RoCE RDMA over Ethernet.

Important APIs/types/functions: targets `baseline:dev` and invokes role `rxe`.

Control flow: Ansible selects baseline/dev hosts and transfers execution to the role.

State/persistence behavior: delegated to role `rxe`, likely udev/module/network configuration.

Dependencies/integration: integrates with kdevops inventory host groups and RDMA role.

Risks/test signals: wrapper risk is host group or role-name drift. Test signals are Ansible role discovery and resulting rxe device/module state.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/rxe.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/scripts/workflows/fstests/sort-expunges.sh -->
# sources/test-tools/kdevops/playbooks/scripts/workflows/fstests/sort-expunges.sh

Purpose: normalizes fstests expunge `.txt` files by sorting and deduplicating entries in a supplied directory tree.

Important APIs/types/functions: Bash argument parsing, `find $DIR -name *.txt`, symlink skip check, `sort`, `uniq`, and `mv`.

Control flow: validates one argument/help, ensures the argument is a directory, finds text files, skips symlinks, writes sorted unique content to `<file>.tmp`, then replaces the original.

State/persistence behavior: rewrites every non-symlink `.txt` file under the supplied directory.

Dependencies/integration: used by fstests workflow scripts to keep expunge lists stable.

Risks/test signals: unquoted variables can break on spaces; tmp file replacement is not trap-protected. Test signals are sorted unique file contents and unchanged symlinks.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/scripts/workflows/fstests/sort-expunges.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/selftests.yml -->
# sources/test-tools/kdevops/playbooks/selftests.yml

Purpose: wrapper playbook to configure and run Linux kernel selftests.

Important APIs/types/functions: targets `baseline:dev` and invokes role `selftests`.

Control flow: hands execution to the role after host selection.

State/persistence behavior: delegated to `selftests` role.

Dependencies/integration: integrates with baseline/dev kdevops workflow.

Risks/test signals: wrapper-level risk is role or inventory drift. Test signals are role execution and selftest result artifacts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/selftests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/siw.yml -->
# sources/test-tools/kdevops/playbooks/siw.yml

Purpose: wrapper playbook for software-emulated iWARP RDMA over TCP/IP setup.

Important APIs/types/functions: targets `baseline:dev` and invokes role `siw`.

Control flow: host selection then role execution.

State/persistence behavior: delegated to `siw`, likely udev/module/network changes.

Dependencies/integration: integrates with RDMA testing workflows.

Risks/test signals: wrapper risk is limited to host/role naming. Test signal is successful role execution and siw interface/module state.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/siw.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/smbd.yml -->
# sources/test-tools/kdevops/playbooks/smbd.yml

Purpose: wrapper playbook to set up a Samba server with shared volume and system integration.

Important APIs/types/functions: targets host group `smbd` and invokes role `smbd`.

Control flow: selects Samba hosts then delegates to the role.

State/persistence behavior: delegated to Samba role, likely packages, services, shares, and storage.

Dependencies/integration: depends on `smbd` inventory group and role availability.

Risks/test signals: wrong inventory targeting can configure unintended hosts. Test signals are Samba service and share availability.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/smbd.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/steady_state.yml -->
# sources/test-tools/kdevops/playbooks/steady_state.yml

Purpose: wrapper playbook for the steady-state storage workflow.

Important APIs/types/functions: targets `all` and invokes role `steady_state`.

Control flow: all inventory hosts run the role.

State/persistence behavior: delegated to steady_state role, including possible destructive device prefill and result collection.

Dependencies/integration: integrates with generated steady-state variables and inventory.

Risks/test signals: broad `hosts: all` means variable gating must prevent accidental device writes. Test signals are role outputs under workflow results.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/steady_state.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/sysbench.yml -->
# sources/test-tools/kdevops/playbooks/sysbench.yml

Purpose: wrapper playbook for sysbench database benchmark workflow.

Important APIs/types/functions: targets `baseline:dev` and invokes role `sysbench`.

Control flow: selects benchmark hosts and delegates setup/run/collection to sysbench role.

State/persistence behavior: delegated to sysbench role, including package installs, filesystem formatting, database state, telemetry, and results.

Dependencies/integration: depends on baseline/dev groups and role variables.

Risks/test signals: wrapper risk is host group drift. Test signals are sysbench role result artifacts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/sysbench.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/terraform.yml -->
# sources/test-tools/kdevops/playbooks/terraform.yml

Purpose: wrapper playbook for Terraform infrastructure lifecycle and SSH access management.

Important APIs/types/functions: targets `localhost` and invokes role `terraform`.

Control flow: executes Terraform role locally for bringup/status/destroy operations.

State/persistence behavior: delegated to Terraform role, including cloud resources, Terraform state, and local SSH config.

Dependencies/integration: depends on localhost controller environment, Terraform binary, cloud credentials, and role variables.

Risks/test signals: local controller mutations and cloud resource cost/destruction are the major risks. Test signals are Terraform state and SSH config output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/terraform.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/update_etc_hosts.yml -->
# sources/test-tools/kdevops/playbooks/update_etc_hosts.yml

Purpose: wrapper playbook that updates target `/etc/hosts` entries and disables cloud-init host management.

Important APIs/types/functions: targets `all:!localhost`, disables initial fact gathering, and invokes `update_etc_hosts`.

Control flow: role handles connectivity wait and fact gathering internally.

State/persistence behavior: delegated to role, mutating `/etc/hosts` and cloud-init config on targets.

Dependencies/integration: depends on inventory hostvars and network facts.

Risks/test signals: excludes localhost but affects every target. Test signals are resolvable hostnames and idempotent `/etc/hosts` changes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/update_etc_hosts.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/update_ssh_config_guestfs.yml -->
# sources/test-tools/kdevops/playbooks/update_ssh_config_guestfs.yml

Purpose: wrapper playbook that updates the controller OpenSSH config for libguestfs kdevops environments.

Important APIs/types/functions: targets `localhost` and invokes `update_ssh_config_guestfs`.

Control flow: delegates to role tasks.

State/persistence behavior: mutates `~/.ssh/config` on the controller.

Dependencies/integration: depends on guestfs-generated SSH config naming.

Risks/test signals: can alter user SSH config. Test signal is correct include directive and SSH connectivity.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/update_ssh_config_guestfs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/update_ssh_config_nixos.yml -->
# sources/test-tools/kdevops/playbooks/update_ssh_config_nixos.yml

Purpose: standalone playbook that generates a kdevops SSH key and SSH config entries for NixOS VMs.

Important APIs/types/functions: `file`, `stat`, `ssh-keygen`, permission setting, shell `virsh list`, and `blockinfile` into `{{ topdir_path }}/.ssh/config`.

Control flow: creates `.ssh`, checks/generates RSA key, sets key permissions, lists libvirt VM names matching the host prefix or `nixos`, and writes an Ansible-managed SSH config block for each VM using hostvars/default IP.

State/persistence behavior: creates `topdir_path/.ssh/kdevops_id_rsa(.pub)` and mutates `topdir_path/.ssh/config`.

Dependencies/integration: depends on libvirt `virsh`, `libvirt_uri`, `kdevops_host_prefix`, `topdir_path`, and hostvars for VM addresses.

Risks/test signals: defaulting HostName to `192.168.100.2` can create wrong entries if hostvars are missing; key generation is not hashed per directory. Test signals are generated key/config and successful SSH to NixOS VMs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/update_ssh_config_nixos.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/vllm.yml -->
# sources/test-tools/kdevops/playbooks/vllm.yml

Purpose: wrapper playbook for deploying and managing vLLM Production Stack or related deployment modes.

Important APIs/types/functions: targets `baseline:dev`, escalates with sudo, sets `ansible_ssh_pipelining`, conditionally runs `create_data_partition`, then role `vllm`.

Control flow: creates data partition when a data device is configured, then delegates deployment/benchmark/cleanup to vLLM role.

State/persistence behavior: delegated to data partition and vLLM roles, including Docker/Kubernetes/systemd/data/result state.

Dependencies/integration: depends on inventory groups, `data_device`, and vLLM generated variables.

Risks/test signals: data partition role may format storage before vLLM tasks. Test signals are successful role deployment and benchmark artifacts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/vllm.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/pyproject.toml -->
# sources/test-tools/kdevops/pyproject.toml

Purpose: project-level tool configuration for codespell.

Important APIs/types/functions: `[tool.codespell]` config sets builtins, summary behavior, ignored words `iam,master`, and `write-changes`.

Control flow: no runtime flow; consumed by codespell.

State/persistence behavior: `write-changes` enables codespell to modify files when run with this config.

Dependencies/integration: integrates with developer/CI spell-check tooling.

Risks/test signals: ignored words can hide real typos; write-changes can dirty worktrees. Test signal is successful codespell run with expected ignore list.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/pyproject.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/requirements.yml -->
# sources/test-tools/kdevops/requirements.yml

Purpose: Ansible Galaxy collection requirements for kdevops playbooks.

Important APIs/types/functions: declares `ansible.posix`, `ansible.utils`, `cloud.terraform`, `community.docker`, `community.general`, and `community.libvirt`.

Control flow: no runtime flow; consumed by `ansible-galaxy collection install`.

State/persistence behavior: installs collections into the Ansible collection path.

Dependencies/integration: required by roles using ipaddr filters, Terraform modules, Docker modules, LVM modules, and libvirt modules.

Risks/test signals: unpinned collection versions may drift. Test signals are collection install success and Ansible playbook syntax resolving modules.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/requirements.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/10-qemu-hw-users.rules -->
# sources/test-tools/kdevops/scripts/10-qemu-hw-users.rules

Purpose: udev rule assigning VFIO devices to the `libvirt` group.

Important APIs/types/functions: single udev match `SUBSYSTEM=="vfio"` with `OWNER="root", GROUP="libvirt"`.

Control flow: evaluated by udev when VFIO device nodes appear.

State/persistence behavior: when installed under udev rules, affects ownership of VFIO device nodes.

Dependencies/integration: used for QEMU/libvirt hardware passthrough workflows.

Risks/test signals: assumes `libvirt` group exists and that group-level VFIO access is acceptable. Test signal is `ls -l /dev/vfio/*` group ownership after reload/trigger.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/10-qemu-hw-users.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/10-qemu-limits.conf -->
# sources/test-tools/kdevops/scripts/10-qemu-limits.conf

Purpose: PAM limits configuration raising memlock limits for the `libvirt` group.

Important APIs/types/functions: two limits entries set hard and soft `memlock` to `20000000`.

Control flow: applied by PAM/session limit handling after installation.

State/persistence behavior: affects login/session resource limits for `libvirt` group members.

Dependencies/integration: supports VFIO/QEMU workloads needing locked memory.

Risks/test signals: unit is kilobytes on many systems; value may be insufficient for large passthrough workloads. Test signal is `ulimit -l` for libvirt sessions.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/10-qemu-limits.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/append-makefile-vars-int.sh -->
# sources/test-tools/kdevops/scripts/append-makefile-vars-int.sh

Purpose: concatenates command-line arguments into a single integer-like Make/Kconfig string, defaulting to `0`.

Important APIs/types/functions: Bash loop over positional arguments and `echo`.

Control flow: prints `0` for no args; otherwise appends all non-empty argument strings and prints the result.

State/persistence behavior: stateless stdout helper.

Dependencies/integration: used from Make/Kconfig variable composition.

Risks/test signals: arguments are concatenated without separators or validation. Test signal is expected stdout for empty and multi-argument cases.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/append-makefile-vars-int.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/append-makefile-vars.sh -->
# sources/test-tools/kdevops/scripts/append-makefile-vars.sh

Purpose: concatenates Make/Kconfig variable fragments, with special handling to append only the first eight characters of the second argument as a hash suffix.

Important APIs/types/functions: Bash positional argument handling, substring expansion `${1:0:8}`, and stdout.

Control flow: prints `""` for no args; uses first arg as prefix, second arg truncated to eight chars when present, then appends remaining args verbatim.

State/persistence behavior: stateless stdout helper.

Dependencies/integration: used for generated paths such as hashed SSH config/key names.

Risks/test signals: no quoting around final echo and no separators; callers must supply exact fragments. Test signal is hash truncation matching Terraform tfvars templates.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/append-makefile-vars.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check-cli-set-var.sh -->
# sources/test-tools/kdevops/scripts/check-cli-set-var.sh

Purpose: checks whether an environment variable is present and prints `y`/`n`.

Important APIs/types/functions: `which env`, `env | grep ^NAME= | head -1 | awk`.

Control flow: requires exactly one argument; returns `n` if `env` is unavailable or variable is absent, otherwise `y`.

State/persistence behavior: read-only environment inspection.

Dependencies/integration: used by Kconfig/Make checks for CLI-provided variables.

Risks/test signals: grep pattern is susceptible to regex metacharacters in the variable name, though variable names are normally simple. Test signals are `y` for exported variables and `n` otherwise.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check-cli-set-var.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check-ssh-key-migration.sh -->
# sources/test-tools/kdevops/scripts/check-ssh-key-migration.sh

Purpose: prints a migration notice when old fixed Terraform SSH keys exist but new directory-hashed keys do not.

Important APIs/types/functions: `sha256sum`, path construction in `$HOME/.ssh`, `test -f`, and heredoc output.

Control flow: computes eight-character hash from `TOPDIR_PATH`, checks old/new public key paths, and prints instructions only when migration may be needed.

State/persistence behavior: read-only; it does not move keys.

Dependencies/integration: supports upgrade flow from old kdevops key naming to hashed per-directory key naming.

Risks/test signals: hash uses raw `echo "$TOPDIR_PATH"` including newline semantics; message only checks public key existence. Test signal is notice output for old-only key state and silence otherwise.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check-ssh-key-migration.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_commit_format.py -->
# sources/test-tools/kdevops/scripts/check_commit_format.py

Purpose: validates latest Git commit message formatting around `Generated-by: Claude AI` and `Signed-off-by:`.

Important APIs/types/functions: `subprocess.run(["git","log","-1","--pretty=format:%B"])`, `check_commit_format`, line scanning, issue list, and CLI `main`.

Control flow: reads latest commit message, finds Generated-by and Signed-off-by lines, requires Signed-off-by to immediately follow Generated-by when present, prints detailed diagnostics and returns nonzero on problems.

State/persistence behavior: read-only Git metadata inspection.

Dependencies/integration: intended for CI or local commit hooks.

Risks/test signals: only checks the latest commit and exact prefix `Generated-by: Claude AI`; multiple Signed-off-by lines collapse to last seen. Test signals are exit code 0/1 and printed offending lines.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_commit_format.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_distro_kconfig.sh -->
# sources/test-tools/kdevops/scripts/check_distro_kconfig.sh

Purpose: placeholder Kconfig helper that always prints `n`.

Important APIs/types/functions: Bash stdout only.

Control flow: unconditional `echo n`.

State/persistence behavior: stateless.

Dependencies/integration: likely used where distro feature autodetection is not implemented.

Risks/test signals: always disables the queried feature. Test signal is stable `n` output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_distro_kconfig.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_docker_mirror.sh -->
# sources/test-tools/kdevops/scripts/check_docker_mirror.sh

Purpose: Kconfig helper that detects Docker mirror directory, registry container, and registry endpoint status.

Important APIs/types/functions: env defaults `DOCKER_MIRROR_PATH` and `DOCKER_REGISTRY_PORT`, functions `check_registry_running` and `check_registry_accessible`, `docker ps`, `curl`, and case handling for Kconfig symbols/status.

Control flow: if mirror directory exists, answers `y` for enable checks, checks registry directory plus HTTP accessibility for use, suggests install when registry is absent or stopped, reports registry running, or prints human-readable status. Defaults to `n`.

State/persistence behavior: read-only filesystem/Docker/HTTP inspection.

Dependencies/integration: used by Kconfig defaults and vLLM Docker mirror configuration.

Risks/test signals: assumes local registry name `kdevops-docker-mirror`; HTTP check only probes localhost. Test signals are `y/n` for Kconfig modes and status text for user mode.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_docker_mirror.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_file_empty.sh -->
# sources/test-tools/kdevops/scripts/check_file_empty.sh

Purpose: ensures a file exists and reports whether it is non-empty.

Important APIs/types/functions: `mkdir --parents $(dirname $FILE)`, `touch`, `test -s`, and `echo y/n`.

Control flow: creates parent directory and file when missing, prints `y` if file has size, otherwise `n`.

State/persistence behavior: creates directories/files as a side effect.

Dependencies/integration: Kconfig/Make helper for generated or sentinel files.

Risks/test signals: unquoted paths break on spaces and the helper is not read-only despite its name. Test signal is file existence and correct `y/n` output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_file_empty.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_mirror.sh -->
# sources/test-tools/kdevops/scripts/check_mirror.sh

Purpose: Kconfig helper for local Linux mirror availability under `/mirror/`.

Important APIs/types/functions: directory check, `ls -1 | wc -l`, and symbol-specific responses.

Control flow: if `/mirror/` exists, answers enable, use, or first-run install depending on requested symbol and directory content; otherwise prints `n`.

State/persistence behavior: read-only filesystem inspection.

Dependencies/integration: used by local Linux mirror Kconfig options.

Risks/test signals: hard-coded path and unquoted variables; `INSTALL_LOCAL_LINUX_MIRROR` emits `KDEVOPS_FIRST_RUN` rather than `y`. Test signals are expected Kconfig stdout for empty/non-empty mirror directories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_mirror.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_mirror_nfs.sh -->
# sources/test-tools/kdevops/scripts/check_mirror_nfs.sh

Purpose: checks whether a mirror path exists and is mounted as NFS.

Important APIs/types/functions: directory test and `mount | grep -q "on $MIRROR_PATH type nfs"`.

Control flow: prints `n` if path does not exist; otherwise prints `y` only if mount output shows NFS at that path.

State/persistence behavior: read-only.

Dependencies/integration: Kconfig/Make helper for NFS mirror configuration.

Risks/test signals: mount parsing is string-based and path regex is unescaped. Test signal is `y` for NFS-mounted mirror path.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_mirror_nfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_mirror_present.sh -->
# sources/test-tools/kdevops/scripts/check_mirror_present.sh

Purpose: reports whether a supplied mirror directory exists.

Important APIs/types/functions: single directory test and `echo y/n`.

Control flow: prints `y` when `$1` is a directory, else `n`.

State/persistence behavior: read-only.

Dependencies/integration: generic Kconfig/Make mirror presence helper.

Risks/test signals: unquoted path can break on spaces. Test signal is expected `y/n`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_mirror_present.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_nix_mirror.sh -->
# sources/test-tools/kdevops/scripts/check_nix_mirror.sh

Purpose: Kconfig helper for Nix cache mirror availability and URL detection.

Important APIs/types/functions: `check_http_mirror`, `check_local_mirror`, `curl --connect-timeout`, `find` for `.narinfo`/`.nar`, `hostname -I`, and case outputs for use/availability/URL.

Control flow: reports mirror use if local cache or HTTP endpoint exists, reports availability for HTTP endpoint, returns an HTTP localhost/host-IP URL when reachable, falls back to `file://` local path, or prints empty/`n`.

State/persistence behavior: read-only filesystem and HTTP inspection.

Dependencies/integration: used by Nix/NixOS kdevops mirror configuration.

Risks/test signals: local directory is treated as configured even if empty; URL detection uses first host IP. Test signals are `y/n` and usable cache URL.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_nix_mirror.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_pciepassthrough_kconfig.sh -->
# sources/test-tools/kdevops/scripts/check_pciepassthrough_kconfig.sh

Purpose: checks whether a PCI passthrough Kconfig file exists.

Important APIs/types/functions: argument validation and tests for `Kconfig.<arg>` or `<arg>`.

Control flow: prints `n` for empty argument, `y` if either expected file path exists, otherwise `n`.

State/persistence behavior: read-only.

Dependencies/integration: Kconfig helper for optional PCI passthrough menus.

Risks/test signals: relative path depends on caller working directory. Test signal is `y` when config file exists.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/check_pciepassthrough_kconfig.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/cloud_list_all.sh -->
# sources/test-tools/kdevops/scripts/cloud_list_all.sh

Purpose: lists cloud instances for the currently configured Terraform provider, with implemented Lambda Labs support and placeholders for other providers.

Important APIs/types/functions: reads `.config`, provider case statement, `scripts/lambdalabs_credentials.py get`, `curl` to Lambda Labs API, inline Python JSON parsing/formatting, uptime/cost display, and provider-specific placeholder commands.

Control flow: detects provider from `.config`, errors if none, for Lambda Labs obtains API key, fetches instances, formats API errors, prints a table of instances and estimated cost; for AWS/GCE/Azure/OCI prints suggested native CLI commands.

State/persistence behavior: read-only except network API calls.

Dependencies/integration: depends on kdevops `.config`, Lambda Labs credential helper, curl, Python JSON, and cloud provider APIs.

Risks/test signals: only Lambda Labs is implemented; API schema changes can break parsing. Test signals are correct provider detection, authenticated Lambda response, formatted instance table, and nonzero exit on missing credentials.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/cloud_list_all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/coccinelle/generation/check_for_atomic_calls.py -->
# sources/test-tools/kdevops/scripts/coccinelle/generation/check_for_atomic_calls.py

Purpose: generates a Coccinelle semantic patch that traces transitive callers of a target function and reports callers reachable from likely atomic contexts.

Important APIs/types/functions: `argparse` requires `--levels`, `--target`, and `--output`; `multiprocessing.cpu_count`; generated SmPL rules include seed caller discovery, IRQ handler/name detection, per-level caller expansion, atomic primitive checks, lock-name checks, spinlock region checks, non-sleeping context checks, network driver context checks, atomic-name checks, and might-sleep checks.

Control flow: parses CLI, writes a Coccinelle file header with Python state sets and `register_caller`, then emits repeated rule blocks for each requested depth. The generated patch dynamically registers virtual identifiers to continue caller-chain exploration and prints warnings during `make coccicheck`.

State/persistence behavior: writes the requested `.cocci` output file. Runtime state inside the generated patch is in Coccinelle Python sets; no source code is modified by the generator.

Dependencies/integration: depends on Python 3 and Coccinelle/Kernel `make coccicheck MODE=report COCCI=<file>`. Integrates with kernel code analysis workflows.

Risks/test signals: comments mark confidence low; generated patterns are heuristic and can produce false positives/negatives. Some output uses Unicode symbols. Test signals are successful generator run, valid Coccinelle syntax, and actionable warning locations under coccicheck.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/coccinelle/generation/check_for_atomic_calls.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/coccinelle/generation/check_for_sleepy_calls.py -->
# sources/test-tools/kdevops/scripts/coccinelle/generation/check_for_sleepy_calls.py

Purpose: generates a Coccinelle semantic patch that explores calls from a target function and reports paths to functions or flags that may sleep.

Important APIs/types/functions: `argparse` options `--function`, `--max-depth`, `--output`, optional `--sleepy-function`, `--expected`; lists of known sleepy functions and GFP flags; temporary stats directory; generated Coccinelle Python helpers `register_call`, `find_path_to`, `register_sleep_point`, `register_func_for_analysis`, `save_stats`, and final stats merge/cleanup.

Control flow: parses CLI, optionally narrows sleepy function list, creates a temp stats directory, writes SmPL rules to find direct calls from the target, optional direct sleepy calls, depth-expanded call discovery, known-sleeper/GFP/mutex/might_sleep/name-pattern checks, and a finalize block that merges per-process JSON stats and prints unique sleep paths.

State/persistence behavior: writes the requested `.cocci` output file and, when the generated patch runs, creates temporary JSON stats files under `/tmp/cocci_stats_<pid>` that are cleaned during finalize.

Dependencies/integration: depends on Python 3, Coccinelle, and kernel `make coccicheck`. Intended for conservative manual review of sleeping behavior.

Risks/test signals: script labels confidence low; generated finalize references variables in no-sleep path that may not be defined, and Coccinelle parallel stats aggregation uses max counters rather than full sums. Test signals are generator success, coccicheck syntax success, stats summary, and manually verified sleep paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/coccinelle/generation/check_for_sleepy_calls.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/compute_sha256sum.sh -->
# sources/test-tools/kdevops/scripts/compute_sha256sum.sh

Purpose: prints the SHA-256 digest of the first command-line argument.

Important APIs/types/functions: `echo $1 | sha256sum | awk '{print $1}'`.

Control flow: unconditional pipeline over argument one.

State/persistence behavior: stateless stdout helper.

Dependencies/integration: used for path/key hashing in Make/Kconfig flows.

Risks/test signals: unquoted `echo` and appended newline mean digest semantics may not match `printf %s`. Test signal is stable digest for simple path inputs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/compute_sha256sum.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/config -->
# sources/test-tools/kdevops/scripts/config

Purpose: command-line helper for editing Kconfig-style `.config` files.

Important APIs/types/functions: environment prefix `CONFIG_`, delimiter `SED_DELIM`, `usage`, `checkarg`, `txt_append`, `txt_subst`, `txt_delete`, `set_var`, `undef_var`, command parsing for enable/disable/module/set-str/set-val/undefine/state/*-after/refresh, and `make oldconfig`.

Control flow: parses optional `--file`, collects commands, uppercases symbols unless `--keep-case`, normalizes symbols by removing prefix, executes repeated mutations against the config file, supports inserting after an anchor, prints option state, and refreshes through `make oldconfig`.

State/persistence behavior: mutates `.config` or the file named by `--file` using temporary `.swp` files and `mv`; `--refresh` can also update config through Kconfig.

Dependencies/integration: derived from Linux kernel config tooling patterns and used by kdevops Make/Kconfig automation.

Risks/test signals: sed-based regex matching can mis-handle special characters; append-after uses both enabled and disabled anchors; no file locking. Test signals are correct config lines after each command, correct `--state` output, and successful `--refresh`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/config -->
