# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-dump.c

Purpose: Builds a binary devcoredump snapshot for MCP251xFD failure diagnosis, recording selected register ranges, controller RAM, and software TEF/RX/TX ring metadata.

Important APIs, types, and functions: `mcp251xfd_dump()` is the exported entry. Internal helpers write object headers, read register spaces, serialize ring metadata for TEF/RX/TX, and append an END marker. Local iterator and descriptor structs track header and payload placement.

Control flow: The function computes dump size from register spaces, ring count, and headers, allocates a vmalloc buffer, places headers before payloads, appends register and ring objects, then publishes the buffer through `dev_coredumpv()`. Register read failures skip that range rather than aborting the whole dump.

State and persistence behavior: Captures transient hardware and in-memory driver state; persistence is delegated to the kernel devcoredump facility.

Dependencies and integration points: Depends on regmap, ring structures, dump object definitions from `mcp251xfd-dump.h`, and core startup/IRQ failure paths. Compiled through the `CONFIG_DEV_COREDUMP` guard.

Risks: Allocation may fail under memory pressure. Consumers must parse the little-endian object format correctly. Regmap assumptions between register and RAM ranges must remain consistent.

Test signals: Force controlled IRQ/start failure, verify devcoredump object sequence and END marker, decode ring keys, and test allocation failure behavior with fault injection.
