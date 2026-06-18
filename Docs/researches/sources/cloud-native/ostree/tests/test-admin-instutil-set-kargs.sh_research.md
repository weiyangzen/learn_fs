# sources/cloud-native/ostree/tests/test-admin-instutil-set-kargs.sh

Purpose: tests `ostree admin instutil set-kargs` replacement, merge, replace, append, and proc-cmdline import behavior.

Important APIs/functions: `setup_os_repository`, `pull-local`, `admin deploy`, `admin instutil set-kargs`, options `--merge`, `--replace`, `--append`, `--import-proc-cmdline`, and loader entry regex assertions.

Control flow: deploys once, replaces all kargs, merges an additional duplicate, replaces matching `FOO`, appends multiple values including duplicates, and imports `/proc/cmdline` while skipping `ostree=`, `initrd=`, and `BOOT_IMAGE=` arguments.

State/persistence: edits the active bootloader entry in `sysroot/boot/loader/entries`. Dependencies include host proc cmdline and admin sysroot state.

Integration/risk/test signals: protects low-level installed-system karg editing. Risks are host-specific cmdline values and options ordering. Five TAP cases align with the command modes.
