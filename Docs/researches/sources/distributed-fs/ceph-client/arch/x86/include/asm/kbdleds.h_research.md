<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kbdleds.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kbdleds.h

## Purpose
Default keyboard LED selection helper for x86 boot options. The header is 18 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/setup.h>`

Notable constants/macros: `#define _ASM_X86_KBDLEDS_H`

Notable declarations and inline helpers: `#define _ASM_X86_KBDLEDS_H`; `static inline int kbd_defleds(void)`

## Control Flow
kbd_defleds() returns configured default LED bits, typically influenced by boot/setup state.

## State and Persistence
State is boot setup data consulted through asm/setup.h; no mutable state is held here.

## Dependencies and Integration Points
Depends on keyboard/VT console code and x86 setup header values.

## Risks
Risks are minor: incorrect default LED state or compile drift with setup fields.

## Test Signals
Tests should verify boot parameter/default LED behavior and compile keyboard-disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kbdleds.h -->
