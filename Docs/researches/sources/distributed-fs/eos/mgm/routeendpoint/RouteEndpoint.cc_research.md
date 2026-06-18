<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.cc -->
# sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.cc

## Purpose
Implements `eos::mgm::RouteEndpoint`, the MGM-side representation of a route target used by path routing. The file provides parsing/formatting for `<fqdn>:<xrd_port>:<http_port>`, move assignment, and active health/status probing through XRootD.

## Important APIs and Functions
- `RouteEndpoint::operator=(RouteEndpoint&&)`: moves/copies endpoint fields into an existing endpoint. It swaps the hostname and copies ports plus atomic status flags.
- `RouteEndpoint::ParseFromString(const std::string&)`: tokenizes on `:`, expects exactly three tokens, parses XRootD and HTTP ports with `std::stoul`, and validates the hostname/IP through `eos::common::ValidHostnameOrIP`.
- `RouteEndpoint::ToString() const`: serializes the endpoint back to `fqdn:xrd_port:http_port`.
- `RouteEndpoint::UpdateStatus()`: builds a `root://host:port//dummy?xrd.wantprot=sss,unix` URL, pings it, then sends an opaque query `/?mgm.pcmd=is_master` to determine master status.

## Control Flow
Parsing is intentionally narrow: token count must be exactly three, both port fields must parse as unsigned integers, and invalid hostnames reject the endpoint. `UpdateStatus()` has three stages: URL construction/validation, `XrdCl::FileSystem::Ping(1)` online check, then an XRootD opaque query for master detection. Any invalid URL or ping failure clears both `mIsOnline` and `mIsMaster`; a successful ping sets online before master probing.

The master query branch is counterintuitive at first read: if `fs.Query(...).IsOK()` is false, it logs that the host is running as master but sets `mIsMaster = false`; if the query succeeds, it logs NOT master but sets `mIsMaster = true`. This may reflect endpoint-side command semantics, but the log strings and stored booleans appear inverted and should be treated as a risk signal.

## State and Persistence
The file mutates only in-memory state: hostname, two port fields, and atomic online/master flags. There is no direct persistence. The status flags are public in the header and are consumed by routing logic/tests, so external code can also set them without `UpdateStatus()`.

## Dependencies and Integration Points
Depends on `common/StringConversion.hh` for tokenization, `common/ParseUtils.hh` for hostname/IP validation, EOS logging through `LogId`, and XRootD client classes `XrdCl::URL`, `XrdCl::FileSystem`, `XrdCl::Buffer`, and `XrdCl::XRootDStatus`. It integrates with `PathRouting`, `RouteCmd`, and the MGM build target that includes `routeendpoint/RouteEndpoint.cc`.

## Risks
- `std::stoul` is not range-checked against `uint32_t` before assignment, so oversized numeric strings can wrap/truncate after parsing depending on platform width.
- Ports are not constrained to valid TCP port range.
- The apparent master-query log/boolean inversion in `UpdateStatus()` is a behavioral hotspot.
- `UpdateStatus()` allocates `XrdCl::Buffer* response` and manually deletes it; early returns before allocation are safe, but future edits should avoid leaks by using RAII if ownership semantics allow it.
- Move assignment copies atomic values but does not reset the moved-from flags or ports.

## Test Signals
`sources/distributed-fs/eos/unit_tests/mgm/RoutingTests.cc` covers valid/invalid parsing, endpoint equality, and routing use with manually set `mIsOnline`/`mIsMaster` flags. There is no direct unit test signal for live XRootD `UpdateStatus()` behavior or the master-query branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.cc -->
