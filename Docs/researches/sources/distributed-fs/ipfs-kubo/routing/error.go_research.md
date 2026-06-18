# sources/distributed-fs/ipfs-kubo/routing/error.go

Purpose: defines a typed error for missing routing configuration parameters.

Important APIs and control flow: `NewParamNeededErr` constructs `ParamNeededError` with the missing param and router type. `Error` formats a message explaining the required configuration parameter for delegated routing types.

State and persistence: none.

Dependencies and integration: used by `httpRoutingFromConfig` when the HTTP router endpoint is missing. Depends on Kubo config router type definitions.

Risks and test signals: no direct tests, but parser error paths can expose this. Message wording says "delegated routing types" generically even when a specific type is involved.
