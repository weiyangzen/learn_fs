# sources/distributed-fs/eos/mgm/proc/user/Version.cc

Purpose: implements `ProcCommand::Version()`, reporting EOS instance name, server version/release, XRootD version, and feature flags.

Important APIs and types: uses `XrdVERSIONINFOREF/XrdVERSIONINFOVAR`, compile-time `VERSION` and `RELEASE`, `gOFS->MgmOfsInstanceName`, `Features::sMap`, `mgm.option`, and MGM stats.

Control flow: with option `m`, it emits one-line monitoring key/value output including parsed XRootD version and all feature map entries. Otherwise it emits human-readable lines for instance and server version, and with option `f` appends feature entries.

State and persistence: read-only except stats.

Dependencies and integration: exposes deployment/runtime metadata to users and monitoring systems.

Risks: output ordering of features depends on `Features::sMap` iteration. XRootD version parsing assumes a space-delimited component prefix. Tests should cover monitoring format, feature format, absent or unusual XRootD version strings, and stable presence of instance/version/release fields.
