# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/Kconfig

Purpose: IP27-specific configuration for SGI Origin/Onyx NUMA systems. It selects node addressing mode and optional mapped-kernel/text-replication support.

Important APIs and control flow: the "Node addressing mode" choice selects `SGI_SN_M_MODE` by default or `SGI_SN_N_MODE`. `MAPPED_KERNEL` changes kernel load mapping for NUMA text replication. `REPLICATE_KTEXT` selects `MAPPED_KERNEL` and enables per-node kernel text copies.

State, persistence, and integration: no runtime state is created directly, but these options determine address decoding, boot compatibility checks, and memory layout logic in IP27 code. Dependencies include hardware firmware mode matching the kernel config. Risks include boot-time panic if N/M mode is mismatched and memory cost or mapping bugs with text replication. Test signals are Kconfig selection, `plat_mem_setup()` mode log, and successful boot on the target Origin mode.
