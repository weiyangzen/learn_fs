# sources/distributed-fs/lizardfs/src/protocol/mltoma.h

Purpose: Defines metalogger/shadow-to-master packets for shadow registration, changelog apply errors, and publishing the client-facing master port.

Important APIs/types/functions: `mltoma::registerShadow` with version, timeout, and metadata version; `mltoma::changelogApplyError`; `mltoma::matoclport`.

Control flow: Macro-generated helpers encode sender state for the master. Registration announces client version, desired timeout, and known metadata version; later packets report apply errors or matocl port.

State and persistence: Stateless wire helpers. Messages describe replication metadata state and port state.

Dependencies and integration: Uses serialization macros and packet constants. It complements `matoml.h` response packets in master/metalogger communication.

Risks and test signals: No direct tests in this subset. Compatibility depends on fixed field order and version semantics matching master-side handlers.
