# sources/distributed-fs/seaweedfs/weed/s3api/s3api_handlers.go

## Purpose
Provides shared S3 API server helpers for filer gRPC access, HTTP success/error responses, data-center reporting, URL adjustment, and `Content-Md5` validation. The central behavior is `S3ApiServer.WithFilerClient`, which gives S3 handlers a `filer_pb.SeaweedFilerClient` while hiding direct gRPC connection setup and multi-filer failover.

## Important APIs, Types, And Functions
`WithFilerClient(streamingMode, fn)` is the package-level filer access facade used by many S3 handlers and helper routines. `withFilerClientFailover(preferred, streamingMode, fn)` orders preferred, current, healthy, then unhealthy filer addresses and calls `pb.WithGrpcClient` for each candidate. `AdjustedUrl`, `GetDataCenter`, `writeSuccessResponseXML`, `writeSuccessResponseXMLBytes`, `writeSuccessResponseEmpty`, `writeFailureResponse`, and `validateContentMd5` are small common helpers. The compile-time `var _ = filer_pb.FilerClient(&S3ApiServer{})` asserts that `S3ApiServer` satisfies the filer client interface expected by `filer_pb.List`.

## Control Flow
`WithFilerClient` uses the newer `s3a.filerClient` path when initialized, otherwise falls back to a direct connection to `s3a.getFilerAddress()` for tests or startup. Failover builds a de-duplicated candidate list from a preferred address, the current filer, and all configured filers. Preferred is always tried first, even if health tracking says it is unhealthy, because routed read-after-write requests need an authoritative answer from the key owner. Non-preferred candidates are split into healthy and unhealthy using `ShouldSkipUnhealthyFiler` and owner-reachability state, then tried in that order. A successful non-preferred failover records success and can promote the current filer. `filer_pb.ErrNotFound` is treated as authoritative and stops failover, while transport-like failures are recorded and wrapped after all candidates fail.

## State And Persistence
The helper mutates only in-memory client state: current filer selection, filer health records, and recently-unreachable owner tracking. It does not write persistent configuration. Response helpers write HTTP response headers/bodies and S3 access logs through `s3err.PostLog`.

## Dependencies And Integration Points
This file connects S3 handlers to `pb.WithGrpcClient`, `filer_pb.NewSeaweedFilerClient`, `S3ApiServer.filerClient`, glog, and S3 XML/error response utilities. It is a core integration point for any S3 path that needs filer metadata or entry mutation.

## Risks And Test Signals
The main risks are failover masking authoritative not-found responses, stale current-filer promotion, inconsistent behavior between initialized and direct fallback modes, and candidate ordering when preferred owners are outside the static filer list. Tests should cover `ErrNotFound` no-fanout semantics, preferred-first routing, current-filer promotion after successful failover, unhealthy deferral, and empty or invalid `Content-Md5` handling.
