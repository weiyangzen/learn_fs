<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/Makefile -->
# sources/distributed-fs/ceph-client/security/integrity/ima/Makefile

## Purpose
Defines how IMA object files are built and conditionally included based on kernel configuration.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_IMA) += ima.o ima_iint.o` builds the core IMA composite object and inode cache support.
- `ima-y` lists always-built core sources: securityfs, queue, init, main hooks, crypto, API, policy, template, and template library.
- Conditional additions include appraisal, module signatures, kexec, blacklist, asymmetric-key measurement, queued early boot keys, and EFI architecture policy.

## Control Flow
The kernel build system expands `ima-y` into the composite `ima.o`. Kconfig symbols determine whether optional source files become part of that object.

## State And Persistence
This file has no runtime state. It controls which code paths exist in the resulting kernel image.

## Dependencies And Integration Points
It maps Kconfig symbols to source files and therefore ties `Kconfig` decisions to link-time composition. EFI architecture policy is included only when both EFI and `IMA_SECURE_AND_OR_TRUSTED_BOOT` are enabled.

## Risks And Edge Cases
Incorrect object inclusion can produce unresolved symbols or silently remove expected enforcement features. Appraisal stubs in `ima.h` must remain consistent with optional object inclusion.

## Test Signals
Build output should include expected IMA objects for a given `.config`; link failures or missing runtime hooks indicate Kconfig/Makefile drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/Makefile -->
