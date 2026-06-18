# sources/distributed-fs/ceph-client/drivers/pnp/support.c

## Purpose
`support.c` contains small shared PnP support and debug-formatting utilities. It detects whether a PnP device appears active, converts packed EISA IDs into strings, maps resource/option types to readable names, and formats current resources and possible options for PnP debug output.

## Important APIs, Types, and Functions
The exported or shared helpers are `pnp_is_active()`, `pnp_eisa_id_to_string()`, `pnp_resource_type_name()`, `dbg_pnp_show_resources()`, `pnp_option_priority_name()`, and `dbg_pnp_show_option()`. It uses `pnp_port_start()`, `pnp_port_len()`, `pnp_mem_start()`, `pnp_mem_len()`, `pnp_irq()`, `pnp_dma()`, `pnp_resource_type()`, `pnp_option_is_dependent()`, `pnp_option_set()`, and `pnp_option_priority()` from the PnP core.

## Control Flow
`pnp_is_active()` applies a conservative current-resource heuristic: no meaningful first port, memory, IRQ, or DMA means inactive. The EISA converter endian-swaps the 32-bit ID and formats three compressed vendor characters plus four hex digits. Debug flows build short strings in a fixed buffer, branch by option resource type, enumerate IRQ/DMA bitmaps, add optional/dependent-set metadata, and emit through `pnp_dbg()`.

## State and Persistence Behavior
There is no persistent state in this file. It reads PnP device resource and option lists and writes only caller-provided output buffers or debug logs. The active heuristic depends on current resources that other PnP code owns and may lag true hardware state after disable paths clear only auto-assigned resources.

## Dependencies and Integration Points
It depends on Linux module, ctype/hex helpers, endian conversion, the public PnP API, and `base.h` debug macros. Integration is mostly internal: protocol parsers and resource registration paths call the debug printers, while `pnp_is_active()` is exported for PnP consumers.

## Risks and Edge Cases
The activity heuristic is explicitly documented as unreliable after `pnp_disable_dev()`. `pnp_eisa_id_to_string()` preserves historical Linux six-bit behavior for the first character, so strict EISA spec validation may disagree. `dbg_pnp_show_option()` uses a 128-byte buffer and `scnprintf()`, so very large option ranges are truncated rather than dynamically allocated. Unknown option types are not rendered beyond the enclosing debug call.

## Test Signals
Test EISA conversion against known IDs including historical lower-case/extended first-character cases, active/inactive devices with zero-length resources, each option type's debug formatting, optional IRQ flags, dependent-set priorities, empty IRQ/DMA masks, and buffer truncation under debug-enabled builds.
