# sources/cloud-native/ostree/man/ostree-admin-instutil.xml

Purpose: documents installer-oriented utility subcommands under `ostree admin instutil`.

Important APIs/types: synopsis `ostree admin instutil SUBCOMMAND ARGS`; subcommands `selinux-ensure-labeled SUBPATH PREFIX` and `set-kargs` with `--merge`, `--import-proc-cmdline`, `--append`, `--replace`, and append args.

Control flow: docs describe SELinux relabeling based on first deployment policy and kernel argument replacement/merge behavior for the default deployment.

State and persistence: can relabel files and persist kernel argument changes in deployment boot metadata.

Dependencies and integration: used by OS installers, SELinux policy, deployment boot config, and initramfs/kernel argument workflows.

Risks and test signals: risk is installer breakage if option docs drift from CLI parser. Signals are install tests for SELinux labels and kargs merge/replace behavior.
