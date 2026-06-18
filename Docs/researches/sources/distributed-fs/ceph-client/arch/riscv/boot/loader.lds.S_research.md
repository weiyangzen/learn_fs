<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/loader.lds.S -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/loader.lds.S

## Purpose
Links the RISC-V loader payload at the kernel link address.

## Important APIs, Types, And Functions
Sets `OUTPUT_ARCH(riscv)`, `ENTRY(_start)`, starts at `KERNEL_LINK_ADDR`, emits `.payload`, and aligns the end to eight bytes.

## Control Flow
The linker script has declarative flow only: it places all `.payload` input sections from `loader.o` into the output image.

## State And Persistence
State is link-time layout of the loader binary.

## Dependencies And Integration Points
Depends on `asm/page.h`, `asm/pgtable.h`, `KERNEL_LINK_ADDR`, and `loader.S`'s `.payload` section.

## Risks And Edge Cases
Wrong link address or section name can produce a loader that firmware jumps into incorrectly or that omits the embedded Image.

## Test Signals
Signals are successful LD invocation for `arch/riscv/boot/loader` and inspection of the payload address/size.

Source read size: 17 lines, 206 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/loader.lds.S -->
