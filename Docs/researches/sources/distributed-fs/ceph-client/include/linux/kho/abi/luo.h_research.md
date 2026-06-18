# sources/distributed-fs/ceph-client/include/linux/kho/abi/luo.h

## Purpose

`luo.h` defines the Live Update Orchestrator ABI built on Kexec Handover. It specifies FDT node names and compatible strings plus packed serialization structures for live-update sessions, preserved files, and file-lifecycle-bound global objects. The source was read as a complete 247-line file.

## Important APIs, Types, and Functions

Key constants include `LUO_FDT_KHO_ENTRY_NAME`, `LUO_FDT_COMPATIBLE`, `LUO_FDT_LIVEUPDATE_NUM`, `LUO_FDT_SESSION_NODE_NAME`, `LUO_FDT_SESSION_COMPATIBLE`, `LUO_FDT_SESSION_HEADER`, `LUO_FDT_FLB_NODE_NAME`, `LUO_FDT_FLB_COMPATIBLE`, and `LUO_FDT_FLB_HEADER`. Types include packed `struct luo_file_ser`, `struct luo_file_set_ser`, `struct luo_session_header_ser`, `struct luo_session_ser`, `struct luo_flb_header_ser`, and `struct luo_flb_ser`.

## Control Flow

The old kernel serializes sessions and global file-bound objects into preserved memory, publishes physical addresses through an FDT subtree named `LUO`, and increments `liveupdate-number`. The new kernel parses compatible nodes, walks session/file arrays and FLB arrays, then invokes matching liveupdate handlers by compatible string.

## State and Persistence Behavior

All structs are packed ABI payloads. They persist across kexec and carry names, handler compatibility strings, opaque handler data, tokens, counts, file-set pointers, and page counts.

## Dependencies and Integration Points

It depends on `uapi/linux/liveupdate.h` for session name sizing and integrates with LUO core, KHO subtree handover, memfd preservation, and handler registration by compatible strings.

## Risks and Edge Cases

The documentation says session examples use v1, while the constant is `luo-session-v2`; consumers must follow constants. Layout changes require compatible-string bumps. Count fields must be validated before array walking to avoid interpreting corrupted preserved memory.

## Test Signals

Live update serialization/restore tests, FDT compatible/version validation, session and FLB count bounds tests, handler lookup tests, and cross-kernel compatibility tests are important.
