<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/main.cc -->
# sources/distributed-fs/lizardfs/src/admin/main.cc

## Purpose
Entry point and dispatcher for the `lizardfs-admin`/`lizardfs-probe` CLI.

## Important APIs, Types, and Functions
Defines `int main(int argc, const char **argv)`. It constructs a vector of `const LizardFsProbeCommand*` containing all command objects, builds `Options` from each command's supported options, dispatches `run`, and prints usage/help on `WrongUsageException`.

## Control Flow, State, and Persistence
Main requires a command name, shifts remaining arguments into strings, finds a matching command, and returns after successful `run`. `help` and `-h` trigger the aggregate help path. Wrong usage prints global usage plus either all non-`magic-*` commands or the specific command usage/options. Generic `Exception` prints `Error:` and returns 1. State is only process heap allocations for command objects; they are not deleted before exit.

## Dependencies and Integration Points
Includes every command header, `Options`, exception/error utilities, version/formatting includes, and protocol constants. It is the single registry where adding a new command becomes user-visible.

## Risks and Test Signals
Risks include raw `new` leaks until process exit, hidden magic command help, commands calling `exit(1)` and bypassing main's exception handling, and unsupported short options except command `-h`. Test signals are no-arg, unknown command, aggregate help, specific wrong-usage help, option parse errors, every command dispatch, and non-`Exception` failures such as `std::out_of_range` from bad command code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/main.cc -->
