# Research: subset-b-000714

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/Kbuild

## Purpose
This Kbuild fragment declares generated and generic asm headers for the m68k architecture include tree. It tells the kernel header build that `syscall_table.h` is generated and that several asm headers are satisfied by `asm-generic`.

## Important APIs, Types, And Functions
- `generated-y += syscall_table.h` registers the generated syscall table header.
- `generic-y += extable.h`, `kvm_para.h`, `mcs_spinlock.h`, `spinlock.h`, and `text-patching.h` select generic implementations.

## Control Flow
There is no runtime control flow. The kernel build system reads these variables while exporting or preparing architecture headers.

## State And Persistence Behavior
The file persists build metadata only. It does not define kernel state, but changes alter which headers are generated or delegated to generic asm code.

## Dependencies And Integration Points
It integrates with Kbuild's `scripts/Makefile.asm-generic` handling and with generated header production for m68k syscalls.

## Risks And Edge Cases
Removing a `generic-y` entry can make include resolution fail. Adding a generated header without a matching generator can break `headers_install` or normal builds.

## Test Signals
Run `make ARCH=m68k headers_check` or an m68k kernel build and verify generated `asm/syscall_table.h` and generic asm includes resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/MC68328.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/MC68328.h

## Purpose
This header is the memory-mapped register contract for Motorola DragonBall MC68328 SoCs used by m68knommu systems. It exposes volatile byte, word, and long register lvalues plus bit masks for system control, chip selects, clocks, interrupts, GPIO, PWM, timers, watchdog, SPI, UART, LCD, and RTC.

## Important APIs, Types, And Functions
- `BYTE_REF`, `WORD_REF`, and `LONG_REF` cast fixed addresses to volatile register references.
- `PUT_FIELD()` and `GET_FIELD()` encode/decode masked bitfields using `*_MASK` and `*_SHIFT` constants.
- Register groups include `SCR`, `MRR`, `CSA` through `CSD`, `PLLCR`, `PLLFSR`, `IVR`/`ICR`/`IMR`/`ISR`/`IPR`, ports A through M, `PWMC`/`PWMP`/`PWMW`/`PWMCNT`, timers `TCTL1/2` through `TSTAT1/2`, watchdog `WRR`/`WCN`/`WCSR`, SPI slave/master, UART `USTCNT`/`UBAUD`/`URX`/`UTX`/`UMISC`, LCD controller registers, and RTC alarm/status/enable registers.
- `typedef volatile struct __packed m68328_uart` provides a packed UART register block abstraction for multi-port code.

## Control Flow
The header has no functions. Drivers and early platform code directly read and write the volatile lvalue macros. Control flow is implicit in hardware side effects: writing chip-select, PLL, interrupt-mask, GPIO, timer, UART, LCD, and RTC registers immediately changes device behavior.

## State And Persistence Behavior
All mutable state is in SoC hardware registers at fixed physical addresses, not in C-owned memory. Values persist according to hardware reset and power domains. The file also creates source compatibility aliases for EZ328-style names, so older driver code can target the primary timer, PWM, UART, and LCD fields through common macros.

## Dependencies And Integration Points
This header is consumed by m68knommu board, serial, timer, framebuffer, RTC, GPIO, and interrupt code for MC68328 systems. It assumes direct addressability of the `0xfffffxxx` peripheral window and correct compiler treatment of volatile memory-mapped I/O.

## Risks And Edge Cases
- The register map is entirely macro-based, so type checking is weak and incorrect register width use can corrupt adjacent hardware state.
- Interrupt status/pending and watchdog registers commonly have write-one-clear or reset-trigger semantics; generic read-modify-write code can be unsafe.
- Some aliases are compatibility shims and may hide differences from MC68EZ328 or MC68VZ328 hardware.
- `STPWCH` is defined through `WORD_REF(STPWCH)` rather than its address macro, which looks suspicious and should be treated carefully if referenced.

## Test Signals
Cross-build affected board configs. On hardware or emulator, verify timer tick, UART console, interrupt mask/status handling, LCD frame setup, RTC alarm/status, watchdog behavior, and GPIO direction/data configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/MC68328.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/MC68EZ328.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/MC68EZ328.h

## Purpose
This header defines the memory-mapped register interface for the Motorola MC68EZ328 DragonBall EZ SoC. It is a fixed-address hardware map for board support and drivers, closely related to the original MC68328 but with EZ-specific clock, interrupt, GPIO, PWM, timer, UART, LCD, and RTC definitions.

## Important APIs, Types, And Functions
- `BYTE_REF`, `WORD_REF`, `LONG_REF`, `PUT_FIELD()`, and `GET_FIELD()` are the same volatile register and bitfield helpers used by sibling DragonBall headers.
- Major register groups cover system control/reset, chip-select base/control, PLL and power control, interrupt vector/control/mask/status/pending, GPIO ports, PWM, timer/watchdog, SPI, UART, LCD controller, and RTC.
- UART register layout is generalized by a packed volatile UART struct, allowing code to treat the single EZ UART as a register block.
- Compatibility macros preserve common `*_ADDR` and mask names expected by older DragonBall drivers.

## Control Flow
No executable control flow is defined. Platform code sequences volatile writes to bring up memory maps, clocks, interrupt masks, timers, serial ports, and display output. Reads from status registers drive interrupt handlers and polling loops.

## State And Persistence Behavior
State is exclusively in hardware registers. Configuration persists until reset, power loss, or a later write by kernel code. The aliases in this header persist only at compile time and are used to share driver source with MC68328/MC68VZ328 variants.

## Dependencies And Integration Points
Consumers are m68knommu DragonBall EZ board files, timer/clock code, serial drivers, LCD framebuffer support, RTC code, and interrupt handlers. Correct use depends on the SoC's peripheral window being mapped as expected.

## Risks And Edge Cases
- Similar macro names across MC68328, MC68EZ328, and MC68VZ328 can make it easy to compile code against the wrong SoC variant.
- Register-width mismatches are not protected by the C type system beyond the chosen `BYTE_REF`/`WORD_REF`/`LONG_REF` macro.
- Polling and interrupt code must honor hardware status clearing semantics; careless read-modify-write can drop interrupts.
- Clock and chip-select fields affect all later memory and peripheral access, so initialization order is critical.

## Test Signals
Build MC68EZ328 board configs and validate boot console, timer interrupts, interrupt masking/acknowledgement, GPIO pin muxing, LCD setup, RTC, and watchdog operation on target hardware or a faithful emulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/MC68EZ328.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/MC68VZ328.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/MC68VZ328.h

## Purpose
This header maps Motorola MC68VZ328 DragonBall VZ control registers for m68knommu systems. It exposes volatile register lvalues and masks for the VZ memory controller, PLL/power control, interrupt controller, larger GPIO set, PWM, timers, SPI, UARTs, LCD controller, RTC, and compatibility names for earlier DragonBall code.

## Important APIs, Types, And Functions
- `BYTE_REF`, `WORD_REF`, `LONG_REF`, `PUT_FIELD()`, and `GET_FIELD()` are the core register helpers.
- Register groups include system control/reset, chip-select group/base/control, emulator chip select, PLL `PLLCR`/`PLLFSR`, power control, interrupt registers, GPIO ports A through M, PWM control/status/period/count, timers and watchdog, SPI master/slave interfaces, UART controls, LCD timing/framebuffer/cursor/palette fields, and RTC time/alarm/status/enable registers.
- Compatibility aliases map VZ names to older `SPI`, `TMR1`, `UART1`, `PWM`, and LCD clock names where driver code expects 328-style identifiers.

## Control Flow
There is no C function control flow. Hardware control is performed by ordered volatile accesses from board and device code. Interrupt flow is mediated through `IMR`, `ISR`, and `IPR` masks and status/pending bits, while timer/UART/LCD/RTC drivers use their register groups for runtime operation.

## State And Persistence Behavior
All state is hardware-resident. Writes can persist across large parts of kernel runtime until reset or explicit reconfiguration. The header does not serialize access; callers must protect shared interrupt, GPIO, and timer registers themselves.

## Dependencies And Integration Points
It integrates with DragonBall VZ platform setup, clock/timer code, serial drivers, framebuffer/LCD support, RTC, keyboard/GPIO paths, and interrupt dispatch. It assumes direct mapped access to `0xfffff000` and related peripheral addresses.

## Risks And Edge Cases
- The VZ has additional ports and interrupt sources compared with older DragonBall parts, so compatibility aliases can mask real feature differences.
- The port D area includes macros around polarity/IRQ/keyboard registers; edits need validation against the data sheet because a misspelled or absent address macro would become a compile or runtime fault.
- Register definitions are raw volatile lvalues, so accidental multiple evaluation or read-modify-write on clear-on-write bits can be harmful.

## Test Signals
Cross-build VZ board support and run hardware tests for timer, UART1/UART2 where present, GPIO keyboard interrupts, LCD frame timing, RTC status/alarms, PWM, SPI, and all interrupt mask/pending paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/MC68VZ328.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/adb_iop.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/adb_iop.h

## Purpose
This header describes the Apple Desktop Bus protocol messages exchanged with a Macintosh IOP channel. It supplies command, status, and message layout definitions for ADB-over-IOP drivers.

## Important APIs, Types, And Functions
- `ADB_IOP` and `ADB_CHAN` select the ISM IOP and channel 2.
- Command bits include `ADB_IOP_LISTEN`, `TALK`, `EXISTS`, `FLUSH`, `RESET`, `INT`, `POLL`, and `UNINT`.
- ADB immediate function codes include `AIF_RESET`, `AIF_FLUSH`, `AIF_LISTEN`, and `AIF_TALK`.
- `struct adb_iopmsg` defines flags, byte count, command byte, eight bytes of ADB payload, and spare padding.

## Control Flow
There is no executable control flow. IOP ADB code fills `struct adb_iopmsg`, sends it to the selected channel, then interprets returned flags such as explicit command completion, autopoll, SRQ, and timeout.

## State And Persistence Behavior
Message state is transient and owned by the caller/IOP transport. Persistent ADB state, such as autopoll enablement or device existence, is maintained by the IOP and ADB stack.

## Dependencies And Integration Points
The file depends on IOP numbering definitions such as `IOP_NUM_ISM` and on fixed-width kernel integer types. It integrates with Macintosh ADB input and IOP transport code.

## Risks And Edge Cases
The packed protocol is implicit rather than marked packed; layout assumptions depend on byte fields and natural alignment. Payload length must not exceed `data[8]`, and timeout/autopoll flags must be interpreted together to avoid stale input state.

## Test Signals
ADB keyboard/mouse detection on IOP-based Macs, command timeout handling, autopoll/SRQ behavior, and reset/flush/talk/listen transaction tests are direct validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/adb_iop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigahw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigahw.h

## Purpose
This header is the central Amiga hardware map for m68k Linux. It describes detected hardware flags, global clock/memory properties, custom chip register layouts, CIA registers, Zorro-II address translation, chip RAM allocation APIs, display shutdown behavior, and Amiga TOD clock register formats.

## Important APIs, Types, And Functions
- Global state includes `amiga_chipset`, `amiga_eclock`, `amiga_colorclock`, `amiga_chip_size`, `amiga_vblank`, `amiga_hw_present`, and `amiga_audio_min_period`.
- `struct amiga_hw_present` records available video, audio, storage, I/O, clock, chipset, PCMCIA, and Zorro features.
- `struct CUSTOM` maps the large Amiga custom chip register block, including DMA, blitter, copper, bitplanes, sprites, audio channels, colors, beam timing, and fetch mode.
- `struct CIA` maps CIAA/CIAB timers, ports, serial, and interrupt registers.
- `amiga_custom`, `ciaa`, `ciab`, `ZTWO_PADDR()`, and `ZTWO_VADDR()` provide fixed register and Zorro-II translations.
- `amiga_chip_init()`, `amiga_chip_alloc()`, `amiga_chip_alloc_res()`, `amiga_chip_free()`, and `amiga_chip_avail()` expose chip RAM allocation.
- `amifb_video_off()` programs ECS/AGA display timing and adjusts minimum audio period.

## Control Flow
Most use is direct volatile hardware access. Platform setup fills hardware-present flags and globals from bootinfo. Drivers probe flags, access `amiga_custom` or CIA registers, and allocate chip RAM. `amifb_video_off()` conditionally writes display timing registers when the chipset supports ECS/AGA.

## State And Persistence Behavior
Persistent kernel state is in the exported globals and `amiga_hw_present`; hardware state persists in custom chips and CIAs. Chip RAM allocations are tracked by the implementation behind the declared allocator APIs. TOD clock structs map battery-backed hardware clock nibbles.

## Dependencies And Integration Points
The file depends on Amiga bootinfo and Linux resource types. It is used by framebuffer, sound, input, serial/parallel, floppy, SCSI/IDE, PCMCIA, Zorro, RTC, and platform initialization code.

## Risks And Edge Cases
- `struct CUSTOM` layout must match the hardware reference exactly; padding or type changes can redirect register writes.
- Chip RAM is shared with DMA-capable custom chips, so allocation alignment/lifetime bugs can corrupt display/audio/disk DMA.
- `amifb_video_off()` changes beam timing and audio limits globally.
- Zorro-II address translation assumes the `zTwoBase` virtual mapping.

## Test Signals
Amiga platform boot, hardware detection, chip RAM allocator stress, framebuffer on/off, audio DMA, CIA timer/interrupt handling, floppy/IDE/SCSI access, RTC reads, and Zorro device probing validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigahw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigaints.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigaints.h

## Purpose
This header defines Amiga interrupt source numbering and register bit masks. It bridges generic m68k IRQ numbers to Amiga custom-chip and CIA interrupt sources.

## Important APIs, Types, And Functions
- `AUTO_IRQS`, `AMI_STD_IRQS`, `CIA_IRQS`, and `AMI_IRQS` define source counts.
- `IRQ_AMIGA_*` constants assign serial, disk, soft, ports, external, copper, vertical blank, blitter, audio, and CIA A/B subinterrupts.
- `IF_*` masks represent Amiga custom interrupt register bits such as `IF_INTEN`, `IF_EXTER`, `IF_RBF`, `IF_AUD*`, `IF_BLIT`, `IF_VERTB`, and `IF_TBE`.
- `CIA_ICR_*` masks represent CIA timer, alarm, serial, flag, all, and set/clear bits.
- Declared APIs include `amiga_init_IRQ()`, `cia_init_IRQ()`, `cia_set_irq()`, and `cia_able_irq()`.

## Control Flow
Initialization code calls `amiga_init_IRQ()` and `cia_init_IRQ()` to register handlers. Runtime interrupt code maps hardware INTREQ/CIA bits to the `IRQ_AMIGA_*` namespace and uses CIA helpers to set, enable, or disable subinterrupt masks.

## State And Persistence Behavior
The header stores no state, but its masks operate on persistent hardware interrupt-enable/request registers and on `ciaa_base`/`ciab_base` runtime descriptors declared here.

## Dependencies And Integration Points
It depends on `asm/irq.h` for base IRQ numbering and integrates with Amiga custom-chip interrupt code, CIA support, serial, audio, disk, input, and timer drivers.

## Risks And Edge Cases
Interrupt numbering is ABI-like inside the arch port. Off-by-one changes can route handlers to the wrong source. CIA set/clear semantics require using `CIA_ICR_SETCLR` correctly or interrupts may be disabled while appearing configured.

## Test Signals
Boot IRQ initialization, vertical blank timer events, serial RX/TX, disk block/sync, audio channel completion, blitter completion, ports/external IRQs, and individual CIA timer/alarm/flag interrupts provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigaints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigayle.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigayle.h

## Purpose
This header maps the Amiga Gayle chip used for A1200-style IDE and PCMCIA support. It defines Gayle memory windows, main registers, interrupt/status/config bits, reset access, and IDE platform data.

## Important APIs, Types, And Functions
- `GAYLE_RAM`, `GAYLE_ATTRIBUTE`, `GAYLE_IO`, `GAYLE_IO_8BITODD`, and size macros define the PCMCIA memory and I/O windows.
- `struct GAYLE` exposes `cardstatus`, `intreq`, `inten`, and `config` registers separated by 0x1000-byte gaps.
- `gayle`, `gayle_reset`, and `gayle_attribute` are volatile register/window accessors.
- `GAYLE_CS_*`, `GAYLE_IRQ_*`, and `GAYLE_CFG_*` define PCMCIA status, interrupt, voltage, and speed bits.
- `struct gayle_ide_platform_data` carries IDE base, IRQ port, and explicit ack requirement.

## Control Flow
Drivers read `gayle.cardstatus`, acknowledge or enable interrupts through `intreq`/`inten`, program voltage/speed via `config`, and use `gayle_reset` for reset sequencing. IDE setup passes `gayle_ide_platform_data` to the relevant platform driver.

## State And Persistence Behavior
Persistent state lives in Gayle hardware registers and the platform data supplied during device registration. PCMCIA card status and interrupt bits change asynchronously with card insertion/removal and device IRQs.

## Dependencies And Integration Points
The header depends on Amiga `zTwoBase` mapping from `amigahw.h` and Linux integer types. It integrates with Amiga PCMCIA, IDE, and interrupt handling.

## Risks And Edge Cases
Status bit names are reused for different card meanings, such as BVD/status-change and busy/IRQ, so callers must interpret bits by card type and context. Odd 8-bit I/O addressing is unusual and easy to mishandle.

## Test Signals
Validate A1200 IDE probing and explicit ack, PCMCIA insert/remove detection, voltage/speed programming, interrupt enable/ack paths, attribute memory reads, and reset sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigayle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amipcmcia.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/amipcmcia.h

## Purpose
This header provides the Amiga PCMCIA API on top of the Gayle chip. It declares card reset/configuration helpers, inline status/interrupt operations, voltage and speed constants, and Card Information Structure tuple/function IDs.

## Important APIs, Types, And Functions
- Declared functions: `pcmcia_reset()`, `pcmcia_copy_tuple()`, `pcmcia_program_voltage()`, `pcmcia_access_speed()`, `pcmcia_write_enable()`, and `pcmcia_write_disable()`.
- Inline helpers read `gayle.cardstatus`, read/ack `gayle.intreq`, and set/clear `GAYLE_IRQ_IRQ` in `gayle.inten`.
- `PCMCIA_INSERTED` tests `GAYLE_CS_CCDET`.
- Constants define valid voltages, access speeds, CIS tuple IDs, and `CISTPL_FUNCID_*` function classes.

## Control Flow
PCMCIA setup sequences reset, voltage, access speed, tuple reads, and write-enable state. Interrupt handlers read pending Gayle bits, acknowledge with `pcmcia_ack_int()`, and enable/disable IRQ delivery with the inline helpers.

## State And Persistence Behavior
Runtime state is in the Gayle registers and card CIS memory. The header owns no persistent state, but helper calls affect card power, timing, write-protect behavior, and interrupt enablement.

## Dependencies And Integration Points
It depends on `amigayle.h` for register definitions. It integrates with Amiga PCMCIA socket support and client drivers that parse CIS tuples.

## Risks And Edge Cases
`pcmcia_ack_int()` writes `0xf8` regardless of its `intreq` parameter, so callers should not expect selective acknowledgement from the argument. Incorrect voltage/speed programming can damage cards or break enumeration.

## Test Signals
Card insertion detection, CIS tuple reads, voltage and speed switching, IRQ enable/disable/ack, write-enable toggling, and network/storage PCMCIA client probing are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amipcmcia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/apollohw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/apollohw.h

## Purpose
This header maps Apollo workstation hardware for the m68k port. It describes serial controller, RTC, PIC, CPU control, timer, model-specific physical addresses, and ISA-style I/O translation.

## Important APIs, Types, And Functions
- `apollo_model` and physical address globals describe selected machine layout.
- `struct SCN2681` maps a dual UART register file with alternating dummy bytes.
- `struct mc146818` maps RTC fields.
- `SAU7_*` and `SAU8_*` constants provide model-specific register offsets.
- `sio01`, `sio23`, `rtc`, `cpuctrl`, `pica`, `picb`, `apollo_timer`, and `addr_xlat_map` are direct memory-mapped accessors.
- `isaIO2mem(x)` translates ISA I/O addresses into Apollo memory space.

## Control Flow
Platform setup selects address globals based on bootinfo/model. Drivers then directly access UARTs, RTC, PICs, CPU control, and timer through volatile pointers and translated I/O addresses.

## State And Persistence Behavior
State lives in hardware registers and selected global physical address variables. RTC values persist in hardware; serial/PIC/timer control persists until reprogrammed or reset.

## Dependencies And Integration Points
The file depends on Apollo bootinfo and Linux types. It integrates with Apollo platform setup, serial, RTC, interrupt, timer, and bus I/O code.

## Risks And Edge Cases
Wrong model address selection maps drivers to invalid hardware. `DECLARE_2681_FIELD` depends on byte spacing matching the SCN2681 bus wiring. `isaIO2mem()` is bit-level address translation and should be changed only with hardware validation.

## Test Signals
Apollo boot, UART console, RTC read/write, PIC interrupt delivery, timer tick, CPU control register access, and ISA I/O translated device access validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/apollohw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-offsets.h

## Purpose
This shim header includes the generated m68k `asm-offsets.h` file. It gives assembly and C sources a stable include path for offsets computed during the build.

## Important APIs, Types, And Functions
- `#include <generated/asm-offsets.h>` is the only interface.

## Control Flow
There is no runtime control flow. The compiler/preprocessor substitutes generated constants at build time.

## State And Persistence Behavior
The header stores no state. The generated include contains build-derived offsets for structures used by low-level assembly.

## Dependencies And Integration Points
It depends on the architecture build generating `generated/asm-offsets.h` before sources that include this file are compiled.

## Risks And Edge Cases
If generated offsets are stale or missing, low-level entry and context-switch code can assemble with wrong or absent constants.

## Test Signals
A clean m68k build from no generated headers validates generation ordering and offset availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-prototypes.h

## Purpose
This header declares compiler helper routines implemented outside normal C code and referenced by m68k assembly or libgcc-like paths.

## Important APIs, Types, And Functions
- Signed helpers: `__divsi3()`, `__modsi3()`, and `__mulsi3()`.
- Unsigned helpers: `__udivsi3()` and `__umodsi3()`.

## Control Flow
There is no header-local control flow. Callers branch to helper implementations when generated code or assembly needs 32-bit division, modulo, or multiplication support.

## State And Persistence Behavior
No persistent state is defined; helpers are pure arithmetic contracts from the caller perspective.

## Dependencies And Integration Points
This integrates with m68k arithmetic helper implementations and modversion/prototype generation for assembly-exported symbols.

## Risks And Edge Cases
Prototype mismatches can corrupt calling conventions for arithmetic helpers. Division helpers must preserve ABI expectations around registers and signedness.

## Test Signals
Builds with symbol versioning and arithmetic-heavy code paths, plus runtime tests for signed/unsigned division, modulo, and multiplication on CPU variants lacking native support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_joystick.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_joystick.h

## Purpose
This header declares the Atari joystick driver interface and shared joystick state structure.

## Important APIs, Types, And Functions
- `atari_joystick_interrupt(char *)` consumes interrupt data from the Atari keyboard/IKBD path.
- `atari_joystick_init()` initializes joystick support.
- `atari_mouse_buttons` exposes mouse button state shared with input handling.
- `struct joystick_status` stores fire/direction data, readiness/activity flags, and a wait queue for blocking readers.

## Control Flow
IKBD input code calls the interrupt handler with device bytes. The driver updates `joystick_status` and wakes waiters. Initialization registers the device/input path.

## State And Persistence Behavior
State persists in driver-owned `joystick_status` instances and `atari_mouse_buttons`. The header only defines the shape and entry points.

## Dependencies And Integration Points
It depends on wait queue types being visible to includers and integrates with Atari keyboard, mouse, joystick, and input drivers.

## Risks And Edge Cases
The interrupt byte buffer has an untyped `char *` interface, so length and packet interpretation must be controlled by the caller. Shared mouse button state can race unless protected by driver locking.

## Test Signals
Joystick event delivery, blocking read wakeups, mouse button state updates, initialization success, and IKBD interrupt packet parsing validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_joystick.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stdma.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stdma.h

## Purpose
This header declares the lock and ownership interface for Atari ST-DMA, a shared DMA engine used by multiple storage-related devices.

## Important APIs, Types, And Functions
- `stdma_try_lock()`, `stdma_lock()`, and `stdma_release()` manage exclusive access and associate an interrupt handler/data pair with the current owner.
- `stdma_islocked()` and `stdma_is_locked_by()` query ownership.
- `stdma_init()` initializes the ST-DMA arbitration layer.

## Control Flow
Device drivers acquire the ST-DMA lock before programming DMA registers, hold it while a transfer and handler are active, and release it when complete. Contenders either fail `try_lock` or block through `stdma_lock`.

## State And Persistence Behavior
Persistent state is implementation-owned: lock status, owner handler, owner data, and initialized hardware state. The header defines the external synchronization contract.

## Dependencies And Integration Points
It depends on `linux/interrupt.h` for `irq_handler_t` and integrates with Atari floppy, ACSI, SCSI, IDE, and other users of the shared ST-DMA hardware.

## Risks And Edge Cases
Releasing from the wrong owner or programming hardware without the lock can corrupt concurrent transfers. Interrupt handlers must match the owner or completion can be delivered to the wrong driver.

## Test Signals
Concurrent ST-DMA clients, failed try-lock paths, blocking lock/release ordering, owner checks, and DMA interrupt delivery for floppy/SCSI/IDE are direct signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stram.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stram.h

## Purpose
This header declares Atari ST-RAM allocation and address-translation services. ST-RAM is required by hardware with DMA addressing limitations.

## Important APIs, Types, And Functions
- `atari_stram_alloc()` and `atari_stram_free()` allocate/free ST-RAM by owner name.
- `atari_stram_to_virt()` and `atari_stram_to_phys()` convert between ST-RAM physical and virtual addresses.
- `atari_stram_init()` and `atari_stram_reserve_pages()` are initialization/reservation hooks used by platform memory setup.

## Control Flow
Boot code initializes and reserves ST-RAM pages. Device drivers allocate ST-RAM buffers for DMA and translate addresses when programming hardware.

## State And Persistence Behavior
Allocator state is implementation-owned and persists across driver lifetime. Allocations represent scarce low-memory/DMA-capable memory and must be explicitly freed.

## Dependencies And Integration Points
It integrates with Atari memory setup, DMA-capable drivers, framebuffer/audio/storage paths, and any device unable to DMA from general RAM.

## Risks And Edge Cases
Leaked ST-RAM depletes a limited resource. Incorrect physical/virtual conversion can program bad DMA addresses. Early reservation must happen before general memory allocation consumes DMA-required pages.

## Test Signals
Boot memory reservation, repeated allocate/free cycles, DMA transfers from allocated ST-RAM, and conversion round trips validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarihw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarihw.h

## Purpose
This is the central Atari hardware register map for m68k Linux. It declares machine identity globals, NVRAM APIs, hardware-present flags, DMA cache maintenance, and volatile register structs for Atari video, DMA, sound, SCSI, SCC, DSP, MFP, SCU, RTC, ACIA, DMA sound, Microwire, and add-on hardware.

## Important APIs, Types, And Functions
- Machine predicates include `MACH_IS_ST`, `MACH_IS_STE`, `MACH_IS_MSTE`, `MACH_IS_TT`, `MACH_IS_FALCON`, `MACH_IS_MEDUSA`, and `MACH_IS_AB40`.
- `struct atari_hw_present` records available shifters, sound, storage interfaces, MFP/SCC/joystick/Microwire, DMA engines, clocks, SCU, blitter, VME, and DSP56K.
- NVRAM APIs are `atari_nvram_read()`, `atari_nvram_write()`, `atari_nvram_get_size()`, `atari_nvram_set_checksum()`, and `atari_nvram_initialize()`.
- `dma_cache_maintenance()` pushes or clears caches for DMA with Medusa and CPU-specific snooping exceptions.
- Register structs map `SHIFTER_ST`, `SHIFTER_TT`, `VIDEL`, `DMA_WD`, `SOUND_YM`, `TT_DMA`, `TT_5380`, `MATRIX`, `CODEC`, `BLITTER`, `SCC`, `DSP56K_HOST_INTERFACE`, `MFP`, `TT_SCU`, `TT_RTC`, `ACIA`, `TT_DMASND`, `TT_MICROWIRE`, and `MSTE_RTC`.
- Helper macros such as `DMASNDSetBase()`, `DMASNDGetAdr()`, `DMASNDSetEnd()`, and `MW_LM1992_*()` encode hardware register programming values.

## Control Flow
Platform setup fills machine globals and hardware-present flags. Drivers test those flags and write directly to the relevant volatile register structs. DMA users call `dma_cache_maintenance()` before or after transfers depending on direction. Sound, video, RTC, keyboard, serial, and storage drivers use the mapped structs to program hardware.

## State And Persistence Behavior
Persistent kernel state is in machine globals and `atari_hw_present`. Hardware state lives in memory-mapped registers and may change asynchronously through DMA, video counters, interrupts, and device activity. NVRAM persists across reboots.

## Dependencies And Integration Points
The header depends on Atari bootinfo, `asm/kmap.h`, MM/cacheflush support, and CPU feature macros. It is used broadly by Atari platform, framebuffer, sound, storage, serial, input, DSP, RTC/NVRAM, and interrupt code.

## Risks And Edge Cases
- Register layouts and padding are hardware contracts; field changes can silently write wrong addresses.
- DMA cache maintenance depends on machine and CPU snooping behavior and is easy to regress for Medusa/060 combinations.
- Many fixed addresses are accessed directly; mapping assumptions must hold before use.
- Duplicated or shared registers, such as Falcon/TT DMA sound fields, require machine-specific interpretation.

## Test Signals
Atari boot across ST/STE/TT/Falcon, hardware-present detection, NVRAM read/write/checksum, video mode changes, ST-DMA storage, SCSI, SCC/ACIA serial, sound/DMA sound, Microwire volume control, DSP host interface, MFP interrupts, and RTC reads are coverage signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarihw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atariints.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atariints.h

## Purpose
This header defines Atari interrupt source numbering and inline MFP interrupt register operations. It provides the mapping between vectors, source indexes, MFP/SCC/VME interrupt domains, and Linux IRQ control.

## Important APIs, Types, And Functions
- Source bases include `STMFP_SOURCE_BASE`, `TTMFP_SOURCE_BASE`, `SCC_SOURCE_BASE`, `VME_SOURCE_BASE`, and `NUM_ATARI_SOURCES`.
- `IRQ_VECTOR_TO_SOURCE()` and `IRQ_SOURCE_TO_VECTOR()` convert between vector numbers and source indexes.
- `IRQ_MFP_*`, `IRQ_TT_MFP_*`, `IRQ_SCC*`, and shared timer constants identify interrupt sources.
- `get_mfp_bit()`, `set_mfp_bit()`, and `clear_mfp_bit()` compute MFP register addresses and operate on enable, pending, service, or mask bits.
- `atari_enable_irq()`, `atari_disable_irq()`, `atari_turnon_irq()`, `atari_turnoff_irq()`, `atari_clear_pending_irq()`, and `atari_irq_pending()` are inline IRQ controls.
- `atari_register_vme_int()` and `atari_unregister_vme_int()` manage VME interrupt allocation.

## Control Flow
Interrupt setup uses source/vector macros to register handlers. Runtime IRQ enable/disable paths update MFP mask registers; turn-on/off paths update MFP enable and pending bits. Pending checks read MFP pending registers to decide dispatch or acknowledge behavior.

## State And Persistence Behavior
The state is in MFP hardware registers, plus VME allocation state in the implementation. The inline helpers mutate hardware directly and do not maintain separate software shadow state.

## Dependencies And Integration Points
It depends on `asm/irq.h` and `atarihw.h` for MFP register mappings. It integrates with Atari interrupt controller code, MFP timer, serial, storage, SCC, VME, and device drivers.

## Risks And Edge Cases
The MFP register address calculation is compact and relies on source numbering layout. `clear_mfp_bit()` has different semantics for pending/service versus enable/mask registers; using the wrong type can lose interrupts. Range checks exclude non-MFP domains from inline helpers.

## Test Signals
Interrupt vector/source conversion tests, MFP enable/mask/pending operations, timer A-D interrupts, serial RX/TX/error interrupts, storage IRQs, SCC interrupts, and VME allocation/free paths validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atariints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarikb.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarikb.h

## Purpose
This header declares the Atari intelligent keyboard controller interface for keyboard, mouse, joystick, and MIDI-related input handling.

## Important APIs, Types, And Functions
- `ikbd_write()` sends raw commands.
- Mouse configuration functions set button action, relative/absolute mode, keyboard-emulation mode, thresholds, scaling, position get/set, origin orientation, and disable state.
- Joystick functions enable/disable events, request state, and disable joystick reporting.
- Hooks include `atari_MIDI_interrupt_hook`, `atari_input_keyboard_interrupt_hook`, and `atari_input_mouse_interrupt_hook`.
- `atari_keyb_init()` initializes the keyboard/input subsystem.

## Control Flow
Input setup initializes IKBD and installs hooks. Drivers send IKBD commands through the declared helpers. Interrupt processing calls the registered keyboard, mouse, MIDI, or joystick hooks with decoded bytes or packet data.

## State And Persistence Behavior
State is held by the IKBD hardware and the implementation: hook pointers, current mouse/joystick mode, scaling, thresholds, and position. The header exposes the mutable hook interface.

## Dependencies And Integration Points
It integrates with Atari keyboard, mouse, joystick, MIDI, serial/ACIA, and Linux input drivers.

## Risks And Edge Cases
Hook pointers are global and must be installed/removed with care. IKBD command sequences are stateful; interleaving mode changes with interrupt packets can produce misdecoded input.

## Test Signals
Keyboard scancode delivery, relative/absolute mouse events, mouse position get/set, joystick event mode, MIDI interrupt hook execution, and init failure paths are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarikb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atomic.h

## Purpose
This header implements m68k `atomic_t` operations for the Linux atomic API. It uses inline assembly for native memory operations and switches between CAS-based read-modify-write instructions and interrupt-disabled fallbacks depending on CPU capability.

## Important APIs, Types, And Functions
- `arch_atomic_read()` and `arch_atomic_set()` use `READ_ONCE` and `WRITE_ONCE`.
- Generated operations implement add, sub, and/or/xor plus return and fetch variants.
- `arch_atomic_inc()`, `arch_atomic_dec()`, `arch_atomic_dec_and_test()`, `arch_atomic_inc_and_test()`, `arch_atomic_sub_and_test()`, and `arch_atomic_add_negative()` use condition-code setting assembly.
- When `CONFIG_RMW_INSNS` is absent, `arch_atomic_cmpxchg()` and `arch_atomic_xchg()` are implemented under `local_irq_save()`.
- `ASM_DI` handles ColdFire immediate-to-memory instruction constraints.

## Control Flow
Most operations expand inline at call sites. CAS-capable builds loop around `casl` until the memory word updates successfully. Non-RMW builds disable local interrupts, update `v->counter`, and restore interrupts to provide uniprocessor atomicity.

## State And Persistence Behavior
The only state mutated is the target atomic counter. Local interrupt flags are temporarily saved/restored on fallback paths. The design assumes no SMP m68k systems.

## Dependencies And Integration Points
It depends on Linux atomic types, irqflags, m68k `cmpxchg`, and barrier definitions. It underpins reference counts, flags, and synchronization throughout the kernel on m68k.

## Risks And Edge Cases
The implementation relies on uniprocessor assumptions; it is not an SMP-safe design without hardware atomics. Inline assembly constraints differ for ColdFire. Missing memory clobbers or wrong output constraints would create subtle races.

## Test Signals
Cross-build ColdFire, non-RMW, and RMW configs. Run atomic API selftests, refcount stress, interrupt-heavy tests around fallback paths, and compare return/fetch semantics for add/sub/bitwise operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/bitops.h

## Purpose
This header implements m68k architecture bit operations for the Linux bitops API. It selects instruction forms for ColdFire, 68000-class CPUs, and 68020+ bitfield-capable CPUs.

## Important APIs, Types, And Functions
- Low-level helpers implement set/clear/change/test-and-set/test-and-clear/test-and-change using `bset`, `bclr`, `bchg`, or bitfield instructions.
- Public arch hooks include `arch___set_bit()`, `arch___clear_bit()`, `arch___change_bit()`, and test-and-operation variants.
- `arch_test_bit` and `arch_test_bit_acquire` defer to generic implementations.
- Bit address calculations use `(nr ^ 31) / 8` and `(nr & 7)` to match m68k big-endian bit numbering.

## Control Flow
Compile-time `CONFIG_COLDFIRE` and `CONFIG_CPU_HAS_NO_BITFIELDS` select register, memory, or bitfield instruction implementations. For constant bit numbers on bitfield-capable CPUs, the code still uses shorter memory bit instructions; dynamic indexes use bitfield operations.

## State And Persistence Behavior
Operations mutate caller-supplied bitmaps in memory. The header stores no global state. Memory clobbers are used where assembly updates through address registers rather than explicit memory outputs.

## Dependencies And Integration Points
It must be included through `<linux/bitops.h>` and depends on compiler attributes and barriers. It is used by core kernel bitmap, flags, scheduler, filesystem, networking, and driver code.

## Risks And Edge Cases
Endian-specific bit numbering is central; changing address math would break on-disk and in-memory bitmaps. Atomicity depends on instruction and CPU behavior. Variant selection must match CPU instruction availability or illegal instructions can occur.

## Test Signals
Kernel bitops selftests, bitmap tests, ext/filesystem bitmap operations, lock bit operations, and cross-builds for ColdFire, 68000/no-bitfield, and 68020+ configs validate the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/blinken.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/blinken.h

## Purpose
This header provides HP300 front-panel LED support for m68k "blinkenlights" diagnostics.

## Important APIs, Types, And Functions
- `HP300_LEDS` is the LED I/O address.
- `hp300_ledstate` is the software shadow byte.
- `blinken_leds(int on, int off)` updates the shadow and writes the inverted value with `out_8()` when `MACH_IS_HP300`.

## Control Flow
Callers request bits to turn on and off. The inline helper ignores non-HP300 machines, updates `hp300_ledstate`, and writes the hardware register.

## State And Persistence Behavior
Persistent state is the global `hp300_ledstate` shadow plus the LED hardware latch. The function is not synchronized, so concurrent updates can race.

## Dependencies And Integration Points
It depends on machine detection from `asm/setup.h` and I/O accessors from `asm/io.h`. It integrates with HP300 platform diagnostics and activity indicators.

## Risks And Edge Cases
The hardware uses inverted output, so direct writes must preserve that convention. Unsynchronized read-modify-write on `hp300_ledstate` can lose concurrent bit changes.

## Test Signals
On HP300 hardware, calls that set and clear individual LED bits should update the panel correctly. Non-HP300 builds should compile and perform no I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/blinken.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootinfo.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootinfo.h

## Purpose
This header wraps the m68k boot information UAPI and declares optional helpers for preserving boot records and processing U-Boot command lines.

## Important APIs, Types, And Functions
- Includes `<uapi/asm/bootinfo.h>` for `struct bi_record` and bootinfo constants.
- `save_bootinfo()` is real when `CONFIG_BOOTINFO_PROC` is enabled and a no-op inline otherwise.
- `process_uboot_commandline()` is real when `CONFIG_UBOOT` is enabled and a no-op inline otherwise.

## Control Flow
Early boot code parses boot records and calls `save_bootinfo()` if proc exposure is enabled. U-Boot boot paths call `process_uboot_commandline()` to merge or translate command-line data.

## State And Persistence Behavior
When enabled, bootinfo is persisted by implementation code for later `/proc` visibility. Otherwise calls are compiled away. Command-line processing mutates the provided command buffer only in U-Boot-enabled builds.

## Dependencies And Integration Points
It integrates with m68k boot parsers, platform config code, `/proc` bootinfo support, and U-Boot entry paths.

## Risks And Edge Cases
No-op stubs can hide missing config dependencies in code that expects side effects. Command buffer size must be honored by the U-Boot implementation.

## Test Signals
Boot with and without `CONFIG_BOOTINFO_PROC` and `CONFIG_UBOOT`; validate boot record parsing, `/proc` bootinfo output, and command-line preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootstd.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootstd.h

## Purpose
This header defines a uClinux/m68k bootloader system-call interface using `trap #2`. It provides syscall numbers and C wrapper-generating macros for bootloader operations such as reset, exec, file I/O, flash programming, environment access, and memory mapping.

## Important APIs, Types, And Functions
- `__BN_*` constants define bootloader call numbers up to `NR_BSC`.
- `__bsc_return()` converts negative bootloader errors in the `[-64, -1]` range into `errno` and `-1`.
- `_bsc0()` through `_bsc5()` generate wrappers with zero to five arguments passed in `%d1` through `%d5`, call number/result in `%d0`, and `trap #2`.

## Control Flow
Generated wrappers load registers, execute `trap #2`, then pass the result through `__bsc_return()`. Control transfers to bootloader firmware and returns with a result or error code.

## State And Persistence Behavior
The header owns no kernel state. Firmware calls may mutate bootloader environment variables, flash contents, file descriptors, mappings, or system reset state.

## Dependencies And Integration Points
It expects C library-style `errno` availability and m68k register calling conventions. It integrates with bootloader-aware standalone or early uClinux code.

## Risks And Edge Cases
Register constraints and return conversion are ABI-sensitive. Flash erase/write and reset calls are destructive. `__BN_setbenv` is commented as "get" but named set, so callers should verify bootloader ABI documentation.

## Test Signals
Bootloader interface tests for `_bsc*` argument passing, file open/read/write/close, environment get/set, flash range operations on safe targets, and error-to-errno conversion validate the macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootstd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/bug.h

## Purpose
This header supplies the m68k architecture `BUG()` implementation when MMU and bug support are enabled, then falls back to generic bug helpers.

## Important APIs, Types, And Functions
- Conditional `BUG()` emits illegal/trap instructions with optional verbose metadata.
- `HAVE_ARCH_BUG` marks the architecture implementation as present.
- Includes `<asm-generic/bug.h>` for the rest of the BUG/WARN API.

## Control Flow
When a `BUG()` path executes, inline assembly emits a trap/illegal instruction sequence that transfers control to exception handling. Verbose builds encode file/line or bug table data depending on config and Sun3 constraints.

## State And Persistence Behavior
The header defines no mutable state. Verbose BUG support contributes static metadata to bug tables, and execution terminates the current faulting path through the kernel exception machinery.

## Dependencies And Integration Points
It depends on `CONFIG_MMU`, `CONFIG_BUG`, `CONFIG_DEBUG_BUGVERBOSE`, and `CONFIG_SUN3`. It integrates with generic BUG/WARN infrastructure and m68k exception handling.

## Risks And Edge Cases
Instruction encoding must be valid for the target CPU family. Sun3 has special constraints. Incorrect bug table metadata breaks diagnostics or exception fixup.

## Test Signals
Build all relevant config combinations and run controlled BUG/WARN tests under m68k emulation or hardware to verify trap handling and diagnostic output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bvme6000hw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/bvme6000hw.h

## Purpose
This header maps BVME6000 board hardware: PIT, RTC, Ethernet, SCSI, SCC serial, configuration switches, IRQ assignments, and VME address control registers.

## Important APIs, Types, And Functions
- `PitRegsPtr` and `RtcPtr_t` map PIT and RTC register blocks.
- Fixed addresses define PIT, RTC, Intel i596 Ethernet, local IRQ/status, NCR53C710 SCSI, SCC channels, config register, and VME ACR registers.
- IRQ constants map printer, timer, Ethernet, SCSI, RTC, abort, and SCC subinterrupts to Linux IRQ numbers.
- `bvme_acr_*` macros expose VME address control registers as volatile bytes.

## Control Flow
Board setup and drivers directly program the mapped registers. Interrupt code uses the IRQ constants to register handlers and read status. VME setup writes ACR registers to configure bus address translation.

## State And Persistence Behavior
State resides in board hardware registers and switch inputs. The header itself has no state but provides direct mutable lvalues for VME address control.

## Dependencies And Integration Points
It depends on `asm/irq.h` and integrates with BVME6000 platform setup, timer, RTC, Ethernet, SCSI, serial, abort button, and VME bus code.

## Risks And Edge Cases
Fixed physical addresses and byte-wide ACR access must match board wiring. Incorrect IRQ numbering can misroute SCC subinterrupts. VME address control writes can make bus devices inaccessible.

## Test Signals
BVME6000 boot, PIT timer tick, RTC access, Ethernet and SCSI interrupts, SCC channel TX/RX, abort interrupt, config switch reading, and VME device probing validate this map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bvme6000hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cache.h

## Purpose
This header defines basic m68k cacheline geometry for generic kernel code.

## Important APIs, Types, And Functions
- `L1_CACHE_SHIFT` is 4.
- `L1_CACHE_BYTES` is 16.
- `ARCH_DMA_MINALIGN` is set to the cache line size.

## Control Flow
No runtime control flow is present. Constants are consumed at compile time by allocators, DMA code, and cache alignment helpers.

## State And Persistence Behavior
No state is stored. The constants influence structure alignment and DMA-safe allocation layout.

## Dependencies And Integration Points
It integrates with Linux cache alignment macros, slab/page allocation, networking, DMA buffers, and architecture-independent cacheline assumptions.

## Risks And Edge Cases
The constants are conservative architecture-wide values. CPU variants with different effective line sizes rely on other cacheflush logic to handle details.

## Test Signals
Cross-build alignment-sensitive code and run DMA/cache coherency tests on representative m68k and ColdFire systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush.h

## Purpose
This dispatcher header selects the MMU or non-MMU m68k cache flush implementation.

## Important APIs, Types, And Functions
- Includes `asm/cacheflush_no.h` when `__uClinux__` is defined.
- Includes `asm/cacheflush_mm.h` otherwise.

## Control Flow
There is no runtime control flow. Preprocessor selection chooses the cache maintenance API implementation at compile time.

## State And Persistence Behavior
No state is stored here. The selected included header defines the actual cache state manipulation behavior.

## Dependencies And Integration Points
It integrates all generic include users with either m68k MMU cache handling or m68knommu/ColdFire cache handling.

## Risks And Edge Cases
The selector uses `__uClinux__`; build environments must define it consistently for non-MMU targets or the wrong implementation will be compiled.

## Test Signals
Build both MMU and uClinux/non-MMU m68k configurations and verify cacheflush API availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_mm.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_mm.h

## Purpose
This header implements cache maintenance for MMU-enabled m68k systems. It covers ColdFire, 68040/060, and older CACR-driven CPUs, and exposes Linux cacheflush hooks used by memory management, DMA, and executable mapping paths.

## Important APIs, Types, And Functions
- ColdFire helpers `clear_cf_icache()`, `clear_cf_dcache()`, `clear_cf_bcache()`, `flush_cf_icache()`, `flush_cf_dcache()`, and `flush_cf_bcache()` manipulate CACR or `cpushl`.
- `flush_icache()` handles whole-instruction-cache flush by CPU family.
- External range helpers: `cache_clear()`, `cache_push()`, and `cache_push_v()`.
- `__flush_cache_all()`, `__flush_cache_030()`, `flush_cache_mm()`, `flush_cache_range()`, and `flush_cache_page()` integrate with VM changes.
- `__flush_pages_to_ram()` pushes/invalidates page data before instruction use or DMA visibility.
- Public hooks include `flush_dcache_page()`, `flush_dcache_folio()`, `flush_icache_pages()`, `flush_icache_user_page()`, `flush_icache_range()`, `copy_to_user_page()`, and `copy_from_user_page()`.

## Control Flow
Flush functions branch on `CPU_IS_COLDFIRE`, `CPU_IS_040_OR_060`, and `CPU_IS_020_OR_030`. VM flushes only act on the current mm for 030-style caches. Page flushing converts kernel virtual addresses to physical addresses for 040/060 `cpushp` loops or set indexes for ColdFire.

## State And Persistence Behavior
The state affected is CPU cache content and, indirectly, memory visibility for DMA and instruction fetch. The header owns no software state but depends on current task/mm and CPU feature state.

## Dependencies And Integration Points
It depends on Linux MM types, page helpers, CPU feature macros, physical address translation, and ColdFire cache constants. It integrates with mmap/munmap, fork, user-page copying, module/text patching, signal trampolines, and DMA/cache coherency paths.

## Risks And Edge Cases
CPU-family-specific assembly must match available instructions. Flushing too little can execute stale instructions or expose stale DMA data; flushing too much costs performance. Current-mm checks are subtle for aliasing caches.

## Test Signals
Run executable mapping/self-modifying-code tests, ptrace/signal trampoline tests, DMA coherency tests, fork/mmap stress, module load/unload, and cross-builds for ColdFire, 030, 040, and 060 targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_no.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_no.h

## Purpose
This header implements cache maintenance for non-MMU m68k/ColdFire systems. It provides whole-cache and range-compatible hooks backed by ColdFire CACR operations and optional `mcf_cache_push()`.

## Important APIs, Types, And Functions
- `flush_cache_all()`, `flush_dcache_range()`, and `flush_icache_range()` map to whole-cache helpers.
- `mcf_cache_push()` is an external writeback helper.
- `__clear_cache_all()`, `__flush_cache_all()`, `__flush_icache_all()`, and `__flush_dcache_all()` manipulate CACR invalidation/push constants.
- `cache_push()` and `cache_clear()` ignore ranges and flush/clear globally.
- Includes `asm-generic/cacheflush.h` for remaining hooks.

## Control Flow
Compile-time cache constants determine whether assembly writes to `CACR` are emitted. Data-cache flush optionally pushes dirty lines first, then invalidates. Range APIs fall back to whole-cache operations because the hardware may not support precise line operations.

## State And Persistence Behavior
The only affected state is CPU cache/write-buffer state. No software state is stored by the header.

## Dependencies And Integration Points
It depends on ColdFire `mcfsim.h`, cache configuration constants, Linux MM types, and generic cacheflush definitions. It integrates with non-MMU executable loading, DMA, and memory update paths.

## Risks And Edge Cases
Range arguments are ignored, which is correct but potentially expensive. Missing `CACHE_PUSH` support risks discarding dirty data if invalidation is used without writeback. CACR constants must match the ColdFire variant.

## Test Signals
Non-MMU ColdFire boot, executable load after writes, DMA coherency, cache-disabled configs, and builds with separate instruction/data cache constants validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_no.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cachetype.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cachetype.h

## Purpose
This header tells generic code that m68k data caches are aliasing.

## Important APIs, Types, And Functions
- `cpu_dcache_is_aliasing()` returns `true`.

## Control Flow
No runtime branching is encoded beyond the inline constant return. Generic MM/cache code can use this as a conservative architecture signal.

## State And Persistence Behavior
No state is stored.

## Dependencies And Integration Points
It includes Linux types and integrates with generic cache alias handling and memory-management decisions.

## Risks And Edge Cases
The unconditional true result is conservative for all variants; it may impose extra flushing on systems without problematic aliasing but avoids stale alias bugs.

## Test Signals
Build generic MM code that queries cache type and run aliasing-sensitive mmap, fork, and executable mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cachetype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/checksum.h

## Purpose
This header provides m68k-optimized Internet checksum helpers unless `CONFIG_GENERIC_CSUM` selects generic code.

## Important APIs, Types, And Functions
- External helpers: `csum_partial()`, `csum_and_copy_from_user()`, and `csum_partial_copy_nocheck()`.
- `ip_fast_csum()` computes IPv4 header checksums using m68k add-with-extend loops.
- `csum_fold()` folds a 32-bit partial checksum to complemented 16-bit form.
- `csum_tcpudp_nofold()` and `csum_tcpudp_magic()` handle IPv4 pseudo-header checksums.
- `ip_compute_csum()` wraps `csum_partial()` and `csum_fold()`.
- `csum_ipv6_magic()` computes IPv6 pseudo-header checksums.

## Control Flow
Checksum functions run inline assembly loops over input words, preserving carry with `addx`/`addxl`. Copy-and-checksum helpers are implemented externally. Generic checksum code is included instead when configured.

## State And Persistence Behavior
The helpers are stateless except for reading buffers and writing destination buffers in copy variants. User-copy variants interact with user memory fault handling in their implementation.

## Dependencies And Integration Points
It depends on Linux checksum types, IPv6 address definitions, user pointer annotations, and networking stack checksum contracts.

## Risks And Edge Cases
Alignment and even-length assumptions matter for `csum_partial()`. Carry handling in inline assembly is architecture-sensitive. User-copy checksum paths must handle faults correctly and not leak partial state.

## Test Signals
Networking checksum selftests, IPv4/IPv6 TCP/UDP traffic, odd final fragment lengths, unaligned buffers, user-copy checksum fault tests, and generic-vs-arch checksum comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cmpxchg.h

## Purpose
This header implements m68k exchange and compare-exchange primitives. It supports CAS-capable CPUs with `casb/casw/casl` and fallback uniprocessor paths protected by local interrupt disabling.

## Important APIs, Types, And Functions
- `__arch_xchg()` exchanges 1-, 2-, or 4-byte values, using `swap()` under IRQ disable when `CONFIG_RMW_INSNS` is absent or CAS loops when present.
- `arch_xchg()` is the typed public macro.
- `arch_cmpxchg64_local()` maps to generic local 64-bit compare-exchange.
- `__cmpxchg()` implements 1-, 2-, and 4-byte CAS for RMW-capable builds.
- `arch_cmpxchg()`, `arch_cmpxchg_local()`, and `arch_cmpxchg64()` expose typed APIs.
- Invalid size hooks are `__invalid_xchg_size()` and `__invalid_cmpxchg_size()`.

## Control Flow
CAS exchange loops read the old value, attempt `cas*`, and retry until successful. Fallback exchange disables local interrupts, swaps by size, and restores interrupts. Non-CAS compare-exchange delegates to generic support.

## State And Persistence Behavior
Only the target memory and temporary interrupt state are mutated. The fallback assumes uniprocessor m68k, so local IRQ exclusion is sufficient for kernel atomicity.

## Dependencies And Integration Points
It depends on irqflags, minmax, generic cmpxchg-local helpers, and generic cmpxchg fallback code. It underpins atomics, locks, reference counts, and lockless kernel algorithms.

## Risks And Edge Cases
Unsupported sizes route to invalid helper symbols. CAS instruction availability must match `CONFIG_RMW_INSNS`. Memory ordering depends on the assembly memory clobbers and surrounding generic barriers.

## Test Signals
Atomic/cmpxchg selftests, xchg size tests, lock/refcount stress, CAS contention loops, and builds with and without `CONFIG_RMW_INSNS` validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/coldfire.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/coldfire.h

## Purpose
This header centralizes default ColdFire platform constants for clock frequency, UART baud base, interrupt vector base, and module base address registers.

## Important APIs, Types, And Functions
- `MCF_CLK` is set from `CONFIG_CLOCK_FREQ` when available, otherwise defaulted.
- `MCF_BUSCLK` derives from the CPU clock.
- `MCF_UARTCLK` and `MCF_BAUDRATE` define serial timing defaults.
- `MCF_MBAR` and `MCF_IPSBAR` are optionally set from Kconfig.
- `MCFINT_VECBASE` defines the ColdFire interrupt vector base.

## Control Flow
No runtime control flow is present. The preprocessor selects constants from config or defaults.

## State And Persistence Behavior
No state is stored. Constants influence timer, serial, interrupt, and peripheral register calculations.

## Dependencies And Integration Points
It integrates with ColdFire board support, serial drivers, timer/clock code, interrupt setup, and peripheral register headers.

## Risks And Edge Cases
Incorrect clock or base-address constants break baud rate, timer tick, and peripheral access. Defaults may be unsuitable for boards that must provide config values.

## Test Signals
ColdFire board builds, UART baud accuracy, timer tick calibration, interrupt vector delivery, and peripheral register access validate the selected constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/coldfire.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/config.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/config.h

## Purpose
This header declares platform-specific bootinfo parsers and configuration entry points for the m68k machine families.

## Important APIs, Types, And Functions
- Bootinfo parsers: `amiga_parse_bootinfo()`, `apollo_parse_bootinfo()`, `atari_parse_bootinfo()`, `bvme6000_parse_bootinfo()`, `hp300_parse_bootinfo()`, `mac_parse_bootinfo()`, `mvme147_parse_bootinfo()`, `mvme16x_parse_bootinfo()`, `q40_parse_bootinfo()`, and `virt_parse_bootinfo()`.
- Configuration functions: `config_amiga()`, `config_apollo()`, `config_atari()`, `config_bvme6000()`, `config_hp300()`, `config_mac()`, `config_mvme147()`, `config_mvme16x()`, `config_q40()`, `config_sun3()`, `config_sun3x()`, and `config_virt()`.

## Control Flow
Early architecture setup selects the active machine, parses boot records through the relevant parser, then calls the matching `config_*()` function to initialize platform callbacks, memory, devices, and IRQs.

## State And Persistence Behavior
State is mutated by the implementations: machine globals, memory layout, platform hooks, device resources, and parsed bootinfo. The header declares the dispatch surface only.

## Dependencies And Integration Points
It depends on `struct bi_record` from bootinfo headers and integrates with arch setup for all supported m68k platforms.

## Risks And Edge Cases
Missing declarations or wrong parser signatures break early boot. Platform config functions have global side effects and must be called exactly for the detected machine.

## Test Signals
Boot each machine family config far enough to parse bootinfo and register platform devices/IRQs. Build coverage across enabled/disabled platform combinations catches declaration drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/contregs.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/contregs.h

## Purpose
This header defines Sun-3/Sun m68k control-space register addresses for MMU, cache, DVMA, bus error, LEDs, VME, and boot SCC access.

## Important APIs, Types, And Functions
- `AC_*` constants identify control address spaces such as IDPROM, pagemap, segment map, context, system enable, bus error, cache tags/data, DVMA map, VME vector, and boot SCC.
- `AC_M_*` constants identify MMU register offsets such as processor control, context table/root pointers, context register, synchronous/asynchronous fault registers, reset, and TLB replacement controls.

## Control Flow
Low-level Sun MMU and platform code uses these constants in special address-space access instructions or control-space mappings. No functions are defined here.

## State And Persistence Behavior
The constants reference persistent processor/platform control registers. Reads observe MMU/cache/fault state; writes can change contexts, mappings, cache state, reset behavior, or VME handling.

## Dependencies And Integration Points
It integrates with Sun3/Sun3x MMU, cache, bus error, DVMA, LED, VME, and serial bootstrap code.

## Risks And Edge Cases
Control-space constants are privileged hardware contracts. Writing wrong registers can corrupt address translation or reset the system. Several offsets are CPU-model-specific and comments encode model applicability.

## Test Signals
Sun3/Sun3x boot, MMU context switching, page/segment map operations, bus error reporting, DVMA mapping, cache tag/data access, VME interrupts, and LED control validate use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/contregs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/current.h

## Purpose
This header defines how m68k obtains the current task pointer and current stack pointer.

## Important APIs, Types, And Functions
- On MMU builds, `current` is a register variable bound to `%a2`.
- On non-MMU builds, `get_current()` returns `current_thread_info()->task` and `current` maps to that helper.
- `current_stack_pointer` is a register variable bound to `sp`.

## Control Flow
MMU code reads `current` directly from the reserved address register. Non-MMU code computes it from thread info. There is no other runtime logic.

## State And Persistence Behavior
The current task pointer is maintained by low-level entry/context-switch code. This header exposes it to C code and does not own the state.

## Dependencies And Integration Points
It integrates with m68k entry code, context switching, thread_info layout, scheduler, and all kernel code using `current`.

## Risks And Edge Cases
MMU builds reserve `%a2`; compiler and assembly code must honor that convention. Non-MMU correctness depends on `current_thread_info()` being valid for the current stack.

## Test Signals
Context-switch stress, syscall/interrupt entry tests, scheduler tests, and builds for MMU/non-MMU configs validate current pointer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/delay.h

## Purpose
This header implements busy-wait delay loops for m68k using `loops_per_jiffy`, with variants for ColdFire alignment and CPUs lacking 32x32-to-64 multiply/divide.

## Important APIs, Types, And Functions
- `__delay()` runs an inline decrement loop, with `DELAY_ALIGN` padding for ColdFire.
- `__bad_udelay()` catches excessive constant microsecond delays.
- `__const_udelay()` is implemented by scaled arithmetic, either with simplified 32-bit math or `mulul`.
- `__udelay()` and `udelay()` provide microsecond delays with compile-time range checking for constants.
- `ndelay()` computes loop counts for nanosecond delays.

## Control Flow
Callers invoke `udelay()` or `ndelay()`. Constant microsecond delays above 20000 route to `__bad_udelay()`. Otherwise the code scales by HZ and `loops_per_jiffy`, then spins in `__delay()`.

## State And Persistence Behavior
The header does not store state. It reads `loops_per_jiffy` and consumes CPU cycles; interrupts are not disabled by these helpers.

## Dependencies And Integration Points
It depends on `asm/param.h`, HZ, `loops_per_jiffy`, CPU config flags, and compiler constant detection. It is used by drivers and early hardware sequencing requiring short waits.

## Risks And Edge Cases
Busy waits depend on calibrated `loops_per_jiffy` and CPU alignment behavior. Long `udelay()` calls are discouraged and constant-checked. Nanosecond scaling is approximate, especially on no-64-multiply CPUs.

## Test Signals
Delay calibration, serial/device reset timing, timer-based measurements of `udelay()`/`ndelay()`, and cross-builds for ColdFire and full m68k multiply support validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/div64.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/div64.h

## Purpose
This header implements `do_div()` for m68k CPUs with 64-bit-capable divide instructions and falls back to generic code for CPUs without required multiply/divide support.

## Important APIs, Types, And Functions
- Includes `<asm-generic/div64.h>` when `CONFIG_CPU_HAS_NO_MULDIV64` is set.
- Architecture `do_div(n, base)` divides a 64-bit value by a 32-bit base, stores the quotient back in `n`, and returns the remainder.
- The implementation uses `divul.l` and `divu.l` over the upper and lower 32-bit words.
- Defines `__div64_32` to suppress unused generic helper construction.

## Control Flow
The macro splits `n` into two 32-bit words, divides the upper word if nonzero, then divides the lower word with the carried remainder. The quotient words are reassembled into `n`.

## State And Persistence Behavior
Only the caller's `n` lvalue is updated. There is no persistent state.

## Dependencies And Integration Points
It depends on m68k divide instruction availability and Linux integer types. It is used throughout kernel code needing 64/32 division.

## Risks And Edge Cases
`do_div` evaluates and writes its first argument as a macro lvalue. Division by zero remains caller-invalid. Endianness of the union word order must match m68k big-endian layout.

## Test Signals
64-bit division unit tests across small/large dividends, upper-word nonzero cases, remainder validation, and builds for generic fallback configs validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/div64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/dma.h

## Purpose
This minimal header defines the m68k `MAX_DMA_ADDRESS` expected by generic bootmem/allocation code.

## Important APIs, Types, And Functions
- `MAX_DMA_ADDRESS` is set to `PAGE_OFFSET`.

## Control Flow
There is no runtime control flow. Generic allocation code consumes the macro.

## State And Persistence Behavior
No state is stored.

## Dependencies And Integration Points
It depends on `PAGE_OFFSET` being defined by memory layout headers before use. It integrates with generic DMA/bootmem allocation expectations.

## Risks And Edge Cases
The comment notes traditional DMA is not meaningful for m68k in this context; platform-specific DMA constraints are handled elsewhere. Incorrect `PAGE_OFFSET` propagation would affect allocator boundaries.

## Test Signals
Kernel build and bootmem/memblock allocation on m68k configs validate the macro is available and harmless.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dsp56k.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/dsp56k.h

## Purpose
This header defines the user-facing ioctl data structures and command numbers for the Atari Falcon DSP56001/DSP56K device driver.

## Important APIs, Types, And Functions
- `struct dsp56k_upload` carries a byte length and user pointer to DSP binary code.
- `struct dsp56k_host_flags` carries host flag write direction bits, output values, and returned status.
- Ioctl command codes include `DSP56K_UPLOAD`, `DSP56K_SET_TX_WSIZE`, `DSP56K_SET_RX_WSIZE`, `DSP56K_HOST_FLAGS`, and `DSP56K_HOST_CMD`.

## Control Flow
Userspace issues ioctls with these structures. The driver copies upload data, configures transmit/receive word sizes, reads/writes host flags, or triggers a host command.

## State And Persistence Behavior
Persistent state is in the DSP device and driver: uploaded program, configured word sizes, and host flag state. The structs are transient syscall payloads.

## Dependencies And Integration Points
It uses `__user` pointer annotation and integrates with the Atari DSP host interface defined in `atarihw.h` and the DSP character device driver.

## Risks And Edge Cases
Ioctl numbers are small raw constants rather than `_IO*` encoded commands. User pointer and length validation must be handled by the driver. Host command values are limited by hardware.

## Test Signals
Userspace DSP upload, TX/RX word size changes, host flag read/write, invalid pointer/length handling, and host command range tests validate the ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dsp56k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dvma.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/dvma.h

## Purpose
This header declares and describes DVMA/IOMMU support for Sun3 and Sun3x m68k systems, including allocation, mapping, unmapping, VME address conversion, and Sun3x onboard DMA register definitions.

## Important APIs, Types, And Functions
- Page constants define 8 KiB DVMA page size/alignment.
- Core APIs include `dvma_init()`, `dvma_map_iommu()`, `dvma_map_align()`, `dvma_malloc_align()`, `dvma_unmap()`, and `dvma_free()`.
- Convenience macros include `dvma_malloc()`, `dvma_map()`, `dvma_map_vme()`, and VME conversion helpers.
- Sun3 defines DVMA pmeg range, `DVMA_START/END/SIZE`, IOMMU entries, and virtual/physical/VME conversion macros.
- Sun3x defines larger IOMMU entry counts, `dvma_map_cpu()`, `dvma_unmap_iommu()`, `struct sparc_dma_registers`, `enum dvma_rev`, and `struct Linux_SBus_DMA`.
- Numerous `DMA_*` condition register bits describe DMA engine status, reset, direction, FIFO, burst, interrupt, and error controls.

## Control Flow
Initialization prepares DVMA mapping resources. Drivers allocate or map kernel buffers into DVMA bus space, program DMA engines with returned bus addresses, and unmap/free after completion. Sun3x SBus DMA code uses revision and condition-register bits to control transfers.

## State And Persistence Behavior
Persistent state is in the DVMA allocator/IOMMU tables, CPU mappings, DMA engine registers, and `dma_chain`. Mappings remain valid until explicitly unmapped/freed.

## Dependencies And Integration Points
It integrates with Sun3/Sun3x SCSI, Ethernet, VME, SBus-style DMA, MMU/IOMMU setup, and platform memory management.

## Risks And Edge Cases
DVMA alignment and address windows are strict, especially Sun3's empirical 0x10000 region alignment. Leaked mappings exhaust IOMMU entries. Revision-specific DMA bits overlap and must be interpreted by hardware revision.

## Test Signals
Sun3/Sun3x boot, DVMA allocation/free stress, SCSI and Ethernet DMA transfers, VME address conversions, IOMMU map/unmap validation, and DMA error/interrupt handling validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dvma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/elf.h

## Purpose
This header defines m68k ELF ABI parameters for executable loading, core dumps, relocation constants, register sets, FDPIC initialization, and platform metadata.

## Important APIs, Types, And Functions
- `R_68K_*` constants define m68k relocation types.
- `elf_greg_t`, `elf_gregset_t`, and `elf_fpregset_t` define core/user register set types.
- `elf_check_arch()` accepts `EM_68K`.
- `ELF_CLASS`, `ELF_DATA`, `ELF_ARCH`, `ELF_EXEC_PAGESIZE`, and `ELF_ET_DYN_BASE` define loader ABI values.
- `ELF_PLAT_INIT()` clears `%a1`; `ELF_FDPIC_PLAT_INIT()` seeds `%d3`/`%d4`/`%d5`.
- `ELF_CORE_COPY_REGS()` copies saved pt_regs and switch_stack state into the ELF core register array.
- `ELF_HWCAP`, `ELF_PLATFORM`, and `ELF_FDPIC_CORE_EFLAGS` expose platform capability metadata.

## Control Flow
The ELF loader checks architecture, initializes process registers, selects load addresses/page size, and sets FDPIC registers where needed. Core-dump code calls `ELF_CORE_COPY_REGS()` to serialize task register state.

## State And Persistence Behavior
The header defines ABI state in process register initialization and core files. It does not store mutable kernel state. Core dump output persists register snapshots for debuggers.

## Dependencies And Integration Points
It depends on `ptrace.h`, `user.h`, `rdusp()`, `struct switch_stack`, and generic ELF binfmt code. It integrates with exec, dynamic linking, FDPIC, ptrace, and coredump paths.

## Risks And Edge Cases
Register array indexes are ABI-sensitive and comments acknowledge awkward mapping. `ELF_ET_DYN_BASE` differs for Sun3. FDPIC register initialization must match userspace ABI expectations.

## Test Signals
Run m68k ELF and FDPIC executable tests, dynamic loader tests, coredump/gdb register inspection, ptrace register validation, and Sun3 load-address tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/entry.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/entry.h

## Purpose
This header defines low-level m68k exception/syscall entry stack layout and assembly macros for saving/restoring register state, interrupt masking, switch-stack handling, user stack pointer access, and current task lookup.

## Important APIs, Types, And Functions
- `ALLOWINT` defines interrupt enable mask, with an Atari-specific HSYNC exclusion.
- Assembly macros include `SAVE_ALL_SYS`, `SAVE_ALL_INT`, `RESTORE_USER`/`RESTORE_ALL`, `SAVE_SWITCH_STACK`, `RESTORE_SWITCH_STACK`, `RDUSP`, `WRUSP`, and `GET_CURRENT`.
- ColdFire paths distinguish software A7 user-stack emulation from modern separate USP/KSP support.
- MMU builds reserve `%a2` as `curptr` and define `get_current` to derive current from stack base.
- C-string macros expose `SAVE_ALL_INT` and `GET_CURRENT(tmp)` for inline assembly in C code.

## Control Flow
Exception and syscall assembly expands these macros at entry. They push `pt_regs` fields, mark non-syscall interrupts with `orig_d0 = -1`, optionally switch stacks, disable interrupts for sensitive ColdFire paths, and restore state with `rte` on return.

## State And Persistence Behavior
The macros mutate the kernel stack, saved register frames, `sw_usp`/`sw_ksp` on older ColdFire, `%a2` current pointer on MMU systems, and processor status. The saved frame persists until exception return or scheduler handling consumes it.

## Dependencies And Integration Points
It depends on setup, page/thread-info sizes, assembler context, `pt_regs` offsets from generated asm offsets, and CPU config flags. It is central to syscall, interrupt, trap, signal, ptrace, and context-switch paths.

## Risks And Edge Cases
Stack layout comments must match generated offsets and assembly users exactly. ColdFire software USP handling disables interrupts because stack switching is fragile. Register ordering affects ptrace, signals, and core dumps.

## Test Signals
Syscall entry/exit, nested interrupts, signal delivery/return, ptrace register inspection, context-switch stress, ColdFire SW_A7 configs, and Atari interrupt masking tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/fbio.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/fbio.h

## Purpose
This header defines Sun-style framebuffer ioctl ABI structures, type IDs, cursor/color-map/window-ID controls, and framebuffer memory-map offsets used by m68k Sun framebuffer drivers and compatible userspace.

## Important APIs, Types, And Functions
- `FBTYPE_*` constants identify many Sun framebuffer device classes.
- `struct fbtype`, `struct fbcmap`, `struct fbsattr`, `struct fbgattr`, `struct fbcursor`, `struct fbcurpos`, `struct fb_wid_alloc`, `struct fb_wid_item`, and `struct fb_wid_list` define ioctl payloads.
- Ioctls include `FBIOGTYPE`, `FBIOPUTCMAP`, `FBIOGETCMAP`, `FBIOSATTR`, `FBIOGATTR`, video on/off, cursor operations, and WID allocate/free/get/put.
- FFB, MDI, and LEO ioctl constants and CLUT structs define additional compatibility commands.
- Kernel-only offsets define CG6, CG3, TCX, and CG14 mmap/register regions.

## Control Flow
Userspace sends ioctls with these structures to framebuffer drivers. Drivers copy payloads, update hardware color maps/cursors/video state, return attributes, and interpret mmap offsets for device memory regions.

## State And Persistence Behavior
Persistent state is held by framebuffer hardware and drivers: color maps, cursor image/position, video enablement, WID allocations, gamma/CLUT state, and mapped framebuffer memory. The header defines ABI layout only.

## Dependencies And Integration Points
It depends on Linux compiler/types and ioctl encoding macros. It integrates with Sun3/m68k framebuffer drivers and legacy Sun framebuffer userspace interfaces.

## Risks And Edge Cases
This is a userspace ABI; structure layout and ioctl numbers are stable contracts. Some ioctl names are unsupported or historical but must remain compatible. 32-bit pointer fields and endian behavior matter for user ABI.

## Test Signals
Framebuffer ioctl tests for type query, color map get/put, cursor get/set/position, video enable/disable, mmap offsets, and legacy Sun fb tools validate compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/fbio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/flat.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/flat.h

## Purpose
This header supplies m68knommu platform initialization for uClinux flat-format executables.

## Important APIs, Types, And Functions
- Includes `<asm-generic/flat.h>` for generic flat loader definitions.
- `FLAT_PLAT_INIT(regs)` sets register `d5` to `current->mm->start_data` when an mm is present.

## Control Flow
During flat binary exec setup, the loader invokes `FLAT_PLAT_INIT()` to seed architecture-specific register state before entering userspace.

## State And Persistence Behavior
The macro mutates the new task's saved register frame. It reads `current->mm->start_data` and persists the value in `%d5` for the executed program.

## Dependencies And Integration Points
It depends on generic flat binary support and `current`/mm state. It integrates with m68knommu exec and FDPIC/flat userspace startup expectations.

## Risks And Edge Cases
The macro silently does nothing without `current->mm`. Userspace ABI may depend on `d5` containing the data segment base, so changing it can break flat binaries.

## Test Signals
Execute flat binaries on m68knommu, verify startup register expectations, and test processes with valid mm setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/flat.h -->
