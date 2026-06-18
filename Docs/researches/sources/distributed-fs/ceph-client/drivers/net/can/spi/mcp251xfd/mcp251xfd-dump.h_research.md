# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-dump.h

Purpose: Defines the private binary object format used by MCP251xFD devcoredumps.

Important APIs, types, and functions: Provides `MCP251XFD_DUMP_MAGIC`, dump object type enum, ring key enum, `struct mcp251xfd_dump_object_header`, and `struct mcp251xfd_dump_object_reg`.

Control flow: No executable flow. `mcp251xfd-dump.c` uses the definitions to create a header table followed by payloads. Each object header points to payload offset and length; END terminates parsing.

State and persistence behavior: Encodes transient state into little-endian fields and effectively acts as an ABI for devcoredump parsers.

Dependencies and integration points: Private to MCP251xFD dump code but visible to userspace tools that parse devcoredumps.

Risks: Reordering enum values or changing struct layout breaks parsers. The END value is `-1` stored as u32 and must be parsed as a sentinel type.

Test signals: Build with `CONFIG_DEV_COREDUMP=y`, generate a dump, and validate magic, offsets, lengths, object order, and ring key count.
