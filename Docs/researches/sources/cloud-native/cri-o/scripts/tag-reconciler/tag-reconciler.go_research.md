# sources/cloud-native/cri-o/scripts/tag-reconciler/tag-reconciler.go

This automation reconciles expected release tags for each active CRI-O release branch. It reads the current version from each release branch, checks whether that version tag already exists on the branch, and if missing creates and pushes the tag and triggers the GitHub `test` workflow.

Important functions are `run`, `pushTagToRemote`, and `hasCurrentReleaseVersionTag`. `run` requires `GITHUB_TOKEN`, reads `REMOTE` and `ORG` defaults, configures git identity, opens the repo, loops over `version.ReleaseMinorVersions`, builds `release-x.y`, reads the current semver using `scripts/utils`, prefixes it with `v`, queries tags for the branch, and pushes missing tags. `pushTagToRemote` creates an annotated/lightweight tag via release-sdk `repo.Tag`, pushes `git push <remote> tag <tag>`, and triggers `gh workflow run test --ref <tag>`.

State changes include branch checkouts in the utils call, tag creation, remote push, and workflow dispatch. Dependencies are release-sdk git, release-utils command/env, logrus, slices, GitHub CLI, and CRI-O version metadata. Risks include trusting the version file on each branch, no rollback if workflow dispatch fails after tag push, branch checkout side effects, and no direct validation that `ORG` is used beyond logging. There are no direct tests here.
