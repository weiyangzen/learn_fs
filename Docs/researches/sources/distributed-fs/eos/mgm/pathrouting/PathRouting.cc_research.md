<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/pathrouting/PathRouting.cc -->
# sources/distributed-fs/eos/mgm/pathrouting/PathRouting.cc

Source read size: 307 lines, 9396 bytes.

## Purpose

Implements the runtime behavior of `PathRouting`, an in-memory MGM route table that maps EOS path prefixes to one or more remote MGM endpoints and chooses a reachable master endpoint for client redirection.

## Important APIs, Types, and Functions

Key methods are `Clear`, `Add`, `Remove`, `Reroute`, `GetListing`, and the background `UpdateEndpointsStatus(ThreadAssistant&)`. It stores `std::map<std::string, std::list<RouteEndpoint>> mPathRoute` guarded by `mPathRouteMutex`, uses `RouteEndpoint::UpdateStatus`, and returns `Status::{REROUTE,NOROUTING,STALL}`.

## Control Flow

`Add` inserts a path-to-endpoint mapping while rejecting duplicate endpoint objects for an existing path. `Reroute` parses `inpath` plus `ininfo` through `XrdCl::URL`, prefers CGI tags `eos.route`, `mgm.path`, then `mgm.quota.space`, URL-decodes and normalizes the path, appends a trailing slash, finds an exact route or longest parent subpath, picks an online master endpoint or the first endpoint, stalls if the selected endpoint is offline, and fills host/port/stat-info for HTTP(S) or XRootD redirect. `GetListing` emits all or one route with `_` for offline and `*` for master endpoints. `UpdateEndpointsStatus` periodically refreshes endpoint online/master state and marks a route offline if two or more online masters are seen.

## State and Persistence Behavior

Routes and endpoint status live only in memory. A background assisted thread is started when the update timeout is nonzero; the destructor joins it. Endpoint online/master flags are atomic fields owned by `RouteEndpoint`.

## Dependencies and Integration Points

Depends on `RouteEndpoint`, `common::Path`, URL decoding, `XrdCl::URL`, logging, and `AssistedThread`. It is used by MGM redirect/proc routing to direct clients to the correct remote MGM.

## Risks and Edge Cases

The destructor unconditionally joins the assisted thread, so construction with zero timeout depends on `AssistedThread::join` being safe. `Reroute` assumes `path.back()` after empty checks and normalized path handling. Multiple masters force all endpoints offline, deliberately stalling clients. Longest-prefix search starts below the full path, so exact matches must be normalized with trailing slash.

## Test Signals

Test exact and longest-prefix routes, CGI tag priority, URL-encoded paths, HTTP/HTTPS versus XRootD ports, offline endpoint stall, multiple-master detection, duplicate add rejection, remove/clear/listing behavior, and background refresh termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/pathrouting/PathRouting.cc -->
