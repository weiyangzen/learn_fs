# sources/cloud-native/containerd/core/sandbox/store.go

## Purpose
Defines the sandbox metadata model, runtime options, store interface, and helper methods for labels/extensions.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Sandbox` stores ID, labels, runtime options, spec, sandboxer name, timestamps, and typed extensions. `RuntimeOpts` stores runtime name/options. `Store` defines create/update/get/list/delete. `AddExtension` initializes the extensions map and marshals arbitrary objects with typeurl. `GetExtension` unmarshals by name and returns `ErrNotFound` when absent. `AddLabel` and `GetLabel` manage labels.

This file defines persistent metadata shape but does not implement storage. Dependencies are context, time, errdefs, and typeurl.

Integration points are metadata DB stores, sandbox proxy store, task manager sandbox checks, and CRI sandbox metadata. Risks include typeurl registration requirements, callers mutating maps after store calls, missing label/extension semantics, and partial update field-name drift. Test signals are extension round-trip tests, label helper tests, and store implementation conformance.
