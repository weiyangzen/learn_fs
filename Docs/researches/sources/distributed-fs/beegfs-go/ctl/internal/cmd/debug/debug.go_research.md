
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/debug/debug.go

- Purpose: hidden `debug <node> <command>` passthrough for node debug commands.
- Important APIs: `NewCmd` and `runGenericDebugCmd`.
- Control flow/state: parses a meta/storage node, concatenates all remaining positionals into a single command string, calls `dbg.GenericDebugCmd`, and prints the raw response.
- Dependencies/integration: uses BeeGFS entity parsing and `ctl/pkg/ctl/debug`; command list is documented in long help but execution is backend-defined.
- Risks/tests: deliberately dangerous debug surface, including cache dropping and state inspection/modification; trailing space in command assembly is benign only if backend tolerates it. No direct tests.
