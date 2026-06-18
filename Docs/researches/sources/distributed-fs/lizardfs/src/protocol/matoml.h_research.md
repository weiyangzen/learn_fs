# sources/distributed-fs/lizardfs/src/protocol/matoml.h

Purpose: Defines master-to-metalogger or master-to-shadow packets for shadow registration responses, changelog apply errors, and session termination.

Important APIs/types/functions: `matoml::registerShadow` with status and response versions; `matoml::changelogApplyError`; `matoml::endSession`.

Control flow: Macro-generated helpers serialize status-only registration failures or successful responses containing package version and metadata version. Changelog errors carry a status byte; end session has no payload.

State and persistence: Stateless wire definitions. Payloads reflect metadata replication state but do not persist data directly.

Dependencies and integration: Depends on `protocol/packet.h` and serialization macros. It pairs with metalogger/shadow registration messages from `mltoma.h`.

Risks and test signals: Version handling is the main compatibility risk. No direct unit test in this subset covers these packets, so regressions may surface only in integration tests.
