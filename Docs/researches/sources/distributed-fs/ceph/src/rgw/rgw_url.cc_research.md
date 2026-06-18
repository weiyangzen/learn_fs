# sources/distributed-fs/ceph/src/rgw/rgw_url.cc

## Purpose
`rgw_url.cc` implements URL authority/userinfo parsing helpers.

## Important APIs, Types, and Functions
`rgw::parse_url_authority()` parses a URI and extracts host, optional port, user, and password. `rgw::parse_url_userinfo()` extracts only user and password.

## Control Flow
Both functions call `boost::urls::parse_uri()`, return false on parse failure, and otherwise copy fields out of the URL view. Authority parsing formats `host:port` when a port is present.

## State and Persistence Behavior
The file is stateless and has no persistence.

## Dependencies and Integration Points
Depends on Boost.URL and fmt. Used by notification, cloud, or external service configuration that embeds credentials in URLs.

## Risks
No scheme allowlist is enforced here despite header comments listing expected schemes. Percent-decoding behavior is whatever Boost.URL exposes for `user()`/`password()`. IPv6 host plus port formatting must be verified against Boost output.

## Test Signals
Cover no port, port, userinfo, password-only/empty password, invalid URI, IPv6 literals, percent-encoded credentials, and unsupported schemes.
