# sources/distributed-fs/ceph-client/net/sctp/Kconfig

Purpose: defines build-time configuration for SCTP protocol support, debugging, default cookie authentication, and inet socket diagnostics.

Important entries: `menuconfig IP_SCTP` is a tristate depending on `INET` and selecting SHA1, SHA256, crypto utils, CRC32C, and UDP tunnel support. `SCTP_DBG_OBJCNT` enables procfs object counters. The cookie authentication choice defaults to `SCTP_DEFAULT_COOKIE_HMAC_SHA256` with `SCTP_DEFAULT_COOKIE_HMAC_NONE` as a weaker alternative. `INET_SCTP_DIAG` depends on and follows `INET_DIAG`.

Control flow: all nested options are visible only when SCTP is enabled. The cookie-HMAC choice sets compile-time defaults used by SCTP runtime policy/sysctl initialization. Diagnostic support builds only when inet diag is available.

State and persistence: values persist in the kernel `.config` and determine compiled code; this file has no runtime state.

Dependencies/integration: feeds Kbuild, SCTP C preprocessor conditionals, crypto libraries, CRC32C, UDP tunnel encapsulation, procfs, sysctl/default cookie policy, and inet diag.

Risks: `IP_SCTP=n` removes all nested SCTP behavior. Cookie HMAC `None` weakens defaults. Missing `INET_DIAG` removes SCTP socket diagnostic support. Debug object counting changes allocation/free instrumentation.

Test signals: build matrix for `IP_SCTP=y/m/n`, debug object counts with procfs, both cookie defaults, `INET_SCTP_DIAG`, and IPv6 combinations.
