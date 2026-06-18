# sources/distributed-fs/ceph-client/net/wireless/Makefile

## Purpose
This Makefile composes the cfg80211 module/object set and generates regulatory certificate source files when configured.

## Important build targets and variables
`obj-$(CONFIG_CFG80211) += cfg80211.o` builds cfg80211. Core objects include `core.o`, `sysfs.o`, `radiotap.o`, `util.o`, `reg.o`, `scan.o`, `nl80211.o`, `mlme.o`, `ibss.o`, `sme.o`, `chan.o`, `ethtool.o`, `mesh.o`, `ap.o`, `trace.o`, `ocb.o`, `michael-mic.o`, and `pmsr.o`. Optional objects include `of.o`, `debugfs.o`, WEXT compatibility, `shipped-certs.o`, and `extra-certs.o`. WEXT core/proc/private objects are built independently from cfg80211.

Generated targets `shipped-certs.c` and `extra-certs.c` produce byte arrays for regulatory DB certificates using shell pipelines over `.hex` or `.x509` files. `clean-files` removes generated certificate sources.

## Control flow
Kbuild aggregates `cfg80211-y` and feature-specific fragments into `cfg80211.o`. Certificate generation writes C files including `reg.h` and defining `shipped_regdb_certs` or `extra_regdb_certs` plus length symbols.

## State and persistence
No runtime state exists. Generated C files are build artifacts, removed by clean rules.

## Dependencies and integration points
The file integrates with Kbuild, Kconfig options, trace include flags, regulatory certificate directories, and optional WEXT/debugfs code.

## Risks
Certificate generation depends on shell tools and correct input formatting; empty or malformed generated arrays would break regulatory DB verification. Object ordering must include symbols used by nl80211, regulatory, and cfg80211 core initialization.

## Test signals
Build tests should cover all optional configs, especially extra certificate directories, generated-file clean behavior, WEXT-only helpers, and debugfs inclusion.
