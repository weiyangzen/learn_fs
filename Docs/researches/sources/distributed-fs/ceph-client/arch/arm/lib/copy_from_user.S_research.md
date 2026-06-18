# sources/distributed-fs/ceph-client/arch/arm/lib/copy_from_user.S

Purpose: implements `arm_copy_from_user`, copying user memory into kernel memory and returning bytes not copied.

Control flow selects domain or normal user load macros, optionally masks speculative user ranges under `CONFIG_CPU_SPECTRE`, then includes `copy_template.S` for optimized forward copying. Fixup code unwinds saved registers and computes the remaining byte count after a fault. State is only copied memory and transient registers. Dependencies include uaccess helpers, exception tables, PAN/domain configuration, and the shared copy template. Risks are speculative range masking bugs, partial-copy accounting, unaligned source handling, and user faults. Test signals include copy tests over page boundaries, invalid user ranges, and Spectre-config builds.
