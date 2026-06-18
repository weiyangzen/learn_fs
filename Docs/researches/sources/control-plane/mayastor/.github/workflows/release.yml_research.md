# sources/control-plane/mayastor/.github/workflows/release.yml

## Purpose
Release-created workflow that validates a release tag and mirrors images from dev registry to Docker Hub.

## Important Jobs and Steps
`preflight-checks` checks out full history/submodules, installs Nix, warms staging shell, logs into Docker Hub, then runs `validate.sh --tag <ref_name> --type release`. `release-images` repeats checkout/Nix/logins for Docker Hub and GHCR, then runs `mirror-images.sh --source ghcr.io/<owner>/mayastor/dev --target docker.io/<owner> --tag <ref_name>`.

## Control Flow
Triggered when a GitHub release is created. Image mirroring requires preflight success.

## State and Persistence
Does not write repo files. Mutates external registries by mirroring images to Docker Hub.

## Dependencies and Integration Points
Requires staging scripts under `utils/dependencies`, Nix, Docker Hub/GHCR credentials, and release tags matching validation policy.

## Risks
Release creation immediately triggers registry operations. Credentials and image source/target paths must match repository owner conventions. Validation is delegated to external scripts not visible in this file.

## Test Signals
Dry-run or staging release validation where supported, successful `validate.sh`, and expected image tags present in Docker Hub after mirroring.
