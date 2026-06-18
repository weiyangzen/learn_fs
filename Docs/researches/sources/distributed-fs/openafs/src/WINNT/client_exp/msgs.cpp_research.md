## sources/distributed-fs/openafs/src/WINNT/client_exp/msgs.cpp

Purpose: Provides localized string loading plus custom varargs formatting for message boxes and formatted strings.

Important APIs/functions: `ShowMessageBox` loads a string resource, substitutes `%` format tokens, and calls `AfxMessageBox`. `GetMessageString` performs the same formatting but returns a `CString`. `LoadString` wraps `GetString` into a `CString`.

Control flow/state: The formatter scans the loaded template for `%` tokens and consumes varargs by token type. It allocates temporary buffers for the paste/cut/converted fragments on each substitution.

Dependencies/integration: Uses MFC `CString`, `AfxMessageBox`, `<tchar.h>`, `TaLocale` string resources, and `resource.h`. Most GUI operation files use it for user-facing messages.

Risks/tests: No `va_end`, manual fixed-size buffers, unsupported width/precision, and `CString` passed through varargs are all fragile. `%l` parsing references `pszdone[x+2]`, which is suspicious during initial formatting. Test every resource string containing substitutions, long inserted strings, Unicode strings, invalid format tokens, and both message-box and string-return paths.
