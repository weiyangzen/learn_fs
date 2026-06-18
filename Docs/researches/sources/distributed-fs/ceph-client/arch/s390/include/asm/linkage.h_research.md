# sources/distributed-fs/ceph-client/arch/s390/include/asm/linkage.h

Purpose: This header defines s390 symbol alignment used by assembly linkage macros.

Important APIs/types/functions: `__ALIGN` expands to `.balign CONFIG_FUNCTION_ALIGNMENT, 0x07`, and `__ALIGN_STR` stringifies it.

Control flow: Assembly symbol macros include this alignment so functions begin on the configured boundary and padding bytes are the s390 no-op pattern.

State and persistence: There is no runtime state; it affects object text layout.

Dependencies and integration points: It integrates Linux linkage macros, s390 assembly sources, and function alignment configuration.

Risks and test signals: Wrong alignment or padding can affect alternatives, ftrace, unwind/probe expectations, or performance. Tests are build/objdump checks for assembly functions and boot coverage with non-default function alignment.
