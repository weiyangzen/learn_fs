<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.h

Purpose: Declares `S2A` and `A2S`, small conversion helper classes that make TCHAR/ANSI bridging concise.

Important APIs/types: `S2A` stores a converted `char *` and exposes casts to mutable/const ANSI pointers. `A2S` stores a converted `LPTSTR` and exposes TCHAR pointer casts.

Control flow: No active logic beyond constructors/destructors implemented in `char_conv.cpp`; callers instantiate objects at the point of API calls.

State and persistence: Object-local converted pointer only, no persistence.

Dependencies and integration points: Requires Win32/TCHAR types and app-library allocation semantics. Used by code that talks to OpenAFS admin APIs and Win32 UI helpers.

Risks: Mutable pointer casts allow callees to write into conversion buffers of unclear size. Temporary lifetime hazards are hidden by implicit operators.

Test signals: Static review for stored `S2A`/`A2S` pointers, build both character modes, and test conversions of non-ASCII cell/admin names if Unicode builds are supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.h -->
