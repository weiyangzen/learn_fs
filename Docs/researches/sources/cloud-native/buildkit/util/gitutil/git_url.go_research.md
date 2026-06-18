## sources/cloud-native/buildkit/util/gitutil/git_url.go

Purpose: parses BuildKit Git remotes, including standard URLs and SCP-like SSH syntax, into a normalized `GitURL` with BuildKit fragment metadata.

Important APIs/types: constants for `http`, `https`, `ssh`, `git`; errors `ErrUnknownProtocol`, `ErrInvalidProtocol`; `GitURL` with scheme/host/path/user/query/options/remote; `GitURLOpts{Ref,Subdir}`. `ParseURL`, `IsGitTransport`, `FromURL`, and internal `fromSCPStyleURL` are the main functions.

Control flow: a protocol regexp detects `scheme://`; unsupported schemes error as invalid. Standard URLs go through `net/url.Parse` and `FromURL`, which strips fragment and raw query from `Remote` while preserving query separately. Non-standard inputs are parsed via `sshutil.ParseSCPStyleURL`. `parseOpts` splits fragment on the first `:` into ref and normalized subdir using `path.Join`.

State/persistence: stateless parser. Dependencies: `net/url`, BuildKit `sshutil`, `path`, `regexp`.

Integration points: used by Git source frontend/resolver to separate clone remote from BuildKit ref/subdir hints. Risks: query params are preserved in `Query` but excluded from `Remote`, so callers must intentionally handle query metadata. Fragment `ref:subdir` cannot represent refs containing a colon. Test signals: `git_url_test.go` covers protocol variants, credentials, ports, queries, fragments, SCP paths, invalid protocol, and case-insensitive schemes.
