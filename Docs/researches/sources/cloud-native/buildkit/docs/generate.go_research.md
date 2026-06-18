# Research: sources/cloud-native/buildkit/docs/generate.go

Purpose: updates generated command-output blocks in markdown files under `./docs`. It is a documentation maintenance tool, not runtime daemon code.

Important APIs and flow: `main` compiles a regexp matching `<!---GENERATE_START command-->...<!---GENERATE_END-->` blocks, opens `./docs` as an `os.Root`, walks markdown files, replaces each block by running `/bin/sh -c <command>` and embedding stdout in fenced code, writes changed files with original mode, prints changed paths, and exits nonzero on errors.

State and dependencies: reads and writes documentation files and executes shell commands embedded in docs. Depends on `os.OpenRoot`, `fs.WalkDir`, regexp replacement, `os/exec`, and error wrapping.

Risks and test signals: commands embedded in docs execute with shell privileges, so this tool must only run on trusted docs. Replacement captures stdout only; command errors are stored in the outer `err` and reported after traversal. No direct tests are present.
