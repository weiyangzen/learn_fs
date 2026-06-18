# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_jump.sh

`test_kexec_jump.sh` gates and runs the x86_64 kexec jump helper. It avoids unsupported or unsafe policy configurations and reports the result through shared kexec logging helpers.

It sources `kexec_common_lib.sh`, calls `require_root_privileges()`, `get_kconfig()`, `kconfig_enabled()`, and `get_secureboot_mode()`, then executes `./test_kexec_jump`.

Control flow requires root, skips when `CONFIG_KEXEC_JUMP` is disabled, records IMA appraisal and architecture policy, detects Secure Boot, skips when Secure Boot and architecture IMA policy are both enabled, and otherwise runs the helper. It reports pass only on helper exit 0.

Dependencies are the common kexec library, generated helper binary, root, config extraction, and kexec jump support. Risk is that the helper can crash the system rather than returning failure. Signals are `kexec_jump succeeded`, skip for unsupported/unsafe configuration, or failure if the helper returns nonzero.
