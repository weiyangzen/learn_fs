# sources/distributed-fs/openafs/src/comerr/et_name.c

Purpose: converts an encoded comerr error number back into its short error-table name.

Important APIs/types/functions: exports `afs_error_table_name(int num)`. It uses `ERRCODE_RANGE` and `BITS_PER_CHAR` from the comerr headers, a 64-character table of uppercase, lowercase, digit, and underscore symbols, a static six-byte output buffer, and `lcstring` to lower-case the generated name.

Control flow: the function discards the low error-code bits, masks the remaining table-number field to 25 bits, decodes five six-bit character slots from high to low, skips zero slots, stores nonzero characters indexed as `ch - 1`, NUL-terminates the static buffer, lowercases it in place, and returns the buffer pointer.

State and persistence: state is limited to the file-static `buf`, so the returned pointer is overwritten by the next call and is not thread-safe. No external state is persisted.

Dependencies and integration: used by `afs_error_message` and diagnostics to report the table name for generated comerr bases. It depends on `error_table.h`, `mit-sipb-cr.h`, `internal.h`, roken, and OpenAFS parameter/config headers.

Risks and test signals: risks include static-buffer reuse in concurrent callers and incorrect names if the error-number encoding constants change. Test signals include known Kerberos/comerr table bases, ordinary UNIX errno values, zero/unknown table numbers, and repeated calls that verify expected overwrite semantics.
