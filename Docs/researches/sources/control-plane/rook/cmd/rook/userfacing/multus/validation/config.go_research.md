## sources/control-plane/rook/cmd/rook/userfacing/multus/validation/config.go

Purpose: provides `rook multus validation config` subcommands that print example validation-test YAML for common deployment scenarios.

Important APIs and functions: `configCmd` is the parent. `converged`, `dedicated-storage-nodes`, and `stretch-cluster` each call a constructor in `pkg/daemon/multus`, convert the resulting config to YAML with `ToYAML()`, and print it to stdout.

Control flow: init attaches the three scenario commands. Each command has no args and returns conversion errors to Cobra. There is no filesystem or Kubernetes interaction.

State and persistence: stateless. Output is generated from defaults in the daemon multus package, so the content version tracks daemon config types rather than static YAML in this file.

Dependencies and integration points: depends on `pkg/daemon/multus` default config constructors and Cobra. It supports the `validation run --config` path by giving users valid config starting points. Risks: scenario defaults can drift from documentation or actual validation behavior; stdout-only output means shell redirection is expected. No direct tests are present in this file.
