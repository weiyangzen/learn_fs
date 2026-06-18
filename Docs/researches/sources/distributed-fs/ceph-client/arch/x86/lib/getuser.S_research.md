# sources/distributed-fs/ceph-client/arch/x86/lib/getuser.S

Purpose: implements low-level `__get_user_*` helpers that load 1, 2, 4, or 8 bytes from user memory and return both an error code and loaded value using a non-standard register ABI.

Important APIs/functions: exports `__get_user_1`, `__get_user_2`, `__get_user_4`, `__get_user_8`, and nocheck variants for each size. Local `__get_user_handle_exception` returns `-EFAULT` and zero value. Macros `check_range` and `UACCESS` implement address limiting and exception-table annotations.

Control flow: checked variants clamp/check the user pointer against `USER_PTR_MAX` on 64-bit or `TASK_SIZE_MAX` on 32-bit with nospec masking. They enable user access with `ASM_STAC`, perform the load under `_ASM_EXTABLE_UA`, clear access with `ASM_CLAC`, zero `%eax` for success, and return loaded data in `%edx` plus `%ecx` high half for 32-bit 8-byte loads. Nocheck variants omit range checks but include a speculation barrier alternative before load.

State and persistence behavior: no persistent state. Reads user memory and transiently toggles SMAP access state. Faults return zeroed value and `-EFAULT`.

Dependencies/integration points: core uaccess implementation, SMAP, runtime constants, nospec alternatives, exception tables, and exported helper ABI used by inline uaccess code.

Risks: ABI is unusual and register clobbers are constrained. Missing `CLAC` on fault would be a security bug; exception handler performs it. Range/nospec logic protects against out-of-range and speculative user pointer misuse. 32-bit 8-byte loads must zero high registers before faults.

Test signals: uaccess selftests for each size, fault injection, SMAP enabled tests, speculation mitigation configs, 32-bit and 64-bit builds, and objtool validation.
