# sources/distributed-fs/ceph-client/arch/mips/include/asm/shmparam.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/shmparam.h

### Purpose
`shmparam.h` defines the MIPS shared-memory attach alignment requirement used to avoid cache aliasing problems.

### Important APIs, Types, And Functions
It exports `__ARCH_FORCE_SHMLBA` and `SHMLBA`, with `SHMLBA` set to `0x40000`.

### Control Flow
SysV shared-memory attach paths use `SHMLBA` when validating or choosing attach addresses.

### State, Persistence, Dependencies, And Integration
There is no local state. Integration is with generic IPC/shmem address placement and MIPS cache-alias avoidance.

### Risks
Lowering the alignment can reintroduce virtual cache alias corruption; raising it can break userspace layout assumptions or waste address space.

### Test Signals
Run SysV shared-memory attach tests, especially with VIPT aliasing-cache CPUs, and verify userspace receives properly aligned mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/shmparam.h -->
