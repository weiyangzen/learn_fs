<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/distribution_inspect.go -->
# sources/cloud-native/moby/client/distribution_inspect.go

Purpose: inspects an image distribution reference and returns descriptor/platform information.

Important APIs/types/functions: `DistributionInspectOptions`, `DistributionInspectResult`, and `Client.DistributionInspect`.

Control flow: rejects empty image refs with an image not-found error, builds the distribution inspect path for the image ref, GETs the daemon endpoint, closes response, and decodes the distribution inspect result.

State and integration behavior: read-only daemon/registry-related operation with no local persistence. Depends on shared request helpers and distribution/image API types.

Risks and test signals: risks include reference path escaping and empty-ref error compatibility. `distribution_inspect_test.go` covers empty id behavior; route/decode coverage is lighter in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/distribution_inspect.go -->
