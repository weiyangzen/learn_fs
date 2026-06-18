## sources/distributed-fs/ipfs-kubo/version_test.go

Purpose: unit tests for fork suffix derivation, implicit suffix precedence, and user-agent version formatting.

Important tests and control flow: `TestSuffixFromForkPath` covers empty/upstream paths, known forge forks, renamed repos, unknown hosts, nested paths, leading/trailing slashes, and short inputs. `TestImplicitAgentSuffix_PrefersBuildOrigin` mutates `buildOrigin` and verifies it overrides build info for forks while upstream/empty origin produce no suffix under the test module path. `TestGetUserAgentVersion` saves/restores globals and verifies combinations of commit, tagged release marker, and suffix.

State and persistence: tests mutate package globals (`CurrentCommit`, `taggedRelease`, `userAgentSuffix`, `buildOrigin`) with cleanup restoration.

Dependencies and integration points: uses `testify/assert` and the implementation in `version.go`.

Risks and test signals: strong coverage for expected string formatting and fork heuristics. Does not test `cmdutils.CleanAndTrim` edge inputs directly beyond using `SetUserAgentSuffix`.
