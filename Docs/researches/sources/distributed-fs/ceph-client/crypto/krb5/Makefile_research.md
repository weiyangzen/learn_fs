<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/Makefile -->
# sources/distributed-fs/ceph-client/crypto/krb5/Makefile

Purpose: Builds the Kerberos 5 crypto module from the API, KDF, simplified profile, enctype profile, and optional selftest objects.

Important APIs/types/functions: `krb5-y` lists `krb5_kdf.o`, `krb5_api.o`, `rfc3961_simplified.o`, `rfc3962_aes.o`, `rfc6803_camellia.o`, and `rfc8009_aes2.o`. `krb5-$(CONFIG_CRYPTO_KRB5_SELFTESTS)` adds `selftest.o` and `selftest_data.o`. `obj-$(CONFIG_CRYPTO_KRB5) += krb5.o` links the module/built-in object.

Control flow: Kbuild aggregates the listed objects into `krb5.o` when `CONFIG_CRYPTO_KRB5` is enabled, adding selftest objects only when configured.

State and persistence behavior: No runtime state. It controls build-time object composition.

Dependencies and integration points: Integrates the Kerberos source files into the kernel crypto Makefile hierarchy and matches the Kconfig option names.

Risks: Omitting an object can leave supported enctype externs unresolved or make the public API incomplete. Adding selftest data unconditionally would increase footprint; omitting it when selftests are enabled would break module init validation.

Test signals: Incremental and clean builds for built-in and module configurations, with and without selftests, plus linker checks for all exported Kerberos symbols and enctype tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/Makefile -->
