<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_build.go -->
# sources/cloud-native/moby/client/image_build.go

Purpose: sends build context streams to the daemon and converts build options into Engine API query/header form.

Important APIs/functions: `Client.ImageBuild` and private `imageBuildOptionsToQuery`.

Control flow: `ImageBuild` converts options to query values, JSON-marshals registry auth configs, base64-url encodes them into `X-Registry-Config`, sets `Content-Type: application/x-tar`, posts the raw build context to `/build`, and returns the daemon response body to the caller. `imageBuildOptionsToQuery` maps tags, security options, extra hosts, booleans, remote context, isolation, CPU/memory/shm/cgroup options, Dockerfile/target, JSON-encoded ulimits/build args/labels/cache sources/outputs, session/build IDs, builder version, and exactly one platform; multiple platforms currently return invalid-argument.

State and integration behavior: no local persistence; daemon may create images/build cache. Build context and response are streams owned by caller/daemon. Auth secrets are marshaled into headers, so logging headers is sensitive.

Dependencies: container/network/build/registry API types, base64, JSON, raw request helpers, and containerd errdefs.

Risks and test signals: risks include secret exposure in headers, unsupported multi-platform behavior, query encoding drift, and leaked response body. `image_build_test.go` covers errors, route, headers, selected query parameters, and response body handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_build.go -->
