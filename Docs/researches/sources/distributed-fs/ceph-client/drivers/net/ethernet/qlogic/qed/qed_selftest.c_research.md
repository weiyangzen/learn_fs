# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_selftest.c

Purpose: Implements QED diagnostic selftests for memory, interrupts, register BIST, clock BIST, and NVRAM image CRC validation.

Important APIs/types/functions: `qed_selftest_memory()` and `qed_selftest_interrupt()` both issue `qed_sp_heartbeat_ramrod()` on every hwfn. `qed_selftest_register()` and `qed_selftest_clock()` acquire a PTT per hwfn and call MCP BIST commands. `qed_selftest_nvram()` gets image count and attributes from MCP, reads each NVM image except MDUMP, endian-normalizes the image payload, computes CRC32, and compares with the stored trailer CRC.

Control flow: Per-engine tests iterate `for_each_hwfn()` and fail fast on the first error. Register/clock tests acquire/release PTT around each MCP call. NVRAM test uses the leading hwfn, acquires one PTT, queries image metadata, allocates a buffer per image, reads NVM contents, converts all dwords except the final CRC to big-endian form, computes inverted big-endian CRC32, frees each buffer before the next image, and releases PTT on all exits.

State and persistence: No persistent driver state is modified. Tests temporarily allocate image buffers, use PTT resources, and invoke firmware diagnostics. NVRAM reads are non-mutating.

Dependencies/integration: Depends on SP heartbeat ramrod, MCP BIST/NVM APIs, PTT management, Linux CRC32, QED logging, and NVM image type definitions.

Risks: Memory and interrupt tests are currently identical heartbeat checks, so they may not distinguish failure classes. NVRAM test assumes image length is at least four bytes and dword-aligned for conversion. MDUMP images are skipped because crash dumps invalidate CRC. Large NVM images can cause large `kzalloc()` allocations.

Test signals: Heartbeat success/failure on each hwfn, PTT acquisition failure, MCP register/clock BIST failures, NVRAM no-image path, image attribute/read errors, MDUMP skip, CRC mismatch, endian conversion correctness, and allocation failure for large images.
