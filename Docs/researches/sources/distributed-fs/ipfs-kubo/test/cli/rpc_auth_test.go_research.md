# sources/distributed-fs/ipfs-kubo/test/cli/rpc_auth_test.go

Purpose: tests RPC authorization scopes across HTTP clients and CLI `--api-auth`, including bearer/basic secrets, path restrictions, disabled auth, unauthenticated rejection, version endpoint exception, multi-user separation, and empty allowed paths.

Important APIs and helpers: `rpcDeniedMsg` captures the expected denial message. `makeAndStartProtectedNode` injects `API.Authorizations` into config and starts the daemon using a special starter token allowed on `/api/v0`. `makeHTTPTest` builds clients using `auth.NewAuthorizedRoundTripper`; `makeCLITest` exercises `node.RunIPFS` with `--api-auth`.

Control flow: table-driven cases cover raw bearer token, `bearer:` secret syntax, basic `user:pass`, and pre-encoded basic credentials. Each case verifies allowed `/id` access and forbidden `/config/show` access for HTTP and CLI. Additional subtests check `/api/v0` grants full access, nil and empty maps disable auth checks, missing Authorization header is rejected when auth exists, `/version` is always accessible, Bob's token cannot access Alice-only paths, empty `AllowedPaths` denies all except version, and CLI commands fail without `--api-auth`.

State and persistence: authorization config is written before daemon startup and governs live RPC access. No runtime mutation or persistence after restart is tested.

Dependencies and integration points: integrates Kubo config, RPC HTTP middleware, CLI API auth flag, client/rpc auth transport, endpoint path matching, and daemon startup under protected APIs.

Risks and test signals: path matching must treat `/api/v0` as a prefix while preserving narrower endpoint controls. Failure signals include token leakage across scopes, unauthenticated access when auth is enabled, CLI not sending tokens, or version endpoint accidentally requiring scoped authorization.
