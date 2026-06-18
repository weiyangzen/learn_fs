# sources/distributed-fs/ceph-client/net/ceph/Kconfig

## Purpose
Defines build-time configuration for the in-kernel Ceph core library used by CephFS and RBD. It also exposes optional debug-output formatting and in-kernel DNS resolver support.

## Important APIs, Types, and Functions
This is Kconfig data rather than C code. `CEPH_LIB` is a tristate depending on `INET` and selecting CRC, crypto, keyring, AES-CBC/GCM, KRB5, SHA-256, and generic crypto support. `CEPH_LIB_PRETTYDEBUG` enables file:line debug output. `CEPH_LIB_USE_DNS_RESOLVER` selects `DNS_RESOLVER` for monitor hostname resolution.

## Control Flow
The selected options drive what objects the Makefile builds and which optional code paths compile. Enabling `CEPH_LIB` makes `libceph.o` available built-in or as a module. The DNS option compiles code expecting kernel DNS resolver integration elsewhere in libceph.

## State and Persistence
There is no runtime state in this file. Its effects persist in the kernel configuration and compiled object set.

## Dependencies and Integration Points
Integrates with the kernel Kconfig system, CephFS/RBD consumers, the kernel crypto API, keyrings, and networking. The crypto selections match the auth and messenger code in this directory, especially CephX and secure messenger modes.

## Risks
Dependency drift is the main risk: auth/crypto code assumes selected algorithms and keyring support are present. Selecting broad crypto dependencies increases kernel size. Pretty debug can enlarge code and slow dynamic-debug-enabled paths. DNS resolver support depends on correct runtime resolver configuration outside this file.

## Test Signals
Build `CEPH_LIB` as built-in and module, confirm all selected crypto/key symbols resolve, enable pretty debug and verify debug format changes, enable DNS resolver and mount with hostname monitor addresses, and verify disabled `CEPH_LIB` excludes libceph consumers unless they select it.
