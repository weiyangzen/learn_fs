# sources/distributed-fs/ceph-client/arch/mips/lantiq/clk.h

Purpose: declares the Lantiq legacy `struct clk`, common clock-rate constants, static clock registration API, and SoC-specific rate calculation functions.

Important APIs/types/functions: `struct clk` embeds `struct clk_lookup`, rate/rate-table fields, module/bits metadata, and optional callbacks for rate, enable, disable, activate, deactivate, and reboot. It declares XWAY-family rate helpers such as `ltq_danube_cpu_hz`, `ltq_vr9_fpi_hz`, `ltq_ar10_pp32_hz`, and `ltq_grx390_cpu_hz`.

Control flow: used by generic and SoC-specific clock providers to create `clkdev` entries and expose fixed or register-derived rates.

State and persistence: state is per allocated `struct clk`, usually static or early-allocated and registered with clkdev.

Dependencies and integration: consumed by `lantiq/clk.c`, `xway/clk.c`, `xway/sysctrl.c`, `falcon/sysctrl.c`, and GPTU clock registration.

Risks: duplicate `CLOCK_60M` macro definition is benign but noisy. The custom clock model lacks modern common-clk semantics.

Test signals: compile warnings, clock lookup behavior, and SoC boot rate validation.
