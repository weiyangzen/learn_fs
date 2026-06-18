# sources/cloud-native/moby/integration-cli/docker_cli_save_load_unix_test.go

## Purpose

`docker_cli_save_load_unix_test.go` is the Unix-only companion for save/load integration behavior that depends on PTYs and Unix stdin/stdout semantics. It verifies streaming save/load through files and stdin, refusal to write archive bytes to a terminal, load progress/conflict messaging, and failure when `docker load` is invoked with an empty terminal-backed stdin.

The file is guarded by `//go:build !windows` and adds tests to `DockerCLISaveLoadSuite`.

## Important APIs, Types, and Helpers

The tests use `cli.DockerCmd`, `dockerBinary`, `deleteImages`, `inspectField`, `build.WithDockerfile`, and `dockerCmdWithError` from the integration harness. `icmd.RunCmd` is used to run CLI commands with explicit stdin/stdout handles. `github.com/creack/pty` provides pseudo-terminal handles for terminal-safety checks. `context.WithTimeout` and `testutil.GetContext` bound the empty-stdin `docker load` case.

## Control Flow and Coverage

`TestSaveAndLoadRepoStdout` creates a container, commits it to `foobar-save-load-test`, saves the image to a temp tar file via stdout, deletes the image, reloads it from the temp file via stdin, and confirms the reloaded image ID matches the committed ID. It then deletes the image again and runs `docker save` with stdin/stdout/stderr all attached to a PTY, expecting failure and a terminal-safety message containing "cowardly refusing".

`TestSaveAndLoadWithProgressBar` builds a small image, saves it to a tar file, removes and retags an older image under the same name, then loads the tar and expects a message that the existing image is being renamed. It is skipped with the snapshotter because that progress/rename path was not implemented there.

`TestLoadNoStdinFail` attaches `docker load` to a PTY with no input and a five-second timeout. It expects the command to fail promptly and emit "requested load from stdin, but stdin is empty" rather than hanging indefinitely.

## State and Persistence Behavior

The tests use temp files for archive storage and persistent image tags to verify deletion and restoration. `TestSaveAndLoadRepoStdout` compares image IDs before deletion and after load, giving a direct persistence signal. The progress-bar test intentionally creates a tag conflict to validate load-time rename behavior and image-store mutation. PTY tests do not persist daemon state beyond attempted commands, but they validate CLI safeguards around terminal I/O.

## Dependencies and Integration Points

This file integrates image archive streaming with Unix file descriptors and terminal detection. It depends on `busybox`, local temp files, PTY support, and normal Unix process semantics. The progress test depends on builder behavior and image-store conflict handling.

## Risks and Maintenance Notes

PTY-driven tests can be sensitive to buffering and exact terminal error messages. The string "cowardly refusing" is a deliberate CLI UX contract but may be brittle. The progress/rename test is skipped under snapshotter, so behavior differs by image store. Empty-stdin failure is timeout-protected to avoid hangs, but slow or unusual terminal behavior could still make the test flaky.

## Test Signals

Passing tests signal that Unix `docker save`/`load` streaming works through regular files and stdin, terminal output safeguards prevent binary tar data from being dumped to a TTY, load handles tag conflicts with user-visible progress messages where supported, and `docker load` fails clearly when no stdin data is provided.
