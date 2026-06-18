# sources/distributed-fs/ceph-client/include/linux/turris-signing-key.h

## Purpose
Declares a Turris-specific signing key subtype interface backed by the kernel key subsystem, typically for MCU/board signing support.

## Important APIs, Types, And Functions
Under `CONFIG_KEYS`, defines `struct turris_signing_key_subtype` with key/data/signature/public-key sizes, hash algorithm name, `get_public_key()` callback, and `sign()` callback. Provides `turris_signing_key_get_dev()` and `devm_turris_signing_key_create()`.

## Control Flow
A device-managed creator registers a signing key with subtype operations and description. Consumers retrieve the associated `struct device` from key payload slot 1 and call subtype callbacks to expose the public key or sign messages.

## State, Persistence, And Dependencies
Key state lives in `struct key` payload fields and device-managed lifetime. Dependencies are key management, base types, and `struct device`.

## Integration Points
Pairs with Turris Omnia MCU crypto commands and kernel keyring infrastructure. Device-managed creation ties key lifetime to driver lifetime.

## Risks And Test Signals
Risks include assumptions about key payload layout, callback size mismatches, missing `CONFIG_KEYS` stubs for callers, and signing hardware failures. Test signals include key creation/destruction, public-key extraction, signature-size validation, key payload device association, and build coverage with `CONFIG_KEYS` disabled.
