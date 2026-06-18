# sources/cloud-native/soci-snapshotter/.github/dependabot.yml

Purpose: configures Dependabot updates for Go modules, Docker base images, and GitHub Actions.

Important APIs/types/functions: daily gomod updates for `/` and `/cmd` with `[DNM]` commit prefix, patch-only allowance for `github.com/containerd/containerd/v2`, ignores for Kubernetes deps and self-dependency, Docker updates for root Dockerfile with Go base image major/minor ignored, and daily GitHub Actions updates.

Control flow: Dependabot opens PRs according to ecosystem schedules and filters.

State and persistence: creates dependency update pull requests; does not mutate code without merge.

Dependencies/integration: aligns with scripts that manually bump deps and CI dependency review.

Risks: daily cadence can create PR noise. Patch-only containerd policy avoids accidental compatibility jumps but may miss security fixes requiring minor upgrades. Comments indicate PRs are tracking-only and not intended for direct merge.

Test signals: Dependabot PR generation and dependency review workflow.
