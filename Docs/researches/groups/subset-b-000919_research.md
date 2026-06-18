# Research: subset-b-000919

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/lcd.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/lcd.c

## Purpose
`lcd.c` is the XTFPGA board-family character LCD driver used during early Xtensa platform bring-up. It writes controller commands and character data directly to board MMIO addresses and displays a boot banner.

## Important APIs, types, and functions
- `LCD_INSTR_ADDR` and `LCD_DATA_ADDR` derive instruction and data MMIO byte addresses from `CONFIG_XTFPGA_LCD_BASE_ADDR`.
- `lcd_put_byte()` emits either one 8-bit write or two 4-bit-nibble writes depending on `CONFIG_XTFPGA_LCD_8BIT_ACCESS`.
- `lcd_init()` programs display mode, display-on, clear-display, and the initial `XTENSA LINUX` string.
- `lcd_disp_at_pos()`, `lcd_shiftleft()`, and `lcd_shiftright()` are the platform-facing LCD operations declared by `<platform/lcd.h>`.

## Control flow
`arch_initcall(lcd_init)` runs after core arch setup. Initialization writes the 8-bit mode command three times with HD44780-style delays, optionally switches into 4-bit mode, enables display output, clears the panel, and writes the banner at position zero. Later callers set DDRAM position with `LCD_DISPLAY_POS | pos` and stream bytes through `LCD_DATA_ADDR`.

## State and persistence behavior
There is no software state. The persistent state is the external LCD controller's display buffer, cursor position, and command mode. Writes use `WRITE_ONCE()` to avoid compiler coalescing or reordering of repeated MMIO-looking byte accesses.

## Dependencies and integration points
The file depends on Xtensa XTFPGA hardware address macros, Linux delay helpers, and the platform LCD header. `setup.c` uses `lcd_disp_at_pos()` during power-off; other platform code may use the shift helpers for board status output.

## Risks and edge cases
The driver assumes the LCD MMIO mapping is valid before `arch_initcall`. Timing is fixed-delay and may be marginal on changed LCD hardware or clocking. The non-8-bit mode writes high nibbles only, so wiring must match the board's expected 4-bit interface. No bounds are enforced for `pos` or string length.

## Test signals
Booting an XTFPGA kernel should show `XTENSA LINUX`; shutdown should show `POWEROFF` through `setup.c`. Useful checks are logic-analyzer/MMIO traces for command ordering, both 4-bit and 8-bit Kconfig builds, and compile coverage that `<platform/lcd.h>` prototypes match these exported functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/setup.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/setup.c

## Purpose
`setup.c` provides XTFPGA board setup: restart and power-off handlers, optional CPU counter calibration, Open Firmware clock and MAC-address fixups, and legacy non-DT platform device registration for Ethernet, USB, and UART.

## Important APIs, types, and functions
- `xtfpga_power_off()` displays `POWEROFF`, disables interrupts, and spins.
- `xtfpga_restart()` writes the software-reset register and falls back to `cpu_reset()`.
- `platform_calibrate_ccount()` reads the FPGA clock-frequency register into `ccount_freq` when `CONFIG_XTENSA_CALIBRATE_CCOUNT` is enabled.
- `xtfpga_clk_setup()` implements `CLK_OF_DECLARE(..., "cdns,xtfpga-clock", ...)` by reading a fixed-rate clock from MMIO.
- `update_local_mac()` copies a DT `local-mac-address` property and replaces the last byte with DIP-switch bits.
- `machine_setup()` is the DT initcall; `xtavnet_init()` is the non-DT initcall registering `ethoc`, `c67x00`, and `serial8250` devices.

## Control flow
Both DT and non-DT paths call `xtfpga_register_handlers()` during `arch_initcall`. In DT builds, clock setup is driven by early OF clock matching, then `machine_setup()` patches the first `opencores,ethoc` node's MAC property. In non-DT builds, static resource arrays describe Ethernet register/buffer/IRQ ranges, USB HPI resources, and DUART16552 serial resources; `xtavnet_init()` fills DIP-switch MAC and clock-dependent fields before `platform_add_devices()`.

## State and persistence behavior
The restart/power-off handlers persist in the kernel sys-off handler registry. DT MAC patching allocates a replacement `struct property` and string name that become owned by the live device tree. Non-DT platform devices and their platform data remain static for the life of the kernel. Hardware state changes include reset-register writes, LCD text, DIP-switch reads, and clock-frequency reads.

## Dependencies and integration points
This file integrates with Linux sys-off, clock provider, OF address/property APIs, Xtensa `cpu_reset()`, XTFPGA hardware constants, the LCD helper, OpenCores `ethoc`, Cypress `c67x00`, and 8250 serial. Endianness-sensitive values come from `XCHAL_HAVE_BE` in variant headers.

## Risks and edge cases
`xtfpga_restart()` assumes the magic software-reset write is sufficient or that jumping through `cpu_reset()` is safe with devices still active. `update_local_mac()` leaks the allocated property intentionally into the OF tree but must allocate both value and name successfully. The non-DT path truncates DIP switches into the last MAC byte without masking, unlike the DT path's `& 0x3f`. Resource constants must match the FPGA bitstream.

## Test signals
Relevant signals are DT boot with a `cdns,xtfpga-clock` node, Ethernet MAC last-byte updates from DIP switches, non-DT registration of `ethoc`, `c67x00`, and `serial8250`, reboot via sys-off, and poweroff LCD/spin behavior. Build tests should cover `CONFIG_USE_OF`, non-OF, and `CONFIG_XTENSA_CALIBRATE_CCOUNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/core.h

## Purpose
This generated Xtensa HAL header describes the `csp`/`xt_lnx` core configuration consumed by kernel assembly, cache, MMU, exception, and interrupt code.

## Important APIs, types, and functions
The file exports only preprocessor constants. Key groups define ISA features (`XCHAL_HAVE_WINDOWED`, density, loops, MAC16, booleans, threadptr, coprocessor support), cache geometry, interrupt masks and types, vector addresses, debug/TRAX support, performance counters, and MMU capability.

## Control flow
There is no runtime control flow. Inclusion selects compile-time code paths in Xtensa low-level code: windowed register spilling, instruction decoding up to 8 bytes, writeback cache maintenance, XEA2 vector placement, timer interrupt selection, and page-table MMU handling.

## State and persistence behavior
No state is stored here. The constants must match the synthesized core: little-endian, 32 address registers, 64 KiB I-cache, 16 KiB D-cache, 64-byte lines, writeback D-cache, 22 interrupts, three timers on interrupts 6/10/13, NMI on 14, profiling on 15, 8 perf counters, PTP MMU with 8 ASID bits and 4 rings.

## Dependencies and integration points
The header is pulled through Xtensa variant include paths and is paired with this variant's `tie.h` and `tie-asm.h`. It supplies `XCHAL_HAVE_BE` to platform code, cache constants to cacheflush/TLB code, and interrupt/vector constants to entry code.

## Risks and edge cases
Any mismatch with hardware can break exception entry, timer delivery, cache maintenance, or user/kernel address translation. The 8-byte max instruction size requires decode paths to handle FLIX-length tables. Non-coherent writeback cache settings require correct DMA/cache synchronization elsewhere.

## Test signals
Build an Xtensa `csp` configuration and boot to user space. Exercise timer ticks, external interrupts, NMI/debug vectors, page faults, cache flush paths, performance counters, and endianness-sensitive platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/tie-asm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/tie-asm.h

## Purpose
This assembler HAL header defines save/restore macros for `csp` non-coprocessor optional state and save-area selection masks.

## Important APIs, types, and functions
- `XTHAL_SAS_*` masks classify optional/TIE state by extension origin, compiler use, and ABI lifetime.
- `xchal_ncp_store` saves `THREADPTR`, `ACCLO`, `ACCHI`, `BR`, `SCOMPARE1`, and `M0`-`M3`.
- `xchal_ncp_load` restores the same registers.
- `XCHAL_NCP_NUM_ATMPS` and `XCHAL_SA_NUM_ATMPS` declare one required temporary register.

## Control flow
The macros are expanded by low-level context-switch, signal, or exception code. They call common `xchal_sa_start`/`xchal_sa_align` helpers, conditionally include register groups based on `select` and `alloc`, then issue `rur`, `rsr`, `wur`, `wsr`, and `s32i/l32i` instructions.

## State and persistence behavior
The macros serialize optional architectural state into the save area described by `tie.h`: thread-global `THREADPTR`, compiler-used MAC16 accumulators, and caller-saved boolean/conditional-store/MAC16 registers. They do not manage CPENABLE because CP7 has no save area.

## Dependencies and integration points
The file depends on assembler save-area support macros and this variant's register names. It must match `XCHAL_NCP_SA_LIST()` ordering and sizes in `tie.h`; otherwise thread switches and signal frames restore incorrect state.

## Risks and edge cases
Incorrect `select`/`alloc` use can skip stores while still reserving space, so callers must use the same policy for load and store. The save area must be 4-byte aligned. Register availability must match `core.h` booleans, MAC16, threadptr, and S32C1I options.

## Test signals
Build assembly users, run context-switch stress with TLS/thread pointer use, MAC16-heavy code, boolean-register use, conditional-store paths, and signal delivery/return tests that cross task switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/tie-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/tie.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/tie.h

## Purpose
This generated C HAL header describes `csp` TIE and optional-state save-area layout for code that builds register save tables.

## Important APIs, types, and functions
It declares one port coprocessor, CP7 `XTIOP`, with no saved state, `XCHAL_CP_MASK`/`XCHAL_CP_PORT_MASK` as `0x80`, a 36-byte non-coprocessor save area aligned to 4 bytes, and a 48-byte total save area after padding. `XCHAL_NCP_SA_LIST(s)` enumerates nine saved registers: `threadptr`, `acclo`, `acchi`, `br`, `scompare1`, and `m0`-`m3`.

## Control flow
There is no runtime code. Callers define `XCHAL_SA_REG` and expand `XCHAL_NCP_SA_LIST()` or CP lists to generate structs, offsets, unwind metadata, or save/restore code.

## State and persistence behavior
The described state is per-thread optional Xtensa state. `threadptr` is thread-global, MAC16 accumulator and multiplier registers are caller-saved optional state, and `br`/`scompare1` cover boolean and conditional-store options. CP7 exists for I/O port instructions but persists no context bytes.

## Dependencies and integration points
This header must align with `core.h` feature flags and `tie-asm.h` store/load ordering. It is consumed by Xtensa kernel context-switch and user ABI code via variant include paths.

## Risks and edge cases
Changing this generated file without matching the hardware and assembler macros corrupts task state. Save-area padding matters because total size is 48 bytes even though NCP payload is 36 bytes. Direct inclusion is discouraged; it should be reached through the core configuration wrapper.

## Test signals
Compile tests should expand all save-list macros. Runtime signals are stable TLS, MAC16/boolean results across preemption, and no corruption after signal delivery, ptrace, or fork/exec on the `csp` variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/tie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/core.h

## Purpose
This generated header describes the `dc232b` Xtensa core for compile-time kernel configuration.

## Important APIs, types, and functions
It defines a little-endian, windowed, 32-register LX2.1.1 core with density, loops, MAC16, threadptr, CPENABLE/XTIOP, 3-byte maximum instructions, 16 KiB I/D caches with 32-byte writeback lines, XEA2 vectors, and a PTP MMU.

## Control flow
The constants select low-level code for windowed ABI entry, cache/TLB maintenance, timer setup, exception vectors, and instruction decoding. No executable code is defined.

## State and persistence behavior
Hardware state described includes 22 interrupts with 17 external inputs, timers on 6/10/13, NMI on 14, no profiling interrupt macro in the extracted set, VECBASE reset at `0xD0000000`, reset vector at `0xFE000000`, 8 ASID bits, and 4 MMU rings.

## Dependencies and integration points
Kernel Xtensa variant selection pulls this header with the corresponding `tie.h`/`tie-asm.h`. Platform serial and network code use `XCHAL_HAVE_BE`; exception and IRQ code consume the masks and vector addresses.

## Risks and edge cases
The LX2-era 3-byte instruction limit differs from FLIX-capable variants. Interrupt masks differ from `csp`, especially external edge/level allocation. Cache line size is 32 bytes, so using another variant's cache constants would break flush ranges.

## Test signals
Boot and run timer, external IRQ, TLB/page-fault, cache flush, and syscall/exception tests on a `dc232b` build. Confirm code paths do not assume boolean registers or wide instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/tie-asm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/tie-asm.h

## Purpose
This assembler header saves/restores `dc232b` optional non-coprocessor state.

## Important APIs, types, and functions
`xchal_ncp_store` and `xchal_ncp_load` handle MAC16 `ACCLO/ACCHI` and `M0`-`M3`, `SCOMPARE1`, and `THREADPTR`. The older macro form accepts `continue`, `ofs`, and `select` but not the newer `alloc` parameter. Two temporary registers are required.

## Control flow
Expanded save/load macros align the save-area pointer and conditionally emit special/user register transfers based on `XTHAL_SAS_*` masks. Stores use `rsr`/`rur` plus `s32i`; loads use `l32i` plus `wsr`/`wur`.

## State and persistence behavior
The macros persist 32 bytes of optional state matching `tie.h`. There is no boolean `BR` state for this variant. CP7 `XTIOP` exists but has no context bytes or load/store macro body.

## Dependencies and integration points
The file must match `dc232b` `tie.h` register ordering and `core.h` feature flags. It integrates with common Xtensa assembly save-area helpers.

## Risks and edge cases
Because this header uses the legacy no-`alloc` macro signature, shared assembly must account for variant macro differences. Save and restore `select` masks must match exactly. Misalignment or use on a core without matching MAC16/threadptr support corrupts register state.

## Test signals
Build this variant's assembly, then stress TLS, MAC16, conditional-store code, context switches, and signal return. Compile shared save-area users against both old and new macro signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/tie-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/tie.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/tie.h

## Purpose
This generated header describes `dc232b` optional and TIE state layout.

## Important APIs, types, and functions
It declares CP7 `XTIOP` as the only coprocessor (`XCHAL_CP_MASK` `0x80`) with zero save size. Non-coprocessor state is 32 bytes aligned to 4 bytes; `XCHAL_NCP_SA_LIST()` contains eight registers: `acclo`, `acchi`, `m0`-`m3`, `scompare1`, and `threadptr`.

## Control flow
No runtime code is present. Consumers define `XCHAL_SA_REG` to expand the save-area list into metadata or code.

## State and persistence behavior
The layout captures MAC16 accumulator/multiplier state, conditional-store state, and thread pointer state. CP state is nominally present only for XTIOP and does not require save/restore.

## Dependencies and integration points
It is paired with `dc232b` `core.h` and `tie-asm.h`; the latter implements the concrete assembler ordering for this list. Kernel thread-switch, signal, and ptrace facilities depend on these sizes.

## Risks and edge cases
The save area is exactly 32 bytes with no larger total padding, unlike `csp`. Reordering list entries or mixing with another variant's assembler macros would silently misrestore registers.

## Test signals
Compile-time expansion of NCP and CP lists, plus runtime TLS/MAC16/conditional-store preservation across preemption and signal delivery, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/tie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/core.h

## Purpose
This generated header describes the `dc233c` Xtensa LX4.0.1 core configuration.

## Important APIs, types, and functions
It exports little-endian windowed ABI constants, density/loops/MAC16/threadptr/CPENABLE, no booleans, no FP/DFP/HiFi, 3-byte maximum instructions, 16 KiB I/D writeback caches with 32-byte lines, 22 interrupts, XEA2 vectors, and PTP MMU constants.

## Control flow
No code executes from this file. Compile-time users choose entry, cache, interrupt, MMU, and instruction-decode paths from these macros.

## State and persistence behavior
The described hardware state includes 17 external interrupts, timers on 6/10/13, NMI on 14, VECBASE reset at `0x00002000`, reset vector at `0xFE000000`, user/kernel/double-exception vectors under VECBASE, 8 ASID bits, and 4 rings.

## Dependencies and integration points
This file is selected by the Xtensa variant include path and must match `dc233c` TIE headers. Interrupt definitions feed IRQ setup; cache definitions feed flush/invalidate code; `XCHAL_HAVE_BE` affects platform data endianness.

## Risks and edge cases
The interrupt layout is close to `dc232b` but vector base differs, so sharing assumptions across variants is risky. The lack of booleans means no `BR` save state. Wrong cache geometry breaks DMA/cache coherency.

## Test signals
Build/boot tests should cover timer ticks, external IRQs, page faults, syscall vectors, cache maintenance, and absence of boolean/FP/HiFi paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/tie-asm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/tie-asm.h

## Purpose
This assembler header implements `dc233c` optional-state save/restore macros.

## Important APIs, types, and functions
It defines the full `XTHAL_SAS_*` mask set including `ANYOT`, `ANYCC`, `ANYABI`, and `XTHAL_SAS3()`. `xchal_ncp_store/load` save and restore `THREADPTR`, `ACCLO`, `ACCHI`, `M0`-`M3`, and `SCOMPARE1`. One temporary register is required.

## Control flow
The macros use common save-area start/alignment helpers, evaluate selected categories, and emit user/special register reads or writes. The `alloc` parameter can reserve space for unselected groups, allowing composition with larger save sequences.

## State and persistence behavior
The 32-byte NCP payload stores thread pointer, MAC16, and conditional-store state. There is no BR/boolean state and no nonempty coprocessor save state.

## Dependencies and integration points
It must match `dc233c` `tie.h` and is used by Xtensa assembly paths that preserve extra architectural state during task switch, exception handling, or user-state save.

## Risks and edge cases
The macro syntax differs from `dc232b` while the register set is similar. Shared assembly should not assume a uniform parameter list. Incorrect `alloc` handling can desynchronize offsets across composed saves.

## Test signals
Compile assembly against this variant, exercise TLS and MAC16 computations across context switches, and run signal-frame tests that validate `SCOMPARE1` and optional state restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/tie-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/tie.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/tie.h

## Purpose
This generated C header describes `dc233c` TIE and optional-state save areas.

## Important APIs, types, and functions
The variant has one CP7 `XTIOP` port coprocessor with zero save size and a 32-byte, 4-byte-aligned NCP area. `XCHAL_NCP_SA_LIST()` lists eight registers: `threadptr`, `acclo`, `acchi`, `m0`-`m3`, and `scompare1`.

## Control flow
Consumers expand macros with their own `XCHAL_SA_REG` definition; this file itself has no runtime behavior.

## State and persistence behavior
The layout persists per-thread TLS, MAC16, and conditional-store state. All CP save lists are empty despite CP7 being present.

## Dependencies and integration points
The file is paired with `dc233c` `tie-asm.h` and `core.h`. It informs kernel save-area sizing and register metadata.

## Risks and edge cases
The order differs from `dc232b` even though the set is the same, with `threadptr` first here. Mixing metadata and assembler macros from different variants would corrupt restored state.

## Test signals
Compile generated save-list users and run context-switch, signal, TLS, and MAC16 tests on `dc233c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/tie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/core.h

## Purpose
This generated header describes the `de212` LX6.0.2 Xtensa core configuration.

## Important APIs, types, and functions
It defines a little-endian, windowed, 32-register core with density, loops, MAC16, no threadptr, no CPENABLE, no booleans, no FP/HiFi, 3-byte max instructions, 8 KiB I/D writeback caches with 32-byte lines, and a reduced MMU configuration.

## Control flow
The macros drive compile-time selection for exception vectors, timers, cache code, and whether coprocessor/threadptr paths exist.

## State and persistence behavior
Hardware state includes 22 interrupts, 17 external inputs, timers on 6/10/13, NMI on 14, no profiling interrupt, VECBASE reset at `0x60000000`, reset vector at `0x50000000`, zero perf counters, `XCHAL_HAVE_PTP_MMU` 0, zero ASID bits, and one ring.

## Dependencies and integration points
This variant is paired with `de212` TIE headers that save only MAC16 and `SCOMPARE1` optional state. MMU and privilege code must honor the lack of PTP MMU/ASIDs despite `XCHAL_HAVE_TLBS` being set.

## Risks and edge cases
Code that assumes `THREADPTR`, CPENABLE, ASIDs, performance counters, or full PTP MMU will fail. The unusual reset/vector addresses must match the board or simulator memory map. Cache size is smaller than most neighboring variants.

## Test signals
Build and boot with this variant, checking exception vectors, timer interrupts, cache maintenance, TLB behavior without PTP MMU, no TLS-register assumptions, and no coprocessor enable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/tie-asm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/tie-asm.h

## Purpose
This assembler header saves/restores `de212` optional non-coprocessor state.

## Important APIs, types, and functions
`xchal_ncp_store/load` cover `ACCLO`, `ACCHI`, `SCOMPARE1`, and `M0`-`M3`. The full selection/alloc macro interface is present, and one temporary register is declared.

## Control flow
Macro expansion aligns the save pointer, conditionally includes compiler-used MAC16 accumulator state and non-compiler-used conditional-store/MAC16 multiplier state, then emits register moves and memory accesses.

## State and persistence behavior
The saved payload is 28 bytes in the `tie.h` layout, padded to a 32-byte total save area. There is no `THREADPTR`, `BR`, or coprocessor state.

## Dependencies and integration points
This file must match `de212` `core.h` feature absence and `tie.h` register list. It is used by low-level Xtensa context preservation paths.

## Risks and edge cases
Using generic code that expects a thread pointer or CP save macro would be incorrect. Offset accounting must preserve the 28-byte payload/32-byte total distinction.

## Test signals
Compile save/restore assembly, run MAC16 and conditional-store tests across preemption and signal delivery, and verify TLS code does not depend on a hardware thread pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/tie-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/tie.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/tie.h

## Purpose
This generated header defines the `de212` optional-state save-area layout.

## Important APIs, types, and functions
It declares no coprocessors (`XCHAL_CP_NUM` 0, masks 0), a 28-byte NCP save area aligned to 4 bytes, and a 32-byte padded total. `XCHAL_NCP_SA_LIST()` contains seven registers: `acclo`, `acchi`, `scompare1`, and `m0`-`m3`.

## Control flow
No code executes here. Consumers expand list macros to derive offsets and save metadata.

## State and persistence behavior
Only MAC16 and conditional-store optional state are persistent across context save. There is no thread-global user register state in this variant.

## Dependencies and integration points
The file is consumed by kernel low-level Xtensa save-area code and must match `de212` `tie-asm.h`.

## Risks and edge cases
The absence of CP and threadptr state is semantically important. Importing another variant's save-area size or assuming 32 bytes of real payload would create ABI drift.

## Test signals
Compile save-list users and run context-switch/signal tests focused on MAC16 and `SCOMPARE1`, with checks that CP state paths remain disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/tie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/core.h

## Purpose
This generated header describes the `fsf` Xtensa LX2.0.0 core configuration.

## Important APIs, types, and functions
It defines a big-endian, windowed core with 64 address registers, density and loops, no MUL32/MAC16/CP/booleans, threadptr support in `core.h`, 3-byte max instructions, 8 KiB I/D caches with 16-byte lines, non-writeback D-cache, 17 interrupts, and PTP MMU with 8 ASID bits.

## Control flow
The macros select compile-time Xtensa entry/cache/MMU behavior. No functions are defined.

## State and persistence behavior
The hardware description includes 10 external interrupts, 4 interrupt levels, EXCM level 1, timers on interrupts 10/11/12, no NMI, reset vector `0xFE000020`, user/kernel/double-exception vectors near `0xD0000200`, and 4 MMU rings.

## Dependencies and integration points
`XCHAL_HAVE_BE` drives big-endian platform choices such as serial I/O type and Ethernet platform data. Cache and interrupt constants feed core arch code. The paired TIE headers oddly describe no saved state despite core threadptr support.

## Risks and edge cases
Big-endian operation, 64 physical address registers, no MAC16/MUL32, no NMI, and 16-byte cache lines distinguish this variant sharply from the others. The threadptr/core-vs-tie discrepancy should be treated carefully by TLS/context-switch code.

## Test signals
Build big-endian Xtensa, run IRQ/timer tests, cache flush tests with 16-byte lines and non-writeback D-cache, syscall/exception vectors, and TLS tests to confirm thread pointer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/tie-asm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/tie-asm.h

## Purpose
This assembler header provides minimal `fsf` non-coprocessor save/restore macros.

## Important APIs, types, and functions
`xchal_ncp_store` saves `THREADPTR`, and `xchal_ncp_load` restores it. The header declares one temporary register and has the older no-`alloc` macro form.

## Control flow
The macros use `xchal_sa_start`, optionally include the thread-global group based on `select`, align the save pointer, then issue `rur`/`wur` for `THREADPTR` and memory load/store.

## State and persistence behavior
The macro body persists a thread pointer value, but the paired `tie.h` reports `XCHAL_NCP_SA_SIZE` and `XCHAL_TOTAL_SA_SIZE` as zero. That mismatch is a notable integration hazard and may reflect historical/generated-header inconsistency.

## Dependencies and integration points
It depends on the common Xtensa assembler save-area helpers and `THREADPTR` register support from `core.h`. Consumers must reconcile it with `fsf` `tie.h`.

## Risks and edge cases
The zero-size C metadata versus nonempty assembler macro can desynchronize save-area allocation. Shared code should verify whether this header is actually used for task state or whether higher-level code treats threadptr separately.

## Test signals
Build the `fsf` variant and inspect generated save-area sizes. Runtime TLS preservation across context switches and signal delivery is the key behavioral test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/tie-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/tie.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/tie.h

## Purpose
This generated header declares the `fsf` TIE/save-area layout as empty.

## Important APIs, types, and functions
It reports no coprocessors, zero CP masks, `XCHAL_NCP_SA_SIZE` 0, `XCHAL_TOTAL_SA_SIZE` 0, `XCHAL_NCP_SA_NUM` 0, and empty CP save lists. It still defines standard instruction-length tables.

## Control flow
There is no runtime behavior; list macros expand to nothing.

## State and persistence behavior
According to this C metadata, no optional or custom state is allocated in generic save areas. This conflicts with `core.h` and `tie-asm.h` indications of `THREADPTR` support/save code, so thread pointer persistence may be handled elsewhere or the generated files are inconsistent.

## Dependencies and integration points
The header is paired with `fsf` `core.h` and `tie-asm.h` and is consumed by kernel save-area sizing logic.

## Risks and edge cases
The biggest risk is save-area allocation of zero bytes while assembler macros can store `THREADPTR`. Any caller expanding both must avoid memory corruption. The big-endian, old-core nature of `fsf` increases the chance of bitrot in rarely built paths.

## Test signals
Compile all `fsf` low-level state-save paths and run TLS/context-switch/signal tests. Static inspection should confirm no code calls `xchal_ncp_store` into a zero-sized save area.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/tie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/core.h

## Purpose
This generated header describes the big-endian `test_kc705_be` LX6.0.2 Xtensa FPGA test core.

## Important APIs, types, and functions
It defines big-endian windowed ABI, 32 address registers, density, loops, 8-byte max instruction size, MAC16, booleans, threadptr, CPENABLE, HiFi2/HiFi2EP audio support, no FP/DFP, 16 KiB I/D writeback caches with 32-byte lines, 22 interrupts, XEA2 vectors, 8 perf counters, and PTP MMU.

## Control flow
The constants select code paths for big-endian I/O, FLIX-length instruction decode, audio/coprocessor state support, cache/TLB handling, and interrupt/vector setup.

## State and persistence behavior
Hardware state includes CP1 AudioEngineLX and CP7 XTIOP via TIE headers, 16 external interrupts, EXCM level 4, timers on 6/10/13, NMI on 14, profiling interrupt 15, VECBASE reset at `0x00002000`, reset vector at `0xFE000000`, 8 ASID bits, and 4 rings.

## Dependencies and integration points
The paired `tie.h`/`tie-asm.h` define a large AudioEngineLX coprocessor save area. Platform code uses `XCHAL_HAVE_BE` to select big-endian resource behavior.

## Risks and edge cases
This variant has the broadest state footprint in the set: big-endian plus HiFi2/AudioEngine state and 8-byte instructions. Missing coprocessor save/restore corrupts audio registers; wrong endianness breaks MMIO drivers.

## Test signals
Build big-endian KC705, boot with timers/IRQs, run audio/HiFi2 context-switch stress, signal return with coprocessor state, cache/MMU tests, and platform device I/O tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/tie-asm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/tie-asm.h

## Purpose
This assembler header saves/restores both non-coprocessor optional state and CP1 AudioEngineLX state for `test_kc705_be`.

## Important APIs, types, and functions
- `xchal_ncp_store/load` handle `THREADPTR`, `ACCLO`, `ACCHI`, `BR`, `SCOMPARE1`, and `M0`-`M3`.
- `xchal_cp_AudioEngineLX_store/load` alias `xchal_cp1_store/load`.
- CP1 macros save user registers `AE_OVF_SAR`, `AE_BITHEAD`, `AE_TS_FTS_BU_BP`, `AE_SD_NO`, `AE_CBEGIN0`, `AE_CEND0`, eight `aep` registers, and four `aeq` registers with audio-engine load/store instructions.
- Empty macros exist for unconfigured CP0 and CP2-CP7.

## Control flow
NCP macros follow the modern select/alloc save-area pattern. CP1 macros align to 8 bytes, save scalar AE user registers, then store packed 24x2 and 56-bit audio register-file state, adjusting the pointer across the 120-byte CP payload. Loads reverse the process.

## State and persistence behavior
The macros persist a 36-byte NCP area plus a 120-byte AudioEngineLX area, matching the 160-byte total save area in `tie.h`. CP7 XTIOP has no state.

## Dependencies and integration points
This file depends on HiFi2/AudioEngine assembler instructions and common Xtensa save-area helpers. It must match `test_kc705_be` `tie.h` and CPENABLE lazy/explicit coprocessor context management.

## Risks and edge cases
Audio state alignment is 8 bytes; incorrect alignment or CP enable handling will fault or corrupt registers. Pointer arithmetic in the macro splits stores across offsets, so metadata and assembler must remain in lockstep. Big-endian builds add coverage risk.

## Test signals
Run assembler builds with AudioEngine instructions enabled, context-switch stress using HiFi2 registers, signal delivery/return with CP state, and lazy coprocessor enable/disable tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/tie-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/tie.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/tie.h

## Purpose
This generated C header describes the `test_kc705_be` optional and coprocessor save-area layout.

## Important APIs, types, and functions
It declares two coprocessors: CP1 `AudioEngineLX` with a 120-byte, 8-byte-aligned save area and CP7 `XTIOP` with zero save size. CP masks are `0x82`, with port mask `0x80`. NCP state is 36 bytes; total optional/CP state is 160 bytes aligned to 8. CP1 has 18 saved registers covering AE user registers and `aep`/`aeq` register files.

## Control flow
No runtime code is present. Consumers expand `XCHAL_NCP_SA_LIST()` and `XCHAL_CP1_SA_LIST()` via `XCHAL_SA_REG`.

## State and persistence behavior
NCP state covers threadptr, MAC16, boolean, and conditional-store registers. CP1 state covers AudioEngineLX scalar/user and register-file state. CP7 persists no state.

## Dependencies and integration points
The header must match `test_kc705_be` `core.h` HiFi2/CP flags and `tie-asm.h` CP1 store/load macros. Kernel coprocessor context code uses these sizes and masks to allocate and switch state.

## Risks and edge cases
The AudioEngineLX save area dominates the ABI. Missing the CP1 list or using only NCP state will pass simple integer tests but fail audio workloads after preemption or signal delivery. Instruction length tables include 8-byte entries for FLIX/audio encodings.

## Test signals
Compile save-list expansion, run AudioEngine register preservation across task switches, signals, fork/exec, and CP enable transitions, plus NCP MAC16/boolean/TLS tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/tie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/core.h

## Purpose
This generated header describes the little-endian `test_kc705_hifi` LX5.0.4 Xtensa FPGA test core.

## Important APIs, types, and functions
It defines windowed ABI, 32 address registers, density, loops, MAC16, booleans, threadptr, CPENABLE, 8-byte max instruction size, HiFi3 support, no FP/DFP, 16 KiB I/D writeback caches with 32-byte lines, 22 interrupts, XEA2 vectors, 8 perf counters, and PTP MMU with 8 ASID bits.

## Control flow
No executable code exists. These macros choose instruction decode, cache, interrupt, vector, MMU, and optional/coprocessor support paths at compile time.

## State and persistence behavior
The hardware description includes 16 external interrupts, EXCM level 3, timers on 6/10/13, NMI on 14, profiling interrupt on 15, VECBASE reset at `0x00002000`, reset vector at `0xFE000000`, 4 MMU rings, and HiFi3-related coprocessor implications handled by this variant's TIE headers outside this work item.

## Dependencies and integration points
The header integrates with Xtensa arch entry, cache/TLB, IRQ, and coprocessor code. It should be read with the corresponding `test_kc705_hifi` `tie.h`/`tie-asm.h` even though only `core.h` is mapped in this item.

## Risks and edge cases
HiFi3 and 8-byte instruction support mean context and instruction-decode paths must not assume base ISA only. Interrupt masks differ slightly from `test_kc705_be` (`INTLEVEL4_MASK` includes `0x9000`), and little-endian platform behavior differs from the BE KC705 variant.

## Test signals
Build and boot this variant, exercise HiFi3/coprocessor context paths, timer and profiling interrupts, NMI, cache/MMU behavior, signal return, and instruction decoding for extended encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/core.h -->
