# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruhandles.h

Purpose: defines the GRU memory map, handle offsets/counts, address conversion helpers, hardware handle structures, state/operation enums, page-size encodings, and prototypes for MCS handle operations.

Important APIs and types: constants describe GSEG/MCS base, GRU size, counts for CB/DSR/TFM/TGH/CBE/TFH/CCH, user resource limits, allocation units, chiplet topology, and GSEG offsets. Inline helpers compute GSEG, CB, DS, TFM/TGH/CBE/TFH/CCH addresses and chiplet physical/virtual addresses. Structures mirror hardware handles: `gru_tlb_fault_map`, `gru_tlb_global_handle`, `gru_tlb_fault_handle`, `gru_context_configuration_handle`, and `gru_control_block_extended`.

Control flow and integration: no high-level runtime flow, but the inline helpers are used everywhere to locate MMIO/cacheline-backed hardware structures. Enums define valid opcodes/status/state/cause values consumed by `gruhandles.c`, `grufault.c`, and dump/proc code.

State and persistence: no allocated state; structure definitions interpret live hardware memory.

Dependencies and risks: layout and bitfields are hardware ABI. `GRU_PAGESIZE()`/`GRU_SIZEAVAIL()` must match hardware encoding. Tests should validate structure sizes/offsets, address arithmetic for every context/handle type, page-size encoding table, and lock/unlock helpers from `grutables.h` that operate on these handles.
