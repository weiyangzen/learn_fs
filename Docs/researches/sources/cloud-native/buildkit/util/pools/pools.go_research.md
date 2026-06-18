## sources/cloud-native/buildkit/util/pools/pools.go

Purpose: generic typed wrapper around `sync.Pool`.

Important API/type: `Pool[T]`, `New(newFn)`, `Get`, and `Put`.

Control flow/state: `New` stores a `sync.Pool` whose `New` returns the typed value as `any`; `Get` type-asserts; `Put` returns values. No cleanup or reset callback.

Integration points: used by overlay differ for reusable byte buffers. Risks: callers must reset values before/after reuse as needed; type assertion assumes only this wrapper writes to the pool. Test signals: no local tests.
