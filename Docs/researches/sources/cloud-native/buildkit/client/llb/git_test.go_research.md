# sources/cloud-native/buildkit/client/llb/git_test.go

Purpose: verifies git source identifier and attribute generation.

Important APIs/types/functions: `TestGit` table-tests `Git` with fragment refs, subdirs, option overrides, bundle URLs, OCI-layout bundle store settings, and checkout bundle mode.

Control flow: each case marshals the state, expects a two-op definition, locates the source op via final pointer, and compares the exact source identifier and attrs map.

State and persistence: no live git network access; source ops are declarative.

Dependencies/integration points: `Git`, `GitRef`, `GitSubDir`, `GitChecksum`, `GitBundleURL`, `GitBundleOCIStore`, `GitCheckoutBundle`, protobuf source attrs.

Risks/test signals: protects canonical URL/id construction and attribute compatibility. It does not exercise SSH known-host keyscan or actual git fetch behavior.
