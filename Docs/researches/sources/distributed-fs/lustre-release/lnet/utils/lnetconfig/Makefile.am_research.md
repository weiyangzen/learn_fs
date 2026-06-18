# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/Makefile.am

## Purpose
Builds `liblnetconfig.la`, the user-space LNet configuration library used by LNet utilities.

## Important Build Targets
`liblnetconfig_la_SOURCES` includes core lnetconfig, LND, cYAML, UDSP, and netlink sources. CPPFLAGS enable large-file support and `LUSTRE_UTILS`. LDFLAGS link yaml, math, readline, and set libtool version `4:0:0`. LIBADD links libcfs and libnl.

## Control Flow
Automake compiles the listed sources into an installed libtool library. Parent utilities link against it.

## State And Persistence
No runtime state. The file controls build artifacts and library ABI metadata.

## Dependencies And Integration Points
Depends on libcfs user-space library, libyaml, libm, readline, libnl3, and the Lustre Autotools configuration.

## Risks
Source omissions cause downstream link failures. Version-info may need updates for ABI changes. Missing optional/configured libs break builds.

## Test Signals
Build `liblnetconfig.la`, link parent utilities, and test configurations with relevant optional dependencies.
