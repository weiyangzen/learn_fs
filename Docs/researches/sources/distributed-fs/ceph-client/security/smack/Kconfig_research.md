# sources/distributed-fs/ceph-client/security/smack/Kconfig

## Purpose
`security/smack/Kconfig` defines build-time configuration for the Smack LSM and its optional policy/audit/network behaviors.

## Important APIs, Types, and Functions
The symbols are `SECURITY_SMACK`, `SECURITY_SMACK_BRINGUP`, `SECURITY_SMACK_NETFILTER`, and `SECURITY_SMACK_APPEND_SIGNALS`. `SECURITY_SMACK` depends on `NET`, `INET`, and `SECURITY`, selects `NETLABEL` and `SECURITY_NETWORK`, and defaults off.

## Control Flow
Kconfig selection controls which source files and conditional code are compiled. `BRINGUP` enables rule mode `b` reporting for granted accesses. `NETFILTER` enables packet marking with secmarks and pulls in netfilter/secmark dependencies. `APPEND_SIGNALS` changes signal-delivery authorization from write-style access to append-style access.

## State and Persistence
This file has no runtime state but controls compiled policy behavior. User-visible semantics can change significantly based on selected options, especially signal permissions and bringup-mode logging.

## Dependencies and Integration Points
The options feed `security/smack/Makefile`, `smack.h` feature macros, and conditional code in Smack access/network paths. They also require kernel security, networking, NetLabel, and optionally netfilter secmark support.

## Risks
Configuration combinations can subtly change access decisions. `SECURITY_SMACK_NETFILTER` alters IPv6 labeling mode in `smack.h`; `SECURITY_SMACK_APPEND_SIGNALS` changes what rules authorize signal delivery. Defaults are conservative, but distro configs need explicit review.

## Test Signals
Build all option combinations that are dependency-valid. Runtime tests should cover bringup logging, packet labeling with and without netfilter, and signal delivery authorization under write versus append mode.
