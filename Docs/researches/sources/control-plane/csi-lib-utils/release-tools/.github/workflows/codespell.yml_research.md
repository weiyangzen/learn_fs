# sources/control-plane/csi-lib-utils/release-tools/.github/workflows/codespell.yml

## Purpose

This GitHub Actions workflow runs `codespell` on pushes and pull requests for the release-tools repository. It provides a repository-level spelling gate outside of Prow.

## Important Behavior

The workflow has one `codespell` job on `ubuntu-latest`. It checks out the repository using a pinned `actions/checkout` commit and invokes a pinned `codespell-project/actions-codespell` commit. Inputs enable filename checks and skip binary/image/checksum files, `.git`, the workflow file itself, and `./prow.sh`.

## State, Dependencies, and Integration

There is no persistent state. Dependencies are GitHub Actions, the checkout action, and the codespell action. It overlaps with `verify-spelling.sh`, but uses a different tool/action path than the shell verifier, giving an additional spelling signal for GitHub-native changes.

## Risks and Test Signals

Pinned action SHAs reduce supply-chain drift but require updates. The broad skip for `prow.sh` avoids noisy false positives in a large shell script, but spelling mistakes there will not be caught by this workflow. The only test signal is the workflow result in GitHub Actions.
