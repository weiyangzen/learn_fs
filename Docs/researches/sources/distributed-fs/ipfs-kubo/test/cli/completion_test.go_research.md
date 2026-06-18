# sources/distributed-fs/ipfs-kubo/test/cli/completion_test.go

Purpose: verifies shell completion generation for Bash and Zsh.

Important APIs/functions: `TestBashCompletion`, `TestZshCompletion`, harness `IPFS("commands", "completion", ...)`, `testutils.RequiresLinux`, and shell runner invocation for `bash`/`zsh`.

Control flow: each test requests generated completion script text, fails if it is unexpectedly short, writes it to a temporary file, then sources it in the target shell and checks the IPFS completion function registration.

State/persistence: uses temporary files only; no daemon or repo persistence is needed.

Dependencies/integration: CLI command tree, completion generator, local `bash` and `zsh` availability, shell startup behavior, and harness temp file helpers.

Risks/test signals: validates generated scripts are syntactically loadable, not full interactive completion semantics. Zsh tool availability and shell environment can affect results.
