# Group Research: group_9_9front_sources_os_plan9_9front_sys_src_9_pc_apm_c_sources_os_plan9_9fr_4c668741d410

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/apm.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/apm.c

Advanced Power Management 1.2 BIOS bridge for 32-bit PC kernels.

Key responsibilities:
- Parses APM register values passed from boot configuration through `isaconfig("apm", ...)`.
- Builds the required consecutive GDT descriptors for APM 32-bit code, 16-bit code, and data segments.
- Exposes `#P/apm`, where reads return the saved `Ureg` argument/result block and writes perform an APM BIOS far call.
- Resets the i8253 timer after APM set-power-state calls because some BIOSes disable timers during suspend.

Important behavior:
- Forces the APM code segment lengths to `0xffffffff` as a workaround for bad BIOS-reported 16-bit lengths.
- Uses `apmfarcall(APMCSEL, ebx, &apmu)` at high interrupt priority.
- Converts real-mode-style segment bases by shifting APM segment values left by four before installing descriptors.

Dependencies:
- Depends on `apmjump.s`, x86 GDT layout, `ISAConf`, `addarchfile`, `i8253reset`, and segment constants from `mem.h`.

Notable risks:
- The file intentionally knows GDT bit layout and uses `KADDR(base)` before descriptor encoding.
- The `#P/apm` write interface requires an exact `Ureg`-sized payload and is privileged by file mode only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/apm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/apmjump.s -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/apmjump.s

Assembly helper for non-reentrant absolute far calls into the APM BIOS.

Key responsibilities:
- Implements `apmfarcall(seg, off, ureg)` for `apm.c`.
- Loads AX/BX/CX/DX from the supplied `Ureg`, saves data segment registers and selected general registers, and performs an indirect far call through `apmjumpstruct`.
- Clears DS/ES/FS/GS before the BIOS call so the BIOS must initialize segment state itself.
- Stores carry flag and selected result registers back into the `Ureg`.

Important behavior:
- Uses a global 8-byte jump structure, so calls are explicitly not reentrant or thread-safe.
- Returns the carry flag as the function result.
- Writes flags to the `Ureg` flags slot and updates AX/BX/CX/DX/SI.

Dependencies:
- Depends on Plan 9 x86 assembler conventions, `mem.h` segment definitions, and the `Ureg` layout expected by `apm.c`.

Notable risks:
- Correctness depends on hard-coded `Ureg` offsets.
- Segment-register and stack manipulation means the function cannot safely use normal frame-pointer access after its first push/pop.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/apmjump.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/archacpi.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/archacpi.c

ACPI-based PC architecture discovery, interrupt routing, AML I/O glue, and reset support.

Key responsibilities:
- Finds and maps ACPI RSDT/XSDT/FADT/DSDT/SSDT/MADT/HPET tables with checksum validation and memory reservation.
- Converts MADT processor, local APIC, I/O APIC, and interrupt-source override entries into the MP/APIC structures used by the rest of the PC kernel.
- Loads DSDT/SSDT AML, calls `_PIC`, discovers embedded controllers, and walks `_PRT` methods to add PCI interrupt routes.
- Provides `#P/acpitbls` for raw mapped table reads and `#P/acpimem` for restricted physical memory access.
- Implements ACPI reset through the FADT reset register when available, then falls back to generic reset.
- Supplies AML address-space handlers for system memory, I/O ports, PCI config space, and embedded-controller space.

Important behavior:
- `maptable()` recursively follows RSDT/XSDT and FADT pointers while de-duplicating physical table addresses.
- `memcheck()` blocks reads/writes that overlap low CPU bootstrap memory, the running kernel image, or configured usable RAM.
- PCI `_PRT` routes can use direct GSIs or link devices via `_PRS`, `_CRS`, and `_SRS`.
- Adds identity-mapped legacy ISA interrupts after ACPI routing.
- Can use HPET or TSC as the architecture fast clock depending on tables and boot options.

Dependencies:
- Depends on the AML interpreter, PCI discovery/config helpers, APIC/MP globals from `mp.h`, memory mapping/reservation, HPET, EC, and generic i8253/i8259 helpers.

Notable risks:
- Fixed arrays track at most 64 visited/mapped ACPI tables.
- The AML PCI address resolver assumes conventional `_ADR`, `_BBN`, bridge, and root-bridge semantics.
- ACPI memory access is powerful; safety relies on `memcheck()` and `#P/acpimem` permissions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/archacpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/archgeneric.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/archgeneric.c

Fallback PC architecture implementation using legacy PIC and PIT hardware.

Key responsibilities:
- Provides `archreset()` using i8042 reset first, then Intel reset-control port `0xcf9`.
- Implements calibrated millisecond and microsecond delays through `delayloop`.
- Exposes low-overhead `perfticks()` backed by TSC when present.
- Defines the `archgeneric` `PCArch` vtable with i8259 interrupt and i8253 timer operations.

Important behavior:
- Writes BIOS warm-boot flag at `0x472` before attempting reset.
- Falls into `idle()` forever if reset does not work.
- Leaves architecture identification as nil so it acts as the default architecture.

Dependencies:
- Depends on i8042, i8259, i8253, TSC cycle helpers, and `PCArch` from `dat.h`.

Notable risks:
- Reset control port `0xcf9` is chipset-specific but used as a pragmatic final path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/archgeneric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/archmp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/archmp.c

Intel MultiProcessor Specification table parser and MP-mode PC architecture backend.

Key responsibilities:
- Locates `_MP_` floating pointer and maps/checks the referenced `PCMP` configuration table.
- Builds processor APIC, bus, I/O APIC, I/O interrupt, and local interrupt structures from PCMP entries.
- Initializes local/I/O APICs and starts application processors through `mpinit()`.
- Provides MP reset by shutting down application processors and delegating to generic reset.
- Supports boot-time `*mp` table override and `*dumpmp` hex dump diagnostics.

Important behavior:
- Rejects MP default configurations and accepts PCMP versions 1 and 4 only.
- Assigns boot processor mach number 0 and increments application processor mach numbers from 1.
- Uses bus defaults for ISA/EISA/PCI polarity and trigger mode.
- Contains a board-specific workaround for an Intel SR1520ML interrupt-routing bug.
- Selects TSC fast clock when available and not disabled by `*notsc`.

Dependencies:
- Depends on MP table structures from `mp.h`, APIC setup, PCI, `sigsearch`, `vmap`, `memreserve`, and generic i8259 IRQ-number compatibility.

Notable risks:
- PCMP entry parsing assumes table entries are ordered sufficiently for one pass.
- Destination I/O APIC value `0xff` for I/O interrupts is treated as unsupported.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/archmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/audioac97.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/audioac97.c

PCI AC'97 audio controller driver with bus-master DMA rings and mixer hookup.

Key responsibilities:
- Matches known AC'97 PCI audio controller IDs and supports I/O-port and MMIO register layouts.
- Allocates input, output, and microphone circular buffers plus 32 hardware descriptors per stream.
- Handles playback writes, capture reads, stream close padding, status reporting, and buffered byte accounting.
- Services controller interrupts by advancing ring positions from current descriptor indices and waking sleepers.
- Initializes AC-link reset, codec readiness, bus-master registers, DMA descriptors, and interrupt routing.
- Hooks `audioac97mix.c` through register read/write callbacks.

Important behavior:
- Uses 32 KiB rings split into 32 descriptors and 4-byte stereo samples.
- ICH4 through ICH7 can use memory BARs; older controllers use paired I/O BARs.
- SiS 7012 has special status-clear behavior and descriptor size handling.
- Playback throttles according to `adev->delay`.

Dependencies:
- Depends on PCI, Plan 9 audio interface, DMA-address macros, interrupt registration, I/O allocation, and AC'97 codec mixer helpers.

Notable risks:
- Device matching includes untested IDs.
- Ring indices are updated from hardware descriptor position and assume descriptor/block alignment.
- Codec access waits are bounded but failures only print diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/audioac97.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/audioac97mix.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/audioac97mix.c

AC'97 codec mixer layer shared by the AC'97 controller driver.

Key responsibilities:
- Defines AC'97 codec register constants, capability bits, and volume controls.
- Implements volume get/set callbacks for master, headphone, audio, CD, line, mic, record gain, sample rate, and delay.
- Publishes mixer reads/writes through generic audio volume helpers.
- Resets codec power state and enables variable-rate audio when supported.

Important behavior:
- Capability masks hide controls unsupported by the codec.
- `speed` writes front DAC and ADC rate registers and then records the actual accepted rate.
- `delay` is a software playback latency setting stored in `Audio`.
- Reports AC'97 extension support such as VRA, SPDIF, and extra DACs.

Dependencies:
- Depends on controller-supplied codec register callbacks and the generic `audioif.h` volume parser/formatter.

Notable risks:
- If VRA is absent, the driver prints a warning but still exposes the speed control.
- The mixer allocation failure leaves the controller without volume callbacks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/audioac97mix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/audiohda.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/audiohda.c

Intel High Definition Audio/Azalia PCI driver with codec graph discovery and stream DMA.

Key responsibilities:
- Matches HDA PCI controllers, maps MMIO registers, applies vendor-specific controller quirks, and starts CORB/RIRB command DMA.
- Enumerates codecs, audio function groups, widgets, connection lists, pin defaults, capabilities, and amplifier ranges.
- Selects default input/output pins, finds audio paths through widget graphs, mutes/disconnects old paths, and connects converter-to-pin routes.
- Allocates input and output DMA streams with buffer descriptor lists and circular audio buffers.
- Implements audio read/write/close/status/control operations and volume controls for output, record gain, speed, and delay.
- Handles stream interrupts, command response interrupts, buffer position updates, underrun/overrun stops, and wakeups.
- Exposes `#P/hdacmd` for raw HDA verb submission and response reading against the last initialized card.

Important behavior:
- Uses 256 blocks over a 256 KiB stream buffer and 16-bit stereo 44.1 kHz format by default.
- Supports explicit route syntax through `pin` and `inpin` control writes.
- Scores output pins by fixed/jack status, green color, rear/external location, and line/headphone function.
- Scores input pins mostly by fixed/jack status.
- Uses CORB/RIRB polling for commands but keeps RIRB interrupt handshakes for QEMU compatibility.

Dependencies:
- Depends on PCI, audio interface helpers, MMIO register access, interrupt routing, queues, and Plan 9 physical DMA address conversion.

Notable risks:
- Codec graph traversal and route strings are compact and assume sane widget connection data.
- `lastcard` means `#P/hdacmd` targets only the most recently initialized HDA controller.
- Some supported PCI IDs are marked untested, and several vendor workarounds use magic config-register writes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/audiohda.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/audiosb16.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/audiosb16.c

ISA Sound Blaster 16 and ESS1688-compatible playback driver.

Key responsibilities:
- Probes configured ISA audio devices, initializes SB16 or ESS1688-compatible hardware, allocates DMA buffers, and registers audio cards.
- Implements mixer controls for master, audio, synth, CD, line, mic, speaker, bass/treble, record/output gain, speed, and delay.
- Provides write-side playback using a circular buffer backed by looped DMA.
- Handles SB16 and ESS1688 command/status protocols, reset sequences, interrupt acknowledgement, and DMA continuation/stop.
- Registers interrupt handlers and audio status/buffered callbacks.

Important behavior:
- Uses 4 KiB transfer blocks inside a 64 KiB ring.
- SB16 playback programs signed 16-bit stereo autoinit DMA; ESS1688 has separate extended-register setup.
- Playback starts when data is available and stops at end of count when less than one block remains buffered.
- The driver registers both `sb16` and `ess1688` card names.

Dependencies:
- Depends on ISA configuration, low DMA helpers, I/O port allocation, interrupt registration, and generic audio volume helpers.

Notable risks:
- The read/capture paths are mostly dormant; the operational path is playback-oriented.
- Port/IRQ/DMA probing is constrained to classic ISA ranges and may mark failed cards as permanently unavailable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/audiosb16.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/bios32.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/bios32.c

BIOS32 Service Directory discovery and call wrapper.

Key responsibilities:
- Searches for the `_32_` BIOS32 Service Directory header.
- Maps the BIOS32 entry point and constructs far pointers using kernel code selector `KESEL`.
- Opens specific BIOS32 services by ID, maps their service regions, and builds callable service far pointers.
- Provides serialized `bios32ci()` calls and `bios32close()` cleanup.

Important behavior:
- Service IDs are packed little-endian into EAX before calling the BIOS32 directory.
- A nonzero low byte of EAX after the directory call means service lookup failed.
- All BIOS32 calls are protected by `bios32lock`.

Dependencies:
- Depends on `sigsearch`, `vmap`/`vunmap`, `bios32call` assembly support, and `BIOS32ci` from `dat.h`.

Notable risks:
- Maps service memory lengths supplied by firmware.
- A small verbose flag exists but is disabled by default.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/bios32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/bootargs.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/bootargs.c

Boot configuration parser and multiboot-to-Plan-9 argument converter.

Key responsibilities:
- Converts multiboot memory maps into `*e820=` lines.
- Converts multiboot framebuffer or VBE information into `*bootscreen=` configuration.
- Imports first multiboot module contents as `plan9.ini` text and appends multiboot command-line tokens.
- Normalizes CR/TAB characters, parses `name=value` configuration lines, and stores case-insensitive configuration keys.
- Exposes `getconf()`, `setconfenv()`, and `writeconf()` for kernel configuration consumers.

Important behavior:
- Later duplicate configuration lines overwrite earlier values for the same case-insensitive name.
- Environment setup stores non-star names as normal environment variables and all names as configuration variables.
- `writeconf()` converts current kernel environment back into `BOOTARGS` format and clears `BOOTLINE`.

Dependencies:
- Depends on boot memory constants, multiboot pointer, VESA/screen helpers, tokenization, and kernel environment helpers.

Notable risks:
- Uses fixed `MAXCONF` and `BOOTARGSLEN` capacities.
- Multiboot pointer is ignored if it is zero or above `MemMin`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/bootargs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/cga.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/cga.c

Text-mode CGA console output backend for early/legacy PC display.

Key responsibilities:
- Maintains an 80x25 text console at physical `0xB8000`.
- Converts Unicode runes to Code Page 437 character cells.
- Implements newline, tab, backspace, scroll, cursor movement, and screen attribute updates.
- Transfers existing CGA screen contents into `kmesg` during first initialization.
- Installs `screenputs` unless disabled by `*nocga`.

Important behavior:
- Uses a lock and avoids deadlock by dropping interrupt-time prints if the console lock is unavailable.
- Maintains partial UTF-8 rune bytes across calls.
- Scrolls by moving screen memory up one row and clearing the final row.

Dependencies:
- Depends on VGA/CGA CRT controller I/O ports, `KADDR`, `kmesg`, UTF/rune helpers, and boot configuration.

Notable risks:
- Code Page 437 lookup is linear for every output rune.
- Direct writes to physical text memory assume a valid CGA-compatible text buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/cga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/cputemp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/cputemp.c

CPU temperature `#P/cputemp` provider for Intel and AMD processors.

Key responsibilities:
- Detects Intel digital thermal sensor support through CPUID leaf 6 and reads thermal MSR `0x19c`.
- Estimates Intel TjMax, including older model handling through MSR `0xee`.
- Reads AMD temperature sensors through PCI configuration or system management network registers for supported families.
- Wires the current process to each CPU to read per-processor Intel sensor values.
- Adds `#P/cputemp` when a supported sensor path is found.

Important behavior:
- Outputs text lines in `temperature±resolution` format, with optional Intel alarm text.
- Unsupported Intel reads return `-1±-1 unsupported`.
- AMD family handling covers families `0x0f`, `0x10`-`0x16`, `0x17`, `0x19`, and `0x1a`.

Dependencies:
- Depends on CPUID/MSR helpers, PCI config access, process CPU wiring, and `addarchfile`.

Notable risks:
- AMD sensor access is noted as largely undocumented and motherboard-dependent.
- Static device lists and TjMax heuristics may be inaccurate on unrecognized CPUs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/cputemp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/dat.h

Core PC architecture data declarations for the 9front kernel.

Key contents:
- Forward declarations for PC-specific kernel structures such as `Mach`, `PCArch`, `ISAConf`, `Segdesc`, `Ureg`, `PCMslot`, and `BIOS32ci`.
- Floating-point save formats for x87 and SSE plus per-process FPU state.
- Physical memory configuration structs and global `Conf`.
- Per-process MMU state including page directory pages, GDT/LDT descriptors, debug registers, kmap tracking, and VMX pointer.
- x86 task-state segment layout.
- `Mach` CPU-local structure with CPU identity, timing, CPUID feature fields, MMU pools, TSS/GDT pointers, debug state, and stack.
- `PCArch` architecture vtable for reset, interrupts, and clocks.
- CPUID feature bit constants, MSR constants, `ISAConf`, device configuration helpers, and BIOS32 call interface registers.

Role:
- Bridges generic `portdat.h` definitions with PC-specific CPU, MMU, interrupt, firmware, ISA, and architecture-selection state.

Dependencies:
- Included by most PC kernel C files and depends on `mem.h` constants plus `../port/portdat.h`.

Notable constraints:
- Many globals are declared or defined directly in the header, matching Plan 9 kernel build conventions.
- Structure layouts are ABI-sensitive for assembly, trap, MMU, and BIOS call code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devarch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devarch.c

PC `#P/arch` device plus CPU identification, architecture selection, low-level controls, and hardware watchpoint setup.

Key responsibilities:
- Implements `#P` files for byte/word/long I/O port access, MSR access, and dynamically registered architecture files.
- Provides `addarchfile()` for other PC subsystems such as ACPI, APM, HDA, and CPU temperature.
- Initializes I/O allocation policy and optional `ioexclude` reservations.
- Identifies CPU vendor/family/model/features, enables TSC, PSE, MCE/MCA, PGE, PAT write-combining, MTRRs, NX, RDRAND, watchpoint width, and FPU support.
- Chooses the active `PCArch` from `knownarch[]` and fills missing hooks from the generic architecture.
- Exposes `cputype`, `archctl`, and `realmodemem` arch files.
- Implements `archctl` controls for PGE, memory-barrier strategy, and MTRR cache regions.
- Provides idle behavior, ISA config parsing, machine-check dump support, NMI enable/handler, and debug watchpoint programming.

Important behavior:
- Raw I/O access checks that ports are unused, with VGA register exceptions.
- `realmodemem` reads below 1 MiB and only permits writes to VGA framebuffer range.
- Coherence defaults progress from no-op to `mb586` or `mfence` depending on CPU features.
- On 386, copy-on-reference is selected because compare-and-swap is interrupt-disabled emulation.

Dependencies:
- Depends on port I/O, MSR/CPUID/CR4 helpers, MTRR, FPU, trap/NMI, `knownarch`, device framework, and kernel configuration parsing.

Notable risks:
- `#P/iob`, `#P/iow`, `#P/iol`, and `#P/msr` are intentionally powerful debugging interfaces.
- CPU tables contain many trial-and-error or guesswork model names/delay constants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devfloppy.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devfloppy.c

Intel 82077A/8272A-compatible floppy disk device driver implementing `#f`.

Key responsibilities:
- Defines supported floppy geometries and controller byte encodings.
- Initializes controller/drive state, DMA channel 2, per-drive track caches, motor state, and watchdog process.
- Exposes `fdNdisk` data files and `fdNctl` control files for up to four drives.
- Handles media change detection, density probing, recalibration, seeking, reading, writing, formatting, eject, reset, and debug controls.
- Performs controller command/result exchange, DMA setup/teardown, interrupt waiting, and error recovery.

Important behavior:
- Reads go through a per-drive track cache; writes invalidate the cached track.
- Media-change handling seeks and reads to clear the change condition, then cycles through compatible densities until one works.
- `floppykproc` turns motors off after roughly five seconds idle.
- Transfer commands cannot cross track boundaries; `floppypos()` truncates lengths accordingly.
- `floppyrevive()` resets the controller when the global state is confused.

Dependencies:
- Depends on PC floppy register constants from `floppy.h`, architecture floppy setup/exec/eject hooks, low DMA helpers, interrupts, and device framework.

Notable risks:
- Controller timing and spin-up delays are empirical.
- Error recovery relies on retry loops and controller reset state.
- Formatting constructs raw per-sector metadata and assumes the selected geometry is correct.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devfloppy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devi82365.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devi82365.c

Intel 82365SL-compatible PCMCIA controller driver implementing legacy `#y`.

Key responsibilities:
- Probes classic PCIC controllers at `0x3e0/0x3e1` and `0x3e2/0x3e3`, including Cirrus and Vadem variants.
- Creates per-slot `pcmNmem`, `pcmNattr`, and `pcmNctl` files.
- Powers slots on/off, reads CIS data, tracks insertion/removal state, and handles card-status-change interrupts.
- Maps PC Card memory/attribute space into ISA memory windows with ref-counted `PCMmap` entries.
- Provides `pcmspecial` and close hooks so ISA-style drivers can claim matching PCMCIA cards and configure I/O windows/IRQs from CIS tables.
- Supports control writes for VPP voltage.

Important behavior:
- Slot enable powers and unresets the card, then calls `pcmcisread()` if occupied.
- Attribute and common memory reads/writes are windowed in 4 KiB granularity and copied byte-wise.
- `pcmio()` chooses a CIS configuration by explicit index, best I/O/IRQ match, or first usable fallback.
- Configuration writes set PCIC IRQ routing, I/O map registers, config-register bits, I/O base, and I/O size where present.

Dependencies:
- Depends on `PCMslot`, `PCMmap`, and CIS structures from `dat.h`/port code, ISA memory allocation, I/O allocation, interrupts, and `_pcmspecial` global hooks.

Notable risks:
- Assumes PC Card CIS data is readable and accurate.
- Does not delete arch/device entries after discovery; slot state is managed by ref counts and power control.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devi82365.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devkbd.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devkbd.c

PS/2 i8042 keyboard and auxiliary-port device implementing raw scancode access.

Key responsibilities:
- Initializes the 8042 controller, enables scan-code set 1 keyboard interrupts, disables auxiliary interrupts by default, and allocates I/O ports.
- Provides `#b/scancode` for exclusive raw scancode reads and `#b/leds` for lock LED writes.
- Handles keyboard and auxiliary interrupts, routing mouse bytes to an installed aux callback.
- Implements i8042 reset command sequence used by architecture reset.
- Provides `i8042auxenable()` and `i8042auxcmd()` for PS/2 mouse support.
- Shuts down keyboard/aux transfers and interrupts on device shutdown.

Important behavior:
- `#b/scancode` can only be opened by `eve` and only one reader at a time.
- The scancode queue is nonblocking and coalescing.
- `kbdpoll()` opportunistically invokes the interrupt handler if the queue is empty.
- LED updates avoid redundant writes and use keyboard command `0xed`.

Dependencies:
- Depends on PC keyboard controller ports, interrupt registration, queues, device framework, and privilege checks.

Notable risks:
- `i8042reset()` is skipped when no keyboard controller was successfully initialized.
- Aux command failure prints returned byte and caller PC for diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devkbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devlml.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devlml.c

LML33/Zoran Motion JPEG capture device driver implementing `#Λ`.

Key responsibilities:
- Probes up to two Zoran 36057/36067 PCI devices and allocates page-aligned shared capture metadata/buffers.
- Maps device registers and registers physical segments for MJPEG buffers and device registers.
- Initializes fragment descriptors and per-fragment JPEG APP3 frame headers.
- Exposes per-card control, JPEG, and raw frame files.
- Handles JPEG-repetition interrupts by finding completed buffers, stamping frame number/time/size/sequence metadata, and waking readers.

Important behavior:
- JPEG reads either return a full `FrameHeader` or a one-byte buffer number; raw reads use non-sleeping buffer polling.
- Only one JPEG/raw open is allowed per card.
- `lmlNctl` reports file names and physical segment ranges used for external mapping.

Dependencies:
- Depends on PCI, physical segment registration, Zoran/LML constants from `devlml.h`, MMIO mapping, interrupts, and `todget`.

Notable risks:
- Debug flags are enabled for read/write/filesystem categories by default.
- Buffer ownership depends on hardware-set `STAT_BIT` in shared memory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devlml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devlml.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devlml.h

Hardware constants and shared-memory structures for the LML33 Motion JPEG driver.

Key contents:
- Defines driver version, maximum LML cards, timing constants, and Zoran vendor/device IDs.
- Defines I2C, interrupt, and register offsets used by `devlml.c`.
- Defines JPEG marker constants and `FrameHeader` layout embedded in captured buffers.
- Defines four-fragment capture buffering, fragment descriptor structures, and `CodeData` shared with hardware.
- Provides rounded `Codedatasize` and `Grabdatasize` constants.

Role:
- Captures the hardware ABI for Zoran/LML frame buffers and descriptors; comments warn not to alter the hardware-used struct layouts.

Dependencies:
- Used directly by `devlml.c` and depends on kernel page size constants/types.

Notable constraints:
- `FrameHeader`, `FragmentTable`, and `CodeData` layouts are hardware-facing and must remain stable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devlml.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devlpt.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devlpt.c

Centronics parallel printer-port device implementing `#L`.

Key responsibilities:
- Supports classic LPT base addresses `0x378`, `0x3bc`, and `0x278`.
- Exposes per-port files for data latch, printer status, printer control, and byte-stream data output.
- Allocates I/O port ranges on attach and detects ECP extended-control register mode when present.
- Writes raw register values or sends bytes with strobe/ready handshaking.
- Handles printer interrupts by waking blocked writers.

Important behavior:
- Attach spec selects 1-based LPT number, defaulting to LPT1.
- `data` writes loop one byte at a time through `outch()`.
- `outch()` waits for not-busy, checks paper/select/error bits, enables interrupts while sleeping, then strobes data.

Dependencies:
- Depends on I/O allocation, parallel-port IRQ, device framework, and low-level port I/O.

Notable risks:
- The initial one-time interrupt disable uses `lptbase[i-1]` before range validation of `i`.
- Error handling resets control register to `Finitbar` on write failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devlpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devpccard.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/devpccard.c

CardBus and 16-bit PC Card bridge driver implementing `#Y` and replacing/competing with older PCMCIA hooks.

Key responsibilities:
- Detects supported PCI/CardBus bridge variants from Ricoh, TI, and O2Micro.
- Maps CardBus socket registers, initializes bridge windows, bus numbers, interrupts, and vendor-specific bridge quirks.
- Maintains a slot state machine for card detected, powered, ejected, and configured events.
- Queues interrupt-driven card events to a kernel process for serialized power/configuration handling.
- Powers PC16 and PC32 cards, configures PC32 CardBus PCI devices, allocates bridge I/O and memory windows, maps child BARs, and assigns interrupts.
- Parses PC16 CIS tuples for version strings, configuration address/present bits, power, timing, I/O ranges, IRQ masks, and memory descriptions.
- Provides `pcmspecial` hooks for ISA-style drivers to claim matching PC16 cards and program PCIC-compatible I/O/IRQ windows.
- Exposes `cbNctl` files showing slot state, child PCI devices, PC16 configuration tables, and accepting `down`/`power` controls.

Important behavior:
- Uses a shared legacy PCIC index/data pair at `0x3e0/0x3e1` for 16-bit card compatibility.
- For PC32 cards, sizes downstream PCI resources, reserves at least 512 bytes I/O and 1 MiB memory, then programs CardBus bridge window registers.
- For PC16 cards, uses 4 KiB ISA memory mapping granularity and PCIC register programming similar to `devi82365.c`.
- `down` control can call a named device's config hook before forcing a CardEjected event.

Dependencies:
- Depends on PCI bridge scanning/sizing/mapping/freeing, I/O and upper-physical memory allocators, PCMCIA CIS structures, `_pcmspecial` hooks, interrupts, and device framework.

Notable risks:
- Event queue is fixed at ten entries and drops excess events.
- PC16 unconfiguration is incomplete beyond clearing in-memory info.
- Vendor setup uses several bridge-specific magic register writes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/devpccard.c -->