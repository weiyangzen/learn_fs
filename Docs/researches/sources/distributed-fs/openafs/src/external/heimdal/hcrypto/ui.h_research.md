# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/ui.h

Purpose: declares the password prompt utility compatibility API.

Important APIs/types/functions: renames `UI_UTIL_read_pw_string` to `hc_UI_UTIL_read_pw_string` and declares `int UI_UTIL_read_pw_string(char *, int, const char *, int)`.

Control flow: callers pass a destination buffer, maximum length, prompt, and verify flag; behavior lives in `ui.c`.

State and persistence: no state is defined in the header.

Dependencies and integration points: included by `ui.c` and any OpenSSL-compatible password prompt callers in Heimdal/OpenAFS.

Risks and test signals: signature compatibility is the main concern. Compile coverage and prompt behavior tests validate integration.
