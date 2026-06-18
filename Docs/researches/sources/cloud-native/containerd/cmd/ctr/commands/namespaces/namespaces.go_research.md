# sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces.go

Purpose: implements `ctr namespaces` create/list/remove/label commands.

Important APIs/functions: `Command`, `createCommand`, `setLabelsCommand`, `listCommand`, and `removeCommand`.

Control flow: create validates namespace and creates it with parsed labels. Label sets or clears each label through namespace service. List prints names or names with sorted labels. Remove builds platform-specific delete options, deletes each target namespace, ignores not-found, logs other failures while returning the first error, and prints each target.

State and persistence: mutates namespace metadata and labels; Linux remove can also request namespace cgroup deletion.

Dependencies/integration: namespace service, shared label/client helpers, platform-specific `deleteOpts()`, errdefs, logging.

Risks: label updates are one RPC per label and not atomic. Remove prints targets even when not found. Namespace must be empty per description, enforced by service.

Test signals: no local tests.
