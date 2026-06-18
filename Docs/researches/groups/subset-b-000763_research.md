# subset-b-000763 research

Grouped research for the requested source-tree-aligned files. Each section is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit.h -->
# sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit.h

## Purpose
Common PA-RISC eBPF JIT header shared by the 32-bit and 64-bit emitters. It defines the HPPA register numbers, JIT context/data structures, instruction encoding helpers, branch-offset helpers, cache/fill hooks, and the architecture-specific emitter/prologue/epilogue interfaces used by `bpf_jit_core.c`.

## Important APIs, Types, And Control Flow
`struct hppa_jit_context` carries the current `bpf_prog`, generated HPPA instruction buffer, instruction count, BPF-to-native offsets, prologue/body/epilogue lengths, and register-use collection flags. `struct hppa_jit_data` stores the allocated `bpf_binary_header`, executable image pointer, and context between multi-pass JIT phases. The header exposes `bpf_jit_build_prologue()`, `bpf_jit_build_epilogue()`, `bpf_jit_emit_insn()`, `hppa_div64()`, and `hppa_div64_rem()`.

Most macros encode PA-RISC instructions such as loads/stores, ALU ops, control-register moves, conditional branches, and long branches using `hppa_t*` format builders. `emit()` appends or counts one 4-byte HPPA instruction, allowing sizing passes and final emission to share code. `hppa_offset()` translates a BPF branch target into a native instruction delta using the collected offset table.

## State, Dependencies, Risks, And Tests
State is transient JIT state in `hppa_jit_context`; persistent output is the executable instruction image. Dependencies include Linux BPF/filter APIs, PA-RISC cache flushing, `REG_SZ`, and the arch emitters. The highest risks are incorrect bit reassembly for PA-RISC immediates, wrong branch displacement accounting around delay slots, and stale register-use collection causing prologue/epilogue save omissions. Test signals include BPF selftests with short/far jumps, JIT dumps compared against expected PA-RISC encodings, 32/64-bit builds, and icache-flush execution tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_comp32.c -->
# sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_comp32.c

## Purpose
32-bit PA-RISC eBPF JIT backend. It lowers eBPF instructions onto a 32-bit big-endian HPPA ABI where 64-bit eBPF registers are represented as high/low 32-bit pairs, with some eBPF registers spilled into JIT scratch stack slots.

## Important APIs, Types, And Control Flow
The main exported entry points are `bpf_jit_emit_insn()`, `bpf_jit_build_prologue()`, and `bpf_jit_build_epilogue()`. The local `regmap` maps BPF registers to HPPA register pairs or negative stack offsets. Register helpers (`bpf_get_reg64()`, `bpf_put_reg64()`, `bpf_get_reg32()`, `bpf_put_reg32()`) load stacked values into temporary pairs and store them back. ALU helpers split 64-bit arithmetic into carry/borrow operations or call libgcc helpers (`__muldi3`, shifts) and PA-RISC millicode (`$$mulI`, `$$divU`, `$$remU`).

`bpf_jit_emit_insn()` dispatches eBPF opcodes: ALU/ALU64, endian swaps, direct branches, conditional 32/64-bit branches, helper calls, tail calls, loads/stores, and unsupported atomics. Branch helpers invert conditions for far branches and compensate for extra emitted instructions. The prologue sizes a PA-RISC stack frame, initializes the tail-call counter, saves only seen callee-saved registers where possible, copies incoming eBPF arguments from the HPPA ABI, and records an epilogue jump pointer. The epilogue restores saved registers and returns the low word of `BPF_REG_0`.

## State, Dependencies, Risks, And Tests
State lives in generated stack layout: saved HPPA registers, BPF scratch register pairs, BPF stack, tail-call counter, and an epilogue pointer. Dependencies include `bpf_jit.h`, Linux libgcc helpers, BPF verifier zero-extension metadata, PA-RISC millicode, and BPF array/program layouts for tail calls. Risks include high/low word ordering, big-endian load/store offsets, division-by-zero skip paths, far branch convergence, tail-call prologue skipping, and save elision based on `reg_seen`. Test with BPF ALU64 selftests, jmp32/jmp64 comparisons, helper-call argument preservation, tail-call exhaustion, unaligned/large-offset memory accesses, and unsupported atomic rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_comp32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_comp64.c -->
# sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_comp64.c

## Purpose
64-bit PA-RISC eBPF JIT backend. It maps eBPF registers to native 64-bit HPPA registers, emits PA-RISC 2.0 wide-mode instructions, handles PA-RISC function descriptors, and advertises kfunc-call support.

## Important APIs, Types, And Control Flow
`bpf_jit_emit_insn()` is the opcode dispatcher. It uses `init_regs()` to map BPF operands, emits native ALU operations where possible, and calls libgcc/division helpers for multiply, division, modulo, and 64-bit helper arithmetic paths. Immediate emission uses `emit_imm32()` and `emit_imm()` to synthesize 64-bit constants. Shift/extract/deposit helpers (`emit_hppa64_depd`, `emit_hppa64_extrd`, `emit_hppa64_shld`, `emit_hppa64_shrd`) implement zero/sign extension, shifts, and endian conversion.

Control flow is built by `emit_branch()` and `emit_jump()`. Near conditional branches reserve two no-ops to stabilize sizing; far branches invert the condition and jump over a long branch. Helper calls marshal BPF arguments to PA-RISC ABI argument registers and load code address/gp from `elf64_fdesc`. Tail calls validate index, decrement the tail-call counter, load `prog->bpf_func`, and jump past the target prologue initializer.

## State, Dependencies, Risks, And Tests
Persistent output is the executable JIT image plus its inline function descriptor words in the prologue. Runtime state includes the upward-growing HPPA stack frame, saved callee registers, BPF stack, tail-call counter, gp, and epilogue pointer. Dependencies include `struct elf64_fdesc`, BPF aux verifier-zext metadata, libgcc helpers, BPF array layout, and PA-RISC 64 kernel address constraints below 4GB for some branch materialization. Risks include function descriptor/gp corruption, 32-bit ALU zero-extension, branch-size convergence, unaligned doubleword load/store handling, probe-memory load behavior, and the extra epilogue nop noted in-source. Test with BPF selftests under 64-bit PA-RISC, kfunc/helper calls, pseudo-function immediates, tail calls, endian swaps, jmp32 signed/unsigned cases, and large JIT images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_comp64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_core.c -->
# sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_core.c

## Purpose
Shared PA-RISC eBPF JIT compilation driver. It runs sizing/convergence passes, allocates executable memory, invokes architecture-width-specific emitters, patches line info, locks the image read-only, and exposes 64-bit division helpers used by emitters.

## Important APIs, Types, And Control Flow
`build_body()` iterates BPF instructions, calls `bpf_jit_emit_insn()`, skips the second half of `BPF_LD | BPF_IMM | BPF_DW`, and records BPF-to-native offsets. `bpf_jit_needs_zext()` returns true. `bpf_int_jit_compile()` owns the compile lifecycle: honor `jit_requested`, allocate/reuse `prog->aux->jit_data`, seed rough offsets, iterate up to `NR_JIT_ITERATIONS`, compute prologue/body/epilogue sizes, allocate `bpf_jit_binary_alloc()` once size converges, emit final code, set extable storage, optionally dump/reboot for debug, lock RO, flush icache, set `prog->bpf_func`, and fill jited line info.

`hppa_div64()` and `hppa_div64_rem()` wrap generic kernel 64-bit divide helpers for generated code.

## State, Dependencies, Risks, And Tests
State is `prog->aux->jit_data` during compilation and final `prog->bpf_func`, `jited`, `jited_len`, `extable`, and jited line info after success. Dependencies include Linux BPF JIT allocation/locking APIs, verifier env, exception table sizing, and the arch-specific emitter functions. Risks include non-converging image sizes, freeing `jit_data` during subprogram extra passes, extable placement after code, incorrect prologue offset adjustment in line info, and failure cleanup for extra-pass functions. Test with BPF JIT selftests, subprogram calls requiring extra pass, exception-table programs, forced allocation failure, branch-heavy programs that stress convergence, and `bpf_jit_enable > 1` dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/video/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/video/Makefile

## Purpose
Minimal PA-RISC video build glue. It adds `video-sti.o` to the architecture video objects when `CONFIG_STI_CORE` is enabled.

## Important APIs, Types, And Control Flow
There are no functions or runtime control paths. The single object rule `obj-$(CONFIG_STI_CORE) += video-sti.o` binds PA-RISC STI firmware framebuffer integration to the STI core Kconfig symbol.

## State, Dependencies, Risks, And Tests
State is build-system selection only. Dependencies are kbuild and `CONFIG_STI_CORE`. Risks are accidental omission of `video-sti.o` from STI-enabled kernels or unwanted inclusion when STI is disabled. Test signals are PA-RISC builds with `CONFIG_STI_CORE=y/m/n` and symbol availability for `video_is_primary_device`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/video/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/video/video-sti.c -->
# sources/distributed-fs/ceph-client/arch/parisc/video/video-sti.c

## Purpose
PA-RISC helper that decides whether a framebuffer device is the primary display when STI firmware graphics are present.

## Important APIs, Types, And Control Flow
`video_is_primary_device(struct device *dev)` is exported for framebuffer/video drivers. It calls `sti_get_rom(0)` to find the default built-in STI graphics device. If no STI ROM exists, it returns true so any framebuffer can become default. If STI exists, it returns true only when `sti->dev == dev`.

## State, Dependencies, Risks, And Tests
The function does not persist state; it reads STI core global/device discovery state. Dependencies include `<video/sticore.h>`, `<asm/video.h>`, and module export infrastructure. Risks include NULL/default-ROM ambiguity, stale `sti->dev`, and multi-adapter systems choosing the wrong primary display. Test signals are PA-RISC boots with no STI, one built-in STI framebuffer, and additional non-primary framebuffers; also module symbol resolution for framebuffer drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/video/video-sti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/Kbuild -->
# sources/distributed-fs/ceph-client/arch/powerpc/Kbuild

## Purpose
Top-level kbuild directory selection for the PowerPC architecture.

## Important APIs, Types, And Control Flow
The file applies `-Werror`/assembler fatal warnings when `CONFIG_PPC_WERROR` is set, always descends into core directories (`kernel`, `mm`, `lib`, `sysdev`, `platforms`, `math-emu`, `crypto`, `net`), and conditionally descends into `xmon`, `kvm`, `perf`, `kexec`, and `purgatory`. `subdir- += boot tools` ensures cleaning reaches non-recursive utility directories.

## State, Dependencies, Risks, And Tests
State is build graph only. Dependencies are Kconfig symbols and kbuild recursion. Risks include omitted subdirectories causing missing object files, or `CONFIG_PPC_WERROR` making older toolchains fail. Test signals are allnoconfig/defconfig/allmodconfig PowerPC builds, clean targets removing boot/tool artifacts, and toggling optional features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/Kconfig

## Purpose
Main PowerPC architecture configuration file. It declares architecture capabilities, compiler feature probes, memory layout defaults, security/trace/debug options, page-size choices, bus options, and includes platform/sysdev/kvm/livepatch configuration.

## Important APIs, Types, And Control Flow
The `PPC` symbol selects a large set of generic kernel features: ELF, BPF JIT, seccomp, ftrace, KASAN/KCSAN support, memory hotplug, VDSO, PCI/IOMMU helpers, module format, and PowerPC-specific facilities. Early feature probes include `CC_HAS_ELFV2`, `CC_HAS_PREFIXED`, and `CC_HAS_PCREL`. The file controls `32BIT`, `64BIT`, `MMU`, address-space randomization bits, IRQ counts, compatibility mode, DCR support, debug register counts, math emulation, transactional memory, ultravisor support, ftrace modes, hotplug CPU, crash dump, NUMA, memory models, page size, command-line policy, secure boot, bus options, and advanced 32-bit memory layout overrides.

Kconfig flow is declarative: defaults and dependencies derive architecture behavior, while `source` statements include cputype, sysdev, platforms, power management, kvm, and livepatch menus.

## State, Dependencies, Risks, And Tests
Persistent state is generated `.config` and derived headers. Dependencies span compiler/linker feature tests, platform symbols, generic kernel Kconfig, and PowerPC platform Kconfigs. Risks are unsatisfied `select` chains, impossible option combinations, page/layout defaults that produce broken early mappings, and compiler probe drift for pcrel/prefixed/ftrace. Test signals are `olddefconfig`, `randconfig`, representative ppc32/ppc64/ppc64le defconfigs, Kconfig warning-free runs, and build/boot coverage for page-size, crash, NUMA, secure boot, and tracing combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/Makefile

## Purpose
PowerPC architecture makefile. It sets cross-compiler defaults, ABI/endian/compiler/linker flags, default configs, boot image targets, generated defconfigs, VDSO preparation, stack protector guard flags, and a binutils guard.

## Important APIs, Types, And Control Flow
The file auto-detects `CROSS_COMPILE`, exports `BITS`, constructs `UTS_MACHINE`, sets endian flags, handles ELFv1/ELFv2 ABI flags, module save/restore linkage, relocatable link flags, model flags, ftrace instrumentation flags, CPU tuning, no-FPU/no-vector kernel flags, and pcrel/prefixed options. The default build target is `zImage`; boot targets recurse into `arch/powerpc/boot`. Generated defconfig targets merge fragments for pseries, powernv, 85xx, corenet, ppc32/ppc64 rand/allmod configs, and others. `prepare` builds VDSO offsets after `prepare0`, and stack protector preparation derives TLS guard offsets from generated asm offsets.

## State, Dependencies, Risks, And Tests
State is the kbuild variable environment and generated configuration targets. Dependencies include toolchain option probes, linker type/version, `scripts/Makefile.defconf`, arch configs, VDSO makefiles, and generated `asm-offsets.h`. Risks include wrong endian/ABI flags, clang/gcc divergence, module TOC model breakage, ftrace flag mismatch, broken cross32 boot wrapper builds, and binutils 2.37 recordmcount incompatibility. Test signals are ppc64le/ppc64/ppc32 builds with GCC and clang, module builds, boot wrapper targets, generated defconfigs, VDSO offset generation, and `checkbin` failure on known-bad linker combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/44x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/44x.h

## Purpose
Small boot-wrapper header declaring board initialization helpers shared by 44x cuboot/treeboot wrappers.

## Important APIs, Types, And Control Flow
It declares `ebony_init(void *mac0, void *mac1)` and `bamboo_init(void *mac0, void *mac1)`. These functions initialize FDT and serial console state and install board-specific fixup/exit callbacks.

## State, Dependencies, Risks, And Tests
State is owned by the implementation files that cache MAC-address pointers and set `platform_ops`. Dependencies are boot-wrapper types and the matching board implementation objects. Risks are prototype drift with board files and missing object inclusion under `CONFIG_44x`. Test by building Ebony and Bamboo wrapper targets and booting with U-Boot board-info MACs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/44x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/4xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/4xx.c

## Purpose
PowerPC 4xx/44x boot-wrapper support for memory-size discovery, clock fixups, EBC ranges, Ethernet quiesce, and reset handling before the decompressed kernel starts.

## Important APIs, Types, And Control Flow
Memory helpers include `ibm4xx_sdram_fixup_memsize()`, `ibm440spe_fixup_memsize()`, and `ibm4xx_denali_fixup_memsize()`, which read SDRAM/MQ/Denali DCRs, account for selected chip errata, and call `dt_fixup_memory()`. Clock helpers (`ibm440gp_fixup_clocks()`, `ibm440ep_fixup_clocks()`, `ibm440gx_fixup_clocks()`, `ibm440spe_fixup_clocks()`) derive CPU/PLB/OPB/EBC/UART/timebase frequencies from CPC/CPR/SDR registers and write device-tree clock properties. `ibm4xx_fixup_ebc_ranges()` builds an EBC `ranges` property from active chip-select registers. `ibm4xx_quiesce_eth()` resets EMAC/MAL, and `ibm44x_dbcr_reset()` requests a system reset through DBCR0.

## State, Dependencies, Risks, And Tests
The file mutates the live flattened device tree and writes hardware DCR/Special Purpose Registers. Dependencies include `dcr.h`, `reg.h`, device-tree ops, and board wrappers that pass clock constants and node paths. Risks include wrong hard-coded sysclk/timer inputs, Denali chip-select workarounds for Sequoia/Rainier, overflow in memory-size arithmetic, incorrect EBC range packing, and hangs waiting for MAL reset. Test with 4xx board wrapper builds/boots, FDT property inspection, clock frequency validation against firmware, and memory sizing on SDRAM, MQ, and Denali controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/4xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/4xx.h

## Purpose
Public boot-wrapper declarations for the 4xx helper routines implemented in `4xx.c`.

## Important APIs, Types, And Control Flow
The header declares memory fixups, reset/quiesce helpers, EBC range fixup, and 440GP/EP/GX/SPE clock fixups. There is no runtime logic in the header; it is the integration contract for board-specific wrappers.

## State, Dependencies, Risks, And Tests
State is managed by `4xx.c` through hardware registers and FDT updates. Dependencies are `u32` types from boot-wrapper headers and object inclusion under `CONFIG_44x`. Risks are stale declarations causing build failures or board wrappers calling helpers not linked for a given config. Test by compiling all 4xx wrapper targets and checking each declared helper resolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/4xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/Makefile

## Purpose
Build system for PowerPC boot wrappers and image formats. It compiles the small pre-kernel runtime, copies decompressor/libfdt sources, selects platform wrappers, invokes the `wrapper` script, and installs boot-wrapper utilities.

## Important APIs, Types, And Control Flow
The makefile defines `BOOTCC`, `BOOTAR`, 32/64-bit boot target flags, soft-float/no-vector flags, generated zlib/libfdt source copies, boot wrapper library sources (`src-wlib-*`), platform sources (`src-plat-*`), host utilities (`addnote`, `hack-coff`, `mktree`), wrapper targets, compressor selection, board image lists, initrd variants, and install targets. Pattern rules build `zImage`, `uImage`, `cuImage`, `dtbImage`, `simpleImage`, and `treeImage` variants, optionally embedding DTBs and initrds.

## State, Dependencies, Risks, And Tests
State is generated object/image files under `arch/powerpc/boot`, copied decompressor/libfdt sources, installed wrapper assets, and symlinked `zImage`. Dependencies include kbuild, DTC output, `wrapper`, libfdt, kernel compression selections, board Kconfig symbols, and cross32 tools. Risks include wrong `-m32/-m64` wrapper ABI, missing copied headers, stale clean-files, DTB path ambiguity between `dts/` and `dts/fsl/`, and default image fallback to `vmlinux.strip` when no platform image is selected. Test with representative `zImage`, `uImage`, `cuImage.*`, `dtbImage.*`, initrd, install, and clean targets for ppc32, ppc64, and ppc64 boot-wrapper configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/addnote.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/addnote.c

## Purpose
Host utility that patches an ELF zImage with CHRP and IBM RPA `PT_NOTE` program headers so Open Firmware on RS/6000-style systems loads it correctly.

## Important APIs, Types, And Control Flow
`main()` opens an ELF file read/write, reads the first 1024 bytes, detects ELF class and endianness, validates program-header layout, checks no `PT_NOTE` already exists, finds zero-filled space after existing headers, writes two new program headers, writes the PowerPC CHRP note and RPA client-config note, increments `e_phnum`, then writes the buffer back. The macros `GET_*` and `PUT_*` abstract ELF32/ELF64 and big/little endian fields.

## State, Dependencies, Risks, And Tests
It mutates the target ELF file in place and assumes all required header/note space is within the initial 1024-byte buffer. Dependencies are POSIX file APIs and ELF layout constants encoded locally. Risks include insufficient zero padding, a likely footgun around the first/second note file-size fields, only partially validating program headers, and host-endian mistakes in note descriptors that are intentionally big-endian. Test with ELF32/ELF64, BE/LE images, images already containing `PT_NOTE`, images without slack space, and `readelf -l -n` validation after patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/addnote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/bamboo.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/bamboo.c

## Purpose
Native Bamboo 440EP boot-wrapper board initialization and FDT fixups.

## Important APIs, Types, And Control Flow
`bamboo_init(void *mac0, void *mac1)` stores firmware MAC-address pointers, sets `platform_ops.fixups` to `bamboo_fixups`, sets `platform_ops.exit` to `ibm44x_dbcr_reset`, initializes the FDT with `_dtb_start`, and initializes serial console. `bamboo_fixups()` applies fixed clock inputs, SDRAM memory sizing, EMAC/MAL quiesce, and MAC-address properties for `ethernet0` and `ethernet1`.

## State, Dependencies, Risks, And Tests
Persistent boot-wrapper state is the cached MAC pointers and `platform_ops` callbacks; external state is FDT mutation and hardware quiesce. Dependencies include `4xx.c`, `44x.h`, DCR helpers, and device-tree ops. Risks include hard-coded clock values, invalid MAC pointers copied from firmware board info, and reset/quiesce behavior on firmware variants. Test with Bamboo cu/tree images, FDT clock/memory/MAC property inspection, and reboot path through DBCR reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/bamboo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cpm-serial.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cpm-serial.c

## Purpose
Boot-wrapper serial console driver for Freescale CPM1/CPM2 SMC/SCC UARTs, assuming firmware has already configured basic port parameters.

## Important APIs, Types, And Control Flow
Hardware structs model SMC/SCC registers, CPM parameter RAM, and buffer descriptors. `cpm_console_init()` detects compatible strings, selects CPM1/CPM2 command format and SMC/SCC enable/disable functions, maps registers via `virtual-reg` or translated `reg`, finds MURAM data space, places RX/TX buffer descriptors at the end of the first MURAM chunk, relocates CPM2 SMC parameter RAM if needed, and fills `serial_console_data` callbacks. `cpm_serial_open()` initializes parameter RAM and BDs, issues `INIT_RX_TX`, and enables the port. `putc`, `getc`, and `tstc` poll BD ownership bits with sync/eieio ordering.

## State, Dependencies, Risks, And Tests
State is global pointers to CPM registers, parameter RAM, BDs, command value, MURAM offsets, and selected function callbacks. Dependencies include boot-wrapper device-tree translation, MMIO endian accessors, and CPM-compatible DT properties. Risks include malformed MURAM/reg properties, CPM command busy-wait hangs, BD placement clobbering firmware data, cache/order bugs, and unsupported compatible strings. Test with CPM1 SMC, CPM2 SMC, and CPM2 SCC device trees, console input/output before decompression, relocated parameter RAM validation, and failure paths returning `-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cpm-serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/crt0.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/crt0.S

## Purpose
PowerPC boot-wrapper entry assembly. It self-relocates PIE-linked wrappers, flushes instruction/data caches, clears BSS, optionally switches stacks, calls `platform_init()`, then branches to the wrapper `start` routine. On ppc64 it also provides an Open Firmware call trampoline.

## Important APIs, Types, And Control Flow
`_zimage_start`/`_zimage_start_lib` compute the runtime base with `bcl/mflr`. The 32-bit path parses `_DYNAMIC`, locates RELA entries, applies `R_PPC_RELATIVE`, flushes text cache lines, clears BSS with stores, and optionally uses `_platform_stack_top`. The 64-bit path saves the PROM pointer, sets r2 TOC, processes `R_PPC64_RELATIVE`, flushes caches, clears BSS, and sets a 64-bit stack frame. Both paths call `platform_init` and branch to `start`. The ppc64 `prom` label saves registers/MSR, switches endian/firmware state through `rfid`, calls firmware via saved PROM entry, then restores state.

## State, Dependencies, Risks, And Tests
State includes relocated data, BSS, runtime stack pointer, TOC, saved PROM pointer, and the register/MSR frame for firmware calls. Dependencies include linker-provided symbols, relocation format, `ppc_asm.h`, cache-line assumptions, and platform wrapper ABI. Risks include relocation parser mismatch, BSS clearing wrong width, cache flush range errors, endian/MSR restore bugs, and stack-frame ABI violations. Test by booting PIE/non-PIE wrappers, ppc32 and ppc64 Open Firmware paths, custom platform stack configs, and firmware calls returning across endian boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/crt0.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/crtsavres.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/crtsavres.S

## Purpose
32-bit PowerPC boot-wrapper runtime support routines for compiler-generated GPR save/restore calls, derived from GCC rs6000 support. PPC64 intentionally uses linker-provided routines instead.

## Important APIs, Types, And Control Flow
The file defines `_savegpr_14` through `_savegpr_31` and `_save32gpr_*` aliases, storing r14-r31 at fixed negative offsets from r11. It defines `_restgpr_14` through `_restgpr_31` and `_rest32gpr_*` aliases, loading the same offsets. The `_restgpr_*_x` variants restore registers, load LR from `4(r11)`, move r11 back to r1, and return for epilogue-with-exit sequences.

## State, Dependencies, Risks, And Tests
State is the caller stack save area addressed by r11 and, for `_x` variants, LR and SP. Dependencies include the PowerPC EABI/SVR4 ABI, GCC code generation, and boot-wrapper linking when not using `CONFIG_PPC64_BOOT_WRAPPER`. Risks are offset/ABI mismatch, accidental ppc64 inclusion, and missing symbols under compiler options that emit save/restore calls. Test by compiling wrapper C with register pressure, linking without unresolved `_savegpr`/`_restgpr` symbols, and booting paths that exercise non-leaf functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/crtsavres.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-52xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-52xx.c

## Purpose
Compatibility wrapper for old non-device-tree-aware U-Boot on MPC5200 systems.

## Important APIs, Types, And Control Flow
`platform_init()` copies U-Boot `bd_t` via `CUBOOT_INIT()`, initializes the embedded DTB and serial console, and installs `platform_fixups()`. The fixup updates memory, MAC address, CPU/timebase/bus clocks, finds the SoC node by devtype or compatible string, writes IPB bus frequency, translates SoC registers, reads the divider at offset `0x204`, and writes `system-frequency`.

## State, Dependencies, Risks, And Tests
State is copied board info, loader info from `cuboot_init()`, allocator state, and FDT properties. Dependencies include MPC52xx `ppcboot.h` layout, device-tree helper APIs, and MMIO accessors. Risks include DT node name/compatible mismatch, incorrect divider detection, endian of `bd_t` fields, and invalid translated SoC register. Test with MPC5200/MPC5200B DTBs, old U-Boot initrd/cmdline inputs, and FDT memory/clock/MAC validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-52xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-824x.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-824x.c

## Purpose
Old U-Boot compatibility wrapper for 824x systems.

## Important APIs, Types, And Control Flow
`platform_init()` performs `CUBOOT_INIT()`, initializes FDT and serial console, and registers `platform_fixups()`. The fixup writes memory, MAC addresses, CPU/timebase/bus clocks, finds the SoC node, writes `bus-frequency`, and updates child serial nodes' `clock-frequency` to the bus clock.

## State, Dependencies, Risks, And Tests
State is copied `bd_t`, loader metadata, and FDT updates. Dependencies include `TARGET_824x` board-info layout and generic DT fixup helpers. Risks include SoC/serial node discovery errors and assuming serial clocks equal `bi_busfreq`. Test by building `cuImage` for 824x and checking memory, serial clock, and bootargs/initrd handoff on old U-Boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-824x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-83xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-83xx.c

## Purpose
Old U-Boot compatibility wrapper for Freescale 83xx boards.

## Important APIs, Types, And Control Flow
The wrapper copies board info, initializes FDT/serial, and installs `platform_fixups()`. The fixup updates memory, Ethernet aliases `ethernet0` and `ethernet1`, CPU/timebase/bus clocks using `bi_busfreq / 4`, sets the SoC `bus-frequency`, and updates direct child serial clock properties.

## State, Dependencies, Risks, And Tests
State is `bd_t bd`, loader info, allocator state, and mutated FDT properties. Dependencies include 83xx `ppcboot.h`, serial nodes under a SoC node, and DT alias conventions. Risks include old DTs without aliases, wrong serial parent filtering, and clock divisor assumptions. Test with 83xx board DTBs and old U-Boot boot paths, validating serial console frequency and MAC properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-83xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-85xx-cpm2.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-85xx-cpm2.c

## Purpose
Old U-Boot compatibility wrapper for 85xx boards with CPM2.

## Important APIs, Types, And Control Flow
`platform_fixups()` updates memory, Ethernet aliases 0-2, CPU/timebase/bus clocks using `bi_busfreq / 8`, SoC `bus-frequency`, direct child serial clocks, and `fsl,cpm2-brg` `clock-frequency` from `bi_brgfreq`. `platform_init()` uses `CUBOOT_INIT()`, initializes FDT/serial, and registers the fixup.

## State, Dependencies, Risks, And Tests
State includes copied CPM2-capable board info and FDT properties. Dependencies include `TARGET_85xx`, `TARGET_CPM2`, DT compatible strings, and serial/CPM nodes. Risks include absent CPM BRG node, missing third Ethernet alias, bus-frequency divisor mistakes, and stale U-Boot board-info values. Test with CPM2 85xx cuImages, serial console, CPM BRG consumers, and FDT property inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-85xx-cpm2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-85xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-85xx.c

## Purpose
Old U-Boot compatibility wrapper for non-CPM2 Freescale 85xx systems with up to four Ethernet addresses.

## Important APIs, Types, And Control Flow
The wrapper defines `TARGET_85xx` and `TARGET_HAS_ETH3`. `platform_fixups()` updates memory, Ethernet aliases 0-3, CPU/timebase/bus clocks, SoC `bus-frequency`, and direct child serial clock properties. `platform_init()` copies board info via `CUBOOT_INIT()`, initializes FDT and serial console, and assigns the fixup callback.

## State, Dependencies, Risks, And Tests
State is board info, loader info, allocator, and FDT. Dependencies include alias naming, 85xx board-info layout, and serial nodes under the SoC. Risks include invalid fourth MAC on boards without ETH3, wrong timebase divisor, and old DT node naming. Test with 85xx board cuImages, four-port and fewer-port DTBs, and serial clock/MAC validation after fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-85xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-8xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-8xx.c

## Purpose
Old U-Boot compatibility wrapper for 8xx systems with CPM.

## Important APIs, Types, And Control Flow
`platform_fixups()` updates memory, two MAC addresses, CPU/timebase/bus clocks using `bi_busfreq / 16`, and CPM/BRG clock properties under `/soc/cpm` and `/soc/cpm/brg`. `platform_init()` copies board info, initializes the embedded DTB and serial console, and registers the fixup.

## State, Dependencies, Risks, And Tests
State is copied 8xx board info, loader info, and FDT mutations. Dependencies include `TARGET_8xx`, `TARGET_HAS_ETH1`, CPM DT paths, and generic DT helpers. Risks include fixed CPM paths not matching a board DTB, divisor assumptions, and MAC ordering. Test with 8xx cuImages, CPM serial boot console, and FDT clock/MAC properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-amigaone.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-amigaone.c

## Purpose
Old U-Boot compatibility wrapper for AmigaOne.

## Important APIs, Types, And Control Flow
`platform_init()` copies board info using `CUBOOT_INIT()`, initializes the embedded DTB, starts serial console, and installs `platform_fixups()`. The fixup writes memory and CPU/timebase/bus clocks from U-Boot board info.

## State, Dependencies, Risks, And Tests
State is copied `bd_t`, loader metadata, allocator state, and FDT memory/clock properties. Dependencies include AmigaOne-compatible `ppcboot.h` fields and serial console availability. Risks include sparse fixups that do not correct MAC or bus child clocks, and old firmware board-info inaccuracies. Test with `cuImage.amigaone`, DT memory/clock validation, and serial output before kernel entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-amigaone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-bamboo.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-bamboo.c

## Purpose
Old U-Boot compatibility wrapper for Bamboo that reuses the native Bamboo initialization path.

## Important APIs, Types, And Control Flow
`platform_init()` copies U-Boot board info with `CUBOOT_INIT()` and calls `bamboo_init(&bd.bi_enetaddr, &bd.bi_enet1addr)`. The actual FDT/serial/fixup setup is delegated to `bamboo.c`.

## State, Dependencies, Risks, And Tests
State is `bd_t bd` plus the state created by `bamboo_init()`. Dependencies include `TARGET_4xx`, `TARGET_44x`, `44x.h`, and linked `bamboo.o`. Risks are board-info MAC pointer lifetime, mismatch between cuboot board fields and native fixup expectations, and missing Bamboo object in the build. Test by building `cuImage.bamboo` and verifying it performs the same clock/memory/MAC fixups as the native Bamboo path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-bamboo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-ebony.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-ebony.c

## Purpose
Old U-Boot compatibility wrapper for Ebony that delegates board-specific setup to `ebony_init()`.

## Important APIs, Types, And Control Flow
`platform_init()` copies `bd_t` through `CUBOOT_INIT()` and passes the first two U-Boot Ethernet addresses to `ebony_init()`. FDT initialization, serial console setup, and fixup registration happen in the Ebony implementation outside this file.

## State, Dependencies, Risks, And Tests
State is copied board info and Ebony initialization state. Dependencies include `TARGET_4xx`, `TARGET_44x`, `44x.h`, and linked Ebony support. Risks include invalid MAC address pointers, missing implementation linkage, and assumptions about old U-Boot `bd_t` layout. Test with `cuImage.ebony`, verifying memory, clock, EBC, and Ethernet properties after delegated fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-ebony.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-katmai.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-katmai.c

## Purpose
Old U-Boot compatibility wrapper for Katmai 440SP-style boards.

## Important APIs, Types, And Control Flow
`platform_init()` copies board info, installs `katmai_fixups()`, initializes FDT, and starts serial console. `katmai_fixups()` uses a fixed 33.333 MHz sysclk, applies 440SPE-like clocks, derives memory size from 440SPE MQ registers, writes Ethernet MAC index 0, and fixes EBC ranges. `BSS_STACK(4096)` provides a local wrapper stack.

## State, Dependencies, Risks, And Tests
State includes copied `bd_t`, platform fixup callback, BSS stack, and FDT updates. Dependencies include 4xx DCR helpers, 440SPE memory/clock logic, and EBC node path `/plb/opb/ebc`. Risks include hard-coded clock accuracy, single-MAC assumption, MQ memory-hole simplification, and EBC path mismatch. Test with `cuImage.katmai`, memory sizing above/below 4GB boundaries, and FDT EBC/MAC/clock inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-katmai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-pq2.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-pq2.c

## Purpose
Old U-Boot compatibility wrapper for PowerQUICC II / CPM2 systems. Beyond basic FDT fixups, it repairs localbus and PCI hardware configuration to match the device tree when firmware setup is incomplete.

## Important APIs, Types, And Control Flow
`update_cs_ranges()` validates `/localbus` address/size formats, translates controller registers, iterates chip-select `ranges`, and rewrites BR/OR pairs for each chip select. `fixup_pci()` validates `/pci` ranges and registers, programs outbound memory/I/O windows, inbound translation, reset enable, command/status bits, and arbitration registers. `pq2_platform_fixups()` updates memory, two MACs, CPU clocks, CPM/BRG clocks, then calls localbus and PCI repair. `platform_init()` copies board info, initializes FDT/serial, and installs the fixup.

## State, Dependencies, Risks, And Tests
State includes copied board info, static range buffers, FDT mutation, and direct MMIO writes to localbus/PCI/SOC registers. Dependencies include `fsl-soc.h`, DT translation, endian MMIO accessors, and exact PQ2 binding formats. Risks are programming hardware from malformed `ranges`, assuming 32-bit PCI and contiguous memory windows, long PCI reset delays, localbus chip-select size mask errors, and fallback to existing firmware setup on unsupported nodes. Test with PQ2 boards covering valid/invalid localbus and PCI nodes, PCI enumeration after boot, CPM serial, and FDT property checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-pq2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-rainier.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-rainier.c

## Purpose
Old U-Boot compatibility wrapper for Rainier 440EP/Denali-memory boards.

## Important APIs, Types, And Control Flow
`platform_init()` copies board info, installs `rainier_fixups()`, sets DBCR reset exit, initializes FDT, and starts serial console. `rainier_fixups()` applies fixed clocks, fixes EBC ranges, computes Denali DDR memory size, and writes Ethernet alias MAC addresses.

## State, Dependencies, Risks, And Tests
State is `bd_t`, platform callbacks, FDT properties, and DCR-derived memory/clock data. Dependencies include Denali memory logic, EBC path, Ethernet aliases, and `ibm44x_dbcr_reset()`. Risks include hard-coded clocks, Denali chip-select workaround behavior shared with Sequoia/Rainier, and missing aliases. Test with `cuImage.rainier`, FDT memory/clock/EBC/MAC validation, and reset callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-rainier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-sam440ep.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-sam440ep.c

## Purpose
Old U-Boot compatibility wrapper for Sam440ep, derived from Bamboo support with Sam-specific clock values.

## Important APIs, Types, And Control Flow
`sam440ep_fixups()` uses a 66.666 MHz sysclk, applies 440EP clocks, reads SDRAM memory size, quiesces EMAC/MAL, and writes two MAC addresses. `platform_init()` copies board info, installs fixup and DBCR reset callbacks, initializes FDT, and starts serial console.

## State, Dependencies, Risks, And Tests
State is copied board info, platform callbacks, and FDT/hardware updates. Dependencies include `4xx.c`, `44x.h`, EMAC MMIO addresses, and U-Boot MAC fields. Risks include hard-coded EMAC addresses, indentation hiding no logic but inviting churn, fixed clocks, and MAC helper argument shape. Test with `cuImage.sam440ep`, serial console, Ethernet reset behavior, and FDT memory/clock/MAC properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-sam440ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-sequoia.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-sequoia.c

## Purpose
Old U-Boot compatibility wrapper for Sequoia 440EP/Denali-memory boards.

## Important APIs, Types, And Control Flow
`sequoia_fixups()` applies fixed 33.333 MHz sysclk and 50 MHz timer clock, fixes EBC ranges, calculates Denali memory size, and writes Ethernet alias MAC addresses. `platform_init()` copies board info, sets fixup and DBCR reset callbacks, initializes FDT, and starts serial console.

## State, Dependencies, Risks, And Tests
State includes board info, callbacks, FDT, and hardware-derived Denali/EBC data. Dependencies include `4xx.c`, EBC path `/plb/opb/ebc`, aliases, and Sequoia-specific Denali chip-select assumptions. Risks are fixed clocks, memory sizing if U-Boot misprogrammed chip selects, and alias absence. Test with `cuImage.sequoia`, memory size compared to installed RAM, clock-frequency properties, and DBCR reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-sequoia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-taishan.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-taishan.c

## Purpose
Old U-Boot compatibility wrapper for Taishan 440GX boards.

## Important APIs, Types, And Control Flow
`taishan_fixups()` uses a fixed 33 MHz sysclk, computes 440GX clocks, reads SDRAM memory size, writes Ethernet aliases 0/1, and fixes EBC ranges. `platform_init()` copies board info, installs the fixup, initializes FDT, and starts serial console. A 4 KiB BSS stack is declared.

## State, Dependencies, Risks, And Tests
State is board info, BSS stack, FDT updates, and DCR-derived clocks/memory. Dependencies include `TARGET_440GX`, 4xx helpers, and EBC path. Risks include the source FIXME that sysclk should come from FPGA registers, MAC alias mismatch, and SDRAM sizing errata. Test with `cuImage.taishan`, measured clock comparison, EBC range validation, and Ethernet MAC propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-taishan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-warp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-warp.c

## Purpose
Old U-Boot compatibility wrapper for PIKA Warp 44x systems.

## Important APIs, Types, And Control Flow
`warp_fixups()` applies 440EP clocks with fixed 66 MHz sysclk, reads SDRAM memory size, fixes EBC ranges, and writes `ethernet0` MAC address. `platform_init()` copies board info, sets fixup and DBCR reset callbacks, initializes FDT, and starts serial console.

## State, Dependencies, Risks, And Tests
State is board info, platform callbacks, FDT properties, and DCR-derived memory/clock data. Dependencies include 4xx helpers and EBC/alias paths. Risks include single-Ethernet assumption, hard-coded clock constants, and firmware/DT mismatch for EBC. Test with `cuImage.warp`, FDT memory/EBC/clock/MAC properties, and reboot through DBCR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-warp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-yosemite.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-yosemite.c

## Purpose
Old U-Boot compatibility wrapper for Yosemite 440EP boards.

## Important APIs, Types, And Control Flow
`yosemite_fixups()` uses fixed clock inputs, applies 440EP clock fixups, reads SDRAM memory size, quiesces EMAC/MAL at hard-coded MMIO addresses, and writes two Ethernet alias MACs. `platform_init()` copies board info, sets fixup and DBCR reset callbacks, initializes FDT, and starts serial console.

## State, Dependencies, Risks, And Tests
State includes copied board info, FDT changes, platform callbacks, and hardware quiesce side effects. Dependencies include 4xx helpers, Ethernet aliases, and EMAC address constants. Risks are fixed clocks, EMAC reset on variants, MAC pointer validity, and SDRAM errata handling. Test with `cuImage.yosemite`, serial boot, Ethernet initialization after kernel starts, and FDT memory/clock/MAC validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-yosemite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot.c

## Purpose
Shared compatibility setup for old U-Boot wrappers that do not receive a ready device tree.

## Important APIs, Types, And Control Flow
`cuboot_init(r4, r5, r6, r7, end_of_ram)` interprets U-Boot registers as initrd start/end and command-line start/end, writes `loader_info`, computes available RAM from `_end` to `end_of_ram`, and initializes the simple allocator with a 1 MiB reserve below the RAM end.

## State, Dependencies, Risks, And Tests
State is global `loader_info` and simple allocator state. Dependencies include boot-wrapper symbols `_end`, `loader_info`, and old U-Boot calling conventions. Risks include bad `end_of_ram` from board info, invalid command-line bounds, reserve underflow on tiny RAM, and assuming `r4 == 0` means no initrd. Test each cuboot wrapper with and without initrd/cmdline and verify allocator placement does not overlap wrapper, kernel, or initrd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot.h

## Purpose
Header contract and convenience macro for old U-Boot compatibility wrappers.

## Important APIs, Types, And Control Flow
It declares `cuboot_init()` and defines `CUBOOT_INIT()`, which copies the firmware `bd_t` at `r3` into the wrapper's local `bd` variable, then calls `cuboot_init(r4, r5, r6, r7, bd.bi_memstart + bd.bi_memsize)`.

## State, Dependencies, Risks, And Tests
State is the wrapper-local `bd` variable and global loader/allocator state set by `cuboot_init()`. Dependencies include each cuboot file declaring `static bd_t bd`, register names in `platform_init()`, and the `ppcboot.h` layout selected by `TARGET_*` macros. Risks are macro capture, wrong `bd_t` layout for a board, and end-of-RAM overflow. Test by compiling every cuboot wrapper and booting with old U-Boot register conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/dcr.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/dcr.h

## Purpose
Boot-wrapper DCR access and register-definition header for IBM/AMCC 4xx support code.

## Important APIs, Types, And Control Flow
Macros `mfdcr`, `mtdcr`, `mfdcrx`, and `mtdcrx` wrap inline assembly for device-control-register reads/writes. The header defines SDRAM, EBC, CPC, MAL, CPR, and SDR register numbers plus helper macros such as `SDRAM0_READ`, `SDRAM_CONFIG_BANK_SIZE`, `EBC_BXCR_BANK_SIZE`, `CPC0_SYS0_*` divider extraction, `SDR0_READ`, and `CPR0_READ`. There is no function-level control flow; callers sequence register writes/reads in 4xx board code.

## State, Dependencies, Risks, And Tests
State is hardware DCR state read or written by callers. Dependencies include 4xx CPU support for DCR instructions and exact controller register encodings. Risks include inline asm constraints accepting only immediate DCR numbers for `mfdcr/mtdcr`, wrong divider masks, static `sdram_bxcr` in a header creating per-translation-unit copies, and destructive writes through helper macros. Test by compiling 405/440 targets, validating decoded memory/clock sizes against hardware docs, and booting board wrappers that use each macro family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/dcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/decompress.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/decompress.c

## Purpose
Boot-wrapper adapter around kernel decompression code that can decompress all or part of a compressed kernel image while supporting output skipping.

## Important APIs, Types, And Control Flow
The file includes gzip or xz decompressor sources depending on kernel compression config. `partial_decompress(inbuf, input_size, outbuf, output_size, _skip)` initializes global progress state, adds skipped bytes to the decompression limit, calls `__decompress()`, and returns either decompressed bytes after skip or the decompressor error. `flush()` is the output callback: it tracks `decompressed_bytes`, discards blocks before `skip`, copies the wanted window into `output_buffer`, and returns `-1` after `limit` to intentionally abort once enough output is produced. `print_err()` suppresses that intentional abort.

## State, Dependencies, Risks, And Tests
State is global and single-threaded: `decompressed_bytes`, `limit`, `skip`, and `output_buffer`. Dependencies include copied/fixed kernel decompressor sources, `min`, boot-wrapper `printf`, and compression Kconfig. Risks include global non-reentrancy, treating intentional abort as success, off-by-one at skip/limit boundaries, and decompressor-specific negative returns. Test gzip/xz images, full and partial decompression, skip crossing flush block boundaries, zero output size, insufficient/corrupt input, and output buffer bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/devtree.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/devtree.c

## Purpose
Boot-wrapper convenience layer for mutating and querying the flattened device tree before handing control to the kernel.

## Important APIs, Types, And Control Flow
Fixup APIs include `dt_fixup_memory()`, `dt_fixup_cpu_clocks()`, `dt_fixup_clock()`, `dt_fixup_mac_address_by_alias()`, `dt_fixup_mac_address()`, and `__dt_fixup_mac_addresses()`. Address helpers include `dt_get_reg_format()`, `dt_xlate_reg()`, `dt_xlate_addr()`, and `dt_get_virtual_reg()`. Compatibility matching is handled by `dt_is_compatible()`.

`dt_xlate()` is the core translation path: it reads a node's `reg`, walks parents, applies `ranges` translations using fixed-width address arrays up to four cells, checks address/size-cell limits, rejects unsupported PCI/special encodings, and returns a CPU physical/virtual address-sized result. `dt_get_virtual_reg()` prefers `virtual-reg` and falls back to translated `reg`.

## State, Dependencies, Risks, And Tests
State is the mutable FDT plus global `timebase_period_ns`; `prop_buf` is a shared scratch buffer. Dependencies include boot-wrapper DT ops (`finddevice`, `getprop`, `setprop`, aliases, parent traversal), endian helpers, and `MAX_PROP_LEN`. Risks include unsupported buses, static scratch buffer reuse, address truncation on 32-bit wrappers, `compare_reg()` boundary subtleties, division by zero if timebase is zero, and fatal exits on unsupported root cell counts. Test memory/clock/MAC fixups, `ranges` translation through nested buses, empty `ranges`, virtual-reg fallback, compatible lists with multiple strings, and 32-bit overflow rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/devtree.c -->
