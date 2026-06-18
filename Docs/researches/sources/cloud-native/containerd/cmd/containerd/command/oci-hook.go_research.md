# sources/cloud-native/containerd/cmd/containerd/command/oci-hook.go

Purpose: implements the hidden-style `containerd oci-hook` utility that templates hook arguments/environment from OCI runtime hook state and then `exec`s the requested hook binary.

Important APIs/functions: `ociHook` CLI command; `hookSpec` shallow config struct; `loadSpec()` reads bundle `config.json`; `loadHookState()` decodes OCI state from stdin; `templateContext` exposes `id`, `bundle`, `rootfs`, `pid`, `annotation`, and `status`; `templateList.render()` rewrites each argument/env entry; `render()` executes Go templates.

Control flow: command reads `specs.State` from stdin, loads bundle OCI config, builds a template context, templates CLI args and current environment, then replaces the process with `syscall.Exec(args[0], args, env)`.

State and persistence: reads bundle config and stdin; does not write state. Process image is replaced on success.

Dependencies/integration: uses Open Containers runtime-spec state/root structs, containerd OCI config filename constant, Go `text/template`, and Unix `syscall.Exec`.

Risks: no explicit check that at least one command arg exists before indexing `args[0]`. `newTemplateContext()` assumes `spec.Root` is non-nil and accesses `spec.Root.Path`. Template execution errors abort the hook; templates can expose annotation values into args/env.

Test signals: no local tests for nil root, missing args, or template behavior in this subset.
