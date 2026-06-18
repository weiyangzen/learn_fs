# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_load.sh

`test_kexec_load.sh` validates legacy `kexec_load` behavior under Secure Boot and IMA architecture policy. It expects legacy loading to fail when that policy combination requires blocking unsigned loads, and otherwise accepts a successful load.

It sources `kexec_common_lib.sh`, probes `CONFIG_KEXEC`, `CONFIG_IMA_APPRAISE`, `CONFIG_IMA_ARCH_POLICY`, and Secure Boot state, then runs `kexec --load $KERNEL_IMAGE` and `kexec --unload` on success.

Control flow requires root, extracts config, skips without `CONFIG_KEXEC`, records policy state, attempts a legacy kexec load, unloads on success, and compares outcome against policy. Kernel state is a transient loaded kexec image.

Dependencies are root, `kexec-tools`, a current kernel image, config extraction, and Secure Boot detection. Risks are policy interpretation and load failures from causes unrelated to signature policy. Pass signals explicitly distinguish expected success from expected failure under Secure Boot plus IMA arch policy.
