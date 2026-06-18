# sources/control-plane/longhorn-engine/pkg/frontend/rest/router.go

Purpose: wires the REST frontend's Rancher-style API routes and error handling.

Important APIs/types/functions: `HandleError` wraps handlers with `api.ApiHandler` and writes API errors through `apiContext.WriteErr`. `NewRouter` creates a strict-slash gorilla mux router with version/schema endpoints and volume list/get/read/write routes.

Control flow: requests first pass through Rancher API context setup, then handler errors are translated to API responses. Volume actions are POSTs to `/v1/volumes/{id}?action=readat` and `writeat`.

State and persistence: no state. Each `NewRouter` call builds a fresh schema set.

Dependencies and integration points: integrates with `rest/model.go` for schemas and `rest/server.go` for handlers. Uses gorilla/mux path variables and Rancher API version/schema handlers.

Risks: route set exposes only one volume but uses collection semantics. No middleware enforces auth, body size, or rate limits. `StrictSlash(true)` can redirect paths, which may interact poorly with action query clients.

Test signals: no direct tests. Route matching and error wrapper behavior are untested in this subset.
