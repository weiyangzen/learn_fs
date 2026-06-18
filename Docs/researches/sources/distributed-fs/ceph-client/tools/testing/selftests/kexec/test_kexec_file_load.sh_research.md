# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_file_load.sh

`test_kexec_file_load.sh` validates `kexec_file_load` behavior against Secure Boot, IMA appraisal, architecture policy, PE signatures, IMA xattrs, appended module signatures, and platform keyring availability.

It sources `kexec_common_lib.sh` and uses `kexec --load --kexec-file-syscall`, `kexec --unload --kexec-file-syscall`, `pesign`, `getfattr`, `tail`, and config/policy probes. Main functions are `is_ima_sig_required()`, `check_for_pesig()`, `check_for_imasig()`, `check_for_modsig()`, and `kexec_file_load_test()`.

The script requires root, extracts kernel config, skips when `CONFIG_KEXEC_FILE` is absent, records policy booleans, detects Secure Boot, checks signatures on the current kernel image, and attempts a file-syscall kexec load. On success it unloads and verifies success is allowed by signature policy. On failure it maps missing keys or missing required signatures to expected pass outcomes.

State changes are a transient loaded kexec image and temporary config extraction. Dependencies are `kexec-tools`, `/boot/vmlinuz-$(uname -r)`, config extraction, optional `pesign` and `getfattr`, IMA/securityfs policy access, Secure Boot state, and platform keyrings. Risks are environment-sensitive tool availability and interpreting expected rejection as pass. Strong signals are pass logs explaining why success or failure matched policy.
