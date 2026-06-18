# sources/distributed-fs/eos/mgm/authz/XrdMgmAuthz.hh

Purpose: declares `XrdMgmAuthz`, the EOS MGM XRootD authorization plugin class implementing `XrdAccAuthorize`.

Important APIs and types: `Access` is the main override returning privileges for a path/operation/environment. `Audit` is overridden as a no-op success. `Test` is overridden but always returns 0. `gMgmAuthz` is declared as the global plugin handle.

Control flow: XRootD obtains an instance through C factory functions in the `.cc`, then calls `Access`, optionally `Audit`/`Test`.

State and persistence: no per-instance state beyond inherited logging identity. The global pointer controls singleton lifecycle.

Dependencies and integration points: includes XRootD authorization headers and EOS logging. The class lives in the global namespace, matching plugin ABI expectations rather than MGM namespace macros.

Risks: `Audit` and `Test` are placeholders, which is safe only if the server does not rely on them for enforcement or audit records. The header exposes a mutable global pointer and default destructor without ownership cleanup.

Test signals: ABI tests should confirm the class satisfies XRootD virtual interface expectations. Integration tests should verify actual XRootD authorization uses `Access` and not `Test` for final decisions.
