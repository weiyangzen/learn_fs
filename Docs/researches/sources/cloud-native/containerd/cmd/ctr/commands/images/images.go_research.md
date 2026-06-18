# sources/cloud-native/containerd/cmd/ctr/commands/images/images.go

Purpose: implements `ctr images` parent command and list/label/check/delete/prune subcommands.

Important APIs/functions: `Command`, `listCommand`, `setLabelsCommand`, `checkCommand`, `removeCommand`, and `pruneCommand`.

Control flow: list prints image refs or detailed table with target type/digest/size/platforms/labels. Label updates image labels with optional replace-all. Check verifies required content and unpack status for default platform/snapshotter and prints table or ready refs. Delete removes named image refs and can request synchronous GC on the last target. Prune requires `--all`, identifies images unused by current containers, and deletes the last one synchronously.

State and persistence: reads/writes image metadata, labels, container references, content availability, and snapshot unpack state; delete/prune can trigger garbage collection.

Dependencies/integration: image service, container service, content store, core images helpers, platform helpers, progress byte formatting, errdefs, tabwriter.

Risks: prune only compares image names used by containers and does not support filters beyond all. Delete reports first non-not-found error while continuing. Label replace-all appends `"labels"` once per supplied label key, which is redundant but functional.

Test signals: no local tests in this subset.
