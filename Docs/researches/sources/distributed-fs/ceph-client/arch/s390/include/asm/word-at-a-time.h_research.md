## sources/distributed-fs/ceph-client/arch/s390/include/asm/word-at-a-time.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/word-at-a-time.h` is a word-at-a-time
zero-byte scanning in the s390 ceph-client Linux source snapshot. It has 65 lines and 1564 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
s390 constants and helpers for has_zero/find_zero/zero_bytemask plus exception-safe unaligned loads
Important macros/constants: `_ASM_WORD_AT_A_TIME_H`, `WORD_AT_A_TIME_CONSTANTS`.
Important types/layouts: `word_at_a_time`.
Important declarations or inline helpers: `__fls`, `volatile`, `prep_zero_mask`, `create_zero_mask`, `find_zero`, `has_zero`, `zero_bytemask`, `load_unaligned_zeropad`.

### Control Flow
The header is mostly inline fast-path code: callers enter small assembly sequences, condition-code
extraction converts hardware results into C values, and fallback or wait loops are selected through
architecture facilities and alternative patching.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic string scanning, strncpy/strnlen, uaccess/string code, and exception-table handling. Direct
include dependencies detected here: `linux/bitops.h`, `linux/wordpart.h`, `asm/asm-extable.h`,
`asm/bitsperlong.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic string scanning, strncpy/strnlen,
uaccess/string code, and exception-table handling. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
incorrect byte-order masks break string termination and bounds handling

### Test Signals
word-at-a-time selftests, unaligned fault tests, and big-endian string cases
