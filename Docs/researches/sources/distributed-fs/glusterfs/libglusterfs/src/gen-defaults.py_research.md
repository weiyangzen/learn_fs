# sources/distributed-fs/glusterfs/libglusterfs/src/gen-defaults.py

## Purpose
`gen-defaults.py` is a build-time code generator that expands `#pragma generate` markers in a template C file into default GlusterFS FOP forwarding and callback functions. It delegates operation metadata and string substitution to `generator.py`.

## Important APIs, Types, and Functions
- Imports `ops`, `fop_subs`, `cbk_subs`, and `generate` from `generator.py`.
- `FAILURE_CBK_TEMPLATE`, `CBK_RESUME_TEMPLATE`, `CBK_TEMPLATE`, `RESUME_TEMPLATE`, `FOP_TEMPLATE`: template strings for default failure unwind, callback resume, normal callback, resume wind, and direct tail-wind functions.
- `gen_defaults()`: iterates all operation names from `ops` and prints generated code for each template class.

## Control Flow
The script reads the path provided as `sys.argv[1]` line by line. If a line contains `#pragma generate`, it emits begin/end generated-code comments and all generated default functions. Otherwise it prints the original line without its trailing newline. The generation order is all failure callbacks, all callback resumes, all callbacks, all resumes, then all FOPs.

## State and Persistence
The script has no persistent state. Its output is stdout, normally redirected by the build to create or refresh a generated C source. Operation order follows Python dictionary insertion order in `generator.py`.

## Dependencies and Integration Points
It integrates with the libglusterfs build system, `defaults-tmpl.c` style inputs, `STACK_UNWIND_STRICT`, `STACK_WIND`, `STACK_WIND_TAIL`, and the operation metadata in `generator.py`. Generated defaults provide pass-through xlator behavior used across translator stacks.

## Risks and Edge Cases
- Missing or reordered metadata in `generator.py` changes generated ABI-facing functions.
- The marker search is substring-based, not syntax-aware.
- The script expects exactly one input argument and does not validate it.
- Generated text formatting is template-driven and not automatically reindented.

## Test Signals
Regenerate defaults from the canonical template and diff against committed/generated output. Add spot checks for representative FOPs with pointer and scalar callback args, especially `readv`/`writev` naming special cases inherited from `generator.py`.
