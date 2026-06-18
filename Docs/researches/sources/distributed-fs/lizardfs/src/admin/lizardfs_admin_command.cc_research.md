<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.cc

## Purpose
Defines shared option-name constants for the `lizardfs-admin` command hierarchy.

## Important APIs, Types, and Functions
Initializes `LizardFsProbeCommand::kPorcelainMode`, `kPorcelainModeDescription`, and `kVerboseMode`.

## Control Flow, State, and Persistence
There is no control flow beyond static initialization of strings. The constants are read by command implementations and `main.cc` help output.

## Dependencies and Integration Points
Includes the base command header and `common/platform.h`. It centralizes the spellings `--porcelain` and `--verbose`.

## Risks and Test Signals
Risks are static initialization order only in theory and option spelling changes affecting all commands. Build/link success and CLI option parsing are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.cc -->
