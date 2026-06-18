<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_efi.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_efi.c

## Purpose
Supplies architecture secure-boot IMA policy rules for EFI/secure-boot systems and enables kernel module and kexec signature enforcement when those rules are active.

## Important APIs, Types, And Functions
- `sb_arch_rules[]` contains secure-boot measurement/appraisal rules for kexec kernels, modules, and optionally IMA policy.
- `arch_get_ima_policy()` returns those rules when `CONFIG_IMA_ARCH_POLICY` is enabled and secure boot is active.

## Control Flow
At policy initialization time, IMA can call `arch_get_ima_policy()`. If secure boot is detected, this function enables module and kexec signature enforcement and returns the static rules; otherwise it returns `NULL`.

## State And Persistence
The rule array is static read-only policy data. Calls may change global kernel enforcement state for module and kexec signatures during the boot.

## Dependencies And Integration Points
Depends on `arch_get_secureboot()`, module signature enforcement, kexec signature enforcement, Kconfig symbols for module/kexec signature availability, machine keyring policy admission, and IMA architecture policy loading.

## Risks And Edge Cases
Rules vary by build options; if kernel module or kexec signature support is already compiled in, the corresponding appraisal rule may be omitted. Secure boot forces stricter behavior that can prevent unsigned module or kexec usage.

## Test Signals
On secure-boot systems, inspect loaded IMA policy for module/kexec measure and appraisal rules, verify unsigned modules/kexec images are denied when required, and confirm no architecture policy is returned when secure boot is off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_efi.c -->
