# sources/distributed-fs/ceph-client/security/keys/trusted-keys/Kconfig

## Purpose

This Kconfig fragment selects the hardware or firmware trust backends available to the common `trusted` key type. It lets TPM, TEE, CAAM, DCP, and IBM PowerVM PKWM providers contribute sealing/unsealing operations when their platform dependencies are present.

## Important APIs, Types, and Functions

The file defines `HAVE_TRUSTED_KEYS` as a backend availability marker and backend booleans `TRUSTED_KEYS_TPM`, `TRUSTED_KEYS_TEE`, `TRUSTED_KEYS_CAAM`, `TRUSTED_KEYS_DCP`, and `TRUSTED_KEYS_PKWM`. Backend options depend on their provider subsystems being at least as available as `TRUSTED_KEYS`, default to `y` when possible, and select provider-specific prerequisites such as ASN.1/OID helpers for TPM and CAAM blob generation for CAAM.

## Control Flow

During configuration, enabling `TRUSTED_KEYS` allows one or more backend selections. If no backend sets `HAVE_TRUSTED_KEYS`, a warning comment is displayed. The resulting symbols drive which provider objects are linked into `trusted.o`.

## State and Persistence Behavior

There is no runtime state. The persistent effect is build-time: which trusted-key backends exist, which crypto parsers are built, and whether the common trusted key module can initialize a source.

## Dependencies and Integration Points

The options integrate with TPM (`TCG_TPM`), TEE, Freescale/NXP CAAM, MXS DCP, and pSeries PLPKS support. They feed the trusted-key `Makefile` and the `trusted_key_sources[]` array in `trusted_core.c`.

## Risks and Test Signals

Dependency mistakes produce link failures or a `trusted` key type with no usable source. Test signals include allmodconfig/allyesconfig builds, platform-specific boot probes, and keyctl creation of `trusted` keys with each configured source.
