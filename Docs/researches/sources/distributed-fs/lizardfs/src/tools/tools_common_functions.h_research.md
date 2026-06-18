# sources/distributed-fs/lizardfs/src/tools/tools_common_functions.h

Purpose: Shared declarations and small inline usage printers for LizardFS tools.

Important APIs/types/functions: Macros `tcpread`/`tcpwrite`; extern `humode`, `eattrtab`, `eattrdesc`; `check_usage`; `set_humode`; `print_number`; `my_get_number`; path helpers; `open_master_conn`; close helpers; `signalHandler`; inline printers for number format, recursive option, and extra attributes.

Control flow: Header provides declarations and inline functions that print common help text. Implementations live in `tools_common_functions.cc` and `master_functions.cc`.

State and persistence: Declares process-global formatting state and master connection functions. No direct persistence.

Dependencies and integration: Included by most tool commands. Depends on sockets and `MFSCommunication.h` constants for eattr metadata.

Risks and test signals: The `tcpread`/`tcpwrite` macros bake in 10-second timeouts for legacy tools. Shared globals can make command behavior order-dependent in interactive mode if not reset. No direct tests in this subset.
