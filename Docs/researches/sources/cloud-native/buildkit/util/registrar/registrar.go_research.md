<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/registrar/registrar.go -->
# sources/cloud-native/buildkit/util/registrar/registrar.go

Purpose: generic concurrent registrar that lets callers register a value by key and lets other callers wait briefly for that value to appear.

Important APIs and types: `Registrar[K,V]`, `New`, `Register`, `Get`, `Discard`, `getOrCreateRegistrar`, and internal `registrarValue`.

Control flow: `Get` creates or retrieves a keyed `registrarValue`, starts a three-second discard timer only for newly created missing registrations, then waits for context cancellation or `notifyCh` closure. `Register` stores a value and closes the notification channel once. `Discard` removes the entry and signals waiters with `context.Canceled`.

State and persistence: process-local map protected by a mutex; per-value state has its own mutex and closed channel. Values persist until explicitly discarded.

Dependencies and integration: depends only on context, sync, and time. Useful for bridging asynchronous component registration.

Risks: `getOrCreateRegistrar` invokes `onCreate` while holding the registrar mutex, but in a goroutine; the timer can race with real registration and will call `Discard` after three seconds if still pending. Once a registrar value is set, subsequent registrations are ignored.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/registrar/registrar.go -->
