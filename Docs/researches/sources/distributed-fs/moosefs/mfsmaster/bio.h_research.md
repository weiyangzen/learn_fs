# sources/distributed-fs/moosefs/mfsmaster/bio.h

This header defines the opaque `bio` interface used by MooseFS master metadata modules for buffered file, socket, and null I/O.

It forward-declares `bio`, defines `BIO_READ` and `BIO_WRITE`, and declares openers, read/write operations, seek/skip, file-position and size accessors, CRC access, EOF/error/errno/descriptor access, sync, shutdown, wait, and close.

The normal flow is open a backend-specific handle, transfer data, inspect status as needed, optionally query/reset write CRC, and close the handle. All buffer, descriptor, CRC, EOF, and error state is hidden in the implementation.

The header depends on `<inttypes.h>` and is consumed by many metadata persistence modules. Risks are implicit ownership, no documented buffer-size preconditions, and return values that require careful signed comparison. Test signals are broad consumer compilation and implementation-level lifecycle tests.
