## sources/distributed-fs/eos/mgm/bulk-request/interface/IMgmFileSystemInterface.hh

Purpose: defines a testable adapter interface over the MGM filesystem operations needed by prepare and query-prepare logic. It decouples `PrepareManager` from direct `XrdMgmOfs` access.

Important APIs: stats recording, tape flag and request-ID limit, error formatting, existence checks by client or virtual identity, xattr listing, access checks, `FSctl`, stat/stat-flag helpers, log ID/host access, and EOS report writing.

Integration: implemented by `RealMgmFileSystemInterface`; consumed by `PrepareManager`. Risks include a broad interface that is still tightly coupled to XRootD and EOS types, and default pointer arguments that fakes must mirror. Test signals should use mocks to drive all prepare validation branches: mapping, redirect/stall, xattr lookup, access failure, stat flags, and workflow dispatch return codes.
