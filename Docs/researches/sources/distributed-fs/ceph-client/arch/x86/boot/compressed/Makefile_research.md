## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/Makefile

### Purpose
`boot/compressed/Makefile` builds the position-independent compressed kernel runtime, compressed payload wrapper, relocation side data, and final compressed `vmlinux` consumed by `arch/x86/boot`.

### Important APIs, Types, And Functions
Key variables include `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `KBUILD_LDFLAGS`, `LDFLAGS_vmlinux`, `vmlinux-objs-y`, `vmlinux-libs-y`, `suffix-y`, `CMD_RELOCS`, and `sed-voffset`. It builds `mkpiggy`, `vmlinux`, `vmlinux.bin`, `vmlinux.relocs`, compressor-specific `vmlinux.bin.*`, generated `piggy.S`, and `../voffset.h`.

### Control Flow
The makefile configures freestanding PIE-friendly flags, selects 32-bit or 64-bit compressed startup objects, includes optional KASLR, ACPI, EFI, TDX, SEV, unaccepted-memory, and SBAT objects, links compressed `vmlinux` with a custom linker script, objcopies the binary, generates relocation data when needed, compresses `vmlinux.bin.all`, and runs `mkpiggy` to emit assembly containing the compressed payload and length symbols.

### State, Persistence, And Dependencies
Persistent outputs are compressed payloads, `piggy.S`, `vmlinux.relocs`, `voffset.h`, and compressed `vmlinux`. Dependencies include selected compression tools from `scripts/Makefile.lib`, `arch/x86/tools/relocs`, EFI stub libraries, startup libraries, generated ACPI/SEV/TDX support, and the top-level `BITS`/`UTS_MACHINE`.

### Integration Points
`arch/x86/boot/Makefile` invokes this directory and objcopies its linked result into `vmlinux.bin` for `bzImage`. The object list directly mirrors Kconfig feature selection for early decompression and firmware handling.

### Risks
The compressed runtime must remain PIE and freestanding because it may execute at arbitrary physical addresses without normal relocation processing. Object inclusion order is critical: startup, decompressor, payload, KASLR, identity mapping, and firmware helpers must be linked with symbols that assembly expects.

### Test Signals
Build every compression format, both x86 widths, EFI/non-EFI, KASLR on/off, AMD memory encryption, TDX, and unaccepted-memory configurations. Inspect generated `piggy.S`, `voffset.h`, and relocation warnings.
