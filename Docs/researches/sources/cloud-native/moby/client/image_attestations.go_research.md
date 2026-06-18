<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_attestations.go -->
# sources/cloud-native/moby/client/image_attestations.go

Purpose: retrieves in-toto attestation statements attached to an image.

Important APIs/functions: `Client.ImageAttestations`.

Control flow: rejects empty image IDs with an image not-found error, requires API version `1.55` via `requiresVersion`, applies functional options, encodes optional platform JSON, repeated predicate `type` filters, and `statement=1`, GETs `/images/{id}/attestations`, closes response, and decodes items.

State and integration behavior: read-only daemon operation; no local persistence. It is feature-gated by negotiated API version and integrates with image attestation API types.

Dependencies and risks: depends on `encodePlatform`, version negotiation, JSON decoding, and option application. Risks are feature gating on older daemons, query encoding of predicate types, and optional statement payload size. No dedicated tests in this subset; compile and request-layer tests are indirect signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_attestations.go -->
