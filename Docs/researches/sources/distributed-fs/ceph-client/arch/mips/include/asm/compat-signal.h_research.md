<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compat-signal.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/compat-signal.h

**Purpose:** Converts signal sets between native and compat user layouts.

**Important APIs/types/functions:** `__copy_conv_sigset_to_user()` uses `put_compat_sigset`; `__copy_conv_sigset_from_user()` uses `get_compat_sigset`.

**Control flow:** Compile-time assertions ensure compat and native signal set sizes match and `_NSIG_WORDS == 2`.

**State, dependencies, integration:** Used by compat signal delivery and return paths.

**Risks and test signals:** Signal mask layout mismatches break 32-bit tasks on 64-bit kernels. Test compat signal mask save/restore and build assertions after signal type changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compat-signal.h -->
