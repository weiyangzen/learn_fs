# sources/distributed-fs/ceph-client/arch/x86/lib/iomem.c

Purpose: implements x86 I/O memory copy and set helpers with string-instruction or unrolled byte operations depending on confidential-computing platform constraints.

Important APIs/functions: exports `memcpy_fromio`, `memcpy_toio`, and `memset_io`. Internal helpers include `string_memcpy_fromio`, `string_memcpy_toio`, `unrolled_memcpy_fromio`, `unrolled_memcpy_toio`, `unrolled_memset_io`, and `rep_movs`.

Control flow: normal paths align odd/word portions then use `rep movsl` plus word/byte tails for IO copy. Confidential guest platforms with `CC_ATTR_GUEST_UNROLL_STRING_IO` use byte-by-byte `readb`/`writeb` loops instead of string IO. `memset_io` uses unrolled `writeb` under that attribute, otherwise plain `memset` to the IO address.

State and persistence behavior: reads or writes MMIO/device memory and normal memory buffers. `memcpy_fromio` unpoisons destination for KMSAN because device-provided data is initialized; `memcpy_toio` checks source initialization before writing to devices.

Dependencies/integration points: Linux IO API, confidential-computing platform attributes, KMSAN, string assembly, and exported architecture IO memory APIs used by drivers.

Risks: string IO can be unsafe or semantically wrong for some confidential guest environments, hence the unrolled path. MMIO ordering and access width patterns can matter for devices. KMSAN annotations prevent false positives and real uninitialized writes to devices.

Test signals: driver IO copy tests, confidential guest boot tests, KMSAN runs, device emulation tests comparing string versus unrolled behavior, and zero-length/unaligned IO copy cases.
