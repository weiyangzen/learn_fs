# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mn.c

Purpose: i.MX8MN topology driver for NOC, memory, CPU, GPU, camera/display/ISI/LCDIF, USB, audio, Ethernet, SDMA, NAND, USDHC, and main PL301 paths.

Important APIs/types/functions: DRAM/NOC adjustment descriptors use divisor 4. `nodes[]` is the topology source; `imx8mn_icc_probe()` calls `imx_icc_register()`.

Control flow: probe registers nodes/links through the common helper; no NoC priority settings are supplied, so runtime behavior is aggregation plus optional PM QoS.

State and persistence: static descriptors plus runtime state in `imx.c`.

Dependencies/integration: `dt-bindings/interconnect/imx8mn.h`, platform driver framework, common i.MX helper.

Risks and test signals: test display/camera, USB, and memory paths; scaling coefficients; missing DDRC phandle behavior; and onecell ID coverage.
