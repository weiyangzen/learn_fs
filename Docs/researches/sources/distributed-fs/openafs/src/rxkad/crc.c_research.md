## sources/distributed-fs/openafs/src/rxkad/crc.c

### Purpose
`crc.c` implements table initialization and incremental CRC32 update helpers used by rxkad ticket/lifetime code.

### Important APIs, Types, And Functions
`_rxkad_crc_init_table()` lazily fills a 256-entry table using polynomial `0xEDB88320`. `_rxkad_crc_update()` updates a caller-supplied CRC accumulator over a byte buffer.

### Control Flow
Initialization returns immediately after the static flag is set. Otherwise it computes each table entry by eight shift/xor iterations. Update walks each byte, indexes the table with `(res ^ byte) & 0xff`, shifts the accumulator, and returns the masked 32-bit result.

### State, Persistence, And Dependencies
The static table and initialization flag persist process-wide. Dependencies include Rx/XDR and rxkad headers, though the implementation itself is standalone CRC logic.

### Integration Points
Used by rxkad code that needs the Heimdal-derived CRC primitive, especially Kerberos-related checksum handling.

### Risks
The lazy initialization flag is not synchronized, so concurrent first use could race while computing identical values. Callers must ensure initialization before update or receive zero-table results.

### Test Signals
Known CRC32 vectors, update-in-chunks equivalence, update-before-init behavior, and thread sanitizer first-use tests are useful.
