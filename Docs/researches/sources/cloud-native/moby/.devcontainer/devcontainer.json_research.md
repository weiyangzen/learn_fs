<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.devcontainer/devcontainer.json -->
# sources/cloud-native/moby/.devcontainer/devcontainer.json

## Purpose
Defines the VS Code devcontainer for Moby. It builds the repository Dockerfile's `devcontainer` target, bind-mounts the local workspace into the Go import path, runs as root in a privileged container, and installs the Go extension.

## Important APIs, Types, And Functions
- `build.context: ".."` and `dockerfile: "../Dockerfile"` point at the repository root.
- `target: "devcontainer"` maps to the Dockerfile stage that copies source and installs `gopls`.
- `workspaceFolder` and `workspaceMount` place the project at `/go/src/github.com/docker/docker`.
- `remoteUser: "root"` and `runArgs: ["--privileged"]` support daemon/container tests.

## Control Flow
The devcontainer CLI or VS Code builds the image, starts a privileged container, bind-mounts the repository, and opens the configured workspace folder. There is no runtime script in this JSON file.

## State And Persistence
The host workspace is persisted through the bind mount. Tooling and packages are provided by the Dockerfile image layers. Docker daemon state inside the container can persist only if volumes are configured elsewhere.

## Dependencies And Integration Points
Depends on the root `Dockerfile` `devcontainer` target, the `golang.go` VS Code extension, Docker privileged container support, and the Moby Makefile paths.

## Risks And Edge Cases
Running privileged as root is necessary for many daemon workflows but broadens local risk. The mount path uses the historical `github.com/docker/docker` import root, while some API module metadata uses `github.com/moby/moby`; path-sensitive tools must tolerate that.

## Test Signals
Successful devcontainer build and VS Code attach are the direct signals. Follow-on signals are `make shell`, Go language server startup, and daemon tests running inside the privileged environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.devcontainer/devcontainer.json -->
