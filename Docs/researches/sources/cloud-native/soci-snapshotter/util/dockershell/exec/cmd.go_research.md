# sources/cloud-native/soci-snapshotter/util/dockershell/exec/cmd.go

Purpose: this file wraps `docker exec` in an `exec.Cmd`-like API for running commands inside a target container.

Important APIs and types: `Supported` runs `docker version`. `Exec` identifies a container by name and creates commands. `New` validates container availability through `docker inspect`. `Exec.Command` constructs a `Cmd`. `Exec.Kill` runs `docker kill`. `Cmd` exposes familiar fields: path, args, env, dir, stdin/stdout/stderr. Methods mirror `exec.Cmd`: `CombinedOutput`, `Output`, `Run`, `Start`, `Wait`, pipes, and `String`.

Control flow: `Command` resolves the `docker` binary once and stores any lookup error. `toDocker` translates `Cmd` into a host command `docker exec` with `-i`, `-w`, and `-e` options as needed, followed by container name and command args. Execution methods check `lookPathErr` for synchronous methods; pipe/start methods call `toDocker` directly.

State and persistence: command state is held in the embedded `*exec.Cmd`; repeated calls mutate the same `dockerExec.Args` and stdio fields. No persistent state is created except effects of commands inside containers.

Dependencies and integration points: used by `dockershell.Shell` and Compose wrapper to execute commands in integration containers.

Risks: `Start`, pipe methods, and `String` do not check `lookPathErr`, so missing Docker may surface inconsistently. Reusing the same `Cmd` after execution is not safe, matching `exec.Cmd` semantics but not enforced. Args include a literal `"docker"` element even though `Path` is set to the docker binary, which is normal for `exec.Cmd` display/argv0.

Test signals: no direct tests in this subset; behavior is likely integration-tested through Docker shell utilities.
