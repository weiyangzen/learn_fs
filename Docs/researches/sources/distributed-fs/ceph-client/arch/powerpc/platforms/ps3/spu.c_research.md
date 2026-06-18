# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/spu.c

Purpose: Provides PS3-specific Cell SPU management and priv1 operations. It constructs logical SPEs through LV1, maps SPU regions, wires SPU interrupts, enumerates SPU resource reservations, and installs platform hooks consumed by the generic SPU/spufs code.

Important APIs/types/functions: Defines `enum spe_type`, `struct spe_shadow`, `enum spe_ex_state`, `struct priv1_cache`, and `struct spu_pdata`. Public `ps3_get_spe_id()` and `ps3_spu_set_platform()` bridge external users. Core helpers include `get_vas_id()`, `construct_spu()`, `setup_areas()`, `setup_interrupts()`, `enable_spu()`, `ps3_create_spu()`, `ps3_destroy_spu()`, `ps3_enumerate_spus()`, and `spu_priv1_ps3_ops`.

Control flow: `ps3_spu_set_platform()` installs management and priv1 ops. Enumeration reads repository SPU resource ids and calls the generic SPU creation callback for exclusive resources. Creation allocates `spu_pdata`, records the resource id, constructs a logical SPE, enables it, maps shadow/local-store/problem/priv2 areas, sets up three interrupt classes, and spins until the shadow execution status reports executed. Destruction disables the SPE, tears down interrupts and mappings, destructs the logical SPE, and frees private data.

State and persistence: Persistent per-SPU state lives in `spu->pdata`: LV1 SPE id, resource id, LV1 area addresses, ioremapped shadow pointer, cached interrupt masks, SR1, and TCLASS id. Shadow registers are read-only mappings of hypervisor-provided SPE state. Interrupt masks and selected priv1 registers are cached because reads are not all directly available from LV1.

Dependencies and integration points: Depends on LV1 SPE calls, PS3 repository resource reservations, PS3 SPE IRQ setup, generic `struct spu`, `spu_management_ops`, `spu_priv1_ops`, spufs, and Cell SPU register definitions.

Risks: `ps3_create_spu()` busy-waits without timeout for executed state. Failure cleanup after allocation calls `ps3_destroy_spu()`, which contains `BUG_ON()` calls and assumes enough fields were initialized. Priv1 mask read-modify-write comments question caller serialization. `mfc_sr1_set()` enforces hypervisor-allowed bits with `BUG_ON()`.

Test signals: SPU enumeration count, spufs mount and SPU context execution, SPU interrupt delivery for all classes, SPU enable/disable paths, priv1 register behavior under workloads, and error injection for LV1 construct/enable/map failures are useful.

Source read size: 620 lines, 14680 bytes.
