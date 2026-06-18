# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/defaultshell.go

Purpose: returns the default shell used for shell-form RUN/CMD/ENTRYPOINT when the image config does not define one.

Important API: `defaultShell(os string) []string`.

Control flow: Windows returns `cmd /S /C`; all other OS values return `/bin/sh -c`.

State and persistence: none.

Dependencies and integration: called by `withShell` in `convert.go`, which influences command args and image config history.

Risks and test signals: risk is platform-specific shell behavior drift, especially Windows escaping. Covered by Dockerfile command integration tests.
