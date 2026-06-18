# sources/distributed-fs/ceph-client/drivers/misc/mei/mkhi.h

## Purpose
This header defines small Management Engine Kernel Host Interface message constants and packed wire structures used by MEI code that talks to MKHI firmware groups, especially firmware capability, firmware version, and graphics/PXP setup messages.

## Important APIs, types, and functions
Constants include `MKHI_FEATURE_PTT`, firmware capability group and command IDs, generic firmware-version command IDs, graphics group `MKHI_GROUP_ID_GFX`, graphics reset/memory-ready commands, and `MKHI_GFX_MEM_READY_PXP_ALLOWED`. Wire structures are `mkhi_rule_id`, `mkhi_fwcaps`, `mkhi_msg_hdr`, `mkhi_msg`, and `mkhi_gfx_mem_ready`.

## Control flow and state
There is no executable flow. Consumers embed `mkhi_msg_hdr` at the start of firmware command packets, fill group/command/result fields, and parse flexible payloads such as `mkhi_fwcaps.data[]` or `mkhi_msg.data[]`.

## State and persistence behavior
The file defines transient packed protocol state only. Data lives in MEI request/response buffers and is not persisted by the header.

## Dependencies and integration points
It depends on `linux/types.h` and is included by MEI code that constructs MKHI messages. In this subset, `mei_lb.c` uses `mkhi_msg_hdr` and `MKHI_GROUP_ID_GFX` for Late Binding v1.

## Risks and test signals
Risk centers on ABI layout: structures are packed and endian-specific fields must match firmware expectations. Tests should validate exact packet sizes, graphics-group command IDs, result-code parsing, and interoperability with firmware responses that contain only a header on error.
