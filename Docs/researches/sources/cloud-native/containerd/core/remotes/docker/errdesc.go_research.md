<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/errdesc.go -->
# sources/cloud-native/containerd/core/remotes/docker/errdesc.go

## Purpose
Defines the Docker registry error descriptor registry used by the package's distribution error model. It maps symbolic Docker error values such as `UNKNOWN`, `UNAUTHORIZED`, and `TOOMANYREQUESTS` to internal `ErrorCode` values, human messages, descriptions, and HTTP status codes.

## Important APIs, Types, And Functions
- Package globals `errorCodeToDescriptors`, `idToDescriptors`, and `groupToDescriptors` are the in-memory registries keyed by generated code, string value, and group.
- `ErrorCodeUnknown`, `ErrorCodeUnsupported`, `ErrorCodeUnauthorized`, `ErrorCodeDenied`, `ErrorCodeUnavailable`, and `ErrorCodeTooManyRequests` are registered during package initialization.
- `Register(group string, descriptor ErrorDescriptor) ErrorCode` assigns monotonic codes starting at `1000`, validates duplicate values/codes, stores the descriptor, and returns the code.
- `GetGroupNames`, `GetErrorCodeGroup`, and `GetErrorAllDescriptors` expose sorted descriptor views.

## Control Flow
Initialization registers known errors by calling `Register`. `Register` takes a mutex, assigns the next code, panics on duplicate descriptor value or generated code, updates all maps, then increments `nextCode`. Read APIs sort group names or descriptor slices before returning.

## State And Persistence
State is process-local and persistent for the package lifetime. It is guarded for writes by `registerLock`, but `GetErrorCodeGroup` sorts the backing slice in place, so callers should treat returned slices as read-only views of global state.

## Dependencies And Integration Points
Uses `net/http` status codes and the package's `ErrorCode`/`ErrorDescriptor` definitions from the Docker error model. The descriptors are consumed when parsing registry error bodies and building user-facing unexpected-status errors elsewhere in the Docker remotes package.

## Risks And Edge Cases
Duplicate registration panics at runtime, so additional error descriptors must use globally unique `Value` strings. Because descriptor groups are sorted in place, concurrent calls while third-party registration is happening could be sensitive, although normal registration happens during init.

## Test Signals
No direct test file is listed for this descriptor registry. Coverage is indirect through resolver/fetcher tests that expect Docker error bodies to surface meaningful messages and HTTP status wrappers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/errdesc.go -->
