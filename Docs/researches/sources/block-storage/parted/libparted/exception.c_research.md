# File Research: sources/block-storage/parted/libparted/exception.c

Implements libparted’s process-global exception mechanism. It maintains a current exception object, a global pending flag `ped_exception`, a handler pointer, and a fetch-depth counter used by callers that want exceptions returned instead of immediately handled.

`ped_exception_throw()` formats a printf-style message into a dynamically grown buffer, stores type/options, and calls `do_throw()`. If `ped_exception_fetch_all()` is active, throws return `PED_EXCEPTION_UNHANDLED`; otherwise the configured handler is invoked and the exception is caught/freed afterward. `ped_exception_rethrow()` repeats handling of the current exception. `ped_exception_catch()` clears the pending flag and frees the current exception.

The default handler prints bug-specific guidance for `PED_EXCEPTION_BUG`, otherwise prints the type and message. It auto-returns only simple single-option cases (`OK`, `CANCEL`, `IGNORE`); other option sets are left unhandled so callers can choose safe defaults. Option-to-string lookup assumes option values are powers of two and uses a local `ped_log2()` helper.

The mechanism is simple and not thread-local. Concurrent use would race on global state; nested throws replace any existing exception by catching it first.
