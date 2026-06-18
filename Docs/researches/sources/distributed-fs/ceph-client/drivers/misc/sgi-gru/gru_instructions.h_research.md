# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gru_instructions.h

Purpose: defines GRU userspace/kernel inline instruction ABI: command formats, opcode/exception constants, cache flush/start helpers, instruction constructors, status polling wrappers, and pointer helpers for GSEG control/data segments.

Important APIs and types: `struct gru_instruction_bits`, `struct gru_instruction`, `struct control_block_extended_exc_detail`, `union gru_mesqhead`, and `struct gru_control_block_status` mirror hardware command/cacheline layout. Inline APIs issue VLOAD/VSTORE/IVLOAD/IVSTORE/VSET/IVSET/VFLUSH/NOP/BCOPY/BSTORE/GAM* and MESQ instructions, read AMO values, build message queue heads, check/wait/abort status, and locate GSEG/CB/data pointers.

Control flow: constructors fill command fields, data addresses, element counts, strides, operands, and call `gru_start_instruction()`, which ordered-stores the low command word with active/start bits, issues a memory barrier, and flushes the command cacheline. `gru_check_status()` falls back to `gru_check_status_proc()` for non-active statuses; `gru_wait()` and abort use external kernel implementations.

State and persistence: no allocated state, but inline functions mutate memory-mapped GRU control blocks and data segments visible to hardware.

Dependencies and integration points: x86_64 cache flushes via `clflush`, external service routines from `grukservices.c`, and hardware constants used by `grufault.c`/`gruhandles.c`. It is ABI-coupled to userspace libraries.

Risks and test signals: bitfield layout and endianness/compiler packing are critical. A wrong barrier/flush sequence can leave hardware seeing partial commands. Tests should validate each instruction encoding against hardware docs/emulator, check status handling for idle/active/exception/call-OS, and verify message queue/AMO helpers.
