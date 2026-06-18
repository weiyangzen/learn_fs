# sources/control-plane/longhorn-engine/pkg/frontend/rest/server.go

Purpose: implements REST handlers for listing the volume and performing base64-encoded random reads and writes against the frontend backend.

Important APIs/types/functions: `ListVolumes` returns a `GenericCollection` with the single device volume. `GetVolume` resolves an encoded ID and returns 404 when it does not match. `ReadAt` decodes `ReadInput`, allocates a buffer of requested length, calls `backend.ReadAt`, and returns base64 data. `WriteAt` decodes `WriteInput`, validates decoded length, calls `backend.WriteAt`, and returns `WriteOutput`. Helpers `listVolumes` and `getVolume` build and locate the single volume.

Control flow: every action first validates the path ID against the current volume. `apiContext.Read` decodes request JSON into inputs. Errors from reads are wrapped with context, while write errors are returned directly after logging.

State and persistence: all durable effects are delegated to the backend. The server itself tracks only the `Device` pointer.

Dependencies and integration points: depends on Rancher API context, gorilla/mux variables, and the `Device.backend` `ReaderWriterUnmapperAt`. This handler layer is the actual REST integration point for volume data access.

Risks: `make([]byte, input.Length)` can panic or exhaust memory for invalid client-supplied lengths. Read ignores partial byte counts and returns the whole buffer even if backend read returns fewer bytes without error. Write ignores short-write counts if no error is returned. There is no request body cap, auth, or method-level locking.

Test signals: no direct tests. Boundary tests around invalid IDs, invalid base64, negative/large lengths, short reads/writes, and backend errors would be valuable.
