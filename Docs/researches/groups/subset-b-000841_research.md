# Research: subset-b-000841

Grouped source research for subset B work item `subset-b-000841`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/mm/tlbflush_32.c -->
# sources/distributed-fs/ceph-client/arch/sh/mm/tlbflush_32.c

## Purpose
This file implements local TLB invalidation for 32-bit SuperH MMU kernels. It provides page, range, kernel-range, full-mm, and global flush paths that respect the SH ASID/MMU context model.

## Important APIs, Types, and Functions
The main APIs are `local_flush_tlb_page()`, `local_flush_tlb_range()`, `local_flush_tlb_kernel_range()`, `local_flush_tlb_mm()`, and `__flush_tlb_global()`. They operate on `struct vm_area_struct`, `struct mm_struct`, CPU-local `cpu_context()`/`cpu_asid()` state, the current hardware ASID from `get_asid()`, and low-level `local_flush_tlb_one()`, `local_flush_tlb_all()`, `activate_context()`, `set_asid()`, and `MMUCR` accessors.

## Control Flow
Page and small-range flushes first check that the target mm has a valid CPU context. If the target mm is not the current mm, interrupts are disabled, the current ASID is saved, the target ASID is installed, individual TLB entries are flushed, and the saved ASID is restored. Large ranges and whole-mm flushes avoid entry-by-entry invalidation by marking `cpu_context(cpu, mm) = NO_CONTEXT`; if the mm is active, `activate_context()` allocates/reloads a fresh context. Kernel-range flushes use `init_mm`'s ASID or fall back to `local_flush_tlb_all()` when the span exceeds a quarter of the TLB. `__flush_tlb_global()` sets `MMUCR_TI`, invalidating all UTLB/ITLB entries including wired mappings.

## State and Persistence Behavior
The file mutates per-mm/per-CPU context state and transient hardware TLB state. Context invalidation persists until the mm is next activated; ASID swaps are protected by `local_irq_save()` so interrupt handlers do not run with the wrong ASID. There is no storage outside CPU MMU registers and `mm_context` metadata.

## Dependencies and Integration Points
It depends on SH MMU context helpers from `asm/mmu_context.h`, SH TLB primitives from `asm/tlbflush.h`, `current->mm`, `init_mm`, `PAGE_SIZE`, `MMU_NTLB_ENTRIES`, and raw MMUCR I/O. It is called by generic MM unmap, mprotect, page-table teardown, vmalloc/module permission changes, and SMP shootdown wrappers outside this local file.

## Risks
The highest-risk behavior is temporary ASID switching: missing interrupt masking or failed ASID restoration can corrupt unrelated address spaces. The large-range threshold trades correctness for context rollover and must keep active mms reloaded. `__flush_tlb_global()` is destructive because it also removes wired entries; callers must only use it for global invalidation cases.

## Test Signals
Build SH MMU configs and exercise fork/exec/exit, `mmap()`/`munmap()`, `mprotect()`, vmalloc/module loads, and high churn across multiple address spaces. Useful signals are no stale translations after page removal, no faults caused by wrong ASID restore, correct kernel mapping invalidation, and stable behavior around large range flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/mm/tlbflush_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/mm/uncached.c -->
# sources/distributed-fs/ceph-client/arch/sh/mm/uncached.c

## Purpose
This file tracks the SH cached-to-uncached virtual alias window. It exposes the uncached range used by legacy 29-bit mappings, no-MMU builds, or PMB-managed 32-bit MMU systems.

## Important APIs, Types, and Functions
Global state includes `cached_to_uncached`, `uncached_size`, `uncached_start`, and `uncached_end`; `uncached_start` and `uncached_end` are exported. `virt_addr_uncached()` tests whether a kernel address lies in the uncached range. `uncached_init()` initializes the range from `P2SEG` for 29-bit/no-MMU systems or from `memory_end` otherwise. `uncached_resize()` changes the tracked size.

## Control Flow
Early architecture setup calls `uncached_init()` after memory sizing is available. Platform/PMB code may later call `uncached_resize()` when it needs a different uncached window. Runtime callers use `virt_addr_uncached()` as a pure range check.

## State and Persistence Behavior
The range variables are global kernel state and persist after boot. There is no allocation or persistent storage; changing `uncached_size` recomputes `uncached_end` but does not itself create mappings.

## Dependencies and Integration Points
It depends on SH address-space constants, `memory_end`, `CONFIG_29BIT`, and `CONFIG_MMU`. It integrates with low-level cache-alias handling, DMA/cache maintenance, and code that converts between cached and uncached aliases.

## Risks
The default 512 MiB offset is only valid for legacy 29-bit layout until PMB code updates it. Incorrect start/end values can classify cached memory as uncached or the reverse, causing coherency bugs or invalid accesses. `uncached_resize()` assumes `uncached_start` was already initialized.

## Test Signals
Boot SH 29-bit, 32-bit PMB, and no-MMU configurations; verify exported range symbols, uncached alias conversions, DMA buffers, and `virt_addr_uncached()` around boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/mm/uncached.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/tools/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/tools/Makefile

## Purpose
This small Kbuild makefile wires SuperH generated-header tooling into the kernel build.

## Important APIs, Types, and Functions
It declares the generated target `include/generated/machtypes.h`, marks it under `targets`, and defines the rule that runs `arch/sh/tools/gen-mach-types` over `arch/sh/tools/mach-types`.

## Control Flow
When `archheaders` or dependent generated headers are requested, Kbuild invokes the awk generator and writes the generated machine-type header. The rule is purely build-time.

## State and Persistence Behavior
It persists only a generated header under `include/generated`. No runtime state exists.

## Dependencies and Integration Points
It depends on Kbuild variables such as `src`, `obj`, `targets`, and `quiet_cmd`/`cmd`, plus the companion awk script and machine-type input table. SH board/platform code consumes the generated `MACH_*` and `mach_is_*()` macros.

## Risks
Build reproducibility depends on stable input ordering and awk behavior. Missing dependency tracking would leave stale machine-type macros after `mach-types` changes.

## Test Signals
Run `make ARCH=sh archheaders` and verify `include/generated/machtypes.h` is regenerated and changes when `arch/sh/tools/mach-types` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/tools/gen-mach-types -->
# sources/distributed-fs/ceph-client/arch/sh/tools/gen-mach-types

## Purpose
This awk script generates the SH machine-type header from a two-column machine/config table.

## Important APIs, Types, and Functions
The script stores machine names in `mach[]` and corresponding Kconfig symbols in `config[]`. It emits `MACH_<name>` macros gated by `CONFIG_<symbol>` and convenience `mach_is_<lowercase>()` predicates.

## Control Flow
Comments and blank lines are skipped. Two-field rows are accumulated, then the `END` block writes a guarded C header with generated comments, `MACH_*` definitions, and predicate macros.

## State and Persistence Behavior
State exists only inside the awk process. The generated header is the persistent build artifact.

## Dependencies and Integration Points
It is invoked by `arch/sh/tools/Makefile` and depends on the format of `arch/sh/tools/mach-types`. Generated macros are included by SH platform code until per-board `sh_machtype` assignment replaces legacy placeholders.

## Risks
Rows with unexpected field counts are silently ignored, and machine names are inserted directly into macro names. Input naming mistakes therefore become missing or malformed compile-time predicates.

## Test Signals
Regenerate `include/generated/machtypes.h` from known input and inspect `CONFIG_*` gates, `MACH_*` values, lowercase predicate names, and header guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/tools/gen-mach-types -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sparc/Kbuild

## Purpose
This top-level SPARC Kbuild file selects architecture subdirectories for the kernel build.

## Important APIs, Types, and Functions
It adds `kernel/`, `mm/`, `math-emu/`, `net/`, and `crypto/` to `obj-y`, and adds `vdso/` only when `CONFIG_SPARC64` is enabled.

## Control Flow
Kbuild includes this file after architecture configuration; object-directory traversal follows the `obj-y` list.

## State and Persistence Behavior
There is no runtime state. Build state is the set of subdirectories compiled into the SPARC kernel.

## Dependencies and Integration Points
It depends on standard Kbuild object directory semantics and `CONFIG_SPARC64`. It connects the arch root to SPARC kernel, MM, math emulation, networking, crypto, and vDSO code.

## Risks
Omitting a directory silently drops architecture functionality. Adding `vdso/` to 32-bit builds would break because the included vDSO rules are SPARC64-specific.

## Test Signals
Build SPARC32 and SPARC64 defconfigs and confirm the expected subdirectories are visited, with `arch/sparc/vdso` only in 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sparc/Kconfig

## Purpose
This is the main SPARC architecture configuration file. It defines 32-bit versus 64-bit SPARC selection, architecture capabilities, CPU/SMP/memory options, boot command-line defaults, LEON/U-Boot support, bus options, PCI variants, compatibility mode, and compiler user flags.

## Important APIs, Types, and Functions
Key symbols are `64BIT`, `SPARC`, `SPARC32`, `SPARC64`, `MMU`, `HIGHMEM`, `PGTABLE_LEVELS`, `SMP`, `NR_CPUS`, `EMULATED_CMPXCHG`, `EARLYFB`, `HOTPLUG_CPU`, `US3_MC`, `NUMA`, `ARCH_FORCE_MAX_ORDER`, `CMDLINE_BOOL`, `CMDLINE`, `SUN_PM`, `SPARC_LED`, `SERIAL_CONSOLE`, `SPARC_LEON`, U-Boot address symbols, `SBUS`, `SUN_LDOMS`, `PCIC_PCI`, `LEON_PCI`, `SPARC_GRPCI1/2`, `SUN_OPENPROMFS`, `SPARC64_PCI`, `SPARC64_PCI_MSI`, `COMPAT`, `ARCH_CC_CAN_LINK`, and `ARCH_USERFLAGS`. It also selects many generic kernel capabilities used by common code.

## Control Flow
The `64BIT` choice derives from `ARCH=sparc64` by default, then `SPARC32` and `SPARC64` def_bool branches select their capability sets. Menus expose processor, memory, LEON boot, and bus options. Several symbols are internal helper gates for Makefiles rather than user-facing features.

## State and Persistence Behavior
The file persists selected build configuration in `.config`. Runtime behavior changes through compiled-in options: page size, SMP limits, PCI/LDOM support, compatibility ABI, power management, serial console defaults, and boot command line.

## Dependencies and Integration Points
It integrates with generic Kconfig files (`kernel/Kconfig.hz`, `kernel/power/Kconfig`, `drivers/cpufreq/Kconfig`, `drivers/sbus/char/Kconfig`) and feeds SPARC Makefiles, MM code, boot code, PCI, SBUS, crypto, vDSO, tracing, audit, perf, and compatibility subsystems.

## Risks
Capability selections are broad and cross-cutting. Incorrect 32/64-bit gating can produce incompatible compiler flags, page-table layout, or ABI exposure. `CMDLINE` can override PROM bootargs, and `EMULATED_CMPXCHG` on SPARC32 is explicitly not fully atomic, so lock-free assumptions are risky there.

## Test Signals
Run `olddefconfig` and build SPARC32, SPARC64, SMP, NUMA, LEON, PCI, and COMPAT configurations. Verify compiler flag tests for `ARCH_CC_CAN_LINK`, generated `.config` selections, boot logs for selected buses, and 32-bit user compatibility on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/Makefile

## Purpose
This architecture Makefile sets SPARC build flags, default defconfigs, linked libraries, boot targets, install hooks, generated headers, vDSO installation, packaged image path, and help text.

## Important APIs, Types, and Functions
It selects `sparc64_defconfig` or `sparc32_defconfig`, sets `CHECKFLAGS`, `KBUILD_LDFLAGS`, `BITS`, `UTS_MACHINE`, `KBUILD_CFLAGS`, and `KBUILD_AFLAGS`, and defines targets `image`, `zImage`, `uImage`, `tftpboot.img`, `vmlinux.aout`, `install`, and `archheaders`. It also defines `KBUILD_IMAGE := arch/sparc/boot/zImage`.

## Control Flow
Before configuration it keys off `ARCH`; after configuration it branches on `CONFIG_SPARC32`. SPARC32 builds use 32-bit v8, no-FPU, and assembler v8 flags. SPARC64 builds use 64-bit UltraSPARC, medlow code model, fixed global registers, undeclared-reg handling, optional mcount profiling, and UltraSPARC3 tuning when available. Boot targets delegate to `arch/sparc/boot`.

## State and Persistence Behavior
No runtime state exists. The file controls compiler/linker state and generated boot artifacts.

## Dependencies and Integration Points
It depends on Kbuild infrastructure, compiler option probing, `arch/sparc/prom`, `arch/sparc/lib`, optional power/video drivers, boot make rules, syscall header generation, and vDSO debug objects.

## Risks
SPARC ABI depends heavily on fixed global registers, no-FPU flags, linker emulation, and bitness. Wrong flags can produce unbootable kernels or corrupt register conventions. Boot target delegation assumes `vmlinux` is already linked.

## Test Signals
Build SPARC32 and SPARC64 defconfigs, inspect compiler/linker command lines, build each advertised image target, and run `make ARCH=sparc archheaders` plus vDSO install on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/boot/Makefile

## Purpose
This boot Makefile builds SPARC boot images, including raw images, compressed images, TFTP/install images, a.out images, and LEON U-Boot images.

## Important APIs, Types, and Functions
It declares host tool `piggyback`, targets `tftpboot.img`, `image`, `zImage`, `vmlinux.aout`, and optional `uImage`. Rules use `OBJCOPY`, `OBJDUMP`, `NM`, `ELFTOAOUT`, gzip, `piggyback`, and `mkimage` with `UIMAGE_LOADADDR` and `UIMAGE_ENTRYADDR`.

## Control Flow
The file strips or converts `vmlinux` into bootable forms. SPARC64 uses `elftoaout` for `vmlinux.aout`; SPARC32 copies a binary image. `zImage` compresses the raw image. `tftpboot.img` combines the a.out kernel, `System.map`, and optional initrd through `piggyback`. LEON builds `uImage` and `uImage.o` through U-Boot tooling.

## State and Persistence Behavior
It creates build artifacts under `arch/sparc/boot`. There is no runtime state in the Makefile itself.

## Dependencies and Integration Points
It integrates top-level `arch/sparc/Makefile` targets with PROM/a.out boot expectations, initrd embedding, U-Boot image creation, and the host `piggyback` utility.

## Risks
Boot image layout is sensitive to alignment, symbol addresses, and host tool availability. Incorrect `piggyback` input or U-Boot load/entry addresses can make an otherwise linked kernel unbootable.

## Test Signals
Build `image`, `zImage`, `tftpboot.img`, `vmlinux.aout`, and LEON `uImage` where configured. Verify file formats with `file`, expected headers, and bootloader acceptance under PROM/U-Boot/QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/sparc/boot/install.sh

## Purpose
This install helper copies a built SPARC kernel image into the installed boot path and optionally runs a system install hook.

## Important APIs, Types, and Functions
The script receives kernel version, image path, System.map path, and install directory arguments from Kbuild. It handles `INSTALLKERNEL` when present and otherwise copies the image to the target install directory.

## Control Flow
Kbuild invokes the script through `make install`. The script normalizes arguments, checks for an executable external installer, delegates when available, or performs a default copy workflow.

## State and Persistence Behavior
It mutates the filesystem under the requested install path. It has no runtime kernel state.

## Dependencies and Integration Points
It depends on shell utilities and the kernel build `install` convention. It integrates with distribution boot installation scripts and SPARC boot image naming.

## Risks
Wrong install paths or missing permissions can overwrite or fail to install the kernel image. Delegating to an external installer means behavior varies by distribution.

## Test Signals
Run `make ARCH=sparc install INSTALL_PATH=<tmp>` and verify image/System.map placement and successful external installer delegation when `INSTALLKERNEL` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/piggyback.c -->
# sources/distributed-fs/ceph-client/arch/sparc/boot/piggyback.c

## Purpose
`piggyback` is a host utility that modifies a SPARC a.out kernel image in place so it can carry an initial ramdisk for PROM/TFTP booting without NFS.

## Important APIs, Types, and Functions
Important helpers are `align()`, `ld2()`, `st4()`, `die()`, `usage()`, `start_line()`, `end_line()`, `get_start_end()`, and `get_hdrs_offset()`. `main()` accepts `bits vmlinux.aout System.map fs_img.gz`, verifies the a.out magic, finds `_start`/`_end`, locates the `HdrS` boot header, writes root/ramdisk metadata, updates SPARC64 a.out text/data/bss fields, and appends the initrd at an aligned offset.

## Control Flow
The tool parses the bitness, stats the ramdisk, scans `System.map` for `_start` and `_end`, opens the kernel image read-write, validates a.out magic, and locates the boot header either at the SPARC64 fixed offset or by decoding a branch target and searching backward for `HdrS`. It writes big-endian header fields, seeks to the aligned post-kernel payload offset, streams the ramdisk into the image, and closes both files.

## State and Persistence Behavior
The kernel image is modified in place. The utility stores no state outside the output image; all numeric fields are written big-endian because the image is SPARC-facing even when built on a little-endian host.

## Dependencies and Integration Points
It is built as a host program by `arch/sparc/boot/Makefile` and depends on a.out image layout, `System.map` symbol format, `HdrS` layout in SPARC boot assembly, page-size alignment conventions, and optional initrd images.

## Risks
Offset calculation is fragile: stale `System.map`, missing `HdrS`, wrong bitness, short reads, or older `elftoaout` output can corrupt the image. The tool modifies in place and only performs format sanity checks, so callers must provide a disposable boot artifact.

## Test Signals
Run on known SPARC32 and SPARC64 boot images with small initrd inputs. Verify a.out headers, embedded ramdisk size/address fields, appended payload offset, and successful PROM/TFTP boot or QEMU boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/piggyback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/Kconfig

## Purpose
This Kconfig file exposes SPARC64 crypto-opcode accelerated cipher modules.

## Important APIs, Types, and Functions
It defines `CRYPTO_AES_SPARC64` and `CRYPTO_CAMELLIA_SPARC64`, both dependent on `SPARC64`, `KERNEL_MODE_NEON`, and their generic cipher dependencies, and both selecting the matching crypto manager support.

## Control Flow
When enabled, the symbols cause the SPARC crypto Makefile to build AES or Camellia opcode glue and assembly. Runtime module init still checks hardware capability before registering algorithms.

## State and Persistence Behavior
It persists choices in `.config` and controls which modules or built-ins are compiled. Runtime availability depends on CPU features.

## Dependencies and Integration Points
It integrates with the kernel crypto API, SPARC64 opcode detection, and module autoload through OF device aliases.

## Risks
Building the module does not guarantee the processor exposes the opcode; init must return `-ENODEV` on unsupported hardware. Missing generic cipher dependencies would leave registered modes without shared crypto infrastructure.

## Test Signals
Build with AES and Camellia enabled as modules and built-ins. On hardware with and without crypto opcodes, verify module load success/failure, algorithm registration, and crypto selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/Makefile

## Purpose
This makefile maps SPARC crypto Kconfig symbols to accelerated crypto objects.

## Important APIs, Types, and Functions
`aes_sparc64-y` contains `aes_asm.o` and `aes_glue.o`; `camellia_sparc64-y` contains `camellia_asm.o` and `camellia_glue.o`. `obj-$(CONFIG_CRYPTO_AES_SPARC64)` and `obj-$(CONFIG_CRYPTO_CAMELLIA_SPARC64)` emit the corresponding modules/built-ins.

## Control Flow
Kbuild compiles the assembly and C glue together only when the matching config symbol is enabled.

## State and Persistence Behavior
No runtime state exists here; it controls build artifacts.

## Dependencies and Integration Points
It depends on Kbuild composite object naming and the crypto Kconfig symbols. It links opcode assembly entry points with crypto API glue.

## Risks
Object ordering and naming must match module names and extern declarations. Omitting either assembly or glue object breaks linkage.

## Test Signals
Build both crypto options as modules and built-ins, then run `modinfo`, load modules, and execute crypto selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/aes_glue.c -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/aes_glue.c

## Purpose
This file registers AES skcipher implementations accelerated by SPARC64 crypto opcodes for ECB, CBC, and CTR modes.

## Important APIs, Types, and Functions
`struct aes_ops` dispatches key loading and mode operations for 128/192/256-bit keys. `struct crypto_sparc64_aes_ctx` stores the expanded key, selected ops table, key length, and expanded-key length. Key and mode handlers include `aes_set_key_skcipher()`, `ecb_encrypt()`, `ecb_decrypt()`, `cbc_encrypt()`, `cbc_decrypt()`, `ctr_crypt_final()`, and `ctr_crypt()`. Module setup uses `sparc64_has_aes_opcode()`, `aes_sparc64_mod_init()`, and `aes_sparc64_mod_fini()`.

## Control Flow
`setkey` validates AES key length, chooses the ops table, expands the key, and records the expanded length. Mode functions walk scatterlists with `skcipher_walk_virt()`, load encrypt or decrypt keys into the SPARC floating-point/crypto register state, process full blocks through assembly, finish partial CTR tails with one ECB keystream block plus XOR, and clear FPRS with `fprs_write(0)`. Module init checks `sparc64_elf_hwcap` and ASR26 `CFR_AES` before registering skcipher algorithms.

## State and Persistence Behavior
Per-transform state is the expanded key in `crypto_sparc64_aes_ctx`; per-request state is the skcipher walk and IV. Hardware crypto/FPU register state is transient and explicitly cleared after operations. Module registration persists until unload.

## Dependencies and Integration Points
It depends on the kernel crypto skcipher API, generic AES constants, SPARC64 assembly routines, `fpumacro`, `opcodes`, `pstate`, ELF hardware capabilities, and `crop_devid.c` for module device-table aliasing.

## Risks
The code assumes opcode availability after init and relies on correct key-end pointer selection for decrypt operations. Failing to clear FPRS can leak/dirty floating-point state. CTR partial-block handling must increment the counter exactly once. Algorithm priority can shadow generic AES, so selftest failures would affect normal crypto users.

## Test Signals
Run crypto selftests for `ecb(aes)`, `cbc(aes)`, and `ctr(aes)` with 128/192/256-bit keys, scatter-gather splits, misaligned buffers, partial CTR lengths, and unsupported-hardware module load paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/aes_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_asm.S -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_asm.S

## Purpose
This assembly file implements SPARC64 opcode-accelerated Camellia key expansion and block/mode encryption routines.

## Important APIs, Types, and Functions
Exported entry points include `camellia_sparc64_key_expand`, `camellia_sparc64_crypt`, `camellia_sparc64_load_keys`, ECB helpers for 3 and 4 grand rounds, and CBC encrypt/decrypt helpers for 3 and 4 grand rounds. Major macros include `CAMELLIA_6ROUNDS`, `CAMELLIA_6ROUNDS_FL_FLI`, `ROTL128`, and opcode macros from `asm/opcodes.h`; `SIGMA` holds Camellia key-schedule constants.

## Control Flow
Key expansion loads the input key into VIS/FPU registers, derives intermediate keys using Camellia F/FL/FLI operations, handles 128-bit versus 192/256-bit schedules, writes encryption subkeys, and builds the decrypt schedule. Runtime encryption loads subkeys, chooses 3-grand-round paths for 128-bit keys and 4-grand-round paths for longer keys, then processes ECB or CBC blocks through hardware opcodes.

## State and Persistence Behavior
The file does not own persistent memory; callers pass key tables and buffers. It uses VIS/FPU registers transiently and follows the SPARC calling convention through `VISEntry`/related macros.

## Dependencies and Integration Points
It is linked with `camellia_glue.c`, depends on Linux linkage macros, SPARC crypto opcode definitions, and VIS assembly helpers. The C glue exposes these routines through the kernel crypto API.

## Risks
Assembly offset tables and key schedule layout must match `CAMELLIA_TABLE_BYTE_LEN` and C declarations exactly. Register clobbering, endian assumptions, or wrong 3/4 grand-round selection would produce silent cryptographic corruption. FPU/VIS state handling is architecture-sensitive.

## Test Signals
Run Camellia known-answer tests for 128/192/256-bit keys, ECB/CBC mode tests with multi-block and odd scatterlist boundaries, objdump symbol checks, and module unload/reload stress on SPARC64 crypto-opcode hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_glue.c -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_glue.c

## Purpose
This file registers Camellia cipher and skcipher implementations accelerated by SPARC64 Camellia opcodes.

## Important APIs, Types, and Functions
`struct camellia_sparc64_ctx` stores encryption and decryption key tables plus key length. Key setup uses `camellia_set_key()` and `camellia_set_key_skcipher()`. Single-block cipher APIs are `camellia_encrypt()` and `camellia_decrypt()`. Skcipher paths are `__ecb_crypt()`, `ecb_encrypt()`, `ecb_decrypt()`, `cbc_encrypt()`, and `cbc_decrypt()`. Module setup uses `sparc64_has_camellia_opcode()`, `camellia_sparc64_mod_init()`, and `camellia_sparc64_mod_fini()`.

## Control Flow
Key setup validates 16/24/32-byte keys and calls the assembly key expansion to fill encrypt/decrypt schedules. Cipher and skcipher paths choose encrypt or decrypt tables, select 3-grand-round assembly for 128-bit keys or 4-grand-round assembly for longer keys, walk request buffers, process full blocks, return leftovers to the skcipher walker, and clear FPRS. Module init gates registration on `HWCAP_SPARC_CRYPTO` plus ASR26 `CFR_CAMELLIA`, then registers both the single-block cipher and ECB/CBC skciphers.

## State and Persistence Behavior
Each crypto transform owns its key schedules. Request state is limited to buffer walkers and IVs. Hardware VIS/FPU state is transient and cleared after operations. Registered algorithms persist until module exit.

## Dependencies and Integration Points
It depends on the crypto API, SPARC64 Camellia assembly entry points, opcode capability bits, FPU state helpers, ELF hwcap, and `crop_devid.c` device-table aliasing.

## Risks
Algorithm registration must unwind correctly if skcipher registration fails after cipher registration. Key schedule length and assembly function selection must match key size. As with AES, stale FPU state or incorrect scatterlist remainder handling can affect unrelated kernel code or corrupt crypto output.

## Test Signals
Run crypto manager Camellia tests for cipher, `ecb(camellia)`, and `cbc(camellia)` with 128/192/256-bit keys, scatterlist splits, IV mutation checks, unsupported CPU load failure, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/crop_devid.c -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/crop_devid.c

## Purpose
This small C fragment supplies Open Firmware module device IDs for SPARC crypto-opcode modules.

## Important APIs, Types, and Functions
It defines `crypto_opcode_match[]` with compatible string `sun4v-cwq` and exports it through `MODULE_DEVICE_TABLE(of, crypto_opcode_match)`.

## Control Flow
The file is included directly by AES and Camellia glue sources, so each module receives the same OF device table. Module autoload can then match firmware nodes advertising the crypto work queue/opcode capability.

## State and Persistence Behavior
The only state is a constant device-id table compiled into the module metadata.

## Dependencies and Integration Points
It depends on Linux OF module-device-table support and is integrated by textual inclusion from crypto glue files.

## Risks
Because it is included rather than linked separately, changes affect multiple modules. An incorrect compatible string would prevent module autoload even though manual loading could still work.

## Test Signals
Check `modinfo` aliases for AES and Camellia modules and verify OF-based autoload on systems exposing `sun4v-cwq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/crop_devid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/Kbuild

## Purpose
This exported-headers Kbuild file controls which SPARC asm headers are generated or exposed to userspace.

## Important APIs, Types, and Functions
It uses Kbuild `generic-y`/`generated-y` style header lists for asm include handling. The file is intentionally small but affects `make headers_install` and generated asm offsets.

## Control Flow
Kbuild reads this file while preparing architecture headers and decides whether a header is provided by SPARC, generated, or inherited from generic asm.

## State and Persistence Behavior
No runtime state exists. The persistent outputs are installed/generated headers in the build tree.

## Dependencies and Integration Points
It integrates `arch/sparc/include/asm` with generic header generation and userspace header export.

## Risks
Misclassifying a header can break userspace header installation or cause kernel code to include a missing generated file.

## Test Signals
Run `make ARCH=sparc headers_install` and `make ARCH=sparc archheaders`; verify generated asm headers and installed UAPI completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/adi.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/adi.h

## Purpose
This header is the SPARC public `ADI wrapper` dispatcher. It selects the SPARC64 Application Data Integrity declarations when compiling 64-bit SPARC code while presenting the stable `<asm/adi.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/adi.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/adi.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/adi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/adi_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/adi_64.h

## Purpose
This header declares SPARC64 Application Data Integrity capability and configuration state.

## Important APIs, Types, and Functions
It defines `struct adi_caps` and `struct adi_config`, declares global `adi_state`, and provides `adi_capable()`, `adi_blksize()`, `adi_nbits()`, plus `mdesc_adi_init()`.

## Control Flow
Machine-description probing initializes `adi_state`; later callers query inline helpers to decide whether ADI is available and what block/tag geometry applies.

## State and Persistence Behavior
`adi_state` persists global hardware capability information after boot. The inline helpers are read-only views of that state.

## Dependencies and Integration Points
It depends on SPARC64 machine descriptions and Linux type definitions. It integrates with memory tagging/ADI syscall and ELF hardware capability exposure.

## Risks
Incorrect ADI geometry can make tag operations address the wrong granularity. Callers must check `adi_capable()` before using ADI-specific paths.

## Test Signals
Boot ADI-capable and non-ADI SPARC64 systems, verify machine-description parsing, ELF HWCAP_ADI exposure, and ADI userspace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/adi_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/apb.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/apb.h

## Purpose
This header describes SPARC APB (Advanced PCI Bridge) register layout used by platform PCI code.

## Important APIs, Types, and Functions
It defines APB register offsets and bit fields for bridge control/status, interrupt, and bus-facing configuration.

## Control Flow
Platform PCI/probing code includes the header and uses the constants when mapping and programming APB registers.

## State and Persistence Behavior
The header has no state; hardware register writes by users of these constants persist in the bridge until reset or reprogramming.

## Dependencies and Integration Points
It integrates with SPARC PCI host bridge support and low-level I/O accessors.

## Risks
Wrong masks or offsets can misconfigure PCI routing or interrupt behavior. Because this is hardware-facing, errors may appear as device enumeration failures.

## Test Signals
Boot APB-equipped systems, enumerate PCI devices, exercise interrupts and DMA, and compare register dumps against platform documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/apb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm-offsets.h

## Purpose
This placeholder header represents generated assembly offsets for SPARC.

## Important APIs, Types, and Functions
The file itself contains only the generated-header include surface; actual offsets are produced by the architecture build from asm-offset generation sources.

## Control Flow
Assembly files include this path after Kbuild has generated the concrete offsets in the build output tree.

## State and Persistence Behavior
No runtime state exists. Build-time generated offsets persist in the generated include directory.

## Dependencies and Integration Points
It integrates assembly code with C structure layout constants generated during the build.

## Risks
Including it before generation or with stale generated offsets can break assembly/C ABI alignment.

## Test Signals
Run `make ARCH=sparc prepare` and verify generated asm offsets exist and assembly files compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm-prototypes.h

## Purpose
This header declares C prototypes used by SPARC assembly and kallsyms/modversion tooling.

## Important APIs, Types, and Functions
It includes prototypes for low-level routines referenced from assembly, including checksum, memory/string, user access, and trap/interrupt helper surfaces as configured.

## Control Flow
The compiler includes it while building assembly prototype metadata, allowing symbol type checking and modversion generation for assembly-visible functions.

## State and Persistence Behavior
There is no state; it is a compile-time contract file.

## Dependencies and Integration Points
It integrates SPARC assembly routines with C declarations and generic asm-prototypes infrastructure.

## Risks
Prototype drift causes link-time or runtime ABI bugs because assembly callers do not get normal C type checking.

## Test Signals
Build with `CONFIG_MODVERSIONS` and sparse/prototype warnings; verify no assembly symbol prototype mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm.h

## Purpose
This header provides SPARC assembly convenience macros for symbol naming, section handling, and low-level assembly source consistency.

## Important APIs, Types, and Functions
It defines assembler-facing macros used by SPARC `.S` files, including common symbol and alignment conventions around C-visible entry points.

## Control Flow
Assembly sources include it before declaring routines or data so that the same conventions are used across boot, trap, crypto, and MM assembly.

## State and Persistence Behavior
No runtime state exists; it shapes assembled object metadata.

## Dependencies and Integration Points
It depends on GNU assembler conventions and integrates with Linux linkage macros and SPARC assembly files.

## Risks
Changing symbol or alignment macros can silently alter ABI, exception table layout, or linker-visible names.

## Test Signals
Full SPARC assembly build and objdump inspection of exported symbols, alignment, and section placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asmmacro.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/asmmacro.h

## Purpose
This header defines SPARC assembly macros for saving/restoring register windows and common low-level instruction sequences.

## Important APIs, Types, and Functions
The macros are consumed by trap, syscall, context-switch, and low-level entry assembly. They encode SPARC register-window and stack-frame assumptions.

## Control Flow
Assembly entry paths expand these macros inline at build time; there is no callable C control flow.

## State and Persistence Behavior
Runtime effects are the register and stack changes performed by expanded assembly. The header itself stores no state.

## Dependencies and Integration Points
It integrates with SPARC trap tables, window-management code, thread structures, and assembler constants.

## Risks
Register-window handling is fragile; a clobber or stack offset error can corrupt traps, syscalls, or context switches.

## Test Signals
Boot SPARC32/SPARC64 kernels, exercise syscall/trap paths, run signal and context-switch stress, and inspect generated assembly for expected save/restore sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asmmacro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic.h

## Purpose
This header is the SPARC public `atomic wrapper` dispatcher. It selects 32-bit or 64-bit atomic operation implementations while presenting the stable `<asm/atomic.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/atomic.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/atomic.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic_32.h

## Purpose
This header implements SPARC32 atomic integer operations using architecture-supported instructions and fallback locking/emulation where needed.

## Important APIs, Types, and Functions
It provides `arch_atomic_*` style add/sub/inc/dec/read/set operations and return/fetch variants, with generic `atomic64` selected elsewhere for SPARC32.

## Control Flow
Atomic operations execute inline instruction sequences or helper calls to update memory and return old/new values under the required ordering assumptions.

## State and Persistence Behavior
The persistent state is the target atomic variable. No global state is owned by the header.

## Dependencies and Integration Points
It integrates with Linux `atomic_t`, scheduler, refcounting, locks, and generic atomic APIs on SPARC32.

## Risks
SPARC32 lacks some modern atomic primitives, so emulation and memory ordering must be treated carefully. Incorrect barriers can break lock-free code.

## Test Signals
Run atomic/refcount/lib tests, locktorture, concurrent module load/unload, and SMP SPARC32 stress when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic_64.h

## Purpose
This header implements SPARC64 atomic operations using native compare-and-swap and arithmetic primitives.

## Important APIs, Types, and Functions
It provides `arch_atomic_*` and `arch_atomic64_*` operations, including add/sub/fetch/return/cmpxchg-style helpers with SPARC64 memory-ordering semantics.

## Control Flow
Most operations are inline loops around native atomic instructions and barriers, retrying until the memory update succeeds.

## State and Persistence Behavior
Only the target atomic variables are changed; no persistent global state is held by the header.

## Dependencies and Integration Points
It integrates with generic Linux atomic APIs, queued locks, refcounts, percpu counters, and scheduler synchronization on SPARC64.

## Risks
CAS loop correctness and barrier placement are critical. A wrong constraint or missing memory clobber can create rare SMP data races.

## Test Signals
Run atomic64 selftests, locktorture, refcount tests, KCSAN-style race detection where possible, and SMP stress on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio.h

## Purpose
This header is the SPARC public `AUXIO wrapper` dispatcher. It declares the shared `auxio_register` and selects the 32-bit or 64-bit AUXIO register API while presenting the stable `<asm/auxio.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/auxio.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/auxio.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_32.h

## Purpose
This header defines SPARC32 AUXIO register bits and helper macros for floppy, link-test, LED, and power-control functions.

## Important APIs, Types, and Functions
It defines AUXIO bit masks such as `AUXIO_FLPY_DENS`, `AUXIO_FLPY_DCHG`, `AUXIO_FLPY_DSEL`, `AUXIO_LINK_TEST`, `AUXIO_FLPY_TCNT`, `AUXIO_FLPY_EJCT`, `AUXIO_LED`, and power bits. It declares `set_auxio()`, `get_auxio()`, and `auxio_power_register`, and provides `auxio_set_lte()`/`auxio_set_led()` macros.

## Control Flow
Drivers call the helpers/macros to set or clear AUXIO bits. The macros convert high-level on/off requests into `set_auxio(bits_on, bits_off)` operations.

## State and Persistence Behavior
State lives in platform AUXIO hardware registers. Writes persist until hardware changes or later writes; the header itself stores no state.

## Dependencies and Integration Points
It depends on SPARC32 virtual-address constants and I/O types. It integrates with floppy, LED, link-test, and power-management drivers.

## Risks
AUXIO registers contain write-one/reserved bits and platform-specific interpretations, so incorrect masks can affect floppy motor control, LEDs, or power state.

## Test Signals
On sun4m/sun4c-style systems, test LED toggling, floppy operations, link-test controls, and power-failure/off register handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_64.h

## Purpose
This header defines SPARC64 AUXIO and PCIO auxiliary register bits plus helper APIs for LED and link-test control.

## Important APIs, Types, and Functions
It defines AUX1/AUX2/PCIO bit masks for floppy density, link test, monitor/mouse mux, terminal count, LED, power fail, and power off. It declares `auxio_set_lte()` and `auxio_set_led()`.

## Control Flow
SPARC64 platform code maps the relevant auxiliary registers and driver code calls the declared helpers to update specific bits.

## State and Persistence Behavior
Persistent state is in the hardware AUXIO/PCIO registers. The header only describes the bit layout.

## Dependencies and Integration Points
It integrates with SPARC64 platform initialization, LED support, network link-test behavior, floppy support, and power-management paths.

## Risks
Different systems expose different AUXIO variants; using the wrong mask can manipulate unrelated platform signals.

## Test Signals
Boot SPARC64 platforms with AUXIO/PCIO, toggle LEDs/link-test where supported, and validate power-fail/off register handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/backoff.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/backoff.h

## Purpose
This header provides SPARC64 spin/backoff helpers for tight retry loops.

## Important APIs, Types, and Functions
It defines backoff data and macros/functions that perform exponential or bounded delay using SPARC pause/backoff instructions when available.

## Control Flow
Lock or atomic retry loops initialize a backoff state, execute a pause/delay sequence after failed attempts, and increase the delay up to a cap.

## State and Persistence Behavior
Backoff state is local to the caller's loop. No global state is persisted.

## Dependencies and Integration Points
It integrates with qspinlock/qrwlock, atomic loops, and SPARC64 CPU feature support for pause-like instructions.

## Risks
Too little backoff can waste CPU and interconnect bandwidth; too much can harm latency. Inline assembly constraints must not clobber lock state.

## Test Signals
Run locktorture, qspinlock stress, and perf measurements under high contention on SPARC64 SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/backoff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/barrier.h

## Purpose
This header is the SPARC public `barrier wrapper` dispatcher. It selects SPARC32 or SPARC64 memory-barrier definitions while presenting the stable `<asm/barrier.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/barrier.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/barrier.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/barrier_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/barrier_32.h

## Purpose
This header defines SPARC32 memory barrier primitives.

## Important APIs, Types, and Functions
It maps generic barrier APIs to SPARC32 instructions such as `stbar` or compiler barriers as appropriate.

## Control Flow
Barrier macros expand inline at memory-ordering points used by locks, atomics, device I/O, and SMP synchronization.

## State and Persistence Behavior
Barriers do not store state; they constrain ordering of surrounding memory operations.

## Dependencies and Integration Points
It integrates with Linux memory model APIs, atomic operations, locks, and I/O accessors.

## Risks
Under-strength barriers can create data races or device ordering bugs; over-strength barriers degrade performance.

## Test Signals
Run LKMM litmus coverage where possible, locktorture, driver I/O smoke tests, and SMP boot stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/barrier_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/barrier_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/barrier_64.h

## Purpose
This header defines SPARC64 memory barrier and acquire/release primitives.

## Important APIs, Types, and Functions
It maps generic Linux barriers to SPARC64 `membar` variants and related compiler barriers for load/store, SMP, DMA, and device ordering.

## Control Flow
The macros expand inline at synchronization sites and enforce the requested ordering class.

## State and Persistence Behavior
No state is stored. Runtime effect is ordering of CPU memory transactions.

## Dependencies and Integration Points
It integrates with the Linux memory model, atomics, locks, futexes, queued spinlocks, DMA, and MMU updates.

## Risks
SPARC64 has nuanced memory-ordering bits; using the wrong `membar` mask can leave rare SMP or I/O races.

## Test Signals
Run LKMM/litmus tests, locktorture, RCU torture, high-rate futex tests, and DMA driver stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/barrier_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bbc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bbc.h

## Purpose
This header describes the BootBus Controller used on SPARC systems.

## Important APIs, Types, and Functions
It defines register offsets, control/status bit masks, and structures/constants for BBC register blocks used by platform code.

## Control Flow
Platform initialization and error/power-management paths map BBC registers and use these constants to inspect or program hardware.

## State and Persistence Behavior
State lives in the BBC hardware registers. Header constants have no state.

## Dependencies and Integration Points
It integrates with SPARC64 platform support, environmental monitoring, reset/power control, and low-level bus accessors.

## Risks
Incorrect bit definitions can break platform management or acknowledge the wrong hardware status.

## Test Signals
Boot BBC-equipped machines, inspect register dumps, exercise power/reset/environmental paths, and verify no unexpected bus errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bbc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitext.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitext.h

## Purpose
This header declares a bitmap extent allocator interface used by SPARC memory-management code.

## Important APIs, Types, and Functions
It defines the bitext map structure and prototypes for allocating/freeing/searching bit extents.

## Control Flow
Callers initialize a bitmap extent area, request contiguous bit ranges, and release ranges when mappings/resources are freed.

## State and Persistence Behavior
Persistent allocator state is the caller-owned bitmap/metadata. The header itself only declares the interface.

## Dependencies and Integration Points
It integrates with SPARC MM/resource allocation code that needs compact bitmap extent tracking.

## Risks
Off-by-one range handling can leak or double-allocate scarce architecture resources.

## Test Signals
Exercise allocator users under allocation/free churn, with boundary-size requests and full-map exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops.h

## Purpose
This header is the SPARC public `bit operations wrapper` dispatcher. It selects SPARC32 or SPARC64 bit-operation primitives while presenting the stable `<asm/bitops.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/bitops.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/bitops.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_32.h

## Purpose
This header implements SPARC32 bit operations used by generic kernel code.

## Important APIs, Types, and Functions
It provides set/clear/change/test bit operations and scanning helpers, with endian-aware numbering and atomic variants where supported.

## Control Flow
Inline helpers compute word/bit locations and issue the required load/store or atomic sequences.

## State and Persistence Behavior
Only caller-provided bitmaps are mutated. No global state exists.

## Dependencies and Integration Points
It backs Linux bitmap APIs, scheduler flags, page flags, filesystems, and driver bitmaps on SPARC32.

## Risks
Bit numbering and endianness must match generic expectations. Non-atomic helpers must not be used where atomicity is required.

## Test Signals
Run bitmap tests, page flag stress, filesystem mount tests, and SMP bit-operation tests if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_64.h

## Purpose
This header implements SPARC64 bit operations and optimized scanning helpers.

## Important APIs, Types, and Functions
It provides atomic and non-atomic bit set/clear/change/test helpers plus `ffz`/find-bit style primitives, using SPARC64 word operations.

## Control Flow
Helpers calculate the target word, apply masks, and use atomic primitives where required.

## State and Persistence Behavior
State is limited to caller-owned bitmaps.

## Dependencies and Integration Points
It integrates with generic bitops, page flags, cpumasks, nodemasks, locks, and driver bitmaps.

## Risks
Endian bit numbering, alignment, and memory ordering are the main correctness hazards.

## Test Signals
Run lib/bitmap tests, cpumask/nodemask smoke tests, lock bitops users, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/btext.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/btext.h

## Purpose
This header declares early boot text-console discovery for SPARC.

## Important APIs, Types, and Functions
It declares `btext_find_display()`.

## Control Flow
Early boot code calls the function to locate a display usable for boot text output.

## State and Persistence Behavior
The header has no state; the implementation may initialize early console/display state.

## Dependencies and Integration Points
It integrates with SPARC boot console and framebuffer discovery.

## Risks
Incorrect declaration would break early console linkage; display discovery failures reduce boot diagnostics.

## Test Signals
Boot with framebuffer console enabled and verify early boot text appears on supported displays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/btext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bug.h

## Purpose
This header defines SPARC-specific BUG/WARN trap encoding and metadata support.

## Important APIs, Types, and Functions
It supplies architecture hooks for `BUG()`, warning traps, and bug table entries, integrating trap instruction encodings with generic bug handling.

## Control Flow
When a BUG/WARN site executes, SPARC trap handling decodes the instruction/table metadata and routes to generic bug reporting.

## State and Persistence Behavior
Bug table metadata is compiled into the kernel. Runtime state is limited to warning reporting and oops handling.

## Dependencies and Integration Points
It integrates with generic `asm-generic/bug.h`, exception handling, module bug tables, and debug options.

## Risks
Wrong trap encoding or table layout can turn warnings into illegal instructions without useful diagnostics.

## Test Signals
Build with `CONFIG_BUG`/verbose bug reporting, trigger WARN/BUG test paths, and verify file/line reporting for built-in and module code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cache.h

## Purpose
This header defines SPARC cache-line sizing and cache-alignment constants.

## Important APIs, Types, and Functions
It defines `ARCH_SLAB_MINALIGN`, `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `SMP_CACHE_BYTES_SHIFT`, `SMP_CACHE_BYTES`, and `__read_mostly` section placement.

## Control Flow
The values are consumed at compile time by allocators, per-CPU data, cacheline alignment annotations, and linker placement.

## State and Persistence Behavior
No runtime state exists; constants shape object layout and allocation alignment.

## Dependencies and Integration Points
It integrates with slab/slub, SMP cacheline padding, linker sections, and architecture cache maintenance.

## Risks
Wrong cacheline sizes can cause false sharing or insufficient DMA/cache alignment.

## Test Signals
Inspect built object layout, run slab debug, SMP performance smoke tests, and cache-alias sensitive workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush.h

## Purpose
This header is the SPARC public `cache flush wrapper` dispatcher. It defines the common `flushi()` instruction helper and selects 32-bit or 64-bit cache flush APIs while presenting the stable `<asm/cacheflush.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/cacheflush.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/cacheflush.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_32.h

## Purpose
This header provides SPARC32 cache flush APIs for MM, DMA, signal, and user-page coherency.

## Important APIs, Types, and Functions
It maps generic flush calls to `BTFIXUP_CALL` hooks, declares `sparc_flush_page_to_ram()`, `sparc_flush_folio_to_ram()`, `flush_user_windows()`, `kill_user_windows()`, and `flushw_all()`, and defines user-page copy helpers that flush copied executable data.

## Control Flow
MM code invokes flush macros during mapping changes, page copying, vmap/vunmap, and DMA preparation. Runtime-fixed function pointers select CPU-specific flush implementations.

## State and Persistence Behavior
No persistent C state is owned here, but operations alter CPU caches and register-window state.

## Dependencies and Integration Points
It depends on SPARC32 cache/TLB fixups, `struct page`/`folio`, and generic MM cacheflush APIs.

## Risks
Missing flushes can expose stale instructions/data, especially with executable user mappings and virtually indexed caches. Overbroad `flush_cache_all()` hurts performance.

## Test Signals
Run fork/exec, signal trampoline, self-modifying code, DMA, vmap/vunmap, and CPU-specific SPARC32 boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_64.h

## Purpose
This header defines SPARC64 cache and instruction-flush interfaces.

## Important APIs, Types, and Functions
It declares/defines `flush_cache_*`, `flush_icache_range`, page/folio dcache flush hooks, user-page copy helpers, and SPARC64-specific flush routines used by MM and text modification.

## Control Flow
Generic MM calls these hooks when mappings change, pages are copied, executable memory is updated, or vmalloc areas are created/removed.

## State and Persistence Behavior
Operations mutate hardware cache state only. No persistent header-owned state exists.

## Dependencies and Integration Points
It integrates with SPARC64 MMU/cache code, executable mappings, module loading, BPF/ftrace text patching, and DMA coherency.

## Risks
Instruction/data cache coherency is critical for text patching and user executable mappings. Incomplete flushing causes stale instruction execution.

## Test Signals
Run module load/unload, ftrace/BPF text modification, JIT/self-modifying code tests, and mmap executable write/execute coherency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cachetlb_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cachetlb_32.h

## Purpose
This header declares SPARC32 cache/TLB runtime fixup call sites.

## Important APIs, Types, and Functions
It defines `BTFIXUPDEF_CALL` declarations for cache and TLB operations selected for the active SPARC32 CPU/MMU implementation.

## Control Flow
Boot-time CPU/MMU probing patches or selects the concrete functions; later flush macros call through the fixed-up targets.

## State and Persistence Behavior
Persistent state is the runtime-selected fixup table or patched call sequence. The header itself has no state.

## Dependencies and Integration Points
It integrates SPARC32 cacheflush/tlbflush headers with CPU-specific assembly implementations.

## Risks
A wrong fixup target makes all subsequent MM cache/TLB maintenance incorrect.

## Test Signals
Boot representative SPARC32 CPU families and exercise mapping changes, context switches, and cache flush paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cachetlb_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cachetype.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cachetype.h

## Purpose
This header exposes SPARC cache type information.

## Important APIs, Types, and Functions
It defines cache-type identifiers and/or declarations used to describe the active cache implementation.

## Control Flow
CPU probing initializes cache type elsewhere; callers compare against these constants to choose maintenance behavior.

## State and Persistence Behavior
The header has no state; cache-type variables live in CPU/platform code.

## Dependencies and Integration Points
It integrates CPU detection, cache maintenance, and platform-specific MM behavior.

## Risks
Incorrect cache type classification leads to wrong flush strategies.

## Test Signals
Boot varied SPARC systems and verify detected cache type matches expected CPU family and flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cachetype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/chafsr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/chafsr.h

## Purpose
This header defines UltraSPARC Cheetah/Cheetah+/Jalapeno asynchronous fault status register bits.

## Important APIs, Types, and Functions
It defines sticky error bits such as `CHAFSR_PERR`, `CHAFSR_IERR`, `CHAFSR_UE`, `CHAFSR_CE`, Cheetah+ additions, Jalapeno-specific `JPAFSR_*` fields, syndrome masks/shifts, and aggregate masks `CHAFSR_ERRORS`, `CHPAFSR_ERRORS`, and `JPAFSR_ERRORS`.

## Control Flow
Trap and error-handling code reads AFSR/AFAR, masks with these definitions, reports error classes, and writes one bits back to clear sticky status before re-enabling interrupts.

## State and Persistence Behavior
State is in CPU fault-status registers. Bits are sticky and must be explicitly cleared; syndrome/address capture remains frozen until the corresponding logged bit is cleared.

## Dependencies and Integration Points
It integrates with SPARC64 trap handlers, EDAC/memory-controller diagnostics, machine check reporting, and platform-specific CPU error code.

## Risks
Clearing the wrong bit can lose diagnostic evidence or unlock AFAR/syndrome capture too early. Failing to clear disrupting-trap bits can retrigger the same trap.

## Test Signals
Use fault injection or platform error logs, verify decoded error names/syndromes, and confirm handlers clear AFSR without repeated traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/chafsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/checksum.h

## Purpose
This header is the SPARC public `checksum wrapper` dispatcher. It selects 32-bit or 64-bit IP checksum implementations while presenting the stable `<asm/checksum.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/checksum.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/checksum.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/checksum_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/checksum_32.h

## Purpose
This SPARC architecture header defines low-level constants, declarations, or ABI hooks for `checksum_32.h`. It is part of the architecture support surface consumed by platform, MM, interrupt, driver, or userspace-ABI code.

## Important APIs, Types, and Functions
The file's important surface is its exported macros, structure declarations, and prototypes. These encode SPARC-specific register layouts, calling conventions, feature flags, or subsystem hooks rather than standalone algorithms.

## Control Flow
Most behavior is compile-time: including code uses the definitions to build the correct instruction sequences, hardware accesses, or ABI layouts. Runtime control flow occurs in the implementation files that consume these declarations.

## State and Persistence Behavior
The header owns no independent state. Any persistent state is held in CPU/device registers, page tables, per-CPU data, userspace ABI structures, or subsystem objects manipulated by its users.

## Dependencies and Integration Points
It integrates SPARC architecture code with generic Linux subsystems and nearby SPARC implementation files. Include ordering, bit layout, and structure compatibility are the key contracts.

## Risks
Because this is low-level architecture surface, small changes to masks, offsets, types, or prototypes can break boot, traps, device access, userspace ABI, or SMP synchronization.

## Test Signals
At minimum, build SPARC32 and/or SPARC64 configurations that include this header. Stronger signals are boot tests and subsystem-specific stress for the consumers of `checksum_32.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/checksum_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/checksum_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/checksum_64.h

## Purpose
This SPARC architecture header defines low-level constants, declarations, or ABI hooks for `checksum_64.h`. It is part of the architecture support surface consumed by platform, MM, interrupt, driver, or userspace-ABI code.

## Important APIs, Types, and Functions
The file's important surface is its exported macros, structure declarations, and prototypes. These encode SPARC-specific register layouts, calling conventions, feature flags, or subsystem hooks rather than standalone algorithms.

## Control Flow
Most behavior is compile-time: including code uses the definitions to build the correct instruction sequences, hardware accesses, or ABI layouts. Runtime control flow occurs in the implementation files that consume these declarations.

## State and Persistence Behavior
The header owns no independent state. Any persistent state is held in CPU/device registers, page tables, per-CPU data, userspace ABI structures, or subsystem objects manipulated by its users.

## Dependencies and Integration Points
It integrates SPARC architecture code with generic Linux subsystems and nearby SPARC implementation files. Include ordering, bit layout, and structure compatibility are the key contracts.

## Risks
Because this is low-level architecture surface, small changes to masks, offsets, types, or prototypes can break boot, traps, device access, userspace ABI, or SMP synchronization.

## Test Signals
At minimum, build SPARC32 and/or SPARC64 configurations that include this header. Stronger signals are boot tests and subsystem-specific stress for the consumers of `checksum_64.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/checksum_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/chmctrl.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/chmctrl.h

## Purpose
This header describes UltraSPARC Cheetah memory-controller timing, decode, and address-control registers.

## Important APIs, Types, and Functions
It defines register offsets `CHMCTRL_TCTRL*`, `CHMCTRL_DECODE*`, `CHMCTRL_MACTRL`, timing masks/shifts for SDRAM control, refresh, bank presence, read/write delays, decode valid/match/mask fields, physical-address extraction, and memory-address control/interleave fields.

## Control Flow
Memory-controller code uses these constants to decode configured banks, report errors, or program controller timing during low-level platform setup.

## State and Persistence Behavior
State lives in memory-controller registers. Header constants are stateless; writes by users persist until reset/reprogramming.

## Dependencies and Integration Points
It integrates with UltraSPARC-III memory-controller driver/support and error-reporting paths.

## Risks
The definitions are hardware-critical; incorrect masks or shifts can misdecode physical banks or corrupt timing if used for writes. The `TCTRL4_RDWR_RD_PI_MORE_DLY` literal should be treated cautiously because malformed constants here would break compilation or decoding.

## Test Signals
Build SPARC64 with memory-controller support, read register dumps on US3 systems, and validate decoded bank/timing information against firmware/platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/chmctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/clock.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/clock.h

## Purpose
This header declares SPARC clock initialization interfaces.

## Important APIs, Types, and Functions
It provides prototypes used by platform timer/clock code to initialize or register architecture clocks.

## Control Flow
Boot-time timekeeping code calls the declared routines during clocksource/clockevent setup.

## State and Persistence Behavior
The header owns no state; implementations initialize persistent clocksource/clockevent state elsewhere.

## Dependencies and Integration Points
It integrates with SPARC timekeeping, Open Firmware/platform discovery, and generic clocksource code.

## Risks
Prototype drift can break early boot timekeeping. Incorrect integration causes timer interrupt or scheduler-clock failures.

## Test Signals
Boot with clocksource debug, verify timer interrupts, monotonic time, and scheduler tick behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/clocksource.h

## Purpose
This header provides SPARC clocksource declarations for generic timekeeping.

## Important APIs, Types, and Functions
It exposes the architecture clocksource registration surface used by SPARC timer code.

## Control Flow
SPARC timer initialization registers the active clocksource through generic timekeeping APIs.

## State and Persistence Behavior
No header-owned state; registered clocksources persist in generic timekeeping state.

## Dependencies and Integration Points
It integrates with Linux clocksource and SPARC timer hardware.

## Risks
Missing declarations can break architecture timer builds; incorrect clocksource setup produces time drift.

## Test Signals
Boot and check `/sys/devices/system/clocksource`, timekeeping stability, and timer interrupt accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg.h

## Purpose
This header is the SPARC public `compare-exchange wrapper` dispatcher. It selects SPARC32 emulated or SPARC64 native compare/exchange helpers while presenting the stable `<asm/cmpxchg.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/cmpxchg.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/cmpxchg.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_32.h

## Purpose
This header supplies SPARC32 compare/exchange and exchange helpers, including emulated behavior for CPUs without native CAS.

## Important APIs, Types, and Functions
It provides `arch_xchg`, `arch_cmpxchg`, and size-specific helpers used by atomics and locks. `CONFIG_EMULATED_CMPXCHG` reflects the architectural limitation that SPARC32 emulation is not completely atomic.

## Control Flow
Callers invoke inline helpers; the implementation performs supported atomic exchange sequences or emulated compare/update paths.

## State and Persistence Behavior
Only caller-provided memory is updated. No header-owned state exists.

## Dependencies and Integration Points
It integrates with atomic operations, futexes, locks, and generic cmpxchg APIs on SPARC32.

## Risks
Code assuming fully atomic CAS can be unsafe on SPARC32. Size handling and alignment constraints must match generic expectations.

## Test Signals
Run cmpxchg/atomic selftests, futex stress, locktorture, and review code paths gated by `EMULATED_CMPXCHG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_64.h

## Purpose
This header implements SPARC64 native exchange and compare/exchange operations.

## Important APIs, Types, and Functions
It provides size-specific `xchg`/`cmpxchg` helpers, including 64-bit CAS-backed loops and memory-ordering wrappers used by generic atomics.

## Control Flow
Inline assembly attempts the atomic operation and returns the observed or exchanged value, retrying when needed for compound operations.

## State and Persistence Behavior
Only the target memory location changes.

## Dependencies and Integration Points
It underpins atomic APIs, queued locks, refcounts, futexes, and lock-free kernel code on SPARC64.

## Risks
Inline assembly constraints, alignment, and memory barriers are correctness-critical on SMP.

## Test Signals
Run atomic/cmpxchg selftests, qspinlock stress, futex tests, and SMP contention workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat.h

## Purpose
This header defines SPARC64 32-bit compatibility ABI types and helpers.

## Important APIs, Types, and Functions
It defines compat register, pointer, time, stat, signal, IPC, and syscall-layout types/macros used when a SPARC64 kernel runs 32-bit SPARC user programs.

## Control Flow
Compat syscall entry and data marshaling code use these definitions to translate 32-bit userspace structures to native kernel representations.

## State and Persistence Behavior
No state is owned here. It defines ABI layouts that persist as user/kernel contract.

## Dependencies and Integration Points
It integrates with generic compat syscalls, ELF compat loading, signal delivery, ptrace, IPC, and filesystem ioctl translation.

## Risks
ABI layout mistakes break 32-bit userspace or corrupt copied structures. Alignment and big-endian field order are especially important.

## Test Signals
Run 32-bit userspace on SPARC64, including signals, ptrace, stat, IPC, time, and ioctl-heavy programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat_signal.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat_signal.h

## Purpose
This header defines SPARC compat signal handling glue.

## Important APIs, Types, and Functions
It provides compat signal stack/context type declarations and helpers needed by SPARC64 when delivering signals to 32-bit tasks.

## Control Flow
Signal setup and return paths use these definitions to build and restore the 32-bit signal frame.

## State and Persistence Behavior
State is in the user signal frame and task registers; the header has none.

## Dependencies and Integration Points
It integrates with `compat.h`, signal delivery, ptrace, and ELF personality handling.

## Risks
Frame layout drift breaks signal return and can corrupt user registers.

## Test Signals
Run 32-bit signal tests on SPARC64, including alternate stacks, SA_SIGINFO, nested signals, and ptrace signal injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat_signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/contregs.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/contregs.h

## Purpose
This header defines SPARC32 memory-management control register constants.

## Important APIs, Types, and Functions
It provides masks and values for context, system, and MMU control registers used by low-level SRMMU code.

## Control Flow
MMU setup and context-switch assembly/C code read or write these registers using the constants.

## State and Persistence Behavior
State lives in processor/MMU control registers.

## Dependencies and Integration Points
It integrates with SPARC32 SRMMU setup, context switching, TLB handling, and trap code.

## Risks
Wrong control bits can disable the MMU, select wrong contexts, or break cache behavior.

## Test Signals
Boot SPARC32 systems, stress context switches and TLB flushes, and compare register programming against CPU docs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/contregs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpu_type.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpu_type.h

## Purpose
This header declares SPARC CPU type identifiers and CPU implementation state.

## Important APIs, Types, and Functions
It defines enums/macros for CPU families and exposes variables/functions used to identify the running processor implementation.

## Control Flow
Early CPU probing sets the active CPU type; later code branches on it for cache, TLB, workaround, and platform behavior.

## State and Persistence Behavior
Detected CPU type is persistent global boot state. The header only declares the contract.

## Dependencies and Integration Points
It integrates CPU probing with cache/MMU, traps, performance, and errata workarounds.

## Risks
Misclassification selects wrong low-level routines and can destabilize the kernel.

## Test Signals
Boot representative SPARC CPU families and verify detected type in logs and selected fixup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpu_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata.h

## Purpose
This header is the SPARC public `CPU data wrapper` dispatcher. It selects SPARC32 or SPARC64 per-CPU data declarations while presenting the stable `<asm/cpudata.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/cpudata.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/cpudata.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_32.h

## Purpose
This header defines SPARC32 per-CPU data structures.

## Important APIs, Types, and Functions
It declares the CPU data layout used for CPU identity, loops-per-jiffy/calibration, and architecture-specific per-CPU fields.

## Control Flow
Boot CPU and secondary CPU setup initialize these structures; runtime code reads them through per-CPU accessors.

## State and Persistence Behavior
Per-CPU data persists for each online CPU and changes during CPU setup/hotplug-like paths.

## Dependencies and Integration Points
It integrates with SMP setup, scheduler CPU data, delay calibration, and platform CPU probing.

## Risks
Layout assumptions may be shared with assembly; drift can corrupt per-CPU reads.

## Test Signals
Boot UP and SMP SPARC32 configs, verify CPU enumeration, delay calibration, and per-CPU data access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_64.h

## Purpose
This header defines SPARC64 per-CPU data structures and access declarations.

## Important APIs, Types, and Functions
It describes CPU metadata used by SMP, NUMA, scheduler topology, trap handling, and low-level CPU state.

## Control Flow
Early boot and CPU bringup populate per-CPU structures; runtime code uses them for CPU-local decisions.

## State and Persistence Behavior
Per-CPU data persists while CPUs are possible/online and is updated during hotplug or topology initialization.

## Dependencies and Integration Points
It integrates with SPARC64 SMP bringup, NUMA, trap blocks, scheduler, and percpu allocation.

## Risks
Assembly/C layout coupling and hotplug updates are correctness-sensitive.

## Test Signals
Boot large SMP/NUMA SPARC64 configs, exercise CPU hotplug, and verify topology/per-CPU debug data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpudata_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/current.h

## Purpose
This header implements `current` task lookup for SPARC.

## Important APIs, Types, and Functions
It defines `get_current()`/`current` access using the SPARC stack/thread-info layout or dedicated register convention.

## Control Flow
Kernel code expands `current` inline to derive the active `task_struct` quickly.

## State and Persistence Behavior
No state is stored here; it reads the active task pointer/thread information.

## Dependencies and Integration Points
It integrates with scheduler, thread-info layout, context switching, and low-level entry code.

## Risks
Wrong stack masking or register assumptions make `current` point at the wrong task, causing broad corruption.

## Test Signals
Boot, context-switch stress, interrupt-in-task tests, and stack/thread-info debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcr.h

## Purpose
This header defines UltraSPARC Dispatch Control Register bits.

## Important APIs, Types, and Functions
It defines `DCR_*` flags for cache parity, branch prediction, return prediction, instruction dispatch, IRQ FP operation, and multiscalar dispatch controls.

## Control Flow
CPU setup or errata code reads/modifies DCR using these masks.

## State and Persistence Behavior
State is in the CPU DCR register and persists until changed or reset.

## Dependencies and Integration Points
It integrates with SPARC64 CPU initialization and performance/errata handling.

## Risks
Wrong bit programming can disable prediction/cache features or expose parity behavior incorrectly.

## Test Signals
Boot UltraSPARC variants, inspect DCR programming, and run performance/regression tests around CPU feature setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcu.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcu.h

## Purpose
This header defines SPARC64 Data Cache Unit control bits.

## Important APIs, Types, and Functions
It defines `DCU_*` flags for physical/virtual cache enable, store merging, RAW bypass, prefetch, write cache, watchpoint masks/enables, DMMU/IMMU, D-cache, and I-cache enable.

## Control Flow
Low-level CPU/MMU code uses these masks when enabling caches/MMUs or configuring watchpoints.

## State and Persistence Behavior
State lives in the DCU control register.

## Dependencies and Integration Points
It integrates with boot CPU setup, MMU enable, cache control, and debugging/watchpoint facilities.

## Risks
Misprogramming DCU can disable caches/MMUs or corrupt memory ordering during boot.

## Test Signals
Boot SPARC64 systems, validate cache/MMU enable state, run memory stress and watchpoint tests where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay.h

## Purpose
This header is the SPARC public `delay wrapper` dispatcher. It selects SPARC32 or SPARC64 delay-loop helpers while presenting the stable `<asm/delay.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/delay.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/delay.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_32.h

## Purpose
This header declares/implements SPARC32 busy-wait delay helpers.

## Important APIs, Types, and Functions
It exposes `__delay`, `udelay`, and related loop-calibrated delay surfaces for SPARC32.

## Control Flow
Callers request short busy waits; helpers loop based on calibrated CPU speed.

## State and Persistence Behavior
No state is owned here beyond external calibration values used by delay code.

## Dependencies and Integration Points
It integrates with generic delay APIs, timer calibration, and drivers needing short waits.

## Risks
Incorrect calibration causes too-short hardware delays or excessive stalls.

## Test Signals
Boot delay calibration, run driver smoke tests using udelay/mdelay, and compare measured delay duration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_64.h

## Purpose
This header provides SPARC64 delay helper declarations.

## Important APIs, Types, and Functions
It exposes low-level delay routines backed by tick/stick or calibrated loops.

## Control Flow
Drivers and core code call generic delay APIs that route to these SPARC64 helpers.

## State and Persistence Behavior
No header-owned state; timebase calibration persists elsewhere.

## Dependencies and Integration Points
It integrates with SPARC64 timers, generic delay APIs, and hardware drivers.

## Risks
Wrong timebase use can break device timing or boot waits.

## Test Signals
Measure udelay/mdelay accuracy and run boot/device initialization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/device.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/device.h

## Purpose
This header defines SPARC architecture extensions for `struct device`.

## Important APIs, Types, and Functions
It supplies architecture-specific DMA/IOMMU or platform metadata fields embedded in device structures.

## Control Flow
Device discovery and bus setup initialize the archdata; DMA and IOMMU paths later consume it.

## State and Persistence Behavior
Per-device archdata persists for the lifetime of the device.

## Dependencies and Integration Points
It integrates with OF platform devices, PCI/SBUS, DMA mapping, and IOMMU code.

## Risks
Missing or stale archdata can route DMA through the wrong translation path.

## Test Signals
Enumerate OF/PCI/SBUS devices and run DMA-capable driver tests under IOMMU and direct mapping modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma-mapping.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma-mapping.h

## Purpose
This header connects SPARC to the generic DMA mapping API.

## Important APIs, Types, and Functions
It declares/defines architecture DMA mapping hooks and includes generic DMA helpers as needed.

## Control Flow
Drivers call generic DMA APIs, which dispatch through SPARC DMA ops selected for the device/platform.

## State and Persistence Behavior
Header state is none; DMA mappings persist in IOMMU/direct mapping state managed elsewhere.

## Dependencies and Integration Points
It integrates drivers with SPARC IOMMU, PCI/SBUS, and DMA coherent allocation.

## Risks
Incorrect DMA ops selection causes data corruption or bus faults.

## Test Signals
Run DMA API debug, network/storage driver I/O, and IOMMU mapping/unmapping stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma-mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma.h

## Purpose
This header defines SPARC legacy DMA constants, controller registers, and helper declarations.

## Important APIs, Types, and Functions
It includes DMA channel/controller definitions, address/count handling, and architecture-specific DMA limits used by old SBUS/ISA-style devices.

## Control Flow
Legacy drivers program DMA controllers through these constants and helpers before starting device transfers.

## State and Persistence Behavior
State resides in DMA controller hardware and driver-owned descriptors.

## Dependencies and Integration Points
It integrates with legacy floppy/SBUS/ISA-like devices and generic DMA definitions.

## Risks
Wrong count/address programming causes memory corruption. Legacy DMA limits may not match modern DMA API assumptions.

## Test Signals
Exercise floppy/legacy DMA devices, DMA API debug, and transfer boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ebus_dma.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ebus_dma.h

## Purpose
This header declares EBus DMA support for SPARC systems.

## Important APIs, Types, and Functions
It defines EBus DMA channel structures, callback/status definitions, and setup/control APIs used by EBus-attached devices.

## Control Flow
Drivers allocate/configure an EBus DMA channel, program transfer parameters, start/stop transfers, and receive completion/error status.

## State and Persistence Behavior
DMA channel state persists in driver structures and hardware registers while a channel is allocated.

## Dependencies and Integration Points
It integrates with EBus device drivers, interrupt handling, and SPARC DMA mapping.

## Risks
Channel lifecycle mistakes can leak DMA resources or leave devices bus-mastering after teardown.

## Test Signals
Run EBus device transfer tests, interrupt completion paths, and start/stop/error handling scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ebus_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ecc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ecc.h

## Purpose
This header defines sun4m external cache/memory-controller ECC register offsets and bit fields.

## Important APIs, Types, and Functions
It defines ECC register offsets (`ECC_ENABLE`, `ECC_FSTATUS`, `ECC_FADDR`, `ECC_DIGNOSTIC`, `ECC_MBAENAB`, `ECC_DMESG`) and masks for MBus arbiter enable, fault control, fault address, and fault status fields.

## Control Flow
ECC handling code reads status/address registers after memory errors, decodes syndrome/type/address fields, and enables checking/interrupts through control bits.

## State and Persistence Behavior
State is in the ECC controller registers. Fault bits persist until cleared by controller-specific handling.

## Dependencies and Integration Points
It integrates with SPARC32 sun4m memory error handling, SRMMU passthrough ASI access, and platform diagnostics.

## Risks
Wrong decoding can misreport faulting CPUs/addresses or mishandle correctable versus uncorrectable errors.

## Test Signals
Use platform error injection/logs where available, verify syndrome/address decode, and boot with ECC interrupt handling enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ecc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/eeprom.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/eeprom.h

## Purpose
This header exposes SPARC EEPROM/NVRAM interfaces.

## Important APIs, Types, and Functions
It declares constants or functions used to access firmware-stored EEPROM data.

## Control Flow
Platform or char-device code includes it when reading/writing EEPROM-backed configuration.

## State and Persistence Behavior
State persists in EEPROM/NVRAM hardware, not in the header.

## Dependencies and Integration Points
It integrates with OpenPROM/NVRAM drivers and platform identity/configuration code.

## Risks
Writes can persist across reboots; incorrect offsets may corrupt firmware settings.

## Test Signals
Read EEPROM contents, compare with PROM tools, and test write paths only on disposable hardware/configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf.h

## Purpose
This header is the SPARC public `ELF wrapper` dispatcher. It selects SPARC32 or SPARC64 ELF ABI declarations while presenting the stable `<asm/elf.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/elf.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/elf.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_32.h

## Purpose
This header defines the SPARC32 ELF ABI contract for executable loading, core dumps, hardware capabilities, and register sets.

## Important APIs, Types, and Functions
It defines SPARC relocation constants, `HWCAP_SPARC_*`, `ELF_NGREG`, register-set typedefs, `elf_check_arch`, `ELF_ARCH`, `ELF_CLASS`, `ELF_DATA`, `ELF_EXEC_PAGESIZE`, `ELF_ET_DYN_BASE`, `ELF_HWCAP`, and `ELF_PLATFORM`.

## Control Flow
The ELF loader checks binary architecture, configures process personality, maps PIE/interpreter regions, and emits auxv/core-dump data using these macros.

## State and Persistence Behavior
No kernel state is stored here; it defines persistent userspace ABI values.

## Dependencies and Integration Points
It integrates with binfmt_elf, ptrace/core dumps, signal/register layouts, and userspace dynamic loaders.

## Risks
Changing relocation or register constants breaks userspace ABI and core dump compatibility.

## Test Signals
Run SPARC32 ELF binaries, PIE/static/dynamic loads, core dumps, ptrace register inspection, and auxv checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_64.h

## Purpose
This header defines the SPARC64 ELF ABI, including 64-bit execution, 32-bit compat execution, hardware capabilities, vDSO auxv entries, and process personality setup.

## Important APIs, Types, and Functions
It defines relocation constants, `HWCAP_SPARC_*` and `AV_SPARC_*` bits including crypto and ADI, native and compat `ELF_NGREG` layouts, `elf_check_arch`, `compat_elf_check_arch`, `ELF_ET_DYN_BASE`, `COMPAT_ELF_ET_DYN_BASE`, `ELF_HWCAP`, `SET_PERSONALITY`, `ARCH_DLINFO`, `ARCH_HAS_SETUP_ADDITIONAL_PAGES`, and `arch_setup_additional_pages()`.

## Control Flow
The ELF loader uses these definitions to accept SPARCV9/native and SPARC compat binaries, set 32-bit personality when needed, publish hardware/vDSO auxv entries, and install additional vDSO pages.

## State and Persistence Behavior
The header defines ABI constants. Runtime state includes process personality, auxv contents, and vDSO mapping created elsewhere.

## Dependencies and Integration Points
It depends on processor, ptrace, spitfire, and ADI headers. It integrates with binfmt_elf, compat, vDSO, hardware capability detection, ptrace, and core dumping.

## Risks
Hardware capability bits are visible ABI; changing them can break optimized libc/crypto dispatch. Wrong compat personality setup breaks 32-bit user programs.

## Test Signals
Run native and 32-bit SPARC ELF binaries, inspect auxv, test vDSO mapping, core dumps, PIE base placement, and ADI/crypto HWCAP exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/estate.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/estate.h

## Purpose
This header defines UltraSPARC error-state register bits.

## Important APIs, Types, and Functions
It provides masks/shifts for error-state fields used by trap and machine-check code.

## Control Flow
Error handlers read the register and decode processor state using these constants during fault reporting/recovery.

## State and Persistence Behavior
State lives in CPU error registers.

## Dependencies and Integration Points
It integrates with SPARC64 trap/error handling and platform diagnostics.

## Risks
Wrong decoding can obscure fatal hardware errors or misclassify recoverability.

## Test Signals
Validate error logs on hardware/fault injection and compare decoded fields to processor documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/estate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/extable.h

## Purpose
This header defines SPARC exception-table entry handling.

## Important APIs, Types, and Functions
It describes exception-table entry layout and fixup address extraction for fault recovery.

## Control Flow
Fault handlers search exception tables and redirect execution to fixup code when a faulting instruction is recoverable.

## State and Persistence Behavior
Exception tables are compiled metadata. Runtime state changes only through adjusted instruction pointers during faults.

## Dependencies and Integration Points
It integrates with user access, copy routines, module exception tables, and generic extable search.

## Risks
Incorrect relative address decoding or sorting breaks recoverable fault handling and can turn user-copy faults into kernel oopses.

## Test Signals
Run usercopy fault tests, module exception table tests, and fault injection around copy_from/to_user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fbio.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/fbio.h

## Purpose
This header defines SPARC framebuffer ioctl constants and structures.

## Important APIs, Types, and Functions
It exposes framebuffer type, video mode, cursor/color-map, and device-specific ioctl data layouts used by SPARC framebuffer drivers and userspace.

## Control Flow
Userspace issues ioctls; framebuffer drivers copy these structures and apply display configuration or report state.

## State and Persistence Behavior
Persistent state is in framebuffer device settings and userspace ABI; the header has no state.

## Dependencies and Integration Points
It integrates SPARC framebuffer drivers, console support, and legacy userspace tools.

## Risks
This is ABI-facing; layout changes break existing tools. Copying unchecked structures can affect display stability.

## Test Signals
Run framebuffer ioctl smoke tests, console mode changes, color-map/cursor operations, and ABI structure-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fbio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fhc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/fhc.h

## Purpose
This header defines FireHose Controller register bits for SPARC platforms.

## Important APIs, Types, and Functions
It provides FHC register offsets and masks for board status, control, interrupt, reset, and environmental/platform management.

## Control Flow
Platform code maps FHC registers, decodes status, configures interrupts, and performs reset/power/environment control as needed.

## State and Persistence Behavior
State lives in FHC hardware registers.

## Dependencies and Integration Points
It integrates with SPARC64 platform setup, interrupt handling, and environmental monitoring.

## Risks
Wrong register programming can disrupt board-level interrupts or reset behavior.

## Test Signals
Boot FHC systems, verify interrupt routing, platform status reporting, and safe reset/power controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fhc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy.h

## Purpose
This header is the SPARC public `floppy wrapper` dispatcher. It selects SPARC32 or SPARC64 floppy controller integration while presenting the stable `<asm/floppy.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/floppy.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/floppy.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_32.h

## Purpose
This header implements SPARC32 floppy-controller glue, including DMA, AUXIO motor/select control, and platform quirks.

## Important APIs, Types, and Functions
It defines architecture hooks expected by the generic floppy driver: DMA setup/teardown, virtual DMA behavior, controller I/O access, interrupt/DMA limits, and AUXIO-backed drive control.

## Control Flow
The generic floppy driver calls SPARC hooks to request DMA, program transfers, control motor/select/eject lines, handle interrupts, and clean up.

## State and Persistence Behavior
State persists in floppy controller registers, AUXIO bits, DMA controller state, and driver-owned buffers.

## Dependencies and Integration Points
It integrates generic floppy code with SPARC32 AUXIO, DMA, I/O space, and interrupt handling.

## Risks
Legacy floppy timing and DMA boundaries are fragile. Wrong AUXIO bits can select/eject drives unexpectedly or fail transfers.

## Test Signals
Boot with floppy enabled, perform read/write/format/eject tests, and exercise DMA boundary/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_64.h

## Purpose
This header implements SPARC64 floppy-controller integration for the generic floppy driver.

## Important APIs, Types, and Functions
It defines SPARC64-specific controller access, DMA or pseudo-DMA handling, interrupt setup, drive control, and platform quirks needed by generic floppy code.

## Control Flow
Generic floppy operations route through these hooks for register I/O, DMA movement, motor control, and interrupt completion.

## State and Persistence Behavior
Runtime state resides in controller hardware, DMA mappings, AUXIO/PCIO bits, and driver buffers.

## Dependencies and Integration Points
It integrates generic floppy support with SPARC64 I/O, AUXIO, EBus/PCI platform plumbing, and DMA mapping.

## Risks
Large inline architecture hooks make register ordering, DMA mapping, and platform detection error-prone. Mistakes can hang the controller or corrupt buffers.

## Test Signals
Run floppy probe and media read/write tests on SPARC64 systems with floppy hardware; enable DMA debugging and interrupt tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fpumacro.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/fpumacro.h

## Purpose
This header provides SPARC FPU/VIS state-management macros for assembly routines.

## Important APIs, Types, and Functions
It defines macros such as VIS entry/exit or FPU register transfer helpers used by crypto and low-level floating-point assembly.

## Control Flow
Assembly routines expand these macros to enable/use VIS/FPU state safely and preserve required calling conventions.

## State and Persistence Behavior
The macros affect transient FPU/VIS register state and FPRS flags.

## Dependencies and Integration Points
It integrates with SPARC64 crypto assembly, floating-point trap handling, and kernel FPU state rules.

## Risks
Incorrect FPU state management can corrupt user FPU registers or leak kernel crypto state.

## Test Signals
Run crypto selftests, FPU user workload during kernel crypto activity, and preemption/interrupt stress if applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fpumacro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ftrace.h

## Purpose
This header defines SPARC ftrace support hooks and call-site conventions.

## Important APIs, Types, and Functions
It declares architecture-specific ftrace graph/call handling structures or macros used by dynamic function tracing.

## Control Flow
When ftrace is enabled, patched call sites and graph tracer paths use these definitions to route function entry/return events.

## State and Persistence Behavior
Runtime ftrace state is managed by generic tracing and patched text; the header declares architecture contracts.

## Dependencies and Integration Points
It integrates with dynamic ftrace, function graph tracing, module text patching, and SPARC instruction encoding.

## Risks
Wrong call-site size or return-address handling can crash traced functions.

## Test Signals
Enable function and graph tracing, trace module and built-in functions, and run ftrace selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex.h

## Purpose
This header is the SPARC public `futex wrapper` dispatcher. It selects SPARC32 generic or SPARC64 custom futex helpers while presenting the stable `<asm/futex.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/futex.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/futex.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex_32.h

## Purpose
This header routes SPARC32 futex operations to the generic implementation.

## Important APIs, Types, and Functions
It includes `asm-generic/futex.h`, so SPARC32 uses generic futex atomic/user-access behavior.

## Control Flow
Generic futex code performs user-memory atomic operations through the included generic helpers.

## State and Persistence Behavior
State lives in userspace futex words and kernel wait queues; the header has no state.

## Dependencies and Integration Points
It integrates with generic futex syscalls and SPARC32 user access/atomic primitives.

## Risks
The generic path still depends on SPARC32 user access and cmpxchg semantics; emulated cmpxchg can affect atomicity assumptions.

## Test Signals
Run futex selftests, pthread mutex/condvar stress, robust futex tests, and 32-bit SMP contention workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex_64.h

## Purpose
This header implements SPARC64 futex atomic operations on user memory.

## Important APIs, Types, and Functions
It provides `arch_futex_atomic_op_inuser()` and `futex_atomic_cmpxchg_inatomic()` style helpers using SPARC64 inline assembly, exception tables, and user-access checks.

## Control Flow
Futex syscalls request an operation; the helper performs the atomic user-memory update or compare/exchange, captures old values, and returns success or fault/error codes.

## State and Persistence Behavior
State changes are in userspace futex words and kernel futex wait queues managed elsewhere.

## Dependencies and Integration Points
It integrates with generic futex code, SPARC64 user access, exception tables, atomics, and memory barriers.

## Risks
User-memory atomic sequences must be fault-safe and atomic. Exception-table mistakes can oops the kernel on bad user addresses.

## Test Signals
Run futex selftests, robust futex tests, invalid-address fault tests, and high-contention pthread workloads on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq.h

## Purpose
This header is the SPARC public `hardirq wrapper` dispatcher. It selects SPARC32 or SPARC64 hard IRQ accounting declarations while presenting the stable `<asm/hardirq.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/hardirq.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/hardirq.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_32.h

## Purpose
This header defines SPARC32 hard IRQ accounting hooks.

## Important APIs, Types, and Functions
It provides architecture IRQ stack/accounting declarations required by generic interrupt code.

## Control Flow
Interrupt entry/exit updates per-CPU hardirq state through generic mechanisms informed by this header.

## State and Persistence Behavior
Per-CPU interrupt accounting persists in irq/softirq counters outside the header.

## Dependencies and Integration Points
It integrates with generic hardirq, preempt count, and SPARC32 interrupt entry code.

## Risks
Accounting mismatches can break lockdep, preemption, or interrupt nesting diagnostics.

## Test Signals
Boot with lockdep/irq tracing, run interrupt load, and inspect `/proc/interrupts` and preempt count warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_64.h

## Purpose
This header defines SPARC64 hard IRQ accounting and stack integration.

## Important APIs, Types, and Functions
It provides SPARC64-specific hardirq declarations used by generic IRQ handling and per-CPU accounting.

## Control Flow
SPARC64 interrupt entry/exit code updates hardirq state and may switch stacks according to architecture support.

## State and Persistence Behavior
Interrupt accounting is per-CPU runtime state managed elsewhere.

## Dependencies and Integration Points
It integrates with generic IRQ, lockdep, softirq-on-own-stack support, and SPARC64 trap entry.

## Risks
Incorrect IRQ accounting affects lockdep and can hide interrupt nesting bugs.

## Test Signals
Run interrupt-heavy workloads with lockdep/trace irqflags and validate no hardirq/preempt imbalance warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/head.h

## Purpose
This header is the SPARC public `boot-head wrapper` dispatcher. It selects SPARC32 or SPARC64 boot header declarations while presenting the stable `<asm/head.h>` include path to common kernel code.

## Important APIs, Types, and Functions
The important interface is the include selection itself, guarded by `__sparc__` and `__arch64__` where relevant. The concrete APIs, types, and inline functions live in the selected `_32.h` or `_64.h` companion.

## Control Flow
There is no runtime control flow. The preprocessor chooses the architecture-specific implementation at compile time.

## State and Persistence Behavior
No state is stored in this wrapper. Runtime state, if any, belongs to the selected implementation header or its C/assembly users.

## Dependencies and Integration Points
It integrates generic Linux include paths with SPARC32/SPARC64 split implementations. Any subsystem including `<asm/head.h>` depends on this wrapper to select the correct ABI and instruction implementation.

## Risks
Wrong preprocessor gating can include a 64-bit layout in 32-bit builds or the reverse, causing compile failures or ABI/runtime corruption.

## Test Signals
Build both SPARC32 and SPARC64 configurations and ensure all users of `<asm/head.h>` compile and exercise the selected implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_32.h

## Purpose
This header defines SPARC32 boot-header constants shared with early boot code and image tools.

## Important APIs, Types, and Functions
It describes magic/signature fields, boot loader visible offsets, and early kernel image metadata used by boot assembly and tools such as `piggyback`.

## Control Flow
Boot assembly emits these fields; bootloaders and host tools read or patch them before transferring control to the kernel.

## State and Persistence Behavior
The header shapes persistent bytes in the kernel image, not runtime state.

## Dependencies and Integration Points
It integrates with `arch/sparc/boot` image creation, PROM/U-Boot boot paths, and early init assembly.

## Risks
Changing offsets or signatures can break bootloader/tool compatibility.

## Test Signals
Build SPARC32 boot images, inspect headers, run `piggyback`/U-Boot image creation, and boot under target firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_64.h

## Purpose
This header defines SPARC64 boot-header constants and early image metadata.

## Important APIs, Types, and Functions
It provides boot signature/layout values consumed by SPARC64 head assembly and boot tools, including fields patched for initrd support.

## Control Flow
Early assembly emits header fields; `piggyback` and bootloaders locate the `HdrS` signature and patch/read ramdisk metadata.

## State and Persistence Behavior
State is the persistent boot image header. Runtime code consumes values during early boot.

## Dependencies and Integration Points
It integrates with PROM/a.out image handling, `piggyback`, early kernel entry, and initrd setup.

## Risks
Header layout drift breaks in-place image patching and bootloader expectations.

## Test Signals
Build `vmlinux.aout` and `tftpboot.img`, inspect `HdrS` location, and boot SPARC64 images with and without initrd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hibernate.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hibernate.h

## Purpose
This header declares SPARC hibernation support hooks.

## Important APIs, Types, and Functions
It provides architecture interfaces for saving/restoring CPU and memory state across hibernation on supported SPARC64 configurations.

## Control Flow
Generic hibernation code calls architecture hooks during snapshot creation and resume.

## State and Persistence Behavior
Hibernate persists a memory image to storage through generic PM code; architecture state is saved/restored by implementations declared here.

## Dependencies and Integration Points
It integrates with `kernel/power`, CPU state save/restore, MMU context restoration, and SPARC64 platform resume.

## Risks
Incomplete CPU/MMU state restore can crash immediately after resume.

## Test Signals
Build with hibernation, perform suspend/resume cycles, verify CPU, timers, and devices after restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hibernate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/highmem.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/highmem.h

## Purpose
This header defines SPARC32 highmem mapping helpers.

## Important APIs, Types, and Functions
It provides `kmap`/`kunmap`-related architecture definitions, `PKMAP`/fixmap integration, and cache/TLB handling for highmem pages.

## Control Flow
Generic highmem code maps high pages into temporary kernel virtual addresses and unmaps them after use.

## State and Persistence Behavior
Persistent state is in highmem mapping tables managed by generic MM; the header defines architecture hooks.

## Dependencies and Integration Points
It integrates with SPARC32 `CONFIG_HIGHMEM`, `KMAP_LOCAL`, page tables, and cache/TLB flushes.

## Risks
Missing flushes or wrong virtual ranges can expose stale aliases or corrupt highmem access.

## Test Signals
Boot SPARC32 HIGHMEM configs, run highmem stress, filesystem I/O, swap, and kmap-local debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hugetlb.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hugetlb.h

## Purpose
This header defines SPARC hugepage helpers for hugetlbfs and huge mappings.

## Important APIs, Types, and Functions
It provides architecture hooks for huge PTE handling, page size selection, and hugepage address alignment.

## Control Flow
Generic hugetlb code calls these helpers when creating, inspecting, or tearing down hugepage mappings.

## State and Persistence Behavior
State lives in page tables and hugetlb reservations managed elsewhere.

## Dependencies and Integration Points
It integrates with SPARC64 hugepage support, MMU page-table formats, and generic hugetlbfs.

## Risks
Incorrect huge PTE encoding or alignment causes TLB faults and memory corruption.

## Test Signals
Run hugetlbfs tests, mmap/munmap hugepages, fork/exec with huge mappings, and page fault stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hvtramp.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hvtramp.h

## Purpose
This header declares SPARC hypervisor trampoline interfaces.

## Important APIs, Types, and Functions
It exposes data/functions used to enter secondary CPUs or transition through sun4v hypervisor trampoline code.

## Control Flow
CPU bringup or hypervisor-specific boot paths use the trampoline declarations to start execution at the expected low-level entry point.

## State and Persistence Behavior
Trampoline code/data may persist in reserved memory during boot/CPU bringup; the header only declares it.

## Dependencies and Integration Points
It integrates with SPARC64 sun4v, SMP bringup, hypervisor calls, and trap-table setup.

## Risks
Wrong trampoline address or calling convention prevents secondary CPUs from starting.

## Test Signals
Boot sun4v/SPARC64 SMP systems, hotplug CPUs where supported, and verify secondary CPU startup logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hvtramp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hw_irq.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hw_irq.h

## Purpose
This minimal header reserves the SPARC hardware IRQ include path.

## Important APIs, Types, and Functions
It currently provides only the include guard and no declarations.

## Control Flow
Generic code can include `<asm/hw_irq.h>` without pulling additional SPARC definitions.

## State and Persistence Behavior
No runtime or build state is defined.

## Dependencies and Integration Points
It integrates with generic IRQ code that expects an architecture `hw_irq.h` header.

## Risks
The main risk is accidental addition of declarations that conflict with generic IRQ handling.

## Test Signals
Full SPARC builds with IRQ-related configs enabled ensure the empty header remains sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hw_irq.h -->
