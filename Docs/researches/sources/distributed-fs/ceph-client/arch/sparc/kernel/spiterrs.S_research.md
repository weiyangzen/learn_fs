# sources/distributed-fs/ceph-client/arch/sparc/kernel/spiterrs.S

Purpose: provides low-level UltraSPARC Spitfire trap handlers for access errors, correctable ECC events, and instruction/data access exceptions before handing decoded state to C.

Important APIs/symbols: defines `__spitfire_access_error`, `__spitfire_cee_trap`, `__spitfire_data_access_exception_tl1`, `__spitfire_data_access_exception`, `__spitfire_insn_access_exception_tl1`, and `__spitfire_insn_access_exception`. It reads/writes ASIs for `AFSR`, `AFAR`, `UDBH/UDBL_ERROR`, DMMU/IMMU SFSR/SFAR, and calls C handlers such as `spitfire_access_error()`.

Control flow: the access-error path disables error reporting to prevent recursive RED-state traps, captures AFSR/AFAR/trap-level/type, reads and conditionally clears UDB error registers, clears sticky AFSR bits, selects TL0/TL1 trap entry, and calls C with `pt_regs` plus encoded status/address. The CEE path prioritizes uncorrectable errors by branching to the main access-error handler; otherwise it disables only correctable-error reporting and reuses the capture path. Access-exception handlers capture and clear MMU fault status, special-case window spill/fill traps, then enter trap frames and call C.

State and persistence: updates hardware sticky error registers and transient trap registers only; no persistent kernel data is stored here.

Dependencies and integration points: depends on UltraSPARC-I/II ASI semantics, trap entry/return code (`etrap`, `etraptl1`, `rtrap`), window-fixup handlers, and C fault/error reporters.

Risks: ordering and `membar #Sync` are critical to avoid lost or recursive hardware errors. TL1 paths have limited register/state assumptions. Wrong AFSR/UDB clearing can hide ECC or access faults.

Test signals: fault-injection or platform error logs for UE/CE, TL0/TL1 access faults, window spill/fill fault recovery, and confirmation that C handlers see AFAR/SFSR/trap-type data.
