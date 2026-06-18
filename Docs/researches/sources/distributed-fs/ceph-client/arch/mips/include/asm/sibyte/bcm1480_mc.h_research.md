# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_mc.h

Purpose: defines BCM1280/BCM1480 memory-controller register bitfields and canned values. It is the high-level contract used by early platform firmware/kernel setup code to program DRAM channel layout, chip-select windows, address muxing, DRAM mode commands, memory clocking, delay-locked-loop tuning, drive strength, ECC diagnostics, and global interleave/ECC control.

Important APIs/types/functions: this header has no C functions or types; its API is macro families. `S_BCM1480_MC_*` macros define shifts, `M_BCM1480_MC_*` masks, `V_BCM1480_MC_*(x)` encoded values, `G_BCM1480_MC_*(x)` extractors, and `K_BCM1480_MC_*` symbolic enumerants. Important composite defaults include `V_BCM1480_MC_CONFIG_DEFAULT`, `V_BCM1480_MC_DRAMMODE_DEFAULT`, `V_BCM1480_MC_TIMING_DEFAULT`, and default DLL/clock/timing encodings.

Control flow: runtime control flow is external; callers write the generated values into addresses from `bcm1480_regs.h`. The encoded flow is the hardware initialization sequence: configure chip-select/interleave/address selectors, issue DRAM commands such as EMRS/MRS/precharge/refresh/power-down, then program mode, clock, DLL, drive, timing, and ECC/global status registers.

State and persistence: all state represented here is persistent hardware register state until reset or reprogramming. ECC status/correction fields expose latched error information; global interleave and chip-select fields affect the physical memory map and cannot be treated as transient software state.

Dependencies and integration: depends on `sb1250_defs.h` for 64-bit mask/value helpers and on `SIBYTE_HDR_FEATURE(1480, PASS2)` to expose DDR2, ODT, extra commands, timing2, and ECC RMW fields. It integrates with `bcm1480_regs.h` address macros, boot memory sizing, ECC handlers, and low-level board bring-up.

Risks and test signals: incorrect constants can produce unbootable memory or silent ECC/addressing corruption. Several duplicate definitions are present (`V_BCM1480_MC_COL03`, `S_BCM1480_MC_PG_POLICY`, `S_BCM1480_MC_PVT_BYP_C1_PULLUP`), and `M_DATA_ECC_INVERT` appears to reference the ECC shift rather than the data-invert shift name. Useful tests are compile coverage with constrained `SIBYTE_HDR_FEATURES`, static macro expansion checks for default values, and hardware/boot tests that exercise DRAM init, ECC injection/status, and multi-channel interleave.
