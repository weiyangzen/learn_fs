<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/sdram.S -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/sdram.S

Purpose: This assembly file provides AP325RXA SDRAM self-refresh enter/leave snippets for suspend, designed to be copied to and executed from on-chip memory.

Important APIs/types/functions: It exports `ap325rxa_sdram_enter_start`, `ap325rxa_sdram_enter_end`, `ap325rxa_sdram_leave_start`, and `ap325rxa_sdram_leave_end`.

Control flow: Enter code reads SDCR0, sets self-refresh and clears power-down bits, writes SDCR0, and returns. Leave code clears self-refresh, adjusts refresh timer registers RTCOR/RTCNT with the required key value, and returns.

State and persistence: It directly mutates SDRAM controller registers at fixed physical addresses. The code bytes are used as a relocatable low-level suspend routine.

Dependencies and integration points: It depends on SH7723/AP325RXA SDRAM controller addresses, SuperH assembly ABI, suspend infrastructure, and `setup.c` registering the copied code with suspend support.

Risks and test signals: The routine must be fully self-contained, position-safe, and run from memory that remains accessible while SDRAM is in self-refresh. Tests include suspend/resume cycles, register-value inspection, and ensuring code-size boundaries match exported start/end symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/sdram.S -->
