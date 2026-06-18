# sources/cloud-native/moby/integration/image/tag_test.go

Purpose: integration tests for image tag normalization and invalid tag rejection.

Important APIs and helpers: `TestTagUnprefixedRepoByNameOrName`, `TestTagUsingDigestAlgorithmAsName`, `TestTagValidPrefixedRepo`, `TestTagExistedNameWithoutForce`, `TestTagOfficialNames`, and `TestTagMatchesDigest`.

Control flow: tests tag busybox by name and ID into unprefixed repos, reject `sha256:sometag` ambiguity, accept several valid prefixed repository forms, allow retagging an existing tag, normalize official Docker Hub names, and reject digest references as tag targets while confirming no image is created for that digest.

State and persistence: mutates image tag references in the daemon store and inspects resulting repo tags. Invalid cases should leave no new matching reference.

Dependencies and integration: depends on image tag API, distribution reference parsing/normalization, busybox fixture, and image inspect.

Risks: official-name test comments suggest its assertion may be weak. Tag normalization rules are externally visible compatibility behavior and can be subtle.

Test signals: protects repository/tag parser behavior, ambiguous digest-algorithm name rejection, and digest-reference target rejection.
