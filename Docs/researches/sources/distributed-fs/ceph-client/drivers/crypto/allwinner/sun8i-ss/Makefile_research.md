# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/Makefile

## Purpose

This Makefile builds the Allwinner sun8i Security System module from the core and cipher objects, with optional PRNG and hash objects selected by Kconfig symbols.

## Important APIs, Types, And Functions

It declares `obj-$(CONFIG_CRYPTO_DEV_SUN8I_SS) += sun8i-ss.o`, always includes `sun8i-ss-core.o` and `sun8i-ss-cipher.o`, and conditionally adds `sun8i-ss-prng.o` and `sun8i-ss-hash.o`.

## Control Flow

There is no runtime control flow. Build-time selection determines whether the module exports only skcipher algorithms or also the `stdrng` and ahash/HMAC templates registered by the core file.

## State And Persistence Behavior

No runtime state is stored here. The build state persists in the generated composite object and controls which code paths are linked into the module.

## Dependencies And Integration Points

It integrates with kbuild and the `CONFIG_CRYPTO_DEV_SUN8I_SS*` symbols. The conditional object list must match prototypes and algorithm templates in `sun8i-ss-core.c` and `sun8i-ss.h`.

## Risks And Test Signals

Risks include unresolved symbols if optional object selections do not align with core template `#ifdef`s, and missing features when Kconfig enables an algorithm but the object is not linked. Test all combinations of base, PRNG, and hash config symbols with module and built-in builds.
