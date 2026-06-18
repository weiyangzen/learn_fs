<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/describe.go -->
# sources/cloud-native/buildkit/frontend/subrequests/describe.go

Purpose: implements the client-side `frontend.subrequests.describe` helper and text renderer for listing subrequests supported by a frontend.

Important APIs, types, and functions: `RequestSubrequestsDescribe` is the request id. `SubrequestsDescribeDefinition` advertises version `1.0.0`, RPC type, and both `result.json` and `result.txt`. `Describe(ctx, c)` verifies gateway caps, calls `c.Solve` with `requestid` and `frontend.caps`, extracts `result.json`, and unmarshals `[]Request`. `PrintDescribe(dt, w)` renders a tabular `NAME VERSION DESCRIPTION` list, trimming the `frontend.` prefix.

Control flow and state: `Describe` first checks `CapFrontendCaps`; lack of capability is normalized to an unsupported subrequest error. It then sends a Dockerfile frontend solve request and maps unsupported frontend-cap errors to unsupported subrequest errors for a stable caller contract. It has no persistent state.

Dependencies and integration: uses gateway client solve metadata, `frontend/gateway/pb` capabilities, `solver/errdefs` typed errors, and the local `Request` schema from `types.go`. The text printer is used when `result.txt` needs human-readable output.

Risks and test signals: missing `result.json` or malformed JSON fail hard. Error mapping is important for older daemons/frontends. Tests should exercise unsupported caps, unsupported subrequest propagation, JSON decoding, and tabwriter output.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/describe.go -->
