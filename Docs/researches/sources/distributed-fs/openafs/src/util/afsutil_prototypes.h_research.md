
# sources/distributed-fs/openafs/src/util/afsutil_prototypes.h

Purpose: `afsutil_prototypes.h` centralizes prototypes for OpenAFS utility-library functions so `afsutil.h` consumers can share a consistent declaration set.

Important APIs: declarations cover base32/base64/flipbase64 conversion, directory path construction, NT error mapping, alternate exec lookup, filepath normalization, host parsing and address formatting, HP-UX portability functions, relative and periodic time parsing, logging, tabular output, UUID handling, partition parsing, and numeric parsing helpers.

Control flow and integration: the file is organized by implementation module comments. Conditional blocks expose pthread, Windows, HP-UX, non-kernel, and non-NT functions according to build configuration.

State and persistence: this header defines no storage. Declared functions can affect logs, paths, UUIDs, and parsing outputs depending on their implementation.

Risks and test signals: duplicate base32 declarations appear under both `base32.c` and `flipbase64.c` comments. Prototype drift is a maintenance risk because many modules are listed manually. Test signals include full util-library compilation with strict prototypes across platform macros and consumers that include both specific headers and `afsutil.h`.
