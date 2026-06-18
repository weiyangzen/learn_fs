# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsExports.java

## Purpose
`NfsExports.java` loads configured NFS export host rules and checks whether a client address/hostname has read-only, read-write, or no access.

## Important APIs, Types, and Functions
- Static singleton `getInstance(Configuration)` reads `nfs.exports.allowed.hosts`, cache size, and cache expiry config and creates one `NfsExports`.
- Constructor splits the host rule string on Hadoop's NFS exports separator and converts each non-empty token into a `Match`.
- `getHostGroupList()` returns configured host matcher strings for mount export responses.
- `getAccessPrivilege(InetAddress)` and package-private `getAccessPrivilege(String address, String hostname)` evaluate and cache access.
- `AccessCacheEntry` implements `LightWeightCache.Entry` keyed by host address with an expiration timestamp.
- `Match` subclasses implement matcher types:
  - `AnonymousMatch` for `*`.
  - `CIDRMatch` for short `ip/prefix` or long `ip/netmask` IPv4 CIDR.
  - `ExactMatch` for exact IP or hostname.
  - `RegexMatch` for wildcard/regex-like host strings containing metacharacters.
- `getMatch(String line)` parses `host [rw]`, defaulting to read-only when no access option is provided.

## Control Flow and State
Access evaluation first checks the cache by IP address. If absent or expired, it scans matchers in configured order. `READ_ONLY` immediately wins and breaks; `READ_WRITE` is recorded but later read-only matches can override. If no matcher includes the client, access remains `NONE`. The result is cached until expiration.

## Dependencies and Integration Points
The class uses Hadoop `Configuration`, `CommonConfigurationKeys`, NFS constants for cache keys, Commons Net `SubnetUtils`, Hadoop `LightWeightCache`, `LightWeightGSet`, `StringUtils`, `Preconditions`, and SLF4J. `MountResponse.writeExportList()` uses `getHostGroupList()`.

## Risks and Edge Cases
The singleton ignores subsequent configuration changes after first initialization. Only IPv4 CIDR patterns are supported. Regex patterns are compiled directly from the host string rather than shell-glob translated, so configured `*` and `?` inside hostnames have Java regex meaning. Invalid host strings throw `IllegalArgumentException`; `getInstance()` logs and returns the existing singleton, which may be null. Cache keys by address ignore hostname changes until expiry.

## Test Signals
Expected tests should cover anonymous, exact, CIDR short/long, regex, invalid hostnames, `rw` option, read-only precedence, and cache expiry. This subset does not include those tests.
