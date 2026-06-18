# sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc64.S

Purpose: implements SPARC64 high-speed XOR routines using VIS floating/vector registers and Niagara block operations.

Important APIs and flow: exports `xor_vis_{2,3,4,5}` and Niagara variants. VIS functions enter VIS state if needed, switch ASI to block primary, use `ldda` and `stda` plus `fxor` over 64-byte or 128-byte blocks, issue memory barriers, restore ASI/FPRS, and return.

State and persistence: no durable state; it temporarily changes FPRS and ASI and must restore them before return. Destination memory is updated.

Dependencies and integration: included through `xor-sparc64-glue.c`; selection is forced by `sparc/xor_arch.h` based on `tlb_type` and `sun4v_chip_type`.

Risks and test signals: risks include strict alignment/length requirements, VIS state handling, ASI restoration, and Niagara CPU classification. Signals include sparc64 boot logs, KUnit XOR tests, and RAID parity stress on VIS and Niagara machines.
