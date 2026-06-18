# sources/distributed-fs/moosefs/mfsmaster/bio.c

`bio.c` provides a buffered I/O abstraction for metadata save/load paths and socket transfers. It supports file, socket, and null backends with read/write direction, buffering, file-position accounting, EOF/error tracking, and write-side CRC accumulation.

`struct _bio` stores buffer memory, buffer size and positions, socket timeout, file position, CRC, direction, backend type, error/EOF state, last errno, and descriptor. Openers are `bio_null_open`, `bio_file_open`, and `bio_socket_open`. Core operations are `bio_read`, `bio_write`, `bio_seek`, `bio_skip`, `bio_sync`, `bio_shutdown`, `bio_wait`, and `bio_close`; accessors expose position, size, CRC, EOF, error, errno, and descriptor.

Writes buffer small data and flush or bypass the buffer for large writes. Reads fill a buffer for small reads and use direct reads for large requests after copying leftovers. Large direct operations are split at `0x40000000` bytes. File seeks flush writes or discard read buffers before `lseek`. Socket reads/writes delegate to MooseFS TCP helpers with configured timeouts.

File backends use `O_RDONLY` or `O_WRONLY|O_CREAT|O_TRUNC`; socket backends close through `tcpclose`; null writes only compute CRC. `bio_crc` returns and resets accumulated write CRC. This module is used by metadata and metadata-section modules including `metadata.c`, `csdb.c`, `patterns.c`, `openfiles.c`, `xattr.c`, `posixacl.c`, and `posixlocks.c`.

Risks include clearing buffered write length even after an internal partial write sets error, CRC accounting before write success is known, zero-buffer-size assumptions, and mixed signed byte-count/status semantics. Test signals are file round trips, socket failure handling, CRC reset behavior, seek/skip correctness, large I/O splits, and forced short-write propagation.
