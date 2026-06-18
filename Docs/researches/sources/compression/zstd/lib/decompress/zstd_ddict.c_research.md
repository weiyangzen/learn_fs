# sources/compression/zstd/lib/decompress/zstd_ddict.c

## Purpose
Implements the internals of `ZSTD_DDict`, the pre-digested decompression dictionary object. It owns dictionary content copying or referencing, parses zstd dictionary headers and entropy tables, exposes dictionary metadata to decompression contexts, and implements allocation, static initialization, sizing, and ID lookup for decompression dictionaries.

## Important APIs, Types, And Functions
`struct ZSTD_DDict_s` contains `dictBuffer`, `dictContent`, `dictSize`, preloaded `ZSTD_entropyDTables_t entropy`, `dictID`, `entropyPresent`, and allocator `cMem`. Accessors `ZSTD_DDict_dictContent()` and `ZSTD_DDict_dictSize()` expose internal dictionary bytes to other decompression code.

`ZSTD_copyDDictParameters()` copies dictionary identity, prefix/window pointers, previous-destination pointer, and optional entropy table pointers from a DDict into a `ZSTD_DCtx`. `ZSTD_loadEntropy_intoDDict()` parses dictionary magic, dict ID, and decompression entropy tables. `ZSTD_initDDict_internal()` handles by-copy versus by-reference setup and initializes the HUF table sentinel before entropy loading.

Public constructors and lifetime functions include `ZSTD_createDDict_advanced()`, `ZSTD_createDDict()`, `ZSTD_createDDict_byReference()`, `ZSTD_initStaticDDict()`, `ZSTD_freeDDict()`, `ZSTD_estimateDDictSize()`, `ZSTD_sizeof_DDict()`, and `ZSTD_getDictID_fromDDict()`.

## Control Flow
Dynamic construction validates that custom alloc/free are either both present or both absent, allocates the DDict object, stores allocator state, then calls the internal initializer. The initializer either references the caller dictionary directly or allocates/copies it into `dictBuffer`, records size/content pointers, initializes the HUF table first entry, and parses entropy unless the caller explicitly requested raw content.

Entropy loading treats empty/small dictionaries and non-magic dictionaries as content-only when `ZSTD_dct_auto` allows it. If `ZSTD_dct_fullDict` is requested, those same cases are dictionary corruption. For valid zstd dictionary magic, it reads the 32-bit dict ID after the frame ID field and calls `ZSTD_loadDEntropy()` to populate LL/ML/OF/HUF tables and repeat offsets, then marks `entropyPresent`.

Static initialization validates 8-byte alignment, checks that the supplied buffer can hold the DDict and optional dictionary copy, places copied bytes immediately after the object when requested, then delegates to the same internal initializer by reference. Freeing releases the owned dictionary buffer if any and then the object itself; static DDicts must not be passed to the dynamic free path unless they were dynamically allocated.

## State And Persistence
DDict state is immutable after initialization except for object destruction. `dictBuffer` is non-null only for owned by-copy dictionaries; `dictContent` may point into owned memory, caller memory, or static-buffer trailing memory. Entropy tables live inside the DDict and are shared by pointer into a `ZSTD_DCtx` during decompression. There is no persistence outside process memory.

`ZSTD_copyDDictParameters()` mutates a decompression context by installing dictionary range pointers and entropy table pointers. If entropy is absent, it clears `litEntropy` and `fseEntropy`, telling the decompressor to use frame-provided or default entropy instead.

## Dependencies And Integration Points
The file depends on custom allocation helpers, zstd memory wrappers, CPU feature declarations, low-level endian helpers, FSE/HUF static interfaces, decompression internals, `zstd_ddict.h`, and optional legacy support headers. It integrates with `ZSTD_DCtx` internals through `zstd_decompress_internal.h`, especially prefix/window fields and entropy table pointer fields.

DDict creation APIs are declared publicly in `zstd.h`, while the internal content/size/copy helpers are declared in `zstd_ddict.h`. Dictionary parsing depends on common constants such as `ZSTD_MAGIC_DICTIONARY`, `ZSTD_FRAMEIDSIZE`, and `ZSTD_loadDEntropy()`.

## Risks And Edge Cases
By-reference DDicts rely on caller-owned dictionary memory outliving the DDict and any decompression using it. Static DDict initialization requires 8-byte-aligned storage and exact sizing; misuse can return `NULL` or create lifetime hazards if later freed incorrectly. The distinction between `ZSTD_dct_auto`, `ZSTD_dct_fullDict`, and `ZSTD_dct_rawContent` is security-relevant because malformed dictionaries are either accepted as raw content or rejected as corruption depending on caller intent.

Entropy table pointers copied into `ZSTD_DCtx` point back into the DDict. A DCtx must not keep using those pointers after the DDict is freed. Fuzzing-only dictionary range fields are updated under `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`; tests that inspect those fields depend on compile mode.

## Test Signals
Tests should create DDicts by copy, by reference, with custom allocators, with static buffers, with empty dictionaries, raw-content dictionaries, malformed full dictionaries, and valid full dictionaries with entropy tables. They should verify dictionary ID extraction, memory-size estimates, `ZSTD_sizeof_DDict()`, null-free/null-size behavior, DCtx parameter copying with and without entropy, allocator failure cleanup, and lifetime behavior for by-reference dictionaries.
