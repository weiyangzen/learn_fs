# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-smp.c

Purpose: SMP support for SGI IP30. It enumerates CPUs from MPCONF, sends HEART IPIs, and launches secondary CPUs through firmware-visible structures.

Important APIs and control flow: `ip30_smp_setup()` scans two MPCONF slots for `MPCONF_MAGIC`, marks CPUs possible, sets logical maps, logs slot IDs, and sets coherent-on-write cache mode. IPI helpers write HEART set-ISR bits for reschedule or call-function actions. `ip30_smp_boot_secondary()` fills stack/thread pointers in the target `mpconf`, uses `mb()`, and writes `smp_bootstrap` to `launch`. Secondary init calls `ip30_per_cpu_init()`, and finish enables the CP0 compare IRQ and local interrupts.

State, persistence, and integration: state includes CPU possible/logical maps, MPCONF launch fields, HEART IPI bits, and CP0 cache mode. Dependencies include firmware MPCONF at a fixed address, HEART registers, generic MIPS SMP, and IP30 timer setup. Risks include only two physical CPUs supported, direct fixed-address firmware structure access, and reliance on cache coherency mode for R14000 stability. Test signals are detected CPU count, secondary CPU online, IPI operation, and no userland instruction bus errors.
