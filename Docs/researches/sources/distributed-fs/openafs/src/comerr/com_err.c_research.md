# sources/distributed-fs/openafs/src/comerr/com_err.c

Purpose: implements the formatted error reporting front end for OpenAFS com_err.

Important APIs: `afs_com_err` formats variadic messages, `afs_com_err_va` calls the current hook, `afs_set_com_err_hook` replaces the hook and returns the old hook, and `afs_reset_com_err_hook` restores the default. The default hook prints optional subsystem name, decoded error message from `afs_error_message`, optional formatted text, newline, carriage return, and flushes stderr.

Control flow and state: a static function pointer `com_err_hook` holds reporting behavior. No persistent external storage is touched.

Dependencies and integration: depends on `error_msg.c` for code-to-message lookup and `com_err.h` for API. Used broadly by command-line tools and tests.

Risks and tests: the hook pointer is global and not protected by a mutex, so concurrent hook changes are racy. The default writes an extra carriage return for historical terminal behavior. Coverage is broad through users such as butm tests and command tests.
