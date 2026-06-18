# sources/cloud-native/buildkit/frontend/dockerui/requests.go

## Purpose

This file handles Docker UI frontend subrequests selected through the `requestid` build option. It lets a frontend answer metadata-style requests such as subrequest descriptions, outline, target list, lint results, and LLB conversion without running the normal build path.

## Important APIs, Types, And Functions

- `keyRequestID` is the option key used to select a subrequest.
- `RequestHandler` groups optional handler callbacks for outline, targets, lint, and convert-LLB plus `AllowOther` fallback behavior.
- `(*Client).HandleSubrequest` dispatches the selected request and returns `(*client.Result, handled bool, error)`.
- `describe` builds the supported subrequest list and returns both JSON and text renderings in result metadata.

## Control Flow

`HandleSubrequest` first checks `bc.bopts.Opts["requestid"]`; if absent, it returns `(nil, false, nil)` so the caller can continue the normal build. For recognized requests it checks the matching callback, invokes it with the build context, converts the domain result to a gateway `client.Result`, and marks the request handled even when the callback returns nil. The describe request is synthesized from non-nil handlers. Unknown or unavailable requests return unsupported unless `AllowOther` tells the caller to handle it elsewhere.

## State And Persistence Behavior

The file does not persist state. It only reads build options and creates ephemeral result metadata. Returned metadata keys include `result.json`, `result.txt`, and `version`, which are consumed by clients asking for subrequest capabilities.

## Dependencies And Integration Points

It integrates with BuildKit subrequest packages: `subrequests`, `outline`, `targets`, `lint`, and `convertllb`. It returns gateway client results and uses `errdefs.NewUnsupportedSubrequestError` so unsupported request errors are recognizable by frontend callers.

## Risks And Edge Cases

The dispatch is callback-driven, so a frontend can advertise only handlers it supplies. `describe` currently lists outline and targets plus describe; lint and convert-LLB are handled by `HandleSubrequest` but are not included in the describe list, which may be intentional compatibility behavior or a discoverability gap. `AllowOther` changes unknown-request behavior from hard error to caller fallback, so misuse can hide typos.

## Test Signals

This file has no colocated tests in the subset. Useful tests would validate `handled` semantics for nil callback results, unsupported subrequest errors, and describe metadata contents.
