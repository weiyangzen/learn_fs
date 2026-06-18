# subset-b-009255 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/debian/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `devconfig` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Check if unattended-upgrades is installed`, `Set fact if unattended-upgrades is installed`, `Verify unattended-upgrades is not installed`, `Stop and disable unattended-upgrades related services`, `Update apt cache accepting release info changes`, `Upgrade Packages`, `Remove unattended-upgrades package in case upgrade installed it`, `Remove optional unattended-upgrades configuration files if they exist`, `Stop and disable unattended-upgrades related services`, `Allow for distro source change / upgrade`, `Check for UNAVAIL in /etc/nsswitch.conf hosts line`, `Write custom nsswitch.conf for hop1 mirror heuristic`; plus 13 more. Important modules/directives include `Acquire`, `apt`, `become`, `become_flags`, `become_method`, `changed_when`, `cmd`, `command`, `commands`, `content`, `copy`, `daemon_reload`; plus 43 more. Key variable inputs observed in this file include `item`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Check if unattended-upgrades is installed`, `Set fact if unattended-upgrades is installed`, `Verify unattended-upgrades is not installed`, `Stop and disable unattended-upgrades related services`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `copy`, `file`, `systemd`. Notable path references include `/etc/apt/apt.conf.d/02periodic`, `/etc/apt/apt.conf.d/20auto-upgrades`, `/etc/apt/apt.conf.d/50unattended-upgrades`, `/etc/apt/apt.conf.d/52unattended-upgrades-local`, `/etc/apt/apt.conf.d/99ignore-release-date`, `/etc/nsswitch.conf`, `/etc/snmp/snmpd.conf`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `dpkg-query -W -f='${Status}' unattended-upgrades`, `cmd: apt-get update --allow-releaseinfo-change`, `apt-get update --allow-releaseinfo-change -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false -o Acquire::AllowInsecureRepositories=true`, `grep -E '^hosts:.*UNAVAIL' /etc/nsswitch.conf`.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `devconfig` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Gather os_family`, `Import optional user secret specific variables`, `Import optional distribution specific variables`, `Debian-specific setup`, `SuSE-specific setup`, `Red Hat-specific setup`. Important modules/directives include `gather_subset`, `ignore_errors`, `include_tasks`, `include_vars`, `setup`, `skip`, `tags`, `when`, `with_first_found`. Includes/imports delegate to `debian/main.yml`, `suse/main.yml`, `redhat/main.yml`. Key variable inputs observed in this file include `ansible_facts`, `item`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Gather os_family`, `Import optional user secret specific variables`, `Import optional distribution specific variables`, `Debian-specific setup`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/main.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/redhat/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `devconfig` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Register system with Red Hat`, `Check whether custom repofile exists`, `Add custom yum repo`, `Discover the fastest package update mirrors`, `Increase the maximum number of concurrent package downloads`, `Refresh cache and upgrade all present packages`, `Reboot system to make the new kernel and modules take effect`, `Enable installation of packages from EPEL`, `Build install package list`, `Add btrfs-progs to install package list`, `Add GNU screen to install package list`, `Add Tmux to install package list`; plus 6 more. Important modules/directives include `activationkey`, `become`, `become_method`, `copy`, `delay`, `delegate_to`, `dest`, `dnf`, `enabled`, `force_register`, `group`, `include_role`; plus 24 more. Includes/imports delegate to `name: epel-release`. Key variable inputs observed in this file include `devconfig_custom_yum_repofile`, `packages`, `rhel_activation_key`, `rhel_org_id`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Register system with Red Hat`, `Check whether custom repofile exists`, `Add custom yum repo`, `Discover the fastest package update mirrors`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `copy`, `file`, `lineinfile`, `systemd`. Notable path references include `/etc/dnf/dnf.conf`, `/etc/snmp/snmpd.conf`, `/etc/yum.repos.d/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/suse/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `devconfig` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `The default is to assume we have figured out how to add repos for each`, `Disable things which require a repo to be set but that cannot be done`, `The default is to assume we are not on sle11 or sle10`, `Are we on SLE11 or SLE10?`, `The default is to assume all distros supports nvme-utils`, `Does this release lack nvme-utils`, `The default is to assume all distros supports git-core`, `Does this release lack git-core`, `Does this release use the package name git assume false`; plus 40 more. Important modules/directives include `backrefs`, `become`, `become_flags`, `become_method`, `check_mode`, `cmd`, `command`, `dest`, `enabled`, `fail`, `import_tasks`, `install_kdump`; plus 48 more. Includes/imports delegate to `update-grub/main.yml`. Key variable inputs observed in this file include `ansible_architecture`, `ansible_distribution_major_version`, `ansible_distribution_version`, `devconfig_repos_addon_list`, `item`, `kdump_high`, `kdump_low`, `role_path`, `suse_registration_code`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `The default is to assume we have figured out how to add repos for each`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `file`, `lineinfile`, `systemd`. Notable path references include `/2.1/x86_64`, `/SLED`, `/etc/default/grub`, `/etc/snmp/snmpd.conf`, `/main.yml`, `/scripts/add-suse-repo-if-not-found.sh`, `/scripts/prepare_suse_repos.sh`, `/secret.yml`; plus 1 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `SUSEConnect -p sle-module-python2/{{ ansible_distribution_version }}/{{ ansible_architecture }}`, `cmd: "zypper in -y python-xml`, `kdumptool calibrate | grep ^High | awk '{print $2}'`, `kdumptool calibrate | grep ^Low | awk '{print $2}'`.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; command tasks rely on exact distro command output and idempotence annotations; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/debian/main.yml

## Purpose
Implements the distribution-specific path for revving a test node to the latest distribution kernel-of-the-day or update kernel, then rebooting when the role is enabled.

## Important APIs, Types, and Functions
Ansible task entry points include `Allow for distro source change / upgrade`, `Update apt cache and do dist-upgrade`, `Reboot system to make the new kernel and modules take effect`. Important modules/directives include `apt`, `args`, `become`, `become_flags`, `become_method`, `changed_when`, `command`, `reboot`, `register`, `tags`, `update_cache`, `upgrade`; plus 2 more. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Allow for distro source change / upgrade`, `Update apt cache and do dist-upgrade`, `Reboot system to make the new kernel and modules take effect`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `apt-get update --allow-releaseinfo-change`.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/main.yml

## Purpose
Implements the distribution-specific path for revving a test node to the latest distribution kernel-of-the-day or update kernel, then rebooting when the role is enabled.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional user secret specific variables`, `Import optional distribution specific variables`, `Set the path where we collect our kotd updates`, `Get used target kernel version prior to reving kernel`, `Document used target kernel version prior to reving kernel`, `Distribution specific setup`, `Check kernel uname`, `Get used target kernel version after reving kernel`, `Document used target kernel version after reving kernel`. Important modules/directives include `command`, `debug`, `delegate_to`, `ignore_errors`, `import_tasks`, `include_vars`, `kotd_uname_after`, `kotd_uname_before`, `msg`, `register`, `run_once`, `running_kernel`; plus 7 more. Includes/imports delegate to `debian/main.yml`, `suse/main.yml`, `redhat/main.yml`. Key variable inputs observed in this file include `ansible_facts`, `item`, `kotd_uname_after`, `kotd_uname_before`, `running_kernel`, `uname_cmd`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional user secret specific variables`, `Import optional distribution specific variables`, `Set the path where we collect our kotd updates`, `Get used target kernel version prior to reving kernel`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`. Notable path references include `/.kotd.uname-after.txt`, `/.kotd.uname-before.txt`, `/main.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `uname -r`, `echo {{ uname_cmd.stdout_lines | regex_replace('\]') | regex_replace('\[') }} > {{ kotd_uname_before }}`, `uname -r`, `echo {{ uname_cmd.stdout_lines | regex_replace('\]') | regex_replace('\[') }} > {{ kotd_uname_after }}`.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/redhat/main.yml

## Purpose
Implements the distribution-specific path for revving a test node to the latest distribution kernel-of-the-day or update kernel, then rebooting when the role is enabled.

## Important APIs, Types, and Functions
Ansible task entry points include `Add KOTD repository`, `Parse repository id from repo file`, `Get kernel version from repository-packages`, `Install KOTD`, `Reboot system to make the new kernel and modules take effect`. Important modules/directives include `arch`, `become`, `become_method`, `changed_when`, `dest`, `disable_gpg_check`, `dnf`, `get_url`, `kernel_version`, `name`, `reboot`, `register`; plus 9 more. Key variable inputs observed in this file include `arch`, `devconfig_kotd_repo`, `kernel_version`, `repo_file`, `repo_id`, `result`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Add KOTD repository`, `Parse repository id from repo file`, `Get kernel version from repository-packages`, `Install KOTD`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`, `file`. Notable path references include `/etc/yum.repos.d`, `/etc/yum.repos.d/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `grep -E '\[.*\]' /etc/yum.repos.d/{{ repo_file }} | tr -d '[]'`, `dnf -q --repo={{ repo_id }} repoquery --qf "%{version}-%{release}" kernel.x86_64`.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/suse/main.yml

## Purpose
Implements the distribution-specific path for revving a test node to the latest distribution kernel-of-the-day or update kernel, then rebooting when the role is enabled.

## Important APIs, Types, and Functions
Ansible task entry points include `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `The default is to assume we can add repos for a release`, `Disable things which require a repo to be set but that cannot be done`, `The default is to assume we are not on sle11 or sle10`, `Are we on SLE11 or SLE10?`, `Add extra addon repositories when enabled`, `Install kotd`, `Reboot into kotd`. Important modules/directives include `allow_vendor_change`, `become`, `become_method`, `cmd`, `disable_recommends`, `force`, `force_resolution`, `is_leap`, `is_sle`, `is_sle10`, `is_sle10sp3`, `is_sle11`; plus 21 more. Key variable inputs observed in this file include `ansible_distribution_major_version`, `ansible_distribution_version`, `devconfig_kotd_repo`, `devconfig_kotd_repo_name`, `role_path`. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `The default is to assume we can add repos for a release`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`. Notable path references include `/scripts/add-suse-repo-if-not-found.sh`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/kotd-rev-kernel/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/main.yml

## Purpose
Main task orchestration for the `devconfig` role, which prepares kdevops test nodes for development and workflow execution by installing distribution packages, tuning boot/system services, propagating user configuration, and optionally revving kernels. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional extra_args file`, `Wait for target nodes to become reachable`, `Gathering facts`, `Infer user on declared hosts`, `Infer group on declared hosts`, `Set inferred user and group for declared hosts`, `Ensure /etc/hostname is set`, `Check and fix APT mirrors for Debian testing`, `Install dependencies`, `Configure custom repositories and install packages`, `Configure en_US.UTF-8 locale files`, `Generate and update locales`; plus 54 more. Important modules/directives include `ansible.posix.sysctl`, `args`, `backrefs`, `become`, `become_flags`, `become_method`, `changed_when`, `check_mode`, `command`, `copy`, `create`, `daemon_reload`; plus 47 more. Includes/imports delegate to `check-apt-mirrors.yml`, `install-deps/main.yml`, `config-custom-repos-and-packages/main.yml`, `update-grub/main.yml`, `kotd-rev-kernel/main.yml`. Key variable inputs observed in this file include `ansible_default_ipv4`, `ansible_ssh_host`, `declared_host_group`, `declared_host_user`, `dev_bash_config`, `dev_bash_config_hacks_dest`, `dev_bash_config_hacks_generic`, `dev_bash_config_hacks_name`, `dev_bash_config_hacks_src`, `dev_bash_config_root`, `dev_gitconfig_dest`, `dev_gitconfig_src`, `devconfig_grub_console`, `devconfig_grub_timeout`; plus 10 more. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional extra_args file`, `Wait for target nodes to become reachable`, `Gathering facts`, `Infer user on declared hosts`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `copy`, `file`, `lineinfile`, `systemd`. Notable path references include `/.vimrc`, `/bin/bash`, `/dev/null`, `/etc/default/grub`, `/etc/default/grub.d/15_timeout.cfg`, `/etc/default/locale`, `/etc/hostname`, `/etc/locale.gen`; plus 4 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks. Shell/command integration points observed here include `whoami`, `id -g -n`, `|`, `git config --global --get-all safe.directory`, `git config --global --add safe.directory '*'`, `|`, `|`, `timedatectl set-ntp true`; plus 2 more.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/templates/snmpd.conf -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/templates/snmpd.conf

## Purpose
Template/configuration input consumed by the `devconfig` role. It persists runtime settings on the target host rather than executing control flow itself.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `devconfig` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no Ansible control flow in the template/config file. Control flow happens in the task that installs it; once deployed, the target service or shell sources/reads it at runtime.

## State and Persistence Behavior
State persists wherever the installing task writes this file. Relevant literal paths in or around the file include none detected.

## Dependencies and Integration Points
Integrated by playbooks that target every node before workflow roles. It uses Ansible facts, kdevops configuration variables, package managers, GRUB/systemd files, templates such as `hostname`, `vimrc`, `journal-upload.conf.j2`, and `snmpd.conf`, and downstream roles such as `create_data_partition` and kernel rev tasks.

## Risks
High-risk areas are distro detection, repository enablement, bootloader edits, kdump/SNMP/journal service setup, and assumptions about package names across Debian, Red Hat, and SUSE releases. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include render the template with representative variables; validate the consuming service or shell can parse/read the deployed file; confirm ownership and mode from the installing task.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/templates/snmpd.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/dhclient_cache/defaults/main.yml

## Purpose
Defines default variables for the `dhclient_cache` role, which adds DHCP lease persistence hooks so cloud VMs retain usable network configuration across transient DHCP or reboot races. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `dhclient_cache` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated after networking is present but before long test runs. It relies on `/etc/dhcp`, `/etc/NetworkManager/dispatcher.d`, `/etc/wicked/extensions`, per-interface facts, and lease-cache templates.

## Risks
The main risk is installing hooks for the wrong DHCP stack or interface, which can preserve stale addresses or fail to update cache files after network changes. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/isc-dhclient.yml -->
# sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/isc-dhclient.yml

## Purpose
Main task orchestration for the `dhclient_cache` role, which adds DHCP lease persistence hooks so cloud VMs retain usable network configuration across transient DHCP or reboot races. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Detect primary network interface`, `Create dhclient enter hook for persistent lease caching`, `Create dhclient exit hook for persistent lease caching`, `Update dhclient configuration for aggressive retry`, `Ensure lease cache directory exists`, `Create initial cached lease from current lease`. Important modules/directives include `args`, `become`, `become_flags`, `become_method`, `create`, `creates`, `dest`, `file`, `group`, `line`, `lineinfile`, `loop`; plus 10 more. Key variable inputs observed in this file include `ansible_default_ipv4`, `dhclient_cache_retry_interval`, `dhclient_cache_timeout`, `item`, `primary_interface`. The role-level integration surface is the `dhclient_cache` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Detect primary network interface`, `Create dhclient enter hook for persistent lease caching`, `Create dhclient exit hook for persistent lease caching`, `Update dhclient configuration for aggressive retry`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `template`, `file`, `lineinfile`. Notable path references include `/CentOS/Fedora`, `/etc/dhcp/dhclient-enter-hooks.d/kdevops-persistent-cache`, `/etc/dhcp/dhclient-exit-hooks.d/kdevops-persistent-cache`, `/etc/dhcp/dhclient.conf`, `/var/lib/dhcp/cache`, `/var/lib/dhcp/cache/dhclient.{{`, `/var/lib/dhcp/dhclient.{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after networking is present but before long test runs. It relies on `/etc/dhcp`, `/etc/NetworkManager/dispatcher.d`, `/etc/wicked/extensions`, per-interface facts, and lease-cache templates. Shell/command integration points observed here include `|`.

## Risks
The main risk is installing hooks for the wrong DHCP stack or interface, which can preserve stale addresses or fail to update cache files after network changes. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/isc-dhclient.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/main.yml

## Purpose
Main task orchestration for the `dhclient_cache` role, which adds DHCP lease persistence hooks so cloud VMs retain usable network configuration across transient DHCP or reboot races. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Configure persistent DHCP caching for cloud VMs`, `Detect DHCP client mechanism`, `Display detected DHCP mechanism`, `Configure ISC dhclient persistent caching`, `Configure NetworkManager persistent caching`, `Configure wicked persistent caching`, `Warn about unsupported DHCP mechanism`. Important modules/directives include `block`, `debug`, `dhcp_mechanism`, `include_tasks`, `msg`, `set_fact`, `when`. Includes/imports delegate to `isc-dhclient.yml`, `networkmanager.yml`, `wicked.yml`. Key variable inputs observed in this file include `ansible_facts`, `dhcp_mechanism`. The role-level integration surface is the `dhclient_cache` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Configure persistent DHCP caching for cloud VMs`, `Detect DHCP client mechanism`, `Display detected DHCP mechanism`, `Configure ISC dhclient persistent caching`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after networking is present but before long test runs. It relies on `/etc/dhcp`, `/etc/NetworkManager/dispatcher.d`, `/etc/wicked/extensions`, per-interface facts, and lease-cache templates.

## Risks
The main risk is installing hooks for the wrong DHCP stack or interface, which can preserve stale addresses or fail to update cache files after network changes.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/networkmanager.yml -->
# sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/networkmanager.yml

## Purpose
Main task orchestration for the `dhclient_cache` role, which adds DHCP lease persistence hooks so cloud VMs retain usable network configuration across transient DHCP or reboot races. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Detect primary network interface`, `Create NetworkManager dispatcher script for DHCP cache save`, `Ensure lease cache directory exists`, `Get current IP configuration via NetworkManager`. Important modules/directives include `args`, `become`, `become_flags`, `become_method`, `changed_when`, `creates`, `dest`, `file`, `group`, `mode`, `owner`, `path`; plus 6 more. Key variable inputs observed in this file include `ansible_default_ipv4`, `primary_interface`. The role-level integration surface is the `dhclient_cache` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Detect primary network interface`, `Create NetworkManager dispatcher script for DHCP cache save`, `Ensure lease cache directory exists`, `Get current IP configuration via NetworkManager`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `template`, `file`. Notable path references include `/etc/NetworkManager/dispatcher.d/10-kdevops-dhcp-cache`, `/var/lib/NetworkManager/cache`, `/var/lib/NetworkManager/cache/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after networking is present but before long test runs. It relies on `/etc/dhcp`, `/etc/NetworkManager/dispatcher.d`, `/etc/wicked/extensions`, per-interface facts, and lease-cache templates. Shell/command integration points observed here include `|`.

## Risks
The main risk is installing hooks for the wrong DHCP stack or interface, which can preserve stale addresses or fail to update cache files after network changes. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/networkmanager.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/wicked.yml -->
# sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/wicked.yml

## Purpose
Main task orchestration for the `dhclient_cache` role, which adds DHCP lease persistence hooks so cloud VMs retain usable network configuration across transient DHCP or reboot races. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Detect primary network interface`, `Create wicked extension for DHCP cache save`, `Ensure lease cache directory exists`, `Get current IP configuration via wicked`. Important modules/directives include `args`, `become`, `become_flags`, `become_method`, `changed_when`, `creates`, `dest`, `file`, `group`, `mode`, `owner`, `path`; plus 6 more. Key variable inputs observed in this file include `ansible_default_ipv4`, `primary_interface`. The role-level integration surface is the `dhclient_cache` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Detect primary network interface`, `Create wicked extension for DHCP cache save`, `Ensure lease cache directory exists`, `Get current IP configuration via wicked`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `template`, `file`. Notable path references include `/etc/wicked/extensions/kdevops-dhcp-cache`, `/var/lib/wicked/cache`, `/var/lib/wicked/cache/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after networking is present but before long test runs. It relies on `/etc/dhcp`, `/etc/NetworkManager/dispatcher.d`, `/etc/wicked/extensions`, per-interface facts, and lease-cache templates. Shell/command integration points observed here include `|`.

## Risks
The main risk is installing hooks for the wrong DHCP stack or interface, which can preserve stale addresses or fail to update cache files after network changes. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/wicked.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/docker-mirror/defaults/main.yml

## Purpose
Defines default variables for the `docker-mirror` role, which builds and maintains a local Docker registry mirror/cache for workflow images, including package installation, registry container management, image preloading, and optional systemd refresh. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/debian/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `docker-mirror` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install Docker prerequisites`, `Add Docker GPG key`, `Add Docker repository`, `Install Docker`, `Install Python Docker library`, `Start and enable Docker service`, `Add current user to docker group`. Important modules/directives include `append`, `apt`, `apt_key`, `apt_repository`, `become`, `daemon_reload`, `enabled`, `groups`, `name`, `repo`, `state`, `systemd`; plus 4 more. Key variable inputs observed in this file include `ansible_architecture`, `ansible_distribution`, `ansible_distribution_release`, `ansible_user`. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install Docker prerequisites`, `Add Docker GPG key`, `Add Docker repository`, `Install Docker`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `systemd`. Notable path references include `//download.docker.com/linux/{{`, `/Ubuntu`, `/gpg`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `docker-mirror` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install Docker dependencies on Debian`, `Install Docker dependencies on RedHat`, `Install Docker dependencies on SUSE`. Important modules/directives include `include_tasks`, `when`. Includes/imports delegate to `debian/main.yml`, `redhat/main.yml`, `suse/main.yml`. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install Docker dependencies on Debian`, `Install Docker dependencies on RedHat`, `Install Docker dependencies on SUSE`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/main.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/redhat/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `docker-mirror` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install Docker prerequisites`, `Add Docker repository`, `Install Docker`, `Install Python Docker library`, `Start and enable Docker service`, `Add current user to docker group`. Important modules/directives include `append`, `args`, `become`, `changed_when`, `cmd`, `command`, `creates`, `daemon_reload`, `enabled`, `groups`, `name`, `state`; plus 4 more. Key variable inputs observed in this file include `ansible_user`. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install Docker prerequisites`, `Add Docker repository`, `Install Docker`, `Install Python Docker library`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `systemd`. Notable path references include `//download.docker.com/linux/centos/docker-ce.repo`, `/CentOS/Fedora`, `/etc/yum.repos.d/docker-ce.repo`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows. Shell/command integration points observed here include `cmd: yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo`.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/suse/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `docker-mirror` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install Docker`, `Install Python Docker library`, `Start and enable Docker service`, `Add current user to docker group`. Important modules/directives include `append`, `become`, `daemon_reload`, `enabled`, `groups`, `name`, `state`, `systemd`, `user`, `when`, `zypper`. Key variable inputs observed in this file include `ansible_user`. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install Docker`, `Install Python Docker library`, `Start and enable Docker service`, `Add current user to docker group`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `systemd`. Notable path references include `/openSUSE`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/main.yml

## Purpose
Main task orchestration for the `docker-mirror` role, which builds and maintains a local Docker registry mirror/cache for workflow images, including package installation, registry container management, image preloading, and optional systemd refresh. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Check if Docker mirror directory exists`, `Check if Docker is installed`, `Install Docker dependencies`, `Create Docker mirror directory structure`, `Create Docker registry configuration`, `Check if Docker registry container is running`, `Pull registry image`, `Start Docker registry mirror container`, `Wait for registry to be ready`, `Display Docker mirror status`, `Create Docker images list from workflows`, `Create README in images directory to clarify its purpose`; plus 8 more. Important modules/directives include `become`, `changed_when`, `command`, `daemon_reload`, `debug`, `delay`, `dest`, `enabled`, `failed_when`, `file`, `ignore_errors`, `include_tasks`; plus 19 more. Includes/imports delegate to `install-deps/main.yml`, `pull_images.yml`. Key variable inputs observed in this file include `docker_mirror_dir`, `docker_mirror_path`, `docker_mirror_port`, `item`, `registry_status`. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Check if Docker mirror directory exists`, `Check if Docker is installed`, `Install Docker dependencies`, `Create Docker mirror directory structure`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`, `template`, `file`, `systemd`. Notable path references include `//localhost`, `//registry-1.docker.io`, `/config`, `/config/config.yml`, `/etc/docker/registry/config.yml`, `/etc/systemd/system/docker-mirror-update.service`, `/etc/systemd/system/docker-mirror-update.timer`, `/images`; plus 4 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows. Shell/command integration points observed here include `docker --version`, `docker ps -f name=kdevops-docker-mirror --format "{{ '{{' }}.Status{{ '}}' }}`, `docker pull registry:2`, `|`.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/pull_images.yml -->
# sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/pull_images.yml

## Purpose
Main task orchestration for the `docker-mirror` role, which builds and maintains a local Docker registry mirror/cache for workflow images, including package installation, registry container management, image preloading, and optional systemd refresh. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Ensure update script exists`, `Create update script if it doesn't exist`, `Ensure workflow images list exists`, `Create Docker images list if it doesn't exist`, `Run Docker mirror image preload script`, `Parse preload results`, `Display preload summary`, `Check for saved tarballs`, `Get tarball sizes`, `Display storage information`, `Check for failed images`, `Display warning if images failed`. Important modules/directives include `Location`, `Tarballs`, `async`, `become`, `changed_when`, `command`, `debug`, `dest`, `failed_when`, `http`, `mode`, `msg`; plus 11 more. Key variable inputs observed in this file include `docker_mirror_path`, `docker_mirror_port`, `failed_count`, `line`, `preload_result`, `tarball_count`, `tarball_size`. The role-level integration surface is the `docker-mirror` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Ensure update script exists`, `Create update script if it doesn't exist`, `Ensure workflow images list exists`, `Create Docker images list if it doesn't exist`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`. Notable path references include `//localhost`, `/dev/null`, `/images/workflow-images.txt`, `/logs/`, `/logs/update-`, `/mirror/docker`, `/registry/tarballs`, `/registry/tarballs/`; plus 1 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with workflow image users and optional 9P sharing. It depends on Docker CLI/service, registry image `registry:2`, systemd units, templates under the role, and image lists derived from kdevops workflows. Shell/command integration points observed here include `{{ docker_mirror_path | default('/mirror/docker') }}/scripts/update-docker-images.sh`, `|`, `|`, `|`.

## Risks
The main risks are Docker repository setup, registry container idempotence, image preload partial success, and background systemd updates hiding image pull failures. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker-mirror/tasks/pull_images.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker_mirror_9p/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/docker_mirror_9p/defaults/main.yml

## Purpose
Defines default variables for the `docker_mirror_9p` role, which mounts a host-side Docker mirror directory into guests over 9P for shared image-cache access. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `docker_mirror_9p` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated with guest definitions that expose a 9P tag. It depends on host directory creation, a guest mount point, Linux 9P support, and the `docker_mirror_9p_*` variables.

## Risks
The main risks are missing guest 9P support, stale host mount contents, and treating a mountpoint check as sufficient proof that image data is usable. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; verify block-device and mount topology before and after the run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker_mirror_9p/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker_mirror_9p/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/docker_mirror_9p/tasks/main.yml

## Purpose
Main task orchestration for the `docker_mirror_9p` role, which mounts a host-side Docker mirror directory into guests over 9P for shared image-cache access. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Ensure Docker mirror 9P host directory exists`, `Create Docker mirror 9P guest mount point`, `Mount Docker mirror 9P filesystem in guest`, `Verify Docker mirror 9P mount is active`. Important modules/directives include `changed_when`, `command`, `delegate_to`, `failed_when`, `file`, `fstype`, `mode`, `mount`, `opts`, `path`, `register`, `run_once`; plus 4 more. Key variable inputs observed in this file include `docker_mirror_9p_guest_mount_point`, `docker_mirror_9p_host_path`, `docker_mirror_9p_mount_tag`. The role-level integration surface is the `docker_mirror_9p` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Ensure Docker mirror 9P host directory exists`, `Create Docker mirror 9P guest mount point`, `Mount Docker mirror 9P filesystem in guest`, `Verify Docker mirror 9P mount is active`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`, `file`, `mount`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated with guest definitions that expose a 9P tag. It depends on host directory creation, a guest mount point, Linux 9P support, and the `docker_mirror_9p_*` variables. Shell/command integration points observed here include `mountpoint -q "{{ docker_mirror_9p_guest_mount_point }}`.

## Risks
The main risks are missing guest 9P support, stale host mount contents, and treating a mountpoint check as sufficient proof that image data is usable. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; verify block-device and mount topology before and after the run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/docker_mirror_9p/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/epel-release/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/epel-release/defaults/main.yml

## Purpose
Defines default variables for the `epel-release` role, which enables EPEL package repositories on Red Hat family systems so later roles can install non-base dependencies. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `epel-release` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated early in Red Hat provisioning. It feeds roles that need packages from EPEL and uses `dnf` plus `crb` enablement for newer distributions.

## Risks
The main risk is enabling the wrong repository set for the distribution release, especially CRB/EPEL differences across RHEL clones. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/epel-release/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/epel-release/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/epel-release/tasks/main.yml

## Purpose
Main task orchestration for the `epel-release` role, which enables EPEL package repositories on Red Hat family systems so later roles can install non-base dependencies. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Set epel-release package name for RHEL`, `Install the distribution's epel-release package`, `Enable the EPEL repository`. Important modules/directives include `argv`, `become`, `become_method`, `changed_when`, `command`, `delay`, `disable_gpg_check`, `dnf`, `epel_package`, `name`, `register`, `retries`; plus 3 more. Key variable inputs observed in this file include `ansible_distribution_major_version`, `epel_package`. The role-level integration surface is the `epel-release` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set epel-release package name for RHEL`, `Install the distribution's epel-release package`, `Enable the EPEL repository`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`. Notable path references include `//dl.fedoraproject.org/pub/epel/epel-release-latest-{{`, `/usr/bin/dnf`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated early in Red Hat provisioning. It feeds roles that need packages from EPEL and uses `dnf` plus `crb` enablement for newer distributions. Shell/command integration points observed here include `argv:`.

## Risks
The main risk is enabling the wrong repository set for the distribution release, especially CRB/EPEL differences across RHEL clones. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/epel-release/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/extra_volumes/defaults/main.yml

## Purpose
Defines default variables for the `extra_volumes` role, which exposes provider-created extra block volumes to guests with stable kdevops device naming and provider-specific setup. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `extra_volumes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated after Terraform/provider provisioning. AWS consumes Terraform output and udev templates; other providers are placeholders in this slice.

## Risks
The main risk is provider-specific block device naming drift; incorrect udev or Terraform mapping can point tests at the wrong disk. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/main.yml

## Purpose
Main task orchestration for the `extra_volumes` role, which exposes provider-created extra block volumes to guests with stable kdevops device naming and provider-specific setup. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Include provider-specific tasks`. Important modules/directives include `file`, `include_tasks`, `when`. Includes/imports delegate to `file: "{{ role_path }}/tasks/providers/{{ kdevops_terraform_provider }}.yml`. Key variable inputs observed in this file include `kdevops_terraform_provider`, `role_path`. The role-level integration surface is the `extra_volumes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Include provider-specific tasks`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `file`. Notable path references include `/tasks/providers/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after Terraform/provider provisioning. AWS consumes Terraform output and udev templates; other providers are placeholders in this slice.

## Risks
The main risk is provider-specific block device naming drift; incorrect udev or Terraform mapping can point tests at the wrong disk.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/aws.yml -->
# sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/aws.yml

## Purpose
Provider-specific implementation for the `extra_volumes` role. It adapts the generic extra-volume workflow to the selected cloud provider's device discovery and naming model.

## Important APIs, Types, and Functions
Ansible task entry points include `Install tmpfiles.d configuration for /dev/disk/kdevops/`, `Create /dev/disk/kdevops/ directory using tmpfiles`, `Extract the "extra volumes" map`, `Install the script that creates symlinks in /dev/disk/kdevops`, `Create the "extra volumes" udev rule`, `Force the target node to reload its udev ruleset and trigger block devices`. Important modules/directives include `become`, `binary_path`, `changed_when`, `cloud.terraform.terraform_output`, `command`, `delegate_to`, `dest`, `format`, `group`, `mode`, `name`, `owner`; plus 8 more. Key variable inputs observed in this file include `terraform_binary_path`, `terraform_output`, `topdir_path`. The role-level integration surface is the `extra_volumes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install tmpfiles.d configuration for /dev/disk/kdevops/`, `Create /dev/disk/kdevops/ directory using tmpfiles`, `Extract the "extra volumes" map`, `Install the script that creates symlinks in /dev/disk/kdevops`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`, `template`, `systemd`. Notable path references include `/dev/disk/kdevops`, `/dev/disk/kdevops/`, `/etc/tmpfiles.d/kdevops-disk.conf`, `/etc/udev/rules.d/99-aws-ebs.rules`, `/terraform/aws`, `/usr/local/bin/udev-ebs-tagger`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after Terraform/provider provisioning. AWS consumes Terraform output and udev templates; other providers are placeholders in this slice. Shell/command integration points observed here include `systemd-tmpfiles --create /etc/tmpfiles.d/kdevops-disk.conf`, `udevadm control --reload && udevadm trigger --subsystem-match=block --action=add`.

## Risks
The main risk is provider-specific block device naming drift; incorrect udev or Terraform mapping can point tests at the wrong disk. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/aws.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/azure.yml -->
# sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/azure.yml

## Purpose
Provider-specific implementation for the `extra_volumes` role. It adapts the generic extra-volume workflow to the selected cloud provider's device discovery and naming model.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `extra_volumes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes this file in order as an included task file. Its behavior is primarily controlled by `when` expressions and variables inherited from the role defaults and inventory.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after Terraform/provider provisioning. AWS consumes Terraform output and udev templates; other providers are placeholders in this slice.

## Risks
The main risk is provider-specific block device naming drift; incorrect udev or Terraform mapping can point tests at the wrong disk.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/azure.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/gce.yml -->
# sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/gce.yml

## Purpose
Provider-specific implementation for the `extra_volumes` role. It adapts the generic extra-volume workflow to the selected cloud provider's device discovery and naming model.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `extra_volumes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes this file in order as an included task file. Its behavior is primarily controlled by `when` expressions and variables inherited from the role defaults and inventory.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after Terraform/provider provisioning. AWS consumes Terraform output and udev templates; other providers are placeholders in this slice.

## Risks
The main risk is provider-specific block device naming drift; incorrect udev or Terraform mapping can point tests at the wrong disk.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/gce.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/oci.yml -->
# sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/oci.yml

## Purpose
Provider-specific implementation for the `extra_volumes` role. It adapts the generic extra-volume workflow to the selected cloud provider's device discovery and naming model.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `extra_volumes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes this file in order as an included task file. Its behavior is primarily controlled by `when` expressions and variables inherited from the role defaults and inventory.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after Terraform/provider provisioning. AWS consumes Terraform output and udev templates; other providers are placeholders in this slice.

## Risks
The main risk is provider-specific block device naming drift; incorrect udev or Terraform mapping can point tests at the wrong disk.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/oci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fio-tests/defaults/main.yml

## Purpose
Defines default variables for the `fio-tests` role, which formats or mounts test storage, generates fio job files, runs fio workloads, and collects result archives. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `fio-tests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated as a benchmark workflow role. It depends on fio, optional plotting packages, filesystem tools, generated job templates, remote archive/fetch operations, and localhost result directories.

## Risks
High-risk areas are destructive mkfs/unmount operations, long-running async fio jobs, CPU/cache tuning assumptions, and result archive/fetch path mismatches. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/debian/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fio-tests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install fio for Debian/Ubuntu`, `Install graphing dependencies for Debian/Ubuntu`. Important modules/directives include `become`, `name`, `package`, `state`, `when`. The role-level integration surface is the `fio-tests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install fio for Debian/Ubuntu`, `Install graphing dependencies for Debian/Ubuntu`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/Ubuntu`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a benchmark workflow role. It depends on fio, optional plotting packages, filesystem tools, generated job templates, remote archive/fetch operations, and localhost result directories.

## Risks
High-risk areas are destructive mkfs/unmount operations, long-running async fio jobs, CPU/cache tuning assumptions, and result archive/fetch path mismatches.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fio-tests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Include distribution-specific installation tasks`. Important modules/directives include `include_tasks`. Includes/imports delegate to `{{ ansible_os_family | lower }}/main.yml`. Key variable inputs observed in this file include `ansible_os_family`. The role-level integration surface is the `fio-tests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Include distribution-specific installation tasks`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/main.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a benchmark workflow role. It depends on fio, optional plotting packages, filesystem tools, generated job templates, remote archive/fetch operations, and localhost result directories.

## Risks
High-risk areas are destructive mkfs/unmount operations, long-running async fio jobs, CPU/cache tuning assumptions, and result archive/fetch path mismatches.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/redhat/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fio-tests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install fio for RHEL/CentOS/Fedora`, `Install graphing dependencies for RHEL/CentOS/Fedora`. Important modules/directives include `become`, `name`, `package`, `state`, `when`. The role-level integration surface is the `fio-tests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install fio for RHEL/CentOS/Fedora`, `Install graphing dependencies for RHEL/CentOS/Fedora`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/CentOS/Fedora`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a benchmark workflow role. It depends on fio, optional plotting packages, filesystem tools, generated job templates, remote archive/fetch operations, and localhost result directories.

## Risks
High-risk areas are destructive mkfs/unmount operations, long-running async fio jobs, CPU/cache tuning assumptions, and result archive/fetch path mismatches.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/suse/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fio-tests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install fio for SUSE`, `Install graphing dependencies for SUSE`. Important modules/directives include `become`, `name`, `package`, `state`, `when`. The role-level integration surface is the `fio-tests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install fio for SUSE`, `Install graphing dependencies for SUSE`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a benchmark workflow role. It depends on fio, optional plotting packages, filesystem tools, generated job templates, remote archive/fetch operations, and localhost result directories.

## Risks
High-risk areas are destructive mkfs/unmount operations, long-running async fio jobs, CPU/cache tuning assumptions, and result archive/fetch path mismatches.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/main.yaml -->
# sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/main.yaml

## Purpose
Main task orchestration for the `fio-tests` role, which formats or mounts test storage, generates fio job files, runs fio workloads, and collects result archives. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Install dependencies`, `Ensure data_dir has correct ownership`, `Resolve per-host filesystem configuration`, `Set filesystem-specific mkfs and mount options`, `Set derived configuration variables`, `Check if {{ fio_tests_fs_device }} is mounted`, `Unmount {{ fio_tests_fs_device }} if mounted`, `Create filesystem on {{ fio_tests_fs_device }}`, `Create mount point directory`, `Mount filesystem`, `Set filesystem mount ownership`, `Create results directory`; plus 23 more. Important modules/directives include `Result`, `args`, `async`, `async_status`, `become`, `become_method`, `block_size`, `changed_when`, `command`, `creates`, `debug`, `delay`; plus 59 more. Includes/imports delegate to `install-deps/main.yml`, `name: create_data_partition`, `name: common`. Key variable inputs observed in this file include `data_group`, `data_path`, `data_user`, `fio_job`, `fio_tests_block_ranges`, `fio_tests_block_sizes`, `fio_tests_device`, `fio_tests_effective_block_sizes`, `fio_tests_enable_bs_ranges`, `fio_tests_fs_device`, `fio_tests_fs_label`, `fio_tests_fs_mount_point`, `fio_tests_fs_type`, `fio_tests_io_depths`; plus 12 more. The role-level integration surface is the `fio-tests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install dependencies`, `Ensure data_dir has correct ownership`, `Resolve per-host filesystem configuration`, `Set filesystem-specific mkfs and mount options`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `file`, `fetch`, `mount`. Notable path references include `/bw_`, `/cpufreq/scaling_governor`, `/dev/disk/by-id/virtio-kdevops2`, `/dev/null`, `/fio-tests-results-{{`, `/iops_`, `/jobs`, `/jobs/`; plus 4 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a benchmark workflow role. It depends on fio, optional plotting packages, filesystem tools, generated job templates, remote archive/fetch operations, and localhost result directories. Shell/command integration points observed here include `findmnt --noheadings --output TARGET --source {{ fio_tests_fs_device }}`, `umount {{ fio_tests_fs_device }}`, `>`, `uname -r`, `|`, `|`, `ls {{ fio_tests_results_dir }}/jobs/*.ini 2>/dev/null | wc -l`, `|`; plus 1 more.

## Risks
High-risk areas are destructive mkfs/unmount operations, long-running async fio jobs, CPU/cache tuning assumptions, and result archive/fetch path mismatches. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations; result collection can silently miss files when paths or host-derived names differ.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory; verify block-device and mount topology before and after the run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fio-tests/tasks/main.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests/defaults/main.yml

## Purpose
Defines default variables for the `fstests` role, which builds and runs xfstests/oscheck workflows across local, block, NFS, CIFS, sparse-file, and NVMe-backed configurations, then copies result artifacts back to the workflow tree. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. Key variable inputs observed in this file include `data_path`, `kdevops_fstests_setup_name`. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory; check target systemd unit state after the role.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/handlers/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests/handlers/main.yml

## Purpose
Main task orchestration for the `fstests` role, which builds and runs xfstests/oscheck workflows across local, block, NFS, CIFS, sparse-file, and NVMe-backed configurations, then copies result artifacts back to the workflow tree. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Restart watchdog daemon`. Important modules/directives include `name`, `service`, `state`. Key variable inputs observed in this file include `watchdog_service_name`. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Restart watchdog daemon`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/handlers/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/scripts/add-suse-repo-if-not-found.sh -->
# sources/test-tools/kdevops/playbooks/roles/fstests/scripts/add-suse-repo-if-not-found.sh

## Purpose
Helper script invoked by the `fstests` role to bridge a distribution-specific setup gap that is awkward to express directly in Ansible.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
The script executes linearly: validate/derive repository input, check whether a matching SUSE repository already exists, add it when missing, and return shell exit status to the Ansible caller.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/bin/bash`, `/dev/null`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/scripts/add-suse-repo-if-not-found.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/debian/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional extra_args file`, `Update apt cache`, `Install NVMe tools`, `Install fstests build dependencies`, `Install dependencies for building xfsprogs`. Important modules/directives include `apt`, `become`, `become_method`, `ignore_errors`, `include_vars`, `name`, `skip`, `state`, `tags`, `update_cache`, `when`, `with_first_found`. Key variable inputs observed in this file include `item`, `pkg_libaio`. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional extra_args file`, `Update apt cache`, `Install NVMe tools`, `Install fstests build dependencies`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/extra_vars.json`, `/extra_vars.yaml`, `/extra_vars.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory; verify block-device and mount topology before and after the run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Ensure required /media/ directories are created`, `Oscheck distribution ospecific setup`. Important modules/directives include `become`, `become_method`, `file`, `import_tasks`, `name`, `path`, `state`, `when`, `with_items`. Includes/imports delegate to `name: pkg`, `tasks/install-deps/debian/main.yml`, `tasks/install-deps/suse/main.yml`, `tasks/install-deps/redhat/main.yml`. Key variable inputs observed in this file include `item`, `sparsefiles_path`. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Ensure required /media/ directories are created`, `Oscheck distribution ospecific setup`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `file`. Notable path references include `/install-deps/debian/main.yml`, `/install-deps/redhat/main.yml`, `/install-deps/suse/main.yml`, `/media/`, `/media/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/redhat/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Enable the CodeReady repo`, `Enable installation of packages from EPEL`, `Install build dependencies for fstests`, `Install xfsprogs-xfs_scrub`, `Install btrfs-progs`, `Install dependencies for building xfsprogs`. Important modules/directives include `become`, `become_flags`, `become_method`, `delay`, `dnf`, `enablerepo`, `include_role`, `name`, `packages`, `register`, `retries`, `until`; plus 3 more. Includes/imports delegate to `name: codereadyrepo`, `name: epel-release`. Key variable inputs observed in this file include `packages`. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Enable the CodeReady repo`, `Enable installation of packages from EPEL`, `Install build dependencies for fstests`, `Install xfsprogs-xfs_scrub`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory; verify block-device and mount topology before and after the run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/suse/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `By default we assume we have figured out how to add repos on a release`, `Lets us disable things which require a zypper repo present`, `The default is to assume all distros have the indent package`, `Does this release lack indent`, `The default is to assume all distros supports nvme-utils`, `Does this release lack nvme-utils`, `Install nvme tools`, `Install build dependencies for fstests`, `Install indent when we have it`; plus 13 more. Important modules/directives include `add_benchmark_repo`, `badname_arg`, `become`, `become_method`, `cmd`, `enabled`, `has_indent`, `is_leap`, `is_sle`, `is_sle10`, `is_sle10sp3`, `is_sle11`; plus 20 more. Key variable inputs observed in this file include `ansible_distribution_major_version`, `ansible_distribution_version`, `role_path`. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `By default we assume we have figured out how to add repos on a release`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `systemd`. Notable path references include `//download.opensuse.org/repositories/benchmark/SLE_12_SP5/`, `//download.opensuse.org/repositories/benchmark/SLE_15_SP2/`, `//download.opensuse.org/repositories/benchmark/SLE_15_SP3/`, `/scripts/add-suse-repo-if-not-found.sh`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory; check target systemd unit state after the role; verify block-device and mount topology before and after the run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests/tasks/main.yml

## Purpose
Main task orchestration for the `fstests` role, which builds and runs xfstests/oscheck workflows across local, block, NFS, CIFS, sparse-file, and NVMe-backed configurations, then copies result artifacts back to the workflow tree. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional extra_args file`, `Install dependencies`, `Check if there's an existing xfsprogs directory`, `Set up an iSCSI initiator on target nodes`, `Get nproc`, `Ensure xfsprogs is not root owned`, `Clean old xfsprogs build`, `Clone xfsprogs git repository`, `Configure xfsprogs`, `Build xfsprogs`, `Install xfsprogs`, `Check if there's an existing xfsdump directory`; plus 126 more. Important modules/directives include `DIST_ROOT`, `FSTESTS_EXCLUDE_TEST_GROUPS`, `FSTESTS_LINUX_LOCALVERSION`, `FSTESTS_RUN_AUTO_GROUP_TESTS`, `FSTESTS_RUN_CUSTOM_GROUP_TESTS`, `FSTESTS_RUN_LARGE_DISK_TESTS`, `FSTESTS_SETUP_SYSTEM`, `FSTESTS_SPARSE_FILENAME_PREFIX`, `FSTESTS_SPARSE_FILE_PATH`, `FSTESTS_SPARSE_FILE_SIZE`, `FSTESTS_TESTDEV_SPARSEFILE_GENERATION`, `FSTYP`; plus 147 more. Includes/imports delegate to `name: create_data_partition`, `install-deps/main.yml`, `name: iscsi`, `name: common`, `name: create_partition`, `name: compile_dbench`, `name: nfsd_add_export`, `name: nfsd_add_export`; plus 4 more. Key variable inputs observed in this file include `all_limit_tests`, `ansible_host`, `bad_dmesg_file_stats`, `bad_full_file_stats`, `badname_arg`, `checklog_files`, `checktime_files`, `data_group`, `data_path`, `data_user`, `dev_bash_config`, `dynamic_limit_tests`, `exclude_test_groups`, `failed_tests`; plus 86 more. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional extra_args file`, `Install dependencies`, `Check if there's an existing xfsprogs directory`, `Set up an iSCSI initiator on target nodes`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `copy`, `file`, `lineinfile`, `systemd`, `fetch`, `git`, `parted`. Notable path references include `/../.config`, `/../last-kernel.txt`, `/../monitoring/tasks/monitor_collect.yml`, `/../monitoring/tasks/monitor_run.yml`, `/.begin`, `//github.com/linux-kdevops/dbench.git`, `//{{`, `/bad_results.txt`; plus 4 more. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts. Shell/command integration points observed here include `nproc`, `git clean -f -x -d`, `git clean -f -x -d`, `{{ make }} install`, `make configure`, `./configure --prefix={{ fstests_data_prefix }}`, `nproc`, `{{ make }} install`; plus 15 more.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations; text edits to system config can drift when upstream distro defaults change; result collection can silently miss files when paths or host-derived names differ.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory; check target systemd unit state after the role; verify block-device and mount topology before and after the run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/templates/.kdevops_fstests_setup -->
# sources/test-tools/kdevops/playbooks/roles/fstests/templates/.kdevops_fstests_setup

## Purpose
Template/configuration input consumed by the `fstests` role. It persists runtime settings on the target host rather than executing control flow itself.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. Key variable inputs observed in this file include `ansible_host`, `fstests_fstyp`, `fstests_nfs_server_host`, `fstests_setup_system`, `run_auto_group_tests`, `run_custom_group_tests`, `run_large_disk_tests`, `sparsefiles_filename_prefix`, `sparsefiles_generation`, `sparsefiles_path`, `sparsefiles_size`. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no Ansible control flow in the template/config file. Control flow happens in the task that installs it; once deployed, the target service or shell sources/reads it at runtime.

## State and Persistence Behavior
State persists wherever the installing task writes this file. Relevant literal paths in or around the file include `//`, `/bin/bash`, `/configs`, `/etc/xfsqa.config`, `/export`, `/g`, `/p`, `/var/lib/xfstests}`; plus 1 more.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include render the template with representative variables; validate the consuming service or shell can parse/read the deployed file; confirm ownership and mode from the installing task.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/templates/.kdevops_fstests_setup -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/templates/64-btrfs-zoned.rules -->
# sources/test-tools/kdevops/playbooks/roles/fstests/templates/64-btrfs-zoned.rules

## Purpose
Template/configuration input consumed by the `fstests` role. It persists runtime settings on the target host rather than executing control flow itself.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no Ansible control flow in the template/config file. Control flow happens in the task that installs it; once deployed, the target service or shell sources/reads it at runtime.

## State and Persistence Behavior
State persists wherever the installing task writes this file. Relevant literal paths in or around the file include `/scheduler}`, `/zoned}`.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include render the template with representative variables; validate the consuming service or shell can parse/read the deployed file; confirm ownership and mode from the installing task.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/templates/64-btrfs-zoned.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/templates/nfs/nfsmount.conf -->
# sources/test-tools/kdevops/playbooks/roles/fstests/templates/nfs/nfsmount.conf

## Purpose
Template/configuration input consumed by the `fstests` role. It persists runtime settings on the target host rather than executing control flow itself.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `fstests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no Ansible control flow in the template/config file. Control flow happens in the task that installs it; once deployed, the target service or shell sources/reads it at runtime.

## State and Persistence Behavior
State persists wherever the installing task writes this file. Relevant literal paths in or around the file include none detected.

## Dependencies and Integration Points
Integrated as a heavyweight filesystem validation workflow. It depends on distro package roles, kdevops/fstests/xfsprogs/xfsdump git repositories, storage/NFS/SMB/iSCSI helper roles, generated config templates, monitoring tasks, and result-analysis Python scripts.

## Risks
High-risk areas are destructive storage setup, generated config correctness, root environment propagation, ignored oscheck failures, large artifact handling, and post-run expunge augmentation. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include render the template with representative variables; validate the consuming service or shell can parse/read the deployed file; confirm ownership and mode from the installing task.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests/templates/nfs/nfsmount.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/defaults/main.yml

## Purpose
Defines default variables for the `fstests_prep_localhost` role, which installs localhost-side tooling needed to orchestrate fstests and post-process results. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `fstests_prep_localhost` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated on localhost before driving fstests. It installs Ansible-side packages and Python result tooling such as junitparser.

## Risks
The main risk is missing localhost packages causing late result parsing or orchestration failures rather than target setup failures. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/debian/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests_prep_localhost` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install local dependencies for fstests command and control`. Important modules/directives include `apt`, `become`, `become_method`, `name`. The role-level integration surface is the `fstests_prep_localhost` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install local dependencies for fstests command and control`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated on localhost before driving fstests. It installs Ansible-side packages and Python result tooling such as junitparser.

## Risks
The main risk is missing localhost packages causing late result parsing or orchestration failures rather than target setup failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests_prep_localhost` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Oscheck distribution ospecific setup`. Important modules/directives include `import_tasks`, `when`. Includes/imports delegate to `tasks/install-deps/debian/main.yml`, `tasks/install-deps/suse/main.yml`, `tasks/install-deps/redhat/main.yml`. The role-level integration surface is the `fstests_prep_localhost` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Oscheck distribution ospecific setup`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/install-deps/debian/main.yml`, `/install-deps/redhat/main.yml`, `/install-deps/suse/main.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated on localhost before driving fstests. It installs Ansible-side packages and Python result tooling such as junitparser.

## Risks
The main risk is missing localhost packages causing late result parsing or orchestration failures rather than target setup failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/redhat/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests_prep_localhost` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Install local dependencies for fstests command and control`, `Install junitparser`. Important modules/directives include `become`, `become_method`, `delay`, `dnf`, `name`, `packages`, `pip`, `register`, `retries`, `tags`, `until`, `update_cache`; plus 2 more. Key variable inputs observed in this file include `packages`. The role-level integration surface is the `fstests_prep_localhost` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install local dependencies for fstests command and control`, `Install junitparser`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated on localhost before driving fstests. It installs Ansible-side packages and Python result tooling such as junitparser.

## Risks
The main risk is missing localhost packages causing late result parsing or orchestration failures rather than target setup failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/suse/main.yml

## Purpose
Installs the distribution-specific prerequisites for the `fstests_prep_localhost` role. It maps kdevops workflow needs onto package-manager operations and prerequisite repository setup so later tasks can assume the needed commands and libraries exist.

## Important APIs, Types, and Functions
Ansible task entry points include `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `By default we assume we have figured out how to add repos on a release`, `Lets us disable things which require a zypper repo present`, `Install local dependencies for fstests command and control`, `Install junitparser`. Important modules/directives include `become`, `become_method`, `is_leap`, `is_sle`, `is_sle10`, `is_sle10sp3`, `is_sle11`, `is_sle11sp1`, `is_sle11sp4`, `is_sle12`, `is_sle12sp1`, `is_sle12sp3`; plus 12 more. Key variable inputs observed in this file include `ansible_distribution_major_version`, `ansible_distribution_version`. The role-level integration surface is the `fstests_prep_localhost` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `By default we assume we have figured out how to add repos on a release`, `Lets us disable things which require a zypper repo present`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated on localhost before driving fstests. It installs Ansible-side packages and Python result tooling such as junitparser.

## Risks
The main risk is missing localhost packages causing late result parsing or orchestration failures rather than target setup failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; validate package installation on the matching distro family; confirm later role commands are present in PATH.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/main.yml

## Purpose
Main task orchestration for the `fstests_prep_localhost` role, which installs localhost-side tooling needed to orchestrate fstests and post-process results. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional extra_args file`, `Install our own fstests localhost dependencies`. Important modules/directives include `ignore_errors`, `include_tasks`, `include_vars`, `skip`, `tags`, `with_first_found`. Includes/imports delegate to `install-deps/main.yml`. Key variable inputs observed in this file include `item`. The role-level integration surface is the `fstests_prep_localhost` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional extra_args file`, `Install our own fstests localhost dependencies`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/extra_vars.json`, `/extra_vars.yaml`, `/extra_vars.yml`, `/main.yml`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated on localhost before driving fstests. It installs Ansible-side packages and Python result tooling such as junitparser.

## Risks
The main risk is missing localhost packages causing late result parsing or orchestration failures rather than target setup failures. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_hosts/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/gen_hosts/defaults/main.yml

## Purpose
Defines default variables for the `gen_hosts` role, which renders Ansible inventory and workflow host files from kdevops configuration, enabled workflows, and provider state. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `gen_hosts` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated in inventory generation before playbook execution. It consumes variables from `.config`/extra vars, enabled workflow flags, provider addressing, and Jinja templates under `templates/`.

## Risks
The main risks are stale generated inventory, host/group naming transformations, provider address assumptions, and enabled workflow flags diverging from node generation. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_hosts/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_hosts/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/gen_hosts/tasks/main.yml

## Purpose
Main task orchestration for the `gen_hosts` role, which renders Ansible inventory and workflow host files from kdevops configuration, enabled workflows, and provider state. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional extra_args file`, `Parse declared hosts list when using declared hosts`, `Get our user`, `Get our primary group`, `Check if the inventory file exists already`, `Ensure proper permission on the inventory file`, `Verify Ansible inventory template file exists`, `Set fstests config file variable for {{ fstests_fstyp }}`, `Verify fstest config file exists`, `Infer enabled fstests test section types`, `Infer enabled blktests test section types`, `Debug inferring block test types`; plus 20 more. Important modules/directives include `all_generic_nodes`, `become`, `become_flags`, `become_method`, `blktests_enabled_test_types`, `build_linux_enabled_section_types`, `clean_section_lines`, `command`, `config_prefix`, `debug`, `dest`, `enabled_fs`; plus 53 more. Key variable inputs observed in this file include `ansible_cfg_inventory`, `build_linux_nodes`, `clean_section_lines`, `enabled_fs`, `enabled_fs_sections`, `enabled_fs_sysbench`, `enabled_sysbench_tests`, `fio_tests_node_names`, `fs`, `fs_config_data`, `fs_config_path`, `fs_config_role_path`, `fs_section_variables`, `fstests_fstyp`; plus 22 more. The role-level integration surface is the `gen_hosts` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional extra_args file`, `Parse declared hosts list when using declared hosts`, `Get our user`, `Get our primary group`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `file`. Notable path references include `/.config`, `/extra_vars.json`, `/extra_vars.yaml`, `/extra_vars.yml`, `/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated in inventory generation before playbook execution. It consumes variables from `.config`/extra vars, enabled workflow flags, provider addressing, and Jinja templates under `templates/`. Shell/command integration points observed here include `whoami`, `id -g -n`.

## Risks
The main risks are stale generated inventory, host/group naming transformations, provider address assumptions, and enabled workflow flags diverging from node generation. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_hosts/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/gen_nodes/defaults/main.yml

## Purpose
Defines default variables for the `gen_nodes` role, which renders kdevops node definitions, Terraform inputs, guestfs/libvirt XML support, and workflow-specific node subsets. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `gen_nodes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated before provisioning. It consumes workflow enablement variables, cloud/guestfs/NixOS settings, filesystem test choices, PCI passthrough inputs, and emits node lists or templates consumed by Terraform/libvirt/Ansible.

## Risks
The main risks are incorrect node-count/list expansion, provider template mismatches, PCI address formatting, and generated node files becoming inconsistent with inventory templates. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation; verify block-device and mount topology before and after the run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/python/gen_pcie_passthrough_guestfs_xml.py -->
# sources/test-tools/kdevops/playbooks/roles/gen_nodes/python/gen_pcie_passthrough_guestfs_xml.py

## Purpose
Python helper for generating libvirt guest XML fragments for PCIe passthrough. It converts declarative host/device arguments into a guestfs-compatible XML device stanza.

## Important APIs, Types, and Functions
Python functions include `main`. The role-level integration surface is the `gen_nodes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
The helper parses command-line arguments, builds an XML tree for PCI host-device passthrough, derives domain/bus/slot/function addresses, and prints/writes the generated XML for the caller.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/extra_vars.yaml`, `/hostdev`, `/source`, `/usr/bin/python3`, `/{extra_vars`, `/{name}/pcie_passthrough_`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated before provisioning. It consumes workflow enablement variables, cloud/guestfs/NixOS settings, filesystem test choices, PCI passthrough inputs, and emits node lists or templates consumed by Terraform/libvirt/Ansible.

## Risks
The main risks are incorrect node-count/list expansion, provider template mismatches, PCI address formatting, and generated node files becoming inconsistent with inventory templates.

## Test Signals
Useful test signals include run the helper with representative PCI addresses; parse the emitted XML; validate the generated XML with libvirt tooling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/python/gen_pcie_passthrough_guestfs_xml.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/gitr.yml -->
# sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/gitr.yml

## Purpose
Main task orchestration for the `gen_nodes` role, which renders kdevops node definitions, Terraform inputs, guestfs/libvirt XML support, and workflow-specific node subsets. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Initialize the enabled nodes list for gitr`, `Expand the gitr node list to include -dev nodes`, `Add the kdevops NFS server to the enabled nodes list`, `Add an iSCSI target to the enabled nodes list`, `Generate the kdevops nodes file using {{ kdevops_nodes_template }}`. Important modules/directives include `all_generic_nodes`, `dest`, `force`, `gitr_enabled_nodes`, `mode`, `node_template`, `nodes`, `set_fact`, `src`, `template`, `vars`, `when`; plus 1 more. Key variable inputs observed in this file include `all_generic_nodes`, `gitr_enabled_nodes`, `gitr_enabled_test_groups`, `kdevops_nodes`, `kdevops_nodes_template`, `node_template`, `topdir_path`. The role-level integration surface is the `gen_nodes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Initialize the enabled nodes list for gitr`, `Expand the gitr node list to include -dev nodes`, `Add the kdevops NFS server to the enabled nodes list`, `Add an iSCSI target to the enabled nodes list`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `template`. Notable path references include `/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated before provisioning. It consumes workflow enablement variables, cloud/guestfs/NixOS settings, filesystem test choices, PCI passthrough inputs, and emits node lists or templates consumed by Terraform/libvirt/Ansible.

## Risks
The main risks are incorrect node-count/list expansion, provider template mismatches, PCI address formatting, and generated node files becoming inconsistent with inventory templates.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/gitr.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/ltp.yml -->
# sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/ltp.yml

## Purpose
Main task orchestration for the `gen_nodes` role, which renders kdevops node definitions, Terraform inputs, guestfs/libvirt XML support, and workflow-specific node subsets. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Initialize the enabled nodes list for ltp`, `Expand the ltp node list to include -dev nodes`, `Generate the kdevops nodes file using {{ kdevops_nodes_template }}`. Important modules/directives include `all_generic_nodes`, `dest`, `force`, `ltp_enabled_nodes`, `mode`, `node_template`, `nodes`, `set_fact`, `src`, `template`, `vars`, `when`; plus 1 more. Key variable inputs observed in this file include `all_generic_nodes`, `kdevops_nodes`, `kdevops_nodes_template`, `ltp_enabled_nodes`, `ltp_enabled_test_groups`, `node_template`, `topdir_path`. The role-level integration surface is the `gen_nodes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Initialize the enabled nodes list for ltp`, `Expand the ltp node list to include -dev nodes`, `Generate the kdevops nodes file using {{ kdevops_nodes_template }}`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `template`. Notable path references include `/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated before provisioning. It consumes workflow enablement variables, cloud/guestfs/NixOS settings, filesystem test choices, PCI passthrough inputs, and emits node lists or templates consumed by Terraform/libvirt/Ansible.

## Risks
The main risks are incorrect node-count/list expansion, provider template mismatches, PCI address formatting, and generated node files becoming inconsistent with inventory templates.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/ltp.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/main.yml

## Purpose
Main task orchestration for the `gen_nodes` role, which renders kdevops node definitions, Terraform inputs, guestfs/libvirt XML support, and workflow-specific node subsets. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional extra_args file`, `Get our user`, `Get our primary group`, `Create guestfs directory`, `Create nixos directory`, `Verify Ansible nodes template file exists {{ kdevops_nodes_template_full_path }}`, `Set generic nodes array`, `Set generic nodes array on dual baseline and dev systems`, `Set builder nodes array`, `Set iscsi_nodes list`, `Add an iSCSI target`, `Set nfsd_nodes list`; plus 80 more. Important modules/directives include `ai_enabled_section_types`, `ai_multifs_enabled_configs`, `all_fs_configs`, `all_generic_nodes`, `all_nodes`, `args`, `become`, `become_flags`, `become_method`, `blktests_enabled_test_types`, `btrfs_configs`, `btrfs_std_enabled`; plus 108 more. Includes/imports delegate to `name: gen_nodes`, `name: gen_nodes`, `name: gen_nodes`. Key variable inputs observed in this file include `ai_enabled_section_types`, `all_fs_configs`, `all_generic_nodes`, `all_nodes`, `blktests_enabled_test_types`, `build_linux_enabled_section_types`, `builder_nodes`, `clean_section_lines`, `clean_section_lines_without_fsname`, `config_block_test_types`, `config_mmtests_test_types`, `config_sections_targets`, `config_selftests_test_types`, `config_val`; plus 48 more. The role-level integration surface is the `gen_nodes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional extra_args file`, `Get our user`, `Get our primary group`, `Create guestfs directory`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `file`, `lineinfile`. Notable path references include `/.config`, `/bin/bash`, `/extra_vars.json`, `/extra_vars.yaml`, `/extra_vars.yml`, `/guestfs/{{`, `/python/gen_pcie_passthrough_guestfs_xml.py`, `/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated before provisioning. It consumes workflow enablement variables, cloud/guestfs/NixOS settings, filesystem test choices, PCI passthrough inputs, and emits node lists or templates consumed by Terraform/libvirt/Ansible. Shell/command integration points observed here include `whoami`, `id -g -n`, `timedatectl show -p Timezone --value`, `|`, `set -o pipefail && ss -ltn | grep ':{{ (libvirt_gdb_baseport | int) + (idx | int) }} '`.

## Risks
The main risks are incorrect node-count/list expansion, provider template mismatches, PCI address formatting, and generated node files becoming inconsistent with inventory templates. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation; verify block-device and mount topology before and after the run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/main.yml -->
