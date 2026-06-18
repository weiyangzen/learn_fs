# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/Makefile

Purpose: builds the Lustre PTLRPC GSS security module object set.

Important APIs/types/functions: declares `obj-m += ptlrpc_gss.o` and composes `ptlrpc_gss-objs` from shared policy, bulk, client/server upcall, raw object, lproc, token, mechanism switch, Kerberos, null, and crypto objects. `gss_sk_mech.o` is included only under `CONFIG_LUSTRE_FS_GSS_SSK`; `gss_keyring.o` only under `CONFIG_LUSTRE_FS_GSS_KEYRING`; `GCOV_PROFILE := y` is enabled under `CONFIG_GCOV_PROFILE_LUSTRE`.

Control flow: no runtime control flow. Build-time conditionals decide which mechanisms and keyring policy are present in the module.

State/persistence: no runtime state. The build output determines which registration functions are linked and therefore which security mechanisms can initialize.

Dependencies/integration: integrates with the kernel module build system and the wider Lustre PTLRPC security policy registration path. It assumes objects such as `sec_gss.o` and `gss_svc_upcall.o` outside this work item provide common service-side support.

Risks/test signals: configuration mismatches can compile a module without expected mechanisms or keyring support. Build tests should cover default GSS, SSK enabled, keyring enabled, both enabled, and GCOV profile builds.
