# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/kexec_common_lib.sh

`kexec_common_lib.sh` is the shared library for kexec selftest scripts. It centralizes logging, kselftest exit handling, root checks, kernel config discovery, Secure Boot detection, securityfs mounting, and IMA policy matching.

Important variables are `VERBOSE`, `IKCONFIG`, `KERNEL_IMAGE`, and `SECURITYFS`. Important functions include `log_info()`, `log_pass()`, `log_fail()`, `log_skip()`, `get_efivarfs_secureboot_mode()`, `get_ppc64_secureboot_mode()`, `get_arch()`, `get_secureboot_mode()`, `require_root_privileges()`, `kconfig_enabled()`, `get_kconfig()`, `mount_securityfs()`, and `check_ima_policy()`.

Consumers source the file and call helpers. `get_kconfig()` searches module config, `/proc/config.gz`, and `extract-ikconfig` against the boot image or `configs.ko`. Secure Boot detection reads EFI variables or a ppc64le device-tree file. `check_ima_policy()` mounts securityfs if needed and greps IMA policy for action/key constraints. State includes a temporary extracted config and potential securityfs mount.

Dependencies are root for some operations, `grep`, `awk`, `find`, `hexdump`, `cut`, `modprobe`, `gunzip`, `mount`, `extract-ikconfig`, a boot kernel image, efivarfs or ppc device-tree files, and IMA securityfs. Risks include intentionally inverted return semantics from `kconfig_enabled()` and unquoted shell variables in some tests. Pass signals are reliable config extraction and accurate policy/Secure Boot classification for downstream scripts.
