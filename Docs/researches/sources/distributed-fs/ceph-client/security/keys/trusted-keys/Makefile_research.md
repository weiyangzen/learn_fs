# sources/distributed-fs/ceph-client/security/keys/trusted-keys/Makefile

## Purpose

The Makefile builds the common trusted-key module object and conditionally includes backend providers and TPM2 ASN.1 parser support.

## Important APIs, Types, and Functions

`obj-$(CONFIG_TRUSTED_KEYS) += trusted.o` creates the aggregate object. `trusted-y` always includes `trusted_core.o`. TPM support adds `trusted_tpm1.o`, `trusted_tpm2.o`, and `tpm2key.asn1.o`, with an explicit dependency from `trusted_tpm2.o` to generated `tpm2key.asn1.h`. Other backend symbols add `trusted_tee.o`, `trusted_caam.o`, `trusted_dcp.o`, and `trusted_pkwm.o`.

## Control Flow

Kbuild composes `trusted.o` from the enabled `trusted-*` fragments. ASN.1 code generation must happen before compiling `trusted_tpm2.o`, because that file includes `tpm2key.asn1.h`.

## State and Persistence Behavior

No runtime state is represented. The file determines the final object contents and therefore which backend operation tables are visible to `trusted_core.c`.

## Dependencies and Integration Points

It integrates with Kbuild, Kconfig backend symbols, and the kernel ASN.1 generator. The naming matches exported backend operation tables such as `trusted_key_tpm_ops` and `trusted_key_tee_ops`.

## Risks and Test Signals

Missing objects lead to unresolved backend references or absent trusted-key features. Test with per-backend build matrices, especially TPM where generated ASN.1 headers are required.
