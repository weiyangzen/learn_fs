<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-bash.am -->
## sources/cloud-native/ostree/Makefile-bash.am

### Purpose
This automake fragment installs Bash completion support for the `ostree` command.

### APIs, Types, and Control Flow
It sets `completionsdir` from `@BASH_COMPLETIONSDIR@` and installs `bash/ostree` as distributed completion data. It adds a distcheck configure override so test installs under a temporary prefix resolve the bash-completion directory under `${datadir}`.

### State, Dependencies, and Integration
There is no runtime state. It depends on configure substituting `BASH_COMPLETIONSDIR` and is included by top-level `Makefile.am`.

### Risks and Test Signals
The main risk is incorrect configure substitution or distro-specific completion paths. Test signal is `make distcheck` and package install content containing the completion file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-bash.am -->
