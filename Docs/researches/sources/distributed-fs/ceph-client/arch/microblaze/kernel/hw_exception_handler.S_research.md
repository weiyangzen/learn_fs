# sources/distributed-fs/ceph-client/arch/microblaze/kernel/hw_exception_handler.S

Purpose: provides the real-mode hardware exception fast path for unaligned accesses, bus/illegal/div/FPU exceptions, storage faults, and data/instruction TLB misses.

Important symbols and state: `_hw_exception_handler`, `_unaligned_data_exception`, `set_context`, `giveup_fpu`, `abort`, `tlb_skip`, `tlb_index`, `pt_pool_space`, load/store jump tables, and `ex_tmp_data_loc_*`. The exception vector table maps ESR exception codes to handler labels.

Control flow: the top handler saves a minimal register set, decodes ESR, and jumps to a handler. TLB miss handlers walk Linux page tables in physical mode, set accessed bits, compose MicroBlaze TLB entries, and return directly if resolved; otherwise they restore state and branch to `page_fault_*_trap` in `entry.S`. Unaligned handlers emulate byte-wise word/halfword loads/stores and use exception-table fixups for bad user pages.

State and persistence: updates hardware TLBs, `tlb_index`, PTE accessed bits, PID, saved register pools, and temporary data bytes. No dynamic allocation.

Dependencies and integration: coupled to PTE bit layout, page-table levels, `entry.S` trap labels, exception table format, and `asm-offsets`.

Risks and test signals: register save omissions, TLB replacement masking, endian-sensitive unaligned stores, and page-table bit assumptions are high risk. Test user/kernel TLB misses, storage faults, unaligned loads/stores across page boundaries, exception-table fixups, and context switching.
