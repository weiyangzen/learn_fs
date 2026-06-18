# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx.h

Purpose: provides the core CVMX utility layer for OCTEON: address-space construction, CSR and I/O access, physical/virtual conversion, processor/core identity, node-aware CSR access, bit helpers, cycle counters, polling macros, and core-count discovery.

Important APIs/types/functions: address macros include `CVMX_ADD_SEG`, `CVMX_ADD_IO_SEG`, and 32-bit variants. Constants include `CVMX_MAX_CORES`, cache line size/alignment, and node masks/shifts. Helpers include `cvmx_get_proc_id`, `cvmx_build_mask`, `cvmx_build_io_address`, `cvmx_build_bits`, `cvmx_ptr_to_phys`, `cvmx_phys_to_ptr`, generated typed `cvmx_read64_*`/`cvmx_write64_*`, `cvmx_write_csr`, `cvmx_writeq_csr`, `cvmx_write_io`, `cvmx_read_csr`, `cvmx_readq_csr`, `cvmx_send_single`, `cvmx_read_csr_async`, `cvmx_octeon_is_pass1`, `cvmx_get_core_num`, node/local-core helpers, `cvmx_write_csr_node`, `cvmx_read_csr_node`, `cvmx_pop`, `cvmx_dpop`, `cvmx_get_cycle`, `cvmx_get_cycle_global`, `CVMX_WAIT_FOR_FIELD64`, and `cvmx_octeon_num_cores`.

Control flow: CSR writes issue a volatile store and, for RSL-space addresses, read `CVMX_MIO_BOOT_BIST_STAT` to force completion. Async CSR reads encode an IOBDMA SENDSINGLE request into scratch memory. Node CSR helpers splice node bits into the address. `CVMX_WAIT_FOR_FIELD64` repeatedly reads a CSR field until a predicate is true or a CPU-clock-derived timeout expires. Core count reads CIU/CIU3 fuse registers and counts set bits.

State and persistence: this header holds no persistent state. It directly reads/writes hardware CSRs, cycles, fuses, and address spaces. Timeout behavior depends on `cvmx_sysinfo_get()->cpu_clock_hz`.

Dependencies and integration points: includes Linux kernel headers, delay support, CVMX assembly/packet/sysinfo headers, many CSR definition headers, bootinfo/bootmem, and L2 cache helpers. It is foundational for nearly every OCTEON-specific header in this group.

Risks: pointer/physical conversions mask addresses differently for 32-bit, 64-bit XKSEG/XKPHYS, and hardware limits; misuse can produce inaccessible or truncated DMA addresses. `cvmx_build_mask(bits)` is unsafe for `bits == 64` in plain C shift terms if called that way. `CVMX_WAIT_FOR_FIELD64` depends on initialized sysinfo clock and can busy wait. CSR completion read is address-space-specific. Node address composition must preserve non-node bits.

Test signals: hardware smoke tests should cover CSR read/write completion, physical pointer round trips for DMA buffers, cycle-counter monotonicity, timeout macro behavior, node CSR access on multi-node systems, and core-count fuse interpretation.
