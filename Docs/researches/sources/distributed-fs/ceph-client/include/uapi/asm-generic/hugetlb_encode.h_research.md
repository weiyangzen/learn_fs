# sources/distributed-fs/ceph-client/include/uapi/asm-generic/hugetlb_encode.h

Purpose: Defines the generic encoding for selecting hugetlb page sizes in syscall flag arguments.

Important APIs/types/functions: Exports `HUGETLB_FLAG_ENCODE_SHIFT`, `HUGETLB_FLAG_ENCODE_MASK`, and size encodings from 16KB through 16GB.

Control flow: Preprocessor constants encode log2(page size) into bits 26-31 of flags such as `MAP_HUGETLB`.

State/persistence: No runtime state; constants define ABI flag encoding.

Dependencies/integration: Included by syscall-specific headers that expose hugepage-size flags, such as mmap-related UAPI.

Risks: Encoding collisions or wrong shifts break user requests for non-default hugepage sizes.

Test signals: Compile programs using `MAP_HUGE_*`-style definitions and run mmap hugetlb size-selection tests where supported.
