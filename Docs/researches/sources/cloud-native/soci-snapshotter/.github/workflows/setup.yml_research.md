# sources/cloud-native/soci-snapshotter/.github/workflows/setup.yml

Purpose: reusable workflow that chooses CI runner labels for SOCI Snapshotter workflows.

Important APIs/types/functions: workflow_call outputs `available-runners` and `runner-labels`; matrix entry with `use-codebuild`, CodeBuild runner names `ubuntu-x86` and `al2-arm`, fallback GitHub runner `ubuntu`.

Control flow: determines whether repository owner is `awslabs`; upstream uses CodeBuild labels, forks use Ubuntu GitHub-hosted runner. Outputs JSON arrays/maps for downstream workflow matrices.

State and persistence: no persistent state; prints matrix config.

Dependencies/integration: consumed by build and release workflows.

Risks: CodeBuild label naming embeds run id and attempt; downstream workflows depend on matching configured AWS CodeBuild projects. Forks get reduced platform coverage.

Test signals: downstream matrix expansion in build/release workflows.
