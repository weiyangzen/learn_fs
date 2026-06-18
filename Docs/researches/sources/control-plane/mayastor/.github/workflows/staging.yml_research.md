# sources/control-plane/mayastor/.github/workflows/staging.yml

## Purpose
Manual staging release workflow that validates a tag and builds/pushes dev images.

## Important Jobs and Steps
`workflow_dispatch` requires `tag`. `preflight-checks` checks out submodules, installs Nix, warms staging shell, logs into a registry using `REGISTRY_USERNAME/PASSWORD`, and runs `validate.sh --tag <TAG> --type staging`. `build-images` calls reusable `image.yml` with `registry: ghcr.io`, `namespace: mayastor/dev`, and inherited secrets.

## Control Flow
Image build starts only after preflight succeeds. The tag is also exposed as `TAG` env.

## State and Persistence
No repo writes. Pushes images through the called image workflow.

## Dependencies and Integration Points
Depends on staging scripts, Nix, registry secrets, and `image.yml`. Integrates with the release pipeline that later mirrors dev images.

## Risks
The login step name is incomplete (`Login to`). More importantly, `image.yml`'s event-name condition may not honor `workflow_call` inputs, so staging image tagging should be verified. Registry credential target is implicit because no `registry` input is passed to docker/login-action.

## Test Signals
Manual dispatch with a staging tag, successful validation, and expected images in `ghcr.io/<owner>/mayastor/dev:<tag>`.
