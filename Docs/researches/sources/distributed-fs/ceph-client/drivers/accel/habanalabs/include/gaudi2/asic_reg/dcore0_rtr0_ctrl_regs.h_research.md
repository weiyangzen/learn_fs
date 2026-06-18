# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_ctrl_regs.h

Purpose: Defines DCORE0 router control registers. The block maps memory count/map, read/write rate limits for memory/PCI/SRAM, reduction controls, SRAM and memory regulator tables, watchdog/shift/config registers, RAZWI decoder capture, and write-reduction counters at 0x4140100-0x4140BC4.

Important APIs/types/functions: Exports 134 `mmDCORE0_RTR0_CTRL_*` address macros. Repeated families include 16 SRAM tokens/latencies/bank IDs and 16 memory tokens/latencies/IDs, represented by `mmDCORE0_RTR0_CTRL_MEM_NUM` (0x4140100), `mmDCORE0_RTR0_CTRL_MEM_MAP` (0x4140104), `mmDCORE0_RTR0_CTRL_WR_RL_MEM` (0x4140108), `mmDCORE0_RTR0_CTRL_WR_RL_PCI` (0x414010C), `mmDCORE0_RTR0_CTRL_WR_RL_SRAM` (0x4140110), and `mmDCORE0_RTR0_CTRL_RGL_MEM_DEC_TOKEN_1` (0x4140BC4).

Control flow: Router initialization programs memory maps and regulator tables; runtime or debug code reads RAZWI and reduction counters after routing faults or performance investigations.

State and persistence behavior: Header state is absent. Hardware registers hold router configuration, rate-limit state, regulator tokens, error capture, and counters until reset or reprogramming.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. `gaudi2_security.c` references the router control base for protected region setup.

Risks: Rate-limit and memory-map mistakes can throttle or misroute traffic. RAZWI capture registers must be handled carefully so fault evidence is not lost before diagnostics.

Test signals: Router bring-up, memory-map validation, rate-limit tests, RAZWI fault injection/readback, and security-region coverage for the router control window.
