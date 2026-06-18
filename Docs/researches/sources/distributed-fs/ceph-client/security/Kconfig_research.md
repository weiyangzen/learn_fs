# sources/distributed-fs/ceph-client/security/Kconfig

Purpose: `security/Kconfig` defines top-level Linux security configuration options and sources individual LSM and integrity Kconfig files.

Important APIs, types, and functions: options include `SECURITY_DMESG_RESTRICT`, the `/proc/pid/mem` override choice (`PROC_MEM_ALWAYS_FORCE`, `PROC_MEM_FORCE_PTRACE`, `PROC_MEM_NO_FORCE`), `MSEAL_SYSTEM_MAPPINGS`, `SECURITY`, `HAS_SECURITY_AUDIT`, `SECURITYFS`, `SECURITY_NETWORK`, `SECURITY_INFINIBAND`, `SECURITY_NETWORK_XFRM`, `SECURITY_PATH`, `INTEL_TXT`, `LSM_MMAP_MIN_ADDR`, `STATIC_USERMODEHELPER`, `STATIC_USERMODEHELPER_PATH`, legacy default major LSM choice, `LSM`, and `SECURITY_COMMONCAP_KUNIT_TEST`.

Control flow: Kconfig dependency/default logic gates each option. It sources `security/keys/Kconfig`, multiple LSM Kconfigs, `security/integrity/Kconfig`, and `security/Kconfig.hardening`. The `LSM` string default changes based on the legacy major LSM selection and controls runtime initialization order unless overridden by `lsm=`.

State and persistence: user selections persist in `.config` and generated headers, influencing compiled objects and runtime security behavior.

Dependencies and integration points: top-level integration for security subsystems, KUnit tests, usermode helper hardening, securityfs, audit, networking hooks, and architecture features.

Risks: defaults affect system security posture. `MSEAL_SYSTEM_MAPPINGS` explicitly breaks software such as checkpoint/restore, UML, gVisor, and rr, so dependencies are conservative. The `LSM` order string must stay synchronized with available LSMs and ordering rules.

Test signals: Kconfig dependency tests, allnoconfig/defconfig/allmodconfig builds, boot tests with default and custom `lsm=`, KUnit commoncap tests, and securityfs/LSM module runtime checks.
