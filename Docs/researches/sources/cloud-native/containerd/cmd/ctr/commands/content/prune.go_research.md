# sources/cloud-native/containerd/cmd/ctr/commands/content/prune.go

Purpose: implements `ctr content prune references`, removing GC reference labels from layer content to allow garbage collection.

Important APIs/functions: `pruneCommand`, `pruneReferencesCommand`, `isLayerLabel()`, and `isInteger()`.

Control flow: command creates client/context, optionally sets debug logging for dry run, walks all content, identifies layer reference labels by current and legacy prefixes, removes matching labels unless dry run, updates changed content records, creates a short-lived random lease, then deletes it synchronously unless `--async` was set to trigger GC.

State and persistence: mutates content labels and lease state. Dry run logs intended changes only.

Dependencies/integration: content store walk/update, leases service, containerd log, shared client helper.

Risks: label matching is string-prefix based and intentionally preserves config label index `0`; future label naming changes could be missed. Creating/deleting a lease is used to drive GC side effects.

Test signals: no local tests here for label classification.
