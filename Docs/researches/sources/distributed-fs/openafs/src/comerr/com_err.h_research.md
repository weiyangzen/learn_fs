# sources/distributed-fs/openafs/src/comerr/com_err.h

Purpose: public header for the OpenAFS common error reporting and lookup library.

Important APIs: declares `afs_com_err`, `afs_com_err_va`, `afs_error_table_name`, `afs_error_message`, `afs_error_message_localize`, and hook setters/resetters with printf-format attributes. Under `AFS_OLD_COM_ERR`, maps legacy names such as `com_err` and `error_message` to the AFS-prefixed APIs.

Control flow and state: no executable logic. It defines the public ABI contract consumed by OpenAFS tools and libraries.

Dependencies and integration: requires `afs_int32`, `size_t`, and OpenAFS attributes from included upstream headers. Installed by the comerr Makefile.

Risks and tests: function pointer declaration syntax is hard to read and easy to break. Compatibility macros may shadow non-AFS com_err symbols when `AFS_OLD_COM_ERR` is defined.
