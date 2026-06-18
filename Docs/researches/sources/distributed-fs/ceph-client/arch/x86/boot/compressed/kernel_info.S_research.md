## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/kernel_info.S

### Purpose
`compressed/kernel_info.S` emits the `kernel_info` metadata structure in a dedicated read-only section of the compressed kernel.

### Important APIs, Types, And Functions
The exported symbol is `kernel_info`. The structure starts with the `"LToP"` signature, length fields, and `SETUP_TYPE_MAX`.

### Control Flow
There is no runtime control flow. The assembler lays out fixed header fields followed by currently empty variable-length data.

### State, Persistence, And Dependencies
The persistent output is `.rodata.kernel_info` inside the boot image. It depends on `asm/bootparam.h` for `SETUP_TYPE_MAX` and on external tooling/loaders knowing the metadata format.

### Integration Points
Bootloaders or inspection tools can find `kernel_info` to learn kernel boot-protocol metadata such as maximal setup_data type.

### Risks
The format is ABI-like. Extending variable-length data must keep size fields and signature semantics compatible.

### Test Signals
Inspect built compressed images for the `LToP` signature, correct length fields, and expected `SETUP_TYPE_MAX` value.
