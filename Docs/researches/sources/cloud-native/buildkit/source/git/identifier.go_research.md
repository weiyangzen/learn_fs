# sources/cloud-native/buildkit/source/git/identifier.go

## Purpose
This file defines `GitIdentifier`, git signature verification options, URL parsing, provenance capture, and static validation for git bundle-related attributes.

## Important APIs and Types
`GitIdentifier` stores remote URL, ref, checksum, subdir, auth/SSH options, submodule and mtime behavior, fetch-by-commit, bundle locator/session/store overrides, checkout-bundle flag, and signature verification options. `GitSignatureVerifyOptions` stores public key and signed tag policy. `NewGitIdentifier` normalizes non-transport remotes to HTTPS and parses git URL options. `Scheme` returns `GitScheme`. `Capture` records git provenance and secret/SSH dependencies. `validateBundleAttrs`, `splitBundleLocator`, and `parseBundleLocator` enforce bundle constraints.

## Control Flow
`NewGitIdentifier` checks transport, prepends `https://` if needed, parses with `gitutil.ParseURL`, and copies ref/subdir options. `Capture` appends `#ref` for provenance URL display, records the pinned commit, adds bundle provenance when set, and records optional auth/SSH inputs. `validateBundleAttrs` parses the bundle locator, requires checksum, rejects mismatched SHA refs, and checks checkout-bundle incompatibilities. `parseBundleLocator` avoids `net/url`, parses the body with containerd reference parsing, validates digest and scheme, and requires SHA256.

## State and Persistence
Identifiers hold solve-time configuration only. Bundle fields influence later staging and checkout behavior. Provenance capture writes to the passed capture object.

## Dependencies and Integration Points
It depends on BuildKit git utilities, source type constants, provenance types, containerd reference parsing, and OCI digests. `Source.Identifier` elsewhere populates fields and invokes `validateBundleAttrs`.

## Risks
Bundle locator parsing supports only `docker-image+blob` and `oci-layout+blob`. Requiring SHA256 protects `downloadBundleToFile` verification but rejects other digest algorithms even if content-addressed. `Capture` marks secrets and SSH inputs optional, matching BuildKit provenance conventions but not proving they were actually used.

## Test Signals
`identifier_test.go` exercises URL parsing, subdir sanitization behavior from `gitutil`, valid/invalid bundle locators, checksum requirements, checkout-bundle incompatibilities, and SHA/ref mismatch handling.
