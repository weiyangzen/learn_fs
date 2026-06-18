# sources/cloud-native/moby/daemon/server/httpstatus/status.go

## Purpose
Maps daemon, containerd, gRPC, and distribution errors to HTTP status codes for API responses.

## Important APIs, Types, And Functions
`FromError` is the public mapper. Helpers `statusCodeFromGRPCError` and `statusCodeFromDistributionError` translate gRPC codes and Docker distribution `errcode` values.

## Control Flow
`FromError` resolves containerd errdefs from the outermost error, checks known errdefs categories, then tries gRPC and distribution mappings. If unresolved, it recursively unwraps single or joined errors looking for a non-500 status. Unknown/untyped errors log a debug FIXME and return 500.

## State And Persistence
No persistent state. It emits logs for nil or unexpected errors.

## Dependencies And Integration Points
Used by server error handling and debug middleware. Depends on containerd errdefs, Docker distribution errcode, gRPC status codes, HTTP constants, and containerd logging.

## Risks And Edge Cases
The order favors outermost resolved errdefs, then recursive unwrapping. Joined errors return the first non-500 status found, so ordering can affect responses. Nil errors log and map to 500.

## Test Signals
No listed direct tests, but API error response tests should cover common errdefs, gRPC, distribution, wrapped, and joined errors.
