<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_history.go -->
# sources/cloud-native/moby/client/image_history.go

Purpose: retrieves image layer history, optionally for a specific platform.

Important APIs/functions: `ImageHistoryWithPlatform` and `Client.ImageHistory`.

Control flow: applies options into `imageHistoryOpts`, rejects duplicate platform options, gates platform use on API version `1.48`, encodes platform JSON with `encodePlatform`, GETs `/images/{id}/history`, closes response, and decodes history items.

State and integration behavior: read-only daemon operation with no local persistence. Depends on version negotiation, platform encoding, and image history API types.

Risks and test signals: risks include feature-gating platform incorrectly, duplicate option handling, and empty image IDs not being explicitly validated in this file. `image_history_test.go` covers daemon errors, route, platform query behavior, and response decoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_history.go -->
