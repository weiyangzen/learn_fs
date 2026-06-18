## sources/distributed-fs/ceph-client/security/selinux/include/ibpkey.h

### Purpose
`ibpkey.h` declares the SELinux Infiniband P_Key SID cache interface and provides no-op fallbacks when Infiniband security is not built.

### Important APIs, types, and functions
Under `CONFIG_SECURITY_INFINIBAND`, it declares `sel_ib_pkey_flush()` and `sel_ib_pkey_sid(u64 subnet_prefix, u16 pkey, u32 *sid)`. Without that config, it provides inline fallbacks where flush does nothing and SID lookup returns `SECINITSID_UNLABELED`.

### Control flow
Callers can unconditionally invoke the functions. The preprocessor chooses the real implementation in `ibpkey.c` or the fallback behavior.

### State and persistence
The header has no state. The real implementation caches P_Key mappings in memory; the fallback deliberately has no cache and treats all P_Keys as unlabeled.

### Dependencies and integration points
It includes Linux types and generated Flask initial SID constants. `hooks.c` uses it in Infiniband access checks and in the AVC reset callback.

### Risks
Fallback unlabeled behavior means builds without `CONFIG_SECURITY_INFINIBAND` cannot enforce policy-distinct P_Key labels. Callers must still check return codes in the real build.

### Test signals
Build both with and without `CONFIG_SECURITY_INFINIBAND`; verify hook compilation and runtime P_Key checks or unlabeled fallback behavior.
