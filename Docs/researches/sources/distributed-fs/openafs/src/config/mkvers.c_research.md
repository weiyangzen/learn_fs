# sources/distributed-fs/openafs/src/config/mkvers.c

Purpose: C version-file generator for CML-based builds, kept in C so NT platforms do not need Perl.

Important APIs/types/functions: parses `-d`, `-o`, `-c`, `-v`, `-t`, and `-x`; reads `state` and `stamps` files under a CML directory; stores deltas in `stateDeltas`; and `PrintStamps` emits C source, NT version-info header, text, or XML revision output.

Control flow: `main` finds the CML directory by walking up to six `../` levels unless `-d` is given, chooses the default output file by format, rebuilds only when output is missing or older than `state`/`stamps`, reads state lines whose type is `I`, `N`, `C`, or `O`, and writes formatted version data. If CML data is unavailable, it writes a fallback message when possible and exits nonzero.

State and persistence: writes generated version files such as `AFS_component_version_number.c/.h`, `.txt`, or `.xml`. Runtime state is process-local arrays of up to 128 deltas.

Dependencies and integration: invoked by `Makefile.version-CML.in`; generated C is included/compiled into OpenAFS components for embedded build identification.

Risks and test signals: risks include fixed-size arrays and strings, truncation at output maxima, modifying the selected base-configuration string in place, incomplete XML escaping, and timestamp-only rebuild decisions. Signals include all output formats, prefixed component variable names, missing CML fallback, too-long delta lists, and up-to-date no-op behavior.
