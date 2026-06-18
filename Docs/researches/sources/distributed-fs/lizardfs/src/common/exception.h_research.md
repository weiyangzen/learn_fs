# sources/distributed-fs/lizardfs/src/common/exception.h

Purpose: defines the base LizardFS exception class and macros for derived exception classes.

Important APIs/types/functions: `Exception` derives from `std::exception`, stores `message_` and `status_`, appends `lizardfs_error_string(status)` for known non-OK statuses, and exposes `what()`, `message()`, and `status()`. Macros create named exception classes with standard constructors.

Control flow: constructors set the message/status and assert that status is not `LIZARDFS_STATUS_OK`. Macro-generated derived classes forward to base constructors.

State and persistence: exception objects carry message/status only; no persistence.

Dependencies and integration: depends on `MFSCommunication.h` for status constants and `mfserr.h` for status strings. Used broadly by common wrappers and higher-level code.

Risks: macros generate many small classes but hide declarations from tools. `what()` returns a pointer into `std::string`, valid only while the exception object lives.

Test signals: no direct tests here; usage is exercised by exception-throwing modules.
