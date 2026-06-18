# File Research: sources/block-storage/lvm2/lib/commands/cmd_enum.h

## Summary
Generates an enum of LVM command identifiers by including the generated `cmds.h` table with a local `cmd(a, b)` macro expansion.

## Main Responsibilities
- Wrap generated command definitions in an enum.
- Convert each `cmd(foo_CMD, foo)` entry from `cmds.h` into a unique enum constant `foo_CMD`.
- Provide an include guard for command enum consumers.

## Key Interfaces
- The enum is unnamed and populated from `cmds.h`.
- `cmd_enum.h` is included by `toolcontext.h`, where `cmd_context.command_enum` stores the selected command identifier.

## Cross-File Interactions
Depends on build-generated `cmds.h`, itself derived from command definitions. Command parsing and library code use these enum values to branch on specific command behavior without string comparisons.

## Risks
The file is small but build-order sensitive: `cmds.h` must exist and must use the expected `cmd(a, b)` form. Any macro name change in the generated command table breaks enum generation.
