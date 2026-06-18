# subset-b-000857 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/Kconfig -->
## sources/distributed-fs/ceph-client/arch/x86/Kconfig

### Purpose
`arch/x86/Kconfig` is the top-level x86 architecture configuration contract. It chooses 32-bit versus 64-bit builds, advertises architecture capabilities to generic kernel subsystems, pulls in x86 sub-Kconfig files, and exposes user-facing options for processors, memory layout, security mitigations, firmware, power management, buses, binary emulation, and virtualization.

### Important APIs, Types, And Functions
This is declarative Kconfig rather than C code. Key symbols include `64BIT`, `X86_32`, `X86_64`, the central `X86` capability selector, `PGTABLE_LEVELS`, `SMP`, `X86_X2APIC`, `HYPERVISOR_GUEST`, `PARAVIRT`, `EFI`, `EFI_STUB`, `RELOCATABLE`, `RANDOMIZE_BASE`, `RANDOMIZE_MEMORY`, `CPU_MITIGATIONS`, `APM`, `PCI_*`, `IA32_EMULATION`, and `X86_X32_ABI`. It sources subordinate configuration domains such as `arch/x86/Kconfig.cpu`, `arch/x86/events/Kconfig`, `kernel/livepatch/Kconfig`, ACPI/power/cpuidle/cpufreq Kconfigs, KVM, CPU feature definitions, and assembler feature checks.

### Control Flow
Kconfig evaluation starts by deriving `X86_32` or `X86_64` from `64BIT`, then the `X86` symbol selects a large sorted set of generic capabilities. Menu sections gate features by architecture width and prerequisite subsystems. Processor features define SMP/APIC/MCE/legacy segment and syscall support, memory options define highmem/PAE/NUMA/KASLR/physical alignment, mitigation options are only visible under `CPU_MITIGATIONS`, and firmware/power/bus/binary-emulation menus add platform-specific choices. `source` statements delegate detailed CPU, event, KVM, cpufeature, and assembler configuration to narrower files.

### State, Persistence, And Dependencies
The persistent state is the generated `.config` and generated headers consumed by makefiles and C/assembly. Dependencies are encoded with `depends on`, `select`, `imply`, `default`, `choice`, and compile/link probes such as `$(cc-option,...)`, `$(as-instr,...)`, and `$(success,...)`. The file is highly coupled to generic kernel capability symbols and to build-time architecture decisions used by `arch/x86/Makefile` and boot code.

### Integration Points
Downstream code uses these symbols to include objects, set compiler flags, expose runtime facilities, and build firmware entry paths. Examples include `CONFIG_EFI_STUB` enabling EFI boot objects, `CONFIG_RANDOMIZE_BASE` enabling compressed-boot KASLR, `CONFIG_AMD_MEM_ENCRYPT` enabling SEV/SME boot code, `CONFIG_UNACCEPTED_MEMORY` enabling early memory acceptance, and mitigation symbols selecting compiler flags and objtool behavior.

### Risks
The main risk is dependency drift: `select` can force symbols without satisfying their normal dependencies, and capability symbols must stay synchronized with actual code support. Security options are especially sensitive because build-time defaults interact with runtime command-line overrides. Width-specific options such as `EFI_MIXED`, `X86_X32_ABI`, PAE, and highmem can produce build or boot regressions if their dependencies are relaxed incorrectly.

### Test Signals
Useful signals include `olddefconfig`, `allnoconfig`, `defconfig`, `allyesconfig`, x86_32 and x86_64 build coverage, randconfig with `W=1`, boot tests for EFI/BIOS/KASLR/mitigation combinations, and checks that generated config headers match object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/Makefile -->
## sources/distributed-fs/ceph-client/arch/x86/Makefile

### Purpose
`arch/x86/Makefile` is the unified top-level x86 kbuild recipe for i386 and x86_64. It chooses the default config, exports boot and mitigation compiler flags, selects ABI width, sets architecture-wide C/A/Rust/linker flags, generates architecture headers/tools, and delegates final `bzImage` construction to `arch/x86/boot`.

### Important APIs, Types, And Functions
Important variables include `KBUILD_DEFCONFIG`, `RETPOLINE_CFLAGS`, `RETHUNK_CFLAGS`, `REALMODE_CFLAGS`, `BITS`, `UTS_MACHINE`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `KBUILD_RUSTFLAGS`, `LDFLAGS_vmlinux`, `KBUILD_IMAGE`, and `BOOT_TARGETS`. Targets include `archscripts`, `archheaders`, generated `cpufeaturemasks.h`, `bzImage`, legacy boot image targets, `install`, `checkbin`, optional ORC hash generation, `archclean`, and `archhelp`.

### Control Flow
The file first picks a defconfig based on `ARCH` and host machine. It builds compiler flag fragments for retpoline, return thunks, stack alignment, real-mode code, floating point code, IBT, 32-bit versus 64-bit code generation, stack protector guard placement, tracing workarounds, mitigation flags, call padding, and linker emulation. Build targets then generate helper tools and headers, add x86 libraries/drivers, build `vmlinux`, invoke `arch/x86/boot` to produce `bzImage`, and create compatibility symlinks under `arch/i386` or `arch/x86_64`.

### State, Persistence, And Dependencies
Persistent outputs are generated headers, helper tools, the compressed boot image, and architecture symlinks in the object tree. The makefile depends on Kconfig symbols, compiler support probes, Rust target generation, `arch/x86/tools`, syscall table generation, objtool/ORC inputs, and the boot subdirectory.

### Integration Points
This is the bridge between selected x86 configuration and all compiled architecture code. It exports `REALMODE_CFLAGS` for `arch/x86/boot`, retpoline/rethunk flags for code and vDSO builds, and `BITS` so shared makefiles can choose `*_32` or `*_64` objects.

### Risks
Compiler flag ordering is fragile: floating point avoidance, IBT jump-table disabling, retpoline/rethunk flags, and stack alignment must be applied before affected code is compiled. Incorrect `BITS` or `UTS_MACHINE` breaks object selection and linker emulation. Retpoline or ORC generation failures should be caught by `checkbin` and generated-header dependencies.

### Test Signals
Run x86_32 and x86_64 builds with GCC and Clang where possible, verify `make archheaders archscripts`, build `bzImage`, test mitigation flag combinations, and inspect command lines for real-mode and compressed-boot objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/Makefile -->
## sources/distributed-fs/ceph-client/arch/x86/boot/Makefile

### Purpose
`arch/x86/boot/Makefile` builds the real-mode setup code and wraps the compressed kernel into `bzImage` plus optional legacy disk, hard disk, and ISO images.

### Important APIs, Types, And Functions
Important variables include `SVGA_MODE`, `targets`, `setup-y`, `SETUP_OBJS`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `sed-zoffset`, `OBJCOPYFLAGS_vmlinux.bin`, `LDFLAGS_setup.elf`, `FDARGS`, `FDINITRD`, and `imgdeps`. Build rules generate `cpustr.h`, `zoffset.h`, `setup.elf`, `setup.bin`, `vmlinux.bin`, `compressed/vmlinux`, `bzImage`, `mtools.conf`, and image formats through `genimage.sh`.

### Control Flow
The makefile compiles real-mode setup objects with exported `REALMODE_CFLAGS`, optionally adds `apm.o`, orders video drivers deliberately, builds the compressed kernel subdirectory, extracts symbol offsets from compressed `vmlinux` into `zoffset.h`, links setup code with `setup.ld`, objcopies setup and compressed images to binaries, and concatenates synchronized setup plus compressed payload into `bzImage`.

### State, Persistence, And Dependencies
Build state lives in generated setup binaries, compressed image objects, generated headers, and image artifacts. Dependencies include real-mode C/assembly helpers, `arch/x86/boot/compressed`, `mkcpustr`, `nm`, `sed`, `objcopy`, linker scripts, `mtools.conf.in`, and `genimage.sh`.

### Integration Points
The top-level x86 makefile calls this makefile for `bzImage` and legacy image targets. Runtime setup code produced here populates `boot_params`, enters protected mode, and passes control to compressed kernel startup.

### Risks
The setup image is size and ABI constrained. `sed-zoffset` must track symbols required by the boot header. Video object order is intentional, and changing it can alter mode probing. Legacy image targets depend on external tools such as syslinux and, for EFI hard-disk images, OVMF/EDK2.

### Test Signals
Build `arch/x86/boot/bzImage`, inspect generated `zoffset.h`, boot under BIOS and EFI test environments, and exercise legacy image targets when their external tools are installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/a20.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/a20.c

### Purpose
`a20.c` enables the A20 address line during real-mode setup so the kernel can safely address memory above 1 MiB without 20-bit wraparound.

### Important APIs, Types, And Functions
The exported function is `enable_a20()`. Helpers include `empty_8042()`, `a20_test()`, `a20_test_short()`, `a20_test_long()`, `enable_a20_bios()`, `enable_a20_kbc()`, and `enable_a20_fast()`. It uses `struct biosregs`, `intcall()`, segment helpers, `rdfs32()`, `rdgs32()`, `wrfs32()`, `inb()`, `outb()`, and `io_delay()` from `boot.h`.

### Control Flow
`enable_a20()` loops up to 255 times. Each pass checks if A20 is already enabled, tries BIOS interrupt `INT 15h AX=2401`, drains the keyboard controller, waits for delayed BIOS effects, tries the 8042 keyboard-controller command sequence, and finally toggles fast A20 gate port `0x92`. Short tests catch immediate success; long tests wait for slow external circuitry.

### State, Persistence, And Dependencies
The only persistent hardware state is the enabled A20 line and any side effects on keyboard controller buffers. The A20 test temporarily writes the `int 0x80` vector location through segment aliases and restores it. Dependencies are BIOS behavior, 8042 controller availability, port `0x92`, and real-mode segment access.

### Integration Points
Setup code calls `enable_a20()` before protected-mode transition and before high memory assumptions. It integrates with `bioscall.S` for firmware calls and boot I/O helpers for port access.

### Risks
Firmware and legacy controllers are unreliable. `empty_8042()` guards against absent controllers by treating repeated `0xff` status as failure. The memory alias test must restore its saved vector and must run with interrupts/firmware expectations compatible with early boot.

### Test Signals
Boot under emulators and old BIOS-like environments, verify A20 already-on and forced-controller paths, test systems without 8042, and ensure failures halt cleanly in the caller rather than corrupting memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/a20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/apm.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/apm.c

### Purpose
`apm.c` queries a 32-bit APM BIOS interface during real-mode boot and records connection metadata in `boot_params` for the later kernel.

### Important APIs, Types, And Functions
The exported function is `query_apm_bios()`. It uses `struct biosregs`, `initregs()`, `intcall()`, `X86_EFLAGS_CF`, and `boot_params.apm_bios_info`.

### Control Flow
The function performs APM installation check via `INT 15h AH=53h`, verifies the `"PM"` signature and 32-bit support bit, disconnects any previous interface, requests a 32-bit connection, stores segment/offset/length fields returned by firmware, checks carry for connection failure, then repeats the installation check because some BIOSes expose different flags after connection.

### State, Persistence, And Dependencies
Persistent state is `boot_params.apm_bios_info`, which later APM kernel code can consume. It depends on 16-bit BIOS interrupt services, correct register return conventions, and `CONFIG_X86_APM_BOOT` object inclusion.

### Integration Points
The boot makefile includes `apm.o` when `CONFIG_X86_APM_BOOT` is set. Later APM support uses the saved descriptors to call into firmware from protected mode.

### Risks
APM BIOS implementations are historically inconsistent. The code defensively disconnects and rechecks, but stores returned fields before the carry check, so later consumers must rely on the function result and valid configuration paths. APM is 32-bit only and not relevant to x86_64 boot.

### Test Signals
Test with APM-capable BIOS emulation, no-APM systems, signatures with carry set, BIOSes that lack 32-bit support, and configurations where `CONFIG_X86_APM_BOOT` is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/apm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/bioscall.S -->
## sources/distributed-fs/ceph-client/arch/x86/boot/bioscall.S

### Purpose
`bioscall.S` implements the real-mode `intcall()` trampoline used by C setup code to invoke BIOS interrupts while protecting the boot C environment from register and segment clobbering.

### Important APIs, Types, And Functions
The single exported symbol is `intcall`. The ABI matches `void intcall(u8 int_no, const struct biosregs *ireg, struct biosregs *oreg)`. It operates in `.code16` and uses the `struct biosregs` stack layout defined in `boot.h`.

### Control Flow
`intcall` self-modifies the interrupt vector byte in an `INT` instruction, saves flags, FS/GS, and general registers, copies the caller's input register image to a stack frame, restores full register state from that frame, executes the selected BIOS interrupt, pushes the post-interrupt state, reestablishes C invariants such as direction flag, DS, ES, and 16-bit stack shape, optionally copies the output state to the caller, then restores saved state and returns.

### State, Persistence, And Dependencies
Persistent state is limited to the modified interrupt immediate byte inside the function. It depends on real-mode execution, writable/executable boot text, the exact `biosregs` layout, and C callers passing segment-addressable pointers.

### Integration Points
BIOS users such as A20, APM, memory, EDD, video, and other setup helpers call `intcall()` to perform firmware services before protected-mode handoff.

### Risks
Self-modifying code and register-frame layout are fragile. Any `struct biosregs` layout change must be mirrored here. BIOSes may still corrupt memory or behave asynchronously, but this wrapper prevents common register/segment damage from leaking into C code.

### Test Signals
Exercise BIOS calls that return no output and calls that populate output registers, check segment registers after calls, and boot on emulators with BIOS services for APM/video/memory probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/bioscall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/bitops.h -->
## sources/distributed-fs/ceph-client/arch/x86/boot/bitops.h

### Purpose
`bitops.h` provides a tiny boot-environment replacement for generic Linux bit operations without pulling in the full kernel `linux/bitops.h`.

### Important APIs, Types, And Functions
It defines `_LINUX_BITOPS_H` to inhibit generic inclusion, provides `constant_test_bit()`, `variable_test_bit()`, the `test_bit()` macro, and `set_bit()`.

### Control Flow
`test_bit()` chooses a pure C indexed test when the bit number is compile-time constant and an x86 `btl` instruction when variable. `set_bit()` uses `btsl` on a 32-bit word.

### State, Persistence, And Dependencies
The state is the caller-provided bitmap memory. It depends on x86 inline assembly constraints, `u32`, `bool`, and boot code's limited header environment.

### Integration Points
Included from `boot.h`, it supports boot CPU flag and setup bitmap checks before the full kernel bitops API is available.

### Risks
Operations are not atomic beyond the instruction semantics used and are intended for single-threaded boot code. The implementation assumes little-endian 32-bit word indexing and x86 assembly.

### Test Signals
Compile real-mode setup code, test constant and variable bit positions across word boundaries, and verify generated assembly accepts both immediate and register bit operands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/boot.h -->
## sources/distributed-fs/ceph-client/arch/x86/boot/boot.h

### Purpose
`boot.h` is the shared C header for x86 real-mode setup code. It defines early boot globals, segment-address helpers, heap allocation primitives, BIOS register layout, and prototypes for setup subsystems.

### Important APIs, Types, And Functions
Important declarations include `hdr`, `boot_params`, `STACK_SIZE`, `cpu_relax()`, `io_delay()`, segment helpers for DS/FS/GS, `rdfs*`, `wrfs*`, `rdgs*`, `wrgs*`, `memcmp_fs()`, `memcmp_gs()`, `RESET_HEAP()`, `GET_HEAP()`, `heap_free()`, `struct biosregs`, `intcall()`, `cmdline_find_option()`, `cmdline_find_option_bool()`, and prototypes for A20, APM, CPU validation, console, EDD, memory, protected-mode jump, formatting, tty, and video code.

### Control Flow
Most routines are inline utilities used by setup modules. Segment helpers load FS/GS and perform memory access through segment overrides. Heap helpers bump `HEAP` with alignment and bounds checking. The command-line inline wrappers reject pointers at or above 1 MiB for real-mode access, then call the parser implementation.

### State, Persistence, And Dependencies
Central persistent boot state is `boot_params`, the setup header `hdr`, and the bump heap between `_end` and `heap_end`. The header depends on Linux boot protocol structures, EDD definitions, local boot C type/string/I/O helpers, and exact real-mode compiler assumptions.

### Integration Points
Every real-mode boot C file includes this header. It is the API boundary between setup modules and assembly stubs such as `bioscall.S`, `copy.S`, `pmjump.S`, and `header.S`.

### Risks
The segment helper API can address only what real-mode segmentation permits. The heap is a simple bump allocator with no free path, so ordering and size estimates matter. `struct biosregs` layout is consumed by assembly and cannot be changed casually.

### Test Signals
Build setup objects with `REALMODE_CFLAGS`, check `struct biosregs` offsets against assembly expectations, run boot tests that exercise command line, BIOS calls, memory detection, video, and protected-mode transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/boot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cmdline.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/cmdline.c

### Purpose
`cmdline.c` implements the minimal command-line parser used by real-mode setup and reused by compressed boot with a different segment access shim.

### Important APIs, Types, And Functions
The exported functions are `__cmdline_find_option()` and `__cmdline_find_option_bool()`. The local helper is `myisspace()`. Public inline wrappers in `boot.h` and compressed `cmdline.c` call these internals.

### Control Flow
`__cmdline_find_option()` walks a NUL-terminated command line through FS-relative reads, using a state machine for word start, option comparison, skip, and value copy. Repeated `option=value` instances return the last argument length while truncating the copied buffer safely. `__cmdline_find_option_bool()` walks words similarly and returns the one-based starting position of an exact boolean option or zero when absent.

### State, Persistence, And Dependencies
The parser is stateless except for the caller buffer. It depends on `set_fs()` and `rdfs8()` to read command-line bytes and stops at a 64 KiB segment boundary.

### Integration Points
Real-mode setup uses it for options such as serial/video/CPU behavior. The compressed boot version includes this same file after redefining FS access so KASLR, ACPI, memory encryption, and other early logic can parse the full boot command line.

### Risks
No quoting or escaping is supported; whitespace separates tokens. Real-mode callers cannot parse command lines located above 1 MiB through the `boot.h` wrappers. The non-boolean parser deliberately returns the last instance, so callers must expect override behavior.

### Test Signals
Test absent command lines, boolean exact matches, prefix mismatches, repeated `key=value`, truncated buffers with correct returned length, whitespace edge cases, and 64 KiB boundary termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/Makefile -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/acpi.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/acpi.c

### Purpose
`compressed/acpi.c` discovers ACPI RSDP early in the compressed kernel and, when KASLR and memory hotremove are enabled, parses SRAT memory affinity subtables to identify immovable memory regions that KASLR should prefer.

### Important APIs, Types, And Functions
Exports are `get_rsdp_addr()`, `count_immovable_mem_regions()`, and `immovable_mem`. Helpers include `__efi_get_rsdp_addr()`, `efi_get_rsdp_addr()`, `compute_checksum()`, `scan_mem_for_rsdp()`, `bios_get_rsdp_addr()`, `get_cmdline_acpi_rsdp()`, and `get_acpi_srat_table()`.

### Control Flow
`get_rsdp_addr()` checks an existing `boot_params_ptr->acpi_rsdp_addr`, then EFI configuration tables, then BIOS EBDA and high-memory scan windows. EFI lookup prefers ACPI 2.0 GUID and falls back to ACPI 1.0 GUID. BIOS scanning validates both signature and checksums. `count_immovable_mem_regions()` ignores ACPI when `acpi=off`, finds SRAT via RSDP/XSDT/RSDT, walks subtables, and records non-hotpluggable memory affinity entries into `immovable_mem`.

### State, Persistence, And Dependencies
Persistent early state is `boot_params_ptr->acpi_rsdp_addr` set by `misc.c` and the global `immovable_mem` array used by KASLR. Dependencies include compressed EFI helpers, ACPI table definitions, command-line parsing, `boot_params`, and direct physical memory mapping.

### Integration Points
`extract_kernel()` saves the RSDP for the real kernel. `kaslr.c` calls `count_immovable_mem_regions()` to constrain placement when memory hotremove support wants the kernel in immovable memory.

### Risks
This code dereferences firmware-provided physical addresses before full kernel validation, so bad tables can cause early boot faults. SRAT parsing must reject zero-length subtables and cap the array at `MAX_NUMNODES*2`. Command-line `acpi_rsdp` is considered only for kexec-related builds and intentionally is not written back to boot params.

### Test Signals
Boot with EFI ACPI 2.0, EFI ACPI 1.0, BIOS RSDP, no ACPI, `acpi=off`, `acpi=rsdt`, kexec `acpi_rsdp=`, malformed checksums, zero-length SRAT entries, and many memory affinity entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/cmdline.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/cmdline.c

### Purpose
`compressed/cmdline.c` adapts the real-mode command-line parser for the compressed-kernel environment where the full 64-bit command-line pointer can be directly dereferenced through identity mappings.

### Important APIs, Types, And Functions
It defines a local `set_fs()`/`rdfs8()` shim, includes `../cmdline.c`, and exports `get_cmd_line_ptr()`, `cmdline_find_option()`, and `cmdline_find_option_bool()`.

### Control Flow
`get_cmd_line_ptr()` combines `hdr.cmd_line_ptr` with `ext_cmd_line_ptr`. Parser wrappers pass that full pointer to the shared parser. The local FS model turns segment values into linear base addresses so the included parser can run unchanged.

### State, Persistence, And Dependencies
The file is stateless except for a static `fs` base used during parsing. It depends on `boot_params_ptr`, identity mappings for command-line memory, and the shared parser implementation.

### Integration Points
KASLR, ACPI, memory encryption, early console, and other compressed boot code call these wrappers before the real kernel command-line parser is available.

### Risks
The included parser still has a 64 KiB segment-window loop style. The command-line memory must already be mapped before parsing; `ident_map_64.c` later explicitly maps it for the uncompressed kernel.

### Test Signals
Boot with command lines above 4 GiB on x86_64, extended command-line pointer set, absent command line, repeated options, and options consumed by KASLR or ACPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/cpuflags.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/cpuflags.c

### Purpose
`compressed/cpuflags.c` exposes early CPU feature detection to compressed boot code by reusing the setup CPU flag implementation.

### Important APIs, Types, And Functions
It includes `../cpuflags.c` and exports `has_cpuflag(int flag)`.

### Control Flow
`has_cpuflag()` calls `get_cpuflags()` to populate the shared early `cpu.flags` bitmap and then returns `test_bit(flag, cpu.flags)`.

### State, Persistence, And Dependencies
State is the included CPU flag cache from setup code. Dependencies include early CPUID support, boot bitops, and the compressed build environment.

### Integration Points
Compressed boot users such as KASLR entropy, CPU capability checks, and early platform handling can test feature bits without entering the full kernel CPU initialization path.

### Risks
Feature detection this early must avoid facilities not set up yet, especially under encrypted guests where CPUID may trap. SEV/TDX code arranges exception or paravirtual handling before sensitive CPUID users.

### Test Signals
Boot on CPUs and guests with different CPUID leaves, SEV-ES/SNP/TDX guests, and configurations that call `has_cpuflag()` before and after decompressor setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/cpuflags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/early_serial_console.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/early_serial_console.c

### Purpose
`compressed/early_serial_console.c` reuses the setup early serial console implementation while placing `early_serial_base` in `.data` so it is available before BSS is cleared.

### Important APIs, Types, And Functions
It defines `int early_serial_base __section(".data")` and includes `../early_serial_console.c`, which provides `console_init()` and serial command-line parsing.

### Control Flow
The included setup implementation parses early serial options and initializes the base port. Compressed `misc.c` later uses `early_serial_base` in `__putstr()` to send debug and error output.

### State, Persistence, And Dependencies
Persistent state is the chosen serial I/O base address. It depends on command-line parsing, port I/O, and early boot `.data` survival before BSS initialization.

### Integration Points
Built only when `CONFIG_EARLY_PRINTK` is selected. It feeds compressed boot diagnostics, including decompression, KASLR, ACPI, and error paths.

### Risks
Incorrect base-port detection can hang or delay output loops. Because BSS clearing happens during startup relocation, state that must survive initial output has to be in `.data`, as this wrapper enforces.

### Test Signals
Boot with early serial enabled and disabled, valid and invalid serial options, and verify decompressor messages appear over serial before and after BSS clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/early_serial_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/efi.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/efi.c

### Purpose
`compressed/efi.c` provides minimal early helpers for reading EFI system and configuration tables from `boot_params` without including full kernel EFI headers.

### Important APIs, Types, And Functions
Exports are `efi_get_type()`, `efi_get_system_table()`, `efi_get_conf_table()`, and `efi_find_vendor_table()`. Internal helpers include `get_kexec_setup_data()` and `get_vendor_table()`.

### Control Flow
`efi_get_type()` validates the loader signature as `EL64` or `EL32` and rejects inaccessible high addresses on non-64-bit builds. `efi_get_system_table()` reconstructs the system-table physical address. `efi_get_conf_table()` handles 64-bit, 32-bit, and kexec-provided configuration tables. `efi_find_vendor_table()` walks entries and returns the vendor table address for a matching GUID.

### State, Persistence, And Dependencies
The file is stateless and reads `boot_params->efi_info` plus optional `SETUP_EFI` setup_data. Dependencies are local EFI structure definitions in `efi.h`, `boot_params`, setup_data traversal, and direct physical mappings of EFI tables.

### Integration Points
ACPI RSDP discovery, unaccepted-memory table discovery, EFI soft reserve handling, and other compressed boot firmware consumers use these helpers.

### Risks
Firmware-provided table lengths and addresses are trusted enough to walk in early boot. x86_32 cannot access EFI structures above 4 GiB. kexec handling intentionally falls back to normal EFI paths when setup_data is missing or incomplete, so callers must handle zero results.

### Test Signals
Boot EFI32, EFI64, no-EFI, mixed high-address x86_32 failure, kexec with `SETUP_EFI`, and vendor table lookup for ACPI and unaccepted-memory GUIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/efi.h -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/efi.h

### Purpose
`compressed/efi.h` defines the compressed boot environment's private EFI types, GUIDs, memory descriptors, system table layouts, and soft-reserve helper declarations.

### Important APIs, Types, And Functions
It defines `efi_guid_t`, `EFI_GUID()`, ACPI and unaccepted-memory GUID constants, loader signatures, `efi_table_hdr_t`, memory types and attributes, `efi_memory_desc_t`, `efi_early_memdesc_ptr()`, 32-bit and 64-bit config/system table structures, `struct efi_unaccepted_memory`, `efi_guidcmp()`, and `efi_soft_reserve_enabled()`.

### Control Flow
This header has no runtime control flow beyond inline helpers. `efi_early_memdesc_ptr()` performs descriptor-size-indexed pointer arithmetic, `efi_guidcmp()` wraps `memcmp`, and `efi_soft_reserve_enabled()` gates the external soft-reserve query behind `CONFIG_EFI_SOFT_RESERVE`.

### State, Persistence, And Dependencies
No mutable state is owned here. It depends on basic integer types, `guid_t`, `memcmp`, and build-time `CONFIG_EFI`.

### Integration Points
Included by compressed `efi.c`, `acpi.c`, `kaslr.c`, `mem.c`, and `misc.h` so early code can inspect EFI data without pulling in kernel-proper EFI namespaces, which the header explicitly forbids.

### Risks
The private structure definitions must match UEFI layout exactly for both 32-bit and 64-bit firmware. Namespace guards prevent accidental inclusion conflicts with full kernel EFI headers.

### Test Signals
Compile EFI and non-EFI compressed boot, validate descriptor walking against known EFI memory maps, compare GUID matching for ACPI/unaccepted tables, and test soft-reserve filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/efi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/error.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/error.c

### Purpose
`compressed/error.c` centralizes fatal and warning reporting for compressed boot code.

### Important APIs, Types, And Functions
Exports are `warn()`, `error()`, and, when `CONFIG_EFI_STUB` is enabled, `panic()`.

### Control Flow
`warn()` prints blank lines, the message, and more spacing using `error_putstr()`. `error()` prints the warning, appends `-- System halted`, then halts forever with `hlt`. `panic()` formats a message with EFI libstub `vsnprintf()`, trims a trailing newline, and calls `error()`.

### State, Persistence, And Dependencies
There is no mutable state. Output goes through `misc.c` print routines, which may target serial and/or video. `panic()` depends on EFI stub formatting support.

### Integration Points
Compressed boot modules call `error()` for unrecoverable decompression, mapping, firmware, or memory-acceptance failures and `warn()` for degraded paths such as disabled KASLR.

### Risks
`error()` never returns, so callers must only use it for fatal states. Output availability depends on early console and video initialization state.

### Test Signals
Force invalid ELF, bad relocation, KASLR placement failure warnings, EFI panic formatting, and verify halt behavior and output routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/error.h -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/error.h

### Purpose
`compressed/error.h` declares compressed boot warning and fatal-error APIs with noreturn/cold annotations.

### Important APIs, Types, And Functions
It declares `warn(const char *m)`, `error(char *m) __noreturn`, and `panic(const char *fmt, ...) __noreturn __cold`.

### Control Flow
The header has no control flow; it supplies function contracts for callers and compiler analysis.

### State, Persistence, And Dependencies
No state is defined. It depends on `linux/compiler.h` for annotations.

### Integration Points
Included by compressed boot C files that need fatal diagnostics without depending directly on `misc.c` internals.

### Risks
The `error()` prototype takes `char *` rather than `const char *`, matching existing implementation but potentially requiring casts for literal-correct code. Noreturn annotations must match behavior.

### Test Signals
Compile all compressed boot objects with warnings enabled and check that noreturn paths suppress false fallthrough diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/head_32.S -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/head_32.S

### Purpose
`compressed/head_32.S` is the 32-bit compressed-kernel entry path. It relocates the compressed image to a safe buffer, clears BSS, calls `extract_kernel()`, and jumps to the decompressed kernel entry.

### Important APIs, Types, And Functions
Important symbols are `startup_32`, local `.Lrelocated`, `gdt`, `boot_stack`, and `boot_stack_end`. It uses boot protocol fields such as `BP_scratch`, `BP_kernel_alignment`, and `BP_init_size`, plus constants like `LOAD_PHYSICAL_ADDR` and `BOOT_STACK_SIZE`.

### Control Flow
`startup_32` disables interrupts, computes the load-time GOT delta with a local call/pop, installs a GDT, loads flat segments, chooses the decompression output address based on relocatability and alignment, computes a relocation target at the end of the init buffer, sets a stack, zeroes EFLAGS, copies the compressed image backward to prevent overlap corruption, reloads the GDT from its relocated copy, jumps to `.Lrelocated`, clears BSS, calls `extract_kernel(output, real_mode_pointer)`, and jumps to the returned entry with `%ebx` cleared.

### State, Persistence, And Dependencies
State includes relocated compressed text/data, boot stack, GDT descriptor, and cleared BSS. It depends on exact boot protocol register conventions, real/protected-mode setup having passed `boot_params` in `%esi`, and C `extract_kernel()`.

### Integration Points
Linked into compressed `vmlinux` for 32-bit kernels. The outer setup code transfers control here after protected-mode setup.

### Risks
The overlap-safe backward copy and output address calculations are critical. Wrong `init_size`, `_end`, or alignment values can overwrite the decompressor or payload. The startup address and ABI expectations are fixed by the x86 boot protocol.

### Test Signals
Boot 32-bit relocatable and non-relocatable kernels, vary load address and alignment, test multiple compression formats, and inspect early failures around BSS clearing or image overlap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/head_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/head_64.S -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/head_64.S

### Purpose
`compressed/head_64.S` implements both 32-bit and 64-bit entry paths for a 64-bit compressed kernel. It verifies long mode, builds early page tables, handles SEV setup, transitions to long mode when needed, relocates the decompressor, configures IDT and identity maps, calls `extract_kernel()`, and jumps to the decompressed kernel.

### Important APIs, Types, And Functions
Major symbols are `startup_32`, `startup_64`, `.Lrelocated`, `.Lno_longmode`, `verify_cpu`, `gdt64`, `gdt`, `boot_idt_desc`, `boot_idt`, `boot_stack`, `pgtable`, and `top_pgtable`. It calls `startup32_load_idt`, `get_sev_encryption_bit`, `startup32_check_sev_cbit`, `load_stage1_idt`, `sev_enable`, `configure_5level_paging`, `load_stage2_idt`, `initialize_identity_maps`, and `extract_kernel`.

### Control Flow
The 32-bit entry computes the runtime base, loads a GDT, sets segments and stack, installs SEV-ES IDT if configured, verifies long-mode CPU support, selects a decompression target, builds initial 4 GiB page tables with optional SEV C-bit mask, enables PAE and long mode, verifies C-bit correctness, and far-returns into `startup_64`. The 64-bit entry handles direct 64-bit bootloader entry, sets segments and stack, installs a GDT with a 32-bit code segment, preserves `boot_params` in `%r15`, loads stage-1 IDT, enables SEV handling, normalizes CR4, configures 5-level paging via trampoline if needed, relocates the compressed image backward, reloads GDT, jumps to relocated code, clears BSS, loads stage-2 IDT, initializes identity maps, calls `extract_kernel`, and jumps to the returned entry with `%rsi` restored to boot params.

### State, Persistence, And Dependencies
State spans page tables, GDT/IDT, boot stack, relocated image, SEV status globals, CR0/CR3/CR4/EFER, and preserved boot params. Dependencies include x86 boot ABI entry offsets, page table constants, SEV/TDX support objects, 5-level paging helpers, and compressed C runtime.

### Integration Points
This is the first compressed-kernel code for x86_64 regardless of 32-bit or 64-bit bootloader entry. It coordinates with `ident_map_64.c`, `idt_64.c`, `mem_encrypt.S`, SEV code, and `misc.c`.

### Risks
Mode transition ordering is extremely fragile: CPUID in encrypted guests needs handlers, CR4.LA57 cannot be changed directly in long mode, page-table encryption bits must be correct before memory access, and relocation must not overwrite live code. ABI entry offsets `0` and `0x200` are immutable.

### Test Signals
Boot via 32-bit and 64-bit entry, relocatable and fixed kernels, 4-level and 5-level paging, SEV/SEV-ES/SEV-SNP guests, KASLR on/off, and load addresses above 4 GiB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/head_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/ident_map_64.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/ident_map_64.c

### Purpose
`compressed/ident_map_64.c` builds and updates early identity mappings for x86_64 compressed boot, including fault-driven mapping expansion and encryption attribute changes for SEV/SNP.

### Important APIs, Types, And Functions
Exports include `kernel_add_identity_map()`, `initialize_identity_maps()`, `set_page_decrypted()`, `set_page_encrypted()`, `set_page_non_present()`, `do_boot_page_fault()`, and `do_boot_nmi_trap()`. Key state includes `pgt_data`, `top_level_pgt`, `physical_mask`, and `mapping_info`.

### Control Flow
`initialize_identity_maps()` initializes mapping callbacks, selects whether to append to existing boot page tables or allocate a new top-level table, maps the compressed image, boot params, command line, and setup_data chain, performs SEV/SNP preparation, loads CR3, and checks SNP features. `kernel_add_identity_map()` aligns ranges to PMD boundaries and delegates to generic identity mapping code. Page-attribute helpers ensure a mapped PTE exists, split large PMDs if needed, flush caches for encryption changes, update SNP RMP state, modify PTE flags, and reload CR3. `do_boot_page_fault()` validates the fault, rejects unexpected or GHCB faults, and identity maps the faulting 2 MiB range.

### State, Persistence, And Dependencies
State persists in early page tables under `_pgtable`, CR3, page-table allocation offsets, encryption mask handling, and `spurious_nmi_count`. Dependencies include `../../mm/ident_map.c`, low-level page table macros, SEV/SNP helpers, command-line pointer retrieval, setup_data traversal, and boot IDT handlers.

### Integration Points
`head_64.S` calls `initialize_identity_maps()` after loading the stage-2 IDT. SEV code calls page encryption helpers. `idt_handlers_64.S` routes page faults and NMIs into these handlers.

### Risks
Running out of `BOOT_PGT_SIZE` prevents required mappings and halts boot. Large-PMD splitting deliberately avoids a clear-then-flush sequence because the current code/stack may reside in the mapping. Encryption attribute changes must coordinate PTE flags, cache flushing, and SNP RMP transitions in the correct order.

### Test Signals
Boot with command line/setup_data above existing mappings, trigger early page faults, test SEV-SNP page shared/private transitions, exercise 5-level paging, and verify low page-table buffer warnings are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/ident_map_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/idt_64.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/idt_64.c

### Purpose
`compressed/idt_64.c` constructs and loads the minimal early IDT used by compressed boot for SEV #VC handling, page faults, and NMIs.

### Important APIs, Types, And Functions
Exports are `load_stage1_idt()`, `load_stage2_idt()`, and `cleanup_exception_handling()`. Helpers include `set_idt_entry()` and `load_boot_idt()`. It uses `boot_idt`, `boot_idt_desc`, and handler symbols from `idt_handlers_64.S`.

### Control Flow
`load_stage1_idt()` sets the IDT base and, for AMD memory encryption builds, installs a stage-1 #VC handler before loading IDT. `load_stage2_idt()` installs page-fault and NMI handlers, then either installs stage-2 #VC or clears the #VC entry based on `sev_status`. `cleanup_exception_handling()` shuts down the SEV GHCB, sets a null IDT descriptor, and loads it before jumping to the real kernel.

### State, Persistence, And Dependencies
State is the boot IDT array and descriptor. Dependencies include x86 gate descriptor layout, trap vector numbers, SEV status, and handler entry points.

### Integration Points
Called from `head_64.S` before SEV CPUID-sensitive code and before identity-map initialization. It connects assembly exception entry points to C handlers in `ident_map_64.c` and SEV code.

### Risks
Installing the wrong #VC handler stage can break SEV-ES/SNP boot because GHCB availability changes over time. Nulling exception handling too early would remove page-fault support; leaving it enabled when entering the real kernel could expose stale boot handlers.

### Test Signals
Boot plain x86_64, SEV, SEV-ES, and SEV-SNP guests, trigger early page faults, count spurious NMIs, and verify `cleanup_exception_handling()` runs before kernel entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/idt_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/idt_handlers_64.S -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/idt_handlers_64.S

### Purpose
`compressed/idt_handlers_64.S` defines early 64-bit exception entry stubs for compressed boot.

### Important APIs, Types, And Functions
The `EXCEPTION_HANDLER` macro emits handlers for `boot_page_fault`, `boot_nmi_trap`, and, under AMD memory encryption, `boot_stage1_vc` and `boot_stage2_vc`.

### Control Flow
Each handler optionally synthesizes a zero error code, pushes general-purpose registers into a `pt_regs`-like layout, passes `%rsp` as the first C argument and the saved error code as the second, calls the target C function, restores registers, removes the error code, and returns with `iretq`.

### State, Persistence, And Dependencies
The only state is the interrupt stack frame and saved registers on the current boot stack. It depends on `ORIG_RAX` layout from `entry/calling.h`, kernel code segment expectations, and handler prototypes.

### Integration Points
`idt_64.c` installs these symbols into the boot IDT. C handlers live in `ident_map_64.c` and SEV code.

### Risks
The synthetic `pt_regs` layout must match what C handlers expect. Error-code handling differs by vector and is encoded in macro arguments. Any stack alignment or register-save mismatch can corrupt early boot.

### Test Signals
Trigger page faults before identity mapping, inject or observe NMI handling, boot SEV-ES/SNP to exercise #VC paths, and inspect register preservation across handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/idt_handlers_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/kaslr.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/kaslr.c

### Purpose
`compressed/kaslr.c` implements early physical and virtual kernel address randomization. It gathers entropy, parses memory restrictions, builds avoid ranges, scans EFI/E820/KHO memory maps, and chooses a safe aligned load address for decompression.

### Important APIs, Types, And Functions
The exported function is `choose_random_location()`. Important helpers include `get_boot_seed()`, `parse_memmap()`, `mem_avoid_memmap()`, `parse_gb_huge_pages()`, `handle_mem_options()`, `mem_avoid_init()`, `mem_avoid_overlap()`, `store_slot_info()`, `process_gb_huge_pages()`, `slots_fetch_random()`, `__process_mem_region()`, `process_mem_region()`, `process_efi_entries()`, `process_e820_entries()`, `process_kho_entries()`, `find_random_phys_addr()`, and `find_random_virt_addr()`. State includes `mem_limit`, `memmap_too_large`, `mem_avoid`, `num_immovable_mem`, `slot_areas`, `slot_area_index`, `slot_max`, and `max_gb_huge_pages`.

### Control Flow
`choose_random_location()` exits early for `nokaslr`, sets `KASLR_FLAG`, initializes the memory limit, records avoid ranges for the compressed image, initrd, command line, boot params, setup_data, command-line `mem`/`memmap`, and ACPI immovable regions, then scans KHO scratch areas, EFI memory, or E820 RAM. Candidate regions are aligned, clipped by avoid overlaps, filtered for huge-page reservations and immovable memory when applicable, converted into slot counts, and one slot is chosen by `kaslr_get_random_long()`. On x86_64 it also chooses a randomized virtual address within `KERNEL_IMAGE_SIZE`.

### State, Persistence, And Dependencies
State persists only during the decompression decision plus `KASLR_FLAG` in boot params and updated output/virtual address values. Dependencies include shared KASLR entropy code, command-line parsing, ACPI immovable-memory detection, EFI memory descriptors, E820 table entries, setup_data, initrd boot fields, and decompressor image layout constants.

### Integration Points
`misc.c` calls `choose_random_location()` before accepting memory and decompressing. The chosen output and virtual address drive ELF relocation and final kernel entry behavior. ACPI, EFI, and KHO support feed candidate/avoid ranges.

### Risks
Incorrect avoid ranges can overwrite the compressed image, initrd, command line, setup_data, or preserved kexec handover memory. More than four unusable `memmap=` regions disables physical KASLR. EFI memory handling is conservative because some firmware expects boot-services memory untouched until later runtime transitions.

### Test Signals
Boot with `nokaslr`, multiple `mem=` and `memmap=` forms, initrd, command line near the kernel, setup_data chains including indirect entries, EFI memory maps with mirrored and soft-reserved memory, E820-only boots, KHO handover, 1 GiB huge page reservations, and memory hotremove SRAT filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/kaslr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/kernel_info.S -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/kernel_info.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mem.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mem.c

### Purpose
`compressed/mem.c` initializes and services early unaccepted-memory support for confidential-computing guests, accepting pages before decompression writes to them.

### Important APIs, Types, And Functions
Exports are `arch_accept_memory()` and `init_unaccepted_memory()`. The internal helper is `early_is_tdx_guest()`.

### Control Flow
`early_is_tdx_guest()` lazily checks CPUID for the TDX signature. `arch_accept_memory()` dispatches to `tdx_accept_memory()` for TDX, `snp_accept_memory()` for SEV-SNP, or halts for an unknown platform. `init_unaccepted_memory()` verifies EFI presence, retrieves EFI configuration table information, finds the Linux unaccepted-memory vendor table, validates version 1, and assigns the global `unaccepted_table` pointer.

### State, Persistence, And Dependencies
State includes cached TDX detection and the global `unaccepted_table` defined by EFI stub code. Dependencies include EFI helpers, TDX shared calls, SEV/SNP detection and acceptance, and boot params.

### Integration Points
`misc.c` calls `init_unaccepted_memory()` and, if true, `accept_memory(__pa(output), needed_size)` before decompression. EFI stub code may also initialize the table earlier, but this file reinitializes it for relocation cases.

### Risks
Calling acceptance on an unknown platform is fatal. CPUID detection happens before some later decompressor detection paths, so it must be safe for early users. Table version mismatch is fatal because memory-acceptance bitmap interpretation would be unsafe.

### Test Signals
Boot TDX with unaccepted memory, SEV-SNP with unaccepted memory, normal EFI without the table, non-EFI, bad table version, and relocation cases where EFI stub copied the image before setting the pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mem_encrypt.S -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mem_encrypt.S

### Purpose
`compressed/mem_encrypt.S` supplies early assembly support for AMD SME/SEV before the full decompressor C environment and SEV runtime are ready.

### Important APIs, Types, And Functions
Exported symbols include `get_sev_encryption_bit`, `startup32_load_idt`, `startup32_check_sev_cbit`, `sme_me_mask`, `sev_status`, and `sev_check_data`. Local helpers include `sev_es_req_cpuid`, `startup32_vc_handler`, and `startup32_set_idt_entry`. It also includes `sev_verify_cbit.S` for 64-bit verification.

### Control Flow
`get_sev_encryption_bit()` uses CPUID leaf `0x8000001f` and `MSR_AMD64_SEV` to return the active encryption C-bit position or zero. `startup32_vc_handler()` handles early SEV-ES #VC CPUID exits through the GHCB MSR protocol, validates critical CPUID responses, skips the trapped CPUID instruction, or terminates the guest. `startup32_load_idt()` installs that #VC handler into a small 32-bit IDT. `startup32_check_sev_cbit()` writes RDRAND values while paging is disabled, enables paging with the selected C-bit, compares memory against registers, and halts if the encryption bit is wrong.

### State, Persistence, And Dependencies
Persistent early state includes `sme_me_mask`, `sev_status`, the temporary 32-bit IDT, and C-bit check data. Dependencies include CPUID, MSRs, GHCB MSR protocol, RDRAND, boot GDT selectors, trap numbers, and the 64-bit SEV verification include.

### Integration Points
`head_64.S` calls these routines while building encrypted page tables and before entering long-mode decompressor code. Later C SEV code reads and refines `sev_status` and `sme_me_mask`.

### Risks
This code runs before ordinary exception handling. Bad C-bit selection makes memory unreadable and intentionally halts. The early #VC handler only supports CPUID exits needed during startup; unexpected exits terminate the guest.

### Test Signals
Boot SME, SEV, SEV-ES, and SEV-SNP guests through the 32-bit entry path, test hypervisor CPUID response validation, verify C-bit mismatch failure under instrumentation, and boot non-SEV systems where the routines return zero/no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mem_encrypt.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/misc.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/misc.h -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/misc.h

### Purpose
`compressed/misc.h` is the central header for compressed boot C code. It defines the constrained environment, physical/virtual address assumptions, debug output macros, shared structures, and cross-module prototypes.

### Important APIs, Types, And Functions
It undefines unsupported instrumentation/paravirt options, defines `__NO_FORTIFY`, `USE_EARLY_PGTABLE_L5`, identity `__pa()`/`__va()`, `memptr`, `struct mem_vector`, debug/error output macros, and prototypes for malloc/free, command-line parsing, KASLR, CPU flags, early serial, SEV/SNP helpers, ACPI, identity maps, IDT cleanup, EFI helpers, unaccepted memory, and `accept_memory()`.

### Control Flow
The header itself only provides inline stubs and macros selected by Kconfig. Disabled features collapse to no-op helpers such as empty `console_init()`, zero `get_rsdp_addr()`, no-op SEV hooks, and false `init_unaccepted_memory()`.

### State, Persistence, And Dependencies
It declares shared state including `_head`, `_end`, `free_mem_ptr`, `free_mem_end_ptr`, `spurious_nmi_count`, `early_serial_base`, `_pgtable`, `boot_idt`, `boot_idt_desc`, `__default_kernel_pte_mask`, and `unaccepted_table`. Dependencies include boot protocol structures, page/descriptor types, local EFI definitions, TDX headers, ACPI definitions, and boot I/O helpers.

### Integration Points
Nearly every compressed boot C file includes this header. It is the compile-time compatibility layer that lets early code call into optional firmware, encryption, page table, and console subsystems without full kernel initialization.

### Risks
The identity `__pa()`/`__va()` assumptions are valid only in the boot stub's identity-mapped phase. Undefining config features must stay synchronized with what the compressed runtime can safely use. Stubs can hide missing object inclusion if Kconfig guards are wrong.

### Test Signals
Build compressed boot under broad Kconfig combinations, especially with optional EFI, ACPI, SEV, TDX, early printk, KASLR, and unaccepted-memory support disabled and enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mkpiggy.c -->
## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mkpiggy.c

### Purpose
`compressed/mkpiggy.c` is a host utility that converts a compressed kernel binary into assembly containing the payload and length symbols needed by the decompressor.

### Important APIs, Types, And Functions
The only function is `main()`. It uses `get_unaligned_le32()` from `tools/le_byteshift.h` and standard C file APIs.

### Control Flow
`main()` requires a compressed-file path, opens it, seeks to the final four bytes, reads the appended uncompressed output length, records the current file length as input length, converts the output length from little endian, and prints assembly defining `.rodata..compressed`, `z_input_len`, `z_output_len`, `input_data`, `input_data_end`, `input_len`, and `output_len` with an `.incbin` directive for the compressed file.

### State, Persistence, And Dependencies
The persistent output is generated assembly on stdout, normally redirected by kbuild to `piggy.S`. It depends on compressor outputs using the kernel `size_append` convention where the uncompressed size is stored in the last four bytes.

### Integration Points
`boot/compressed/Makefile` builds and runs this host program after compression. `misc.c` consumes the generated `input_data`, `input_len`, and `output_len` symbols.

### Risks
The utility assumes the input is seekable and at least four bytes long. Paths are emitted directly in `.incbin`, so build paths with unusual quoting could matter. Any compressor format change to the trailing size convention must update this utility.

### Test Signals
Run on each supported `vmlinux.bin.*` format, verify generated symbol values against file size and appended length, and build with paths containing spaces or special characters if supported by the build environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mkpiggy.c -->
