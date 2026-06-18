# File Research: sources/block-storage/cryptsetup/lib/Makemodule.am

## Purpose
Autotools module defining the main `libcryptsetup.la` build, installed `libcryptsetup.h`, pkg-config metadata, symbol version script, and the small `libutils_io.la` helper archive.

## Key Content
Builds `libcryptsetup.la` from the core setup/device utilities, volume-key handling, dm integration, plain mode, integrity, loop-AES, TCRYPT, LUKS1, LUKS2, verity, OPAL, BITLK, and FileVault2 sources. It links UUID, devmapper, selected crypto backend libraries, optional libargon2, json-c, blkid, dl, gettext, `libcrypto_backend.la`, and `libutils_io.la`.

## Dependencies and Coupling
This file is the central source inventory for the C library under Autotools. The BITLK files in this batch are explicitly included here. `libcrypto_backend.la` is a required dependency and `lib/libcryptsetup.sym` controls exported ABI.

## Invariants and Risks
Source additions to libcryptsetup must be reflected here for Autotools builds. Meson and Autotools source lists must stay synchronized, especially for optional subsystems and vendored crypto code.
