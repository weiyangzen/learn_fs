# sources/distributed-fs/ceph-client/include/soc/arc/mcip.h

Purpose: defines the ARC Multi-Core IP (MCIP/ARConnect) auxiliary registers, bitfield layouts, command encodings, and inline command helpers for IPI, semaphores, debug, GFRC, and IDU interrupt distribution.

Important APIs and types: register constants cover MCIP build, IDU build, GFRC build, command, write-data, and readback aux registers. `struct mcip_cmd` packs `{cmd,param}` differently for big- and little-endian CPUs. `struct mcip_bcr` and `struct mcip_idu_bcr` expose feature and IRQ-count build-register fields. `mcip_idu_bcr_to_nr_irqs()` converts the IDU exponent encoding. `__mcip_cmd()`, `__mcip_cmd_data()`, and `__mcip_cmd_read()` issue simple, data-bearing, and readback commands.

Control flow: callers optionally write MCIP_WDATA, issue a command through MCIP_CMD, and read MCIP_READBACK for query commands. Comments note callers must lock around data-bearing commands to keep WDATA/CMD atomic.

State and persistence: hardware state includes interrupt pending/ack state, semaphores, debug masks, GFRC selection, and IDU routing. The header stores no software state.

Dependencies and integration points: depends on `arc_aux.h` and integrates SMP/IPI, interrupt controller, timer, and platform bring-up code on ARC systems.

Risks and test signals: risks include missing locking around `__mcip_cmd_data()`, endian bitfield drift, wrong IDU IRQ-count decoding, and using unsupported commands on older MCIP builds. Test SMP IPI generation/ack, IDU enable/mode/destination programming, GFRC reads, semaphore claim/release, big-endian ARC builds, and non-ARC compile guards.
