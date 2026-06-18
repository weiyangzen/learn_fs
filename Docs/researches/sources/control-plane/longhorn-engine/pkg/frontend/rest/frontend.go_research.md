# sources/control-plane/longhorn-engine/pkg/frontend/rest/frontend.go

Purpose: implements the optional REST frontend for a Longhorn engine device, exposing backend read/write actions over an HTTP API on localhost.

Important APIs/types/functions: `Device` stores name, size, sector size, `isUp`, and backend `types.ReaderWriterUnmapperAt`. It implements the frontend interface through `FrontendName`, `Init`, `Startup`, `Shutdown`, `State`, `Endpoint`, `Upgrade`, and `Expand`. `start` builds a `Server`, `mux.Router`, Rancher/gorilla handlers, and starts `http.ListenAndServe` on `localhost:9414` in a goroutine.

Control flow: `Startup` assigns the backend then starts the listener and marks the device up. `Shutdown` only flips `isUp` through `stop`; it does not stop the HTTP server. `Endpoint` returns the fixed localhost URL only when `isUp` is true.

State and persistence: no durable state. Runtime state is the backend pointer and `isUp`. HTTP server lifetime is process-wide once started.

Dependencies and integration points: integrates with `rest/server.go`, `rest/router.go`, `types.Frontend`, gorilla handlers, and Rancher API helpers. The endpoint is a debugging/control surface rather than the main iSCSI path.

Risks: fixed port `9414` prevents multiple REST frontends in one process/host namespace. There is no server shutdown or listener handle, so repeated start/stop can leave a listener running. The API is bound to localhost and has no authentication; if exposed through host networking/proxies it allows raw volume reads and writes. Upgrade and expand are unsupported.

Test signals: no direct tests. REST behavior would need HTTP integration tests because shutdown and port collision behavior are not exercised here.
