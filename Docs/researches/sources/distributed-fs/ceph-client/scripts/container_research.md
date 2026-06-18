# sources/distributed-fs/ceph-client/scripts/container

## Purpose
`container` runs a command in a Docker or Podman container with the current directory mounted at `/src`, providing a kernel-development container wrapper.

## Important APIs, Types, and Functions
`ContainerRuntime` is the abstract base with `is_present()`, `_do_run()`, `_do_abort()`, and `run()`. `CommonRuntime` implements shared `run` options: container name, `--rm`, current directory bind mount, working directory, env file, and interactive TTY. `DockerRuntime` adds `--user uid:gid`; `PodmanRuntime` adds `--userns keep-id`. `Runtimes` selects by name or first present runtime. `_get_logger()` creates a tagged logger.

## Control Flow and State
`main()` creates logging, resolves the runtime, and runs the requested image and command. Each invocation creates a UUID container name and aborts it on `KeyboardInterrupt`. No repo state is persisted.

## Dependencies and Integration
It depends on Python 3, Docker or Podman, and filesystem mount permissions. It is documented as a kernel container build helper.

## Risks and Test Signals
The current working directory is mounted read/write into the container, so commands can modify the source tree. UID/GID args are strings from argparse and are passed through directly. Test runtime auto-selection, missing runtime, Docker and Podman option sets, env-file mode, shell TTY mode, interrupt cleanup, and command exit propagation.
