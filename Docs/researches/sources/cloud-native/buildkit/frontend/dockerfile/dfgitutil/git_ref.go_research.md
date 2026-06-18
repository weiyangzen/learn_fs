# sources/cloud-native/buildkit/frontend/dockerfile/dfgitutil/git_ref.go

Purpose: parses Dockerfile-specific Git references used by ADD and Git build contexts, including fragment syntax and query-string options.

Important APIs and types: `GitRef` captures remote, short name, ref, checksum, subdir, flags for local-ambiguous and unencrypted refs, keep-git-dir, submodules, mtime, and fetch-by-commit. `ParseGitRef` parses and validates URLs. `loadQuery` applies query parameters. `FragmentFormat` converts query-form refs to fragment-form display.

Control flow: local `./` and `../` refs are invalid. `github.com/...` legacy refs are accepted as ambiguous local-like refs. HTTP(S) refs must end in `.git`; git/http mark unencrypted TCP. Query processing rejects missing values except boolean flags, rejects duplicate values, normalizes `tag` to `refs/tags/` and `branch` to `refs/heads/`, detects ref/subdir conflicts, parses booleans, and limits mtime values to `checkout` or `commit`.

State and persistence: pure parsing; returned flags control later LLB Git source options.

Dependencies and integration: used by ADD/COPY detection and `SOURCE_DATE_EPOCH` source resolution. Relies on BuildKit `gitutil` and containerd errdefs.

Risks and test signals: risks include ambiguous local refs, query conflict handling, boolean valueless handling, and security warnings not yet emitted for unencrypted TCP. `git_ref_test.go` has extensive coverage.
