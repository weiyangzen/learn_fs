# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-mc.h

Purpose: This small private header names Tegra210 memory-controller register offsets used by Tegra210 MC/EMC code, especially latency allowance, PTSA, EMEM arbitration, refresh-per-bank, and dynamic hysteresis registers.

Important APIs/types/functions: The file exports no functions or types. Its API is the set of `#define` constants such as `MC_LATENCY_ALLOWANCE_*`, `MC_MLL_MPCORER_PTSA_RATE`, `MC_FTOP_PTSA_RATE`, `MC_EMEM_ARB_TIMING_RFCPB`, `MC_EMEM_ARB_REFPB_*`, `MC_PTSA_GRANT_DECREMENT`, and `MC_EMEM_ARB_DHYST_*`.

Control flow: There is no executable control flow. The constants are consumed by Tegra210 memory-controller programming paths when calculating latency allowance or applying MC arbitration/timing values during EMC frequency changes and MC initialization.

State and persistence: No state is stored in the header. The defined offsets address hardware state in MC registers, which persists only as programmed hardware configuration until reset or reprogramming.

Dependencies and integration: It includes `mc.h` for shared Tegra MC context and is aligned with Tegra210 register layout. It sits between raw hardware documentation and C code that writes MMIO through shared Tegra MC helpers.

Risks and test signals: The main risk is an incorrect offset silently programming the wrong register, which can cause display underruns, memory arbitration stalls, or failed frequency transitions. Test signals are successful Tegra210 boot, stable display/video/USB/storage clients under bandwidth pressure, and matching register dumps against the Tegra210 TRM or downstream reference values.
