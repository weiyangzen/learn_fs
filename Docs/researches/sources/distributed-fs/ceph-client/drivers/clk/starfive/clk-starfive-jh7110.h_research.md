# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110.h

## Purpose
This header shares JH7110-specific helpers and data structures between SYS, AON, STG, ISP, and VOUT clock drivers.

## Important APIs, Types, And Functions
`struct jh7110_top_sysclk` stores a bulk-clock array and count for ISP/VOUT top clocks. `jh7110_reset_controller_register()` is declared for child domains to create reset-controller auxiliary devices.

## Control Flow
There is no standalone flow. Implementations call the reset helper after clock provider registration, and ISP/VOUT use the top-clock struct from runtime PM callbacks.

## State And Persistence
The header defines only types and declarations. Persistent state is allocated by the individual domain drivers.

## Dependencies And Integration Points
It includes `clk-starfive-jh71x0.h`, so all users share the common register-backed clock structures. The reset helper implementation lives in `clk-starfive-jh7110-sys.c` and is exported for module users.

## Risks
Because child modules call a helper implemented in SYS, Kconfig and module dependencies must ensure symbol availability. Changes to `jh7110_top_sysclk` affect ISP and VOUT PM callbacks together.

## Test Signals
Build tests with AON/STG/ISP/VOUT as modules and SYS built-in should verify exported symbol linkage and PM callback data layout.
