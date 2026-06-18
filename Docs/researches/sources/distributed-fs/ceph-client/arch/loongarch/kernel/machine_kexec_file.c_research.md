## sources/distributed-fs/ceph-client/arch/loongarch/kernel/machine_kexec_file.c

### Purpose
`machine_kexec_file.c` implements LoongArch support for the in-kernel `kexec_file_load` path. It selects EFI and ELF file loaders, constructs the modified command line, places initrd and crash dump metadata segments, and prepares cleanup for allocated ELF core headers.

### Important APIs, Types, And Functions
It exports the `kexec_file_loaders` array, `arch_kimage_file_post_load_cleanup`, and `load_other_segments`. Helper functions append `kexec_file`, `initrd=start,size`, `mem=size@start`, and `elfcorehdr=size@start` command-line tokens. Under `CONFIG_CRASH_DUMP`, `prepare_elf_headers` builds a `crash_mem` range list and calls `crash_prepare_elf64_headers`.

### Control Flow
`load_other_segments` allocates a bounded command-line buffer, appends the loader token, optionally creates and loads ELF core headers for crash images, optionally places initrd after the loaded kernel with a 1 GiB aligned/32 GiB window heuristic, checks command-line length, copies the caller command line after generated tokens, and stores `image->arch.cmdline_ptr`. On error it restores the original segment count and frees temporary command-line storage.

### State, Persistence, And Dependencies
Loaded initrd and ELF core header segments persist inside the `struct kimage` segment list until execution or cleanup. `image->elf_headers`, `elf_load_addr`, and `elf_headers_sz` record crash metadata. The code depends on generic `kexec_add_buffer`, memblock range iteration, crashkernel resources, and `COMMAND_LINE_SIZE`.

### Integration Points
Architecture-specific EFI and ELF loaders call `load_other_segments` after loading the kernel. `machine_kexec.c` later copies the generated command line to the safe handoff area. Crash dump tooling consumes `elfcorehdr` and `mem=` parameters generated here.

### Risks
Command-line construction is size-sensitive and uses formatted appends into a fixed buffer; missed bounds before `sprintf` would be dangerous if new tokens are added. Error cleanup resets only `nr_segments`, so any future side state must be cleaned explicitly. Initrd placement constraints need to match LoongArch boot-loader expectations. Crash memory exclusion must handle high and low crashkernel regions exactly.

### Test Signals
Run `kexec_file_load` with EFI and ELF kernels, with and without initrd, and verify `/proc/cmdline` in the next kernel includes `kexec_file` and correct initrd coordinates. Crash-kexec tests should validate vmcore creation and `elfcorehdr` parsing. Negative tests include too-long command lines and forced buffer placement failures.
