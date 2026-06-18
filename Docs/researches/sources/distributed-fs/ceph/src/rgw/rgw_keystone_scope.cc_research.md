# sources/distributed-fs/ceph/src/rgw/rgw_keystone_scope.cc

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This file implements `ScopeInfo::dump()` and `build_scope_info()`, converting `TokenEnvelope` Keystone project/user/role/application-credential data into optional logging/audit scope records. Config controls whether scope is enabled, whether names/user fields are included, and whether role names are included. State is transient, with persistence handled by callers that encode or log `ScopeInfo`. Dependencies are `TokenEnvelope`, `CephContext` config, and `Formatter`. Risks are privacy exposure through user/name/role logging and the fact that `include_user` also controls project/domain names. Tests should cover disabled, ids-only, names/user, roles, app credentials, and formatter output.
