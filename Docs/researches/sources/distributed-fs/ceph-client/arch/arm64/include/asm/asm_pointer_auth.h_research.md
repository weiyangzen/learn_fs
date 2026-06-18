## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm_pointer_auth.h

### Purpose
Defines assembly macros for installing and initializing ARM64 pointer authentication keys.

### Important APIs, Types, And Functions
Important macros include `__ptrauth_keys_install_kernel_nosync`, `ptrauth_keys_install_kernel_nosync`, `ptrauth_keys_install_kernel`, `__ptrauth_keys_install_user`, `__ptrauth_keys_init_cpu`, and `ptrauth_keys_init_cpu`.

### Control Flow
When kernel pointer auth is enabled and address-auth capability is present, macros load kernel APIA key halves from the current task and write `APIAKEYLO/HI_EL1`, optionally followed by `isb`. User-key macros load user keys from thread storage. CPU init reads ID registers, enables SCTLR pointer-auth bits, installs kernel keys, and skips work via alternatives if address auth is absent.

### State, Persistence, And Dependencies
State is in task thread key storage and pointer-auth system registers. Dependencies include alternative patching, generated asm offsets, cpufeature constants, and sysreg encodings.

### Integration Points
Used by entry, context switch, CPU init, and pointer-auth enable paths.

### Risks
Wrong offsets or missing ISB can leave stale keys active. Capability alternatives must not execute pointer-auth system-register writes on unsupported CPUs. Key installation must track task switches exactly.

### Test Signals
Boot with pointer-auth configs on capable and incapable hardware, run context-switch stress, kernel PAC fault tests, userspace PAC tests, and objdump checks for patched alternatives.
