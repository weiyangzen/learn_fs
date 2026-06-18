# File Research: sources/block-storage/lvm2/tools/lvm2cmdline.h

## Purpose
Internal command-line subsystem header shared by the executable and command-library wrapper.

## Key Types
- `struct cmdline_context` stores:
  - option-name table
  - command definition table
  - command-name table
  - valid argument metadata per command name

## Declared Functions
- Top-level execution:
  - `lvm2_main()`
  - `lvm_run_command()`
  - `lvm_return_code()`
- Library lifecycle:
  - `cmdlib_lvm2_init()`
  - `lvm_fin()`
  - `init_lvm()`
- Command registration/parsing:
  - `lvm_register_commands()`
  - `lvm_split()`
- Interactive shell:
  - `lvm_shell()`

## Important Details
- This header bridges the public command library, standalone CLI, and generated command definitions.
- `init_lvm()` accepts flags for connection setup, filter setup, and threaded mode.
