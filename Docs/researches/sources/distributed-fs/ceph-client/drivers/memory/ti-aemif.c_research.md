# sources/distributed-fs/ceph-client/drivers/memory/ti-aemif.c

Purpose: This platform driver configures Texas Instruments asynchronous EMIF chip-select timing and bus-width/extended-wait/select-strobe settings from device tree, then populates child devices behind the configured async bus.

Important APIs/types/functions: `struct aemif_cs_data` stores one chip select's timing and bus config. `struct aemif_device` stores MMIO base, enabled clock, clock rate in kHz, chip-select offset/count, chip-select data, and a configuration mutex. Exported APIs are `aemif_check_cs_timings()` and `aemif_set_cs_timings()`. Internal helpers include `aemif_calc_rate()`, `aemif_config_abus()`, `aemif_get_hw_params()`, `of_aemif_parse_abus_config()`, and `aemif_probe()`.

Control flow: Probe allocates state, enables the clock, derives kHz rate, applies DA850 chip-select offset when needed, maps registers, parses each child node's `ti,cs-*` properties while preserving unspecified hardware defaults, validates timing fields, programs config and timing registers for each CS, then calls `of_platform_populate()` on each child so dependent devices probe after timing is stable.

State and persistence: Runtime state mirrors chip-select settings and protects later exported timing updates with `config_cs_lock`. Hardware ACR registers hold programmed timings. No persistent file state exists.

Dependencies and integration: Depends on Linux clk, OF, platform-device population, MMIO, mutexes, and public `linux/memory/ti-aemif.h`. Compatible strings are `ti,davinci-aemif` and `ti,da850-aemif`. Child devices depend on this driver for safe bus timing before probe.

Risks and test signals: Risks include timing conversion overflow or off-by-one, invalid chip-select numbering, and assuming one user per CS during initial programming. Test signals include DT parse failures for invalid timings, register readback for each CS, successful probing of child NAND/NOR/FPGA devices, and exported timing changes under mutex without corrupting config bits.
