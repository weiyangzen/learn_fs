# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/ui.c

Purpose: implements a small OpenSSL-compatible password prompt helper.

Important APIs/types/functions: private `intr` signal handler, platform-specific `read_string`, and exported `UI_UTIL_read_pw_string(buf, length, prompt, verify)`.

Control flow: Unix `read_string` installs interrupt handlers for most signals, opens `/dev/tty` or falls back to stdin, prints prompt to stderr, disables terminal echo when requested, reads until newline/EOF/interrupt/overflow, restores echo and signal handlers, and returns `0`, `-1` overflow, `-2` interrupt, or `-3` input error. Windows `_getch/_getche` path uses console I/O and SIGINT handling. `UI_UTIL_read_pw_string` reads the password without echo and optionally reads a verification prompt and compares strings.

State and persistence: file-static `intr_flag` tracks signal interruption. Password buffers are caller-owned; verify buffer is heap allocated and freed but not scrubbed.

Dependencies and integration points: depends on `ui.h`, `roken`, terminal APIs, signals, and optional `conio.h`. Used by code expecting OpenSSL `UI_UTIL_read_pw_string` behavior.

Risks and test signals: signal handling across `NSIG` can be invasive, terminal state restoration on unusual errors is critical, overflow handling leaves truncated data, and verification buffer is not zeroed before free. Tests should cover echo restoration, `/dev/tty` fallback, overflow, interrupt, verify mismatch, EOF, and Windows console behavior.
