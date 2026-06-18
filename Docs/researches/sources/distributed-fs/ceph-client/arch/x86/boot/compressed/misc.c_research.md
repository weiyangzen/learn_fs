## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/misc.c

### Purpose
`compressed/misc.c` is the compressed kernel C runtime. It provides decompressor integration, early output, heap setup, ELF segment loading, relocation processing, memory-encryption command-line handling, KASLR invocation, unaccepted-memory acceptance, and the `extract_kernel()` entry used by assembly startup.

### Important APIs, Types, And Functions
Important globals are `boot_params_ptr`, `pio_ops`, `free_mem_ptr`, `free_mem_end_ptr`, `spurious_nmi_count`, `kernel_text_size`, `kernel_inittext_offset`, `kernel_inittext_size`, and `kernel_total_size`. Important functions include `__putstr()`, `__puthex()`, `__putdec()`, `handle_relocations()`, `parse_elf()`, `decompress_kernel()`, `parse_mem_encrypt()`, `early_sev_detect()`, and exported `extract_kernel()`.

### Control Flow
`extract_kernel()` saves boot params, clears transient KASLR flags, parses `mem_encrypt=`, sanitizes boot params, initializes video and I/O, detects TDX before console setup, suppresses video output for SEV-ES where MMIO is unsafe, initializes console, stores RSDP, sets the boot heap, computes the required decompression size, calls `choose_random_location()`, validates physical and virtual placement, accepts unaccepted memory if needed, decompresses the payload with the selected decompressor, parses the resulting ELF into load segments, applies relocations when needed, disables boot exception handling, reports spurious NMIs, and returns the final entry pointer.

### State, Persistence, And Dependencies
State includes boot params mutations, screen cursor updates, heap pointers, serial/video console state, decompressed ELF image, relocation-applied memory, and early IO ops. Dependencies include generated `voffset.h`, decompressor source includes selected by Kconfig, EFI/ACPI/KASLR/TDX/SEV/unaccepted-memory helpers, setup boot param sanitization, and compressed payload symbols from `piggy.S`.

### Integration Points
Called by `head_32.S` and `head_64.S`. It coordinates nearly every compressed boot subsystem and hands control to the uncompressed kernel entry.

### Risks
Static pointers are dangerous because the compressed runtime is PIE but does not process its own relocations. ELF parsing and relocation bounds checks must prevent writes outside the kernel image. Output address validation must match architecture constraints, and unaccepted memory must be accepted before decompression writes.

### Test Signals
Boot every compression format, relocatable/non-relocatable kernels, KASLR on/off, malformed compressed payload, invalid ELF alignment, relocation tables, early serial/video output, TDX/SEV-SNP unaccepted memory, and spurious NMI reporting.
