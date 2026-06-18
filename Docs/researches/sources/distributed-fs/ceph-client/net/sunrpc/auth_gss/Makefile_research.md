# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/Makefile

## Purpose
This Makefile defines how the kernel builds the RPCSEC_GSS core module, the Kerberos 5 mechanism module, and optional Kerberos KUnit tests. It is the build-time integration point that decides which implementation files participate under `CONFIG_SUNRPC_GSS`, `CONFIG_RPCSEC_GSS_KRB5`, and `CONFIG_RPCSEC_GSS_KRB5_KUNIT_TEST`.

## Important APIs, Types, and Functions
There are no runtime APIs. The important build targets are `auth_rpcgss.o`, `rpcsec_gss_krb5.o`, and `gss_krb5_test.o`. `auth_rpcgss-y` combines client auth (`auth_gss.o`), the GSS mechanism switch (`gss_mech_switch.o`), server auth (`svcauth_gss.o`), gssproxy upcall and XDR support (`gss_rpc_upcall.o`, `gss_rpc_xdr.o`), and trace support. `rpcsec_gss_krb5-y` combines the Kerberos mechanism adapter, MIC seal/unseal code, wrap/unwrap buffer handling, crypto helpers, and key derivation.

## Control Flow
Build control is entirely Kconfig driven. Enabling `CONFIG_SUNRPC_GSS` builds the generic RPCSEC_GSS module. Enabling `CONFIG_RPCSEC_GSS_KRB5` builds the Kerberos mechanism and makes it available for autoload aliases such as `rpc-auth-gss-krb5`. Enabling `CONFIG_RPCSEC_GSS_KRB5_KUNIT_TEST` builds the standalone KUnit module with RFC test vectors.

## State and Persistence
No runtime state is stored here. The object composition determines which module init/exit functions will exist and which KUnit-only symbols may be imported under `EXPORTED_FOR_KUNIT_TESTING`.

## Dependencies and Integration Points
The file integrates with kernel Kbuild and Kconfig. It binds user-visible configuration options to object files that register authops, GSS mechanisms, server-side domains, and test suites.

## Risks and Edge Cases
Misconfigured options can build generic RPCSEC_GSS without Kerberos, making GSS auth present but Kerberos pseudoflavors unsupported. Test coverage is also configuration-sensitive: unavailable crypto algorithms or disabled enctype configs cause relevant KUnit parameter cases to skip.

## Test Signals
The explicit `gss_krb5_test.o` target is the main test signal. Successful builds under each feature combination validate object dependencies and exported KUnit symbols.
