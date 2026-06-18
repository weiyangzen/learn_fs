# sources/cloud-native/containerd/cmd/ctr/commands/content/content.go

Purpose: implements the `ctr content` command family for content-store CRUD, active ingests, labels, editing blobs, and low-level remote fetch/push operations.

Important APIs/functions: `Command`, `getCommand`, `ingestCommand`, `activeIngestCommand`, `listCommand`, `setLabelsCommand`, `editCommand`, `deleteCommand`, `fetchObjectCommand`, `fetchBlobCommand`, `pushObjectCommand`, `edit()`, and `onCloser`.

Control flow: commands create a containerd client when operating on local content. `get` streams a blob to stdout. `ingest` writes stdin as a blob with optional expected descriptor. `active` lists active writer statuses. `list` walks content metadata. `label` updates selected label field paths. `edit` copies a blob to a temp file, runs `$EDITOR` command through `sh -c`, writes edited content back under an `edit-<digest>` ref, commits by writer digest, and prints the new digest. `delete` removes blobs. Remote object/blob commands use resolver fetchers. `push-object` reads a local blob and uploads it with a supplied media type.

State and persistence: reads/writes content blobs, content labels, ingest statuses, temp edit files, and remote registry content.

Dependencies/integration: content store APIs, remotes resolver APIs, digest parsing, Docker units, tabwriter, command registry resolver helpers, and `os/exec`.

Risks: `edit()` runs the editor via shell interpolation, so editor strings are shell-evaluated. `push-object` requires caller-supplied media type and digest. Label path construction can be sensitive to label keys containing path separators/dots. `ingest` expects a single invocation and notes it is not reentrant.

Test signals: no local tests in this subset.
