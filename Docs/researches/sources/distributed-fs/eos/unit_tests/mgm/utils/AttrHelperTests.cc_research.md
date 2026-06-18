# sources/distributed-fs/eos/unit_tests/mgm/utils/AttrHelperTests.cc

Purpose: GoogleTest coverage for EOS MGM attribute helper decisions around directory owner authorization, forced atomic upload, and versioning policy.

Important APIs and data: Tests target `eos::mgm::attr::checkDirOwner`, `attr::checkAtomicUpload`, and `attr::getVersioning`. Inputs are `eos::IContainerMD::XAttrMap` maps keyed by constants such as `SYS_OWNER_AUTH`, `SYS_FORCED_ATOMIC`, `USER_FORCED_ATOMIC`, `SYS_VERSIONING`, and `USER_VERSIONING`, plus `eos::common::VirtualIdentity`.

Control flow: `checkDirOwner` coverage includes an empty xattr map, sticky-owner wildcard (`*`), and protocol/user matching (`krb5:testuser`) that should rewrite `dir_uid` and `dir_gid` to the caller identity. Atomic upload tests exercise no attributes, system attribute truthy/falsy/negative/garbage values, user attributes, CGI-triggered atomic upload, and system override precedence. Versioning tests validate CGI string parsing, invalid CGI fallback behavior, CGI override of xattrs, system override of user values, garbage system values, and user-only values.

State and persistence: No persistent state. Each test creates a local xattr map and identity. Mutations are intentionally performed in-place inside test bodies to verify precedence after key changes.

Dependencies and integration: Depends on `mgm/utils/AttrHelper.hh`, MGM constants, namespace metadata xattr map type, and GoogleTest. It is an integration-style unit test because policy constants and helper parsing are checked together.

Risks: Tests cover representative string values but not whitespace, comma edge cases beyond owner auth, very large version values, negative versioning, or null diagnostics behavior beyond passing `nullptr` to `checkDirOwner`. The `checkDirOwner` test uses `EXPECT_TRUE` followed by hard assertions, so a failed owner match still checks mutated IDs.

Test signals: Strong signal for xattr precedence and numeric conversion behavior. A regression that changes sys-over-user priority or invalid string handling should fail here.
