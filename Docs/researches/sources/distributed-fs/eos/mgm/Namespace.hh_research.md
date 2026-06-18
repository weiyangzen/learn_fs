# sources/distributed-fs/eos/mgm/Namespace.hh

Purpose: provides namespace convenience macros for MGM code. It centralizes `namespace eos::mgm` and subnamespace wrappers for FUSE server, TGC, bulk, and REST code, plus matching `using namespace` helper macros.

Important APIs and types: `EOSMGMNAMESPACE_BEGIN/END`, `EOSFUSESERVERNAMESPACE_BEGIN/END`, `EOSTGCNAMESPACE_BEGIN/END`, `EOSBULKNAMESPACE_BEGIN/END`, and `EOSMGMRESTNAMESPACE_BEGIN/END` expand to nested namespace declarations. `USE_EOSMGMNAMESPACE`, `USE_EOSFUSESERVERNAMESPACE`, and `USE_EOSBULKNAMESPACE` expand to `using namespace` statements.

Control flow: no runtime control flow; it is purely preprocessor structure.

State and persistence: no state and no persistence.

Dependencies and integration points: included by MGM headers and implementation files that want consistent namespace spelling. In this work item it scopes `Access`, `Acl`, `AdminSocket`, `AccessChecker`, and `FuseServer::Server`.

Risks: macro-based namespace management hides actual C++ syntax from tools and can make refactors/error messages less direct. `using namespace` macros can broaden lookup and collision risk if used in headers or wide scopes.

Test signals: build coverage is the main signal. Static analysis or style checks can flag accidental macro misuse and unwanted `USE_*` expansion in headers.
