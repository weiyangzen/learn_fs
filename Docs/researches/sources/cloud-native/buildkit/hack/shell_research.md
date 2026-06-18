<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/shell -->
# sources/cloud-native/buildkit/hack/shell

Purpose: builds the BuildKit `dev-env` image target and opens an interactive privileged shell inside it.

Important APIs, types, and functions: shell script creates a temporary Docker iidfile, runs `DOCKER_BUILDKIT=1 docker build --target dev-env .`, traps cleanup to remove the image id, conditionally mounts `SSH_AUTH_SOCK`, the source tree, and a Docker config file, then runs the image with `--privileged`, `/tmp` volume, registry mirror cache env, and `ash`.

Control flow and state: state is Docker image/container state plus any mounted workspace writes. The script primarily resolves environment and delegates to Docker.

Dependencies and integration: integrates with BuildKit's hack scripts and Docker CLI detection in `hack/util`. It is a developer convenience for reproducing CI/build environment behavior.

Risks and test signals: unquoted variables make paths with spaces fragile, and cleanup depends on the iidfile remaining readable. Behavior depends on Docker availability, TTY support, and mount permissions. Validate with `hack/shell` startup and expected tools present inside the container.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/shell -->
