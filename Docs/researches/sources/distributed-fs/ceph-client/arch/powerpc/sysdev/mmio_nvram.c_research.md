<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mmio_nvram.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mmio_nvram.c

Purpose: Registers a memory-mapped NVRAM backend with the PowerPC machine descriptor.

Important APIs/types/functions: Entry point is `mmio_nvram_init()`. Backend callbacks are `mmio_nvram_read()`, `mmio_nvram_write()`, `mmio_nvram_read_val()`, `mmio_nvram_write_val()`, and `mmio_nvram_get_size()`.

Control flow: Initialization finds a node of type or compatible `nvram`, translates its first resource, rejects zero address/length, maps it, logs the mapping, and fills `ppc_md.nvram_*` callbacks. Reads/writes clamp by current index and use `memcpy_fromio()`/`memcpy_toio()` under a spinlock. Byte callbacks return `0xff` or ignore writes past the mapped length.

State and persistence: Persistent state is `mmio_nvram_start`, `mmio_nvram_len`, spinlock, and registered `ppc_md` callback pointers. Data persistence is the underlying NVRAM hardware.

Dependencies and integration points: Uses OF address parsing, MMIO mapping, PowerPC NVRAM callback ABI, and generic NVRAM consumers.

Risks: There is no unmap path because this is boot-time machine setup. `loff_t *index` arithmetic assumes nonnegative offsets from callers. The code serializes access but does not implement hardware-specific write delays or verification.

Test signals: Device-tree NVRAM discovery, `/dev/nvram` read/write bounds checks, byte callback behavior at end of range, concurrent access, and boot without an NVRAM node.

Source read size: 145 lines, 3177 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mmio_nvram.c -->
