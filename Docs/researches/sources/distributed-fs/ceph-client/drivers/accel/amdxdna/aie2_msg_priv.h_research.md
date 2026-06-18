# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_msg_priv.h

## Purpose
This private header defines the AIE2 firmware mailbox protocol used by the AMD XDNA driver. It centralizes opcodes, status values, packed request/response layouts, command-list slot formats, telemetry/error structures, and app-health reports.

## Important APIs, Types, And Functions
`enum aie2_msg_opcode` covers XRT-style execution commands, driver management commands, async event registration, app health, and protocol versioning. `enum aie2_msg_status` partitions AIE, management ERT, app ERT, and NPU RTOS status codes. Important structs include context create/destroy, queue pair descriptions, telemetry/status queries, execute-buffer and DPU requests, CU config, sync BO, debug BO config, async event messages, command-chain slots, and `struct app_health_report`.

## Control Flow
The header has no executable flow, but its packed layouts determine how `aie2_message.c`, `aie2_ctx.c`, and `aie2_error.c` communicate with firmware. Flexible-array command slots carry variable argument counts, while wrapper requests pass device addresses and sizes for firmware-readable buffers.

## State, Dependencies, Integration, Risks, And Tests
The protocol describes persistent firmware-side state such as context IDs, queue pairs, CUs, debug BO registrations, async event buffers, and app health. It depends on fixed-width UAPI-style integer sizes, `__packed`, `GENMASK`, and size constants such as `SZ_4K` and `SZ_8K`. Risks include ABI drift with firmware, alignment/packing mismatches, endianness assumptions, flexible-array size miscalculation, and insufficient reserved-field validation. Test signals include compile-time struct-size checks against firmware specs, mailbox round-trip tests for every opcode, command slot boundary tests, and compatibility tests across firmware versions.
