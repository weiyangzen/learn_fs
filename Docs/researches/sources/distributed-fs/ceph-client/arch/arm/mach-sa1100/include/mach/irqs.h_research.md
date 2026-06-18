# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/irqs.h

## Purpose
This header defines the SA-1100 IRQ namespace, translating on-chip interrupt bits and board/companion chip IRQ ranges into Linux IRQ numbers.

## Important APIs, Types, and Functions
- Register/constant macro families: `IRQ`(62), `NR`(3), `SA1100`(1); examples: `IRQ_GPIO0_SC`, `IRQ_GPIO1_SC`, `IRQ_GPIO2_SC`, `IRQ_GPIO3_SC`, `IRQ_GPIO4_SC`, `IRQ_GPIO5_SC`, `IRQ_GPIO6_SC`, `IRQ_GPIO7_SC`, `IRQ_GPIO8_SC`, `IRQ_GPIO9_SC`, `IRQ_GPIO10_SC`, `IRQ_GPIO11_27`, `IRQ_LCD`, `IRQ_Ser0UDC`, `IRQ_Ser1SDLC`, `IRQ_Ser1UART`, plus 49 more.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: in-memory locks serialize access to shared controller state; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (3143 bytes, 102 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
