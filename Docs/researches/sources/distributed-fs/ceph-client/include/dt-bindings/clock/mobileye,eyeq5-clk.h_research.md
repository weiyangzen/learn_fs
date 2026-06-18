<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq5-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq5-clk.h

Purpose: Defines clock IDs for Mobileye EyeQ5 and related EyeQ6H/EyeQ6L-compatible clock domains represented in the binding header.

Important APIs, types, and functions: Exports `EQ5C_PLL_*`, derived CPU and peripheral child clocks, and additional `EQ6LC_*` and `EQ6HC_*` PLL/peripheral IDs. No structs or functions are present.

Control flow: The header has no logic. Clock providers use the constants when translating DT specifiers to PLL, divider, or gate clock objects.

State and persistence: Constants are DT ABI. PLL lock, divisor, and gate state are represented by hardware and common-clock-framework objects elsewhere.

Dependencies and integration points: Used by Mobileye EyeQ DTS files and drivers for CPU, DDR, PCI, PMA, VDI, VMP, MPC, OSPI, UART, I2C, timer, GPIO, and accelerator domains.

Risks and test signals: Risks include mixing EyeQ5 and EyeQ6 subdomain IDs and broken PLL child mapping. Test with DT schema validation, provider registration, CPU/peripheral rate checks, OSPI and serial probes, accelerator clock requests, and boot logs for unresolved clock specifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq5-clk.h -->
