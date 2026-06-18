<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/system_certificates.S -->
# sources/distributed-fs/ceph-client/certs/system_certificates.S

## Purpose

`system_certificates.S` embeds module-signing and trusted X.509 certificate blobs into the kernel image and exposes their total size and module-certificate subset size. It can also reserve writable image space for an extra certificate.

## Important APIs, Types, And Functions

It defines `system_certificate_list`, `system_certificate_list_size`, `module_cert_size`, and internal labels around `certs/signing_key.x509` and `certs/x509_certificate_list`. With `CONFIG_SYSTEM_EXTRA_CERTIFICATE`, it also defines `system_extra_cert` and `system_extra_cert_used`.

## Control Flow

There is no executable control flow. The assembler concatenates the signing key certificate and additional trusted certificates. `system_keyring.c` later chooses whether to load all certificates or skip the module-cert subset depending on module-signature configuration.

## State And Persistence Behavior

The embedded certificate list is init read-only data. Optional `system_extra_cert` reserves zero-filled image space for post-build certificate insertion without recompilation.

## Dependencies And Integration Points

It depends on generated certificate list files from `certs/Makefile` and integrates with `load_system_certificate_list()` and `load_module_cert()` in `system_keyring.c`.

## Risks And Edge Cases

Ordering matters: module signing certificate bytes must be first so `module_cert_size` can identify the subset. Empty certificate inputs should still yield valid start/end symbols. Reserved extra certificate size must match the configured image patching workflow.

## Test Signals

Build with module signing enabled and disabled, with extra trusted keys, and with `SYSTEM_EXTRA_CERTIFICATE`. Verify symbol sizes and that runtime keyring loading reports the expected certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/system_certificates.S -->
