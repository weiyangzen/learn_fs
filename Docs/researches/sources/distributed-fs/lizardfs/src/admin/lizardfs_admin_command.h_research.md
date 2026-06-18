<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.h -->
# sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.h

## Purpose
Defines the abstract base interface for all `lizardfs-admin` subcommands and the `WrongUsageException` used for CLI errors.

## Important APIs, Types, and Functions
Declares `LIZARDFS_CREATE_EXCEPTION_CLASS(WrongUsageException, Exception)`, `LizardFsProbeCommand::SupportedOptions`, static option constants, virtual destructor, pure virtual `name`, `usage`, and `run`, plus default empty `supportedOptions`.

## Control Flow, State, and Persistence
The base class has no instance state. `main.cc` allocates derived commands and dispatches through this interface.

## Dependencies and Integration Points
Depends on `common/exception.h` and `admin/options.h`. Every admin command includes this as its CLI contract.

## Risks and Test Signals
Risks include raw pointer ownership in `main.cc` despite the virtual destructor, command implementations throwing `WrongUsageException` for help, and no standardized command metadata beyond printed usage. Build coverage of all derived classes and help output are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.h -->
