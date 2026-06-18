<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_attestations_opts.go -->
# sources/cloud-native/moby/client/image_attestations_opts.go

Purpose: declares result and functional option types for image attestations.

Important APIs/types/functions: `ImageAttestationsResult`, `ImageAttestationsOption`, `ImageAttestationsWithPlatform`, `ImageAttestationsWithPredicateTypes`, and `ImageAttestationsWithStatement`.

Control flow: option functions mutate private `imageAttestationsOpts` by setting platform, appending predicate type filters, or enabling statement inclusion.

State and integration behavior: no persistence. Options are accumulated per method call and consumed by `ImageAttestations`.

Dependencies and risks: depends on image attestation API types and OCI platform structs. Risks include repeated option accumulation semantics and no validation of empty predicate strings. Coverage is mainly compile-time in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_attestations_opts.go -->
