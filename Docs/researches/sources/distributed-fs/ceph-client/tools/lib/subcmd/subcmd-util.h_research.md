# sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-util.h

Purpose: Provides small allocation, reporting, fatal-error, and string-append helpers for libsubcmd.

Important APIs/types/functions: `report()` formats prefixed messages. `die()` prints fatal errors and exits 128. `zfree(ptr)` frees a pointer and sets it to NULL. `alloc_nr()` and `ALLOC_GROW()` implement dynamic array growth. `xrealloc()` wraps `realloc()` with fatal OOM. `astrcatf()` and `astrcat()` append formatted/plain text to heap strings.

Control flow: Allocation helpers grow buffers as needed and terminate on unrecoverable allocation/formatting failures. String append helpers allocate a new combined string with `asprintf()`, free the old string, and store the new pointer.

State and persistence: Mutates caller pointers and exits the process on fatal paths. No persistent files.

Dependencies/integration: Includes stdarg/stdlib/stdio and Linux compiler attributes. Used across libsubcmd.

Risks: `zfree(ptr)` evaluates `ptr` as pointer-to-pointer and is macro-based; misuse can double-free or assign through invalid pointers. `ALLOC_GROW()` warns not to pass side-effect expressions. Helpers rely on GNU `asprintf()`. Fatal exit behavior may not suit embedded library consumers.

Test signals: Exercise growth boundaries, append from NULL/non-NULL, OOM/failure injection where practical, and macro misuse coverage via compile tests.
