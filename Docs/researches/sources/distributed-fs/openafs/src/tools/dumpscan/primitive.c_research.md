# sources/distributed-fs/openafs/src/tools/dumpscan/primitive.c

Purpose: low-level big-endian primitive readers/writers for the `XFILE` abstraction.

Important APIs/functions: `ReadByte`, `ReadInt16`, `ReadInt32`, and `ReadString` read raw dump values and convert network order to host order. `ReadString` reads byte-by-byte in 256-byte chunks, growing a NUL-terminated buffer. `WriteByte`, `WriteInt16`, `WriteInt32`, `WriteString`, `WriteTagByte`, `WriteTagInt16`, `WriteTagInt32`, and `WriteTagInt32Pair` serialize values and tag-value combinations.

State/dependencies: no persistent state. It depends on `xfread`/`xfwrite`, libc allocation, string functions, and network byte-order conversion.

Risks/test signals: `ReadString` allocation and `realloc` handling is careful, but very long unterminated strings can allocate until EOF/error. WriteTag helpers manually construct network byte order instead of using `hton*`, so tests should round-trip tags and integer values. These functions are foundational; failures surface throughout all dump parsing/writing tools.
