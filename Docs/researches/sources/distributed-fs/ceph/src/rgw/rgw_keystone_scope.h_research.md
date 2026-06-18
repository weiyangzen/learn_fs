# sources/distributed-fs/ceph/src/rgw/rgw_keystone_scope.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header defines persistent/loggable Keystone `ScopeInfo` data: domain, project, optional user, role vector, and optional application credential, each with versioned Ceph encode/decode. Free encode/decode wrappers support optional/nested serialization. It integrates with Keystone token parsing and operation logging. Risks are storage compatibility if field order/versioning changes, wrapper visibility for template encoding, and privacy controls living in builder code rather than the type. Tests should round-trip ids-only and all optional combinations, verify dump output, and protect future version compatibility.
