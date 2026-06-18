# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa.h

Purpose: Defines common PXA clock macros, CKEN descriptors, PXA2xx frequency data, and shared function prototypes.

Important APIs, types, and functions: Provides CLKCFG bit definitions, helper macros for registering read-only rate clocks, mux clocks, and settable rate clocks, `struct desc_clk_cken`, `PXA_CKEN` and `PXA_CKEN_1RATE`, `struct pxa2xx_freq`, `dummy_clk_set_parent()`, and prototypes for common PXA registration and frequency-change helpers.

Control flow: PXA25x/PXA27x files use these macros to generate CCF registration functions and CKEN descriptor arrays. Common `clk-pxa.c` consumes `struct desc_clk_cken` and `struct pxa2xx_freq`.

State and persistence: Header owns no runtime state. It defines descriptor structures containing embedded CCF hardware that are copied or consumed during init.

Dependencies and integration points: Private contract between PXA common and SoC-specific clock files, plus dt-binding IDs from includers.

Risks: The macros generate static symbols and CCF ops; naming collisions or misuse are easy if new SoC code reuses macro names poorly. `PXA_CKEN` assumes two parents even for one-rate clocks by duplicating parent arrays.

Test signals: Build all PXA variants to catch macro-generated symbol errors. Review generated parent arrays and flags for each CKEN descriptor.
