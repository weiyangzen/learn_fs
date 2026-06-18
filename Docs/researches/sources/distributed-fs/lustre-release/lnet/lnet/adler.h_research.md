# sources/distributed-fs/lustre-release/lnet/lnet/adler.h

## Purpose
Declares the Adler-32 crypto registration entry points implemented by `adler.c`.

## Important APIs
`cfs_crypto_adler32_register(void)` registers the shash algorithm. `cfs_crypto_adler32_unregister(void)` unregisters it.

## Control flow and integration
No executable control flow. Inclusion by LNet crypto/module code allows startup to install the algorithm and shutdown to remove it. The Makefile ensures `adler.o` is linked into the same module.

## State and persistence
No state is declared here. Runtime state lives inside the crypto registration object in `adler.c`.

## Dependencies
Relies on callers including appropriate kernel declarations for `int`/`void`; no include guard is present.

## Risks and test signals
The main risks are duplicate declarations if the header grows without guards and mismatches with `adler.c`. Test signals are clean compilation with warnings enabled and successful LNet crypto register/unregister paths.
