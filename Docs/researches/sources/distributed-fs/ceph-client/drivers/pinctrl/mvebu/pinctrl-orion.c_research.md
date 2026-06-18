# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-orion.c

Purpose: this driver supports Orion 88F5181, 88F5181L, 88F5182, and 88F5281 pinmuxing. It is mostly a table driver, but it needs custom register access because MPP0-15 and MPP16-19 are not laid out contiguously.

Important APIs, types, and functions: `orion_mpp_ctrl_get()` and `orion_mpp_ctrl_set()` read/write low pins from `mpp_base` and high pins from `high_mpp_base`. Variant masks `V_5181`, `V_5182`, `V_5281`, and `V_ALL` filter the `orion_mpp_modes[]` table. The three SoC info objects provide variant-specific GPIO ranges, with 88F5182 exposing 19 GPIOs and the others 16.

Control flow: probe obtains SoC info from the OF match, maps two MMIO resources, and calls `mvebu_pinctrl_probe()` directly because the generic simple helper cannot describe the split high register. The common core builds groups and functions, while runtime muxing uses the custom control callback to select the right register block.

State and persistence behavior: `mpp_base` and `high_mpp_base` are file-static MMIO pointers. Mux state persists in hardware registers. There is no suspend/resume and no per-device private wrapper beyond the core allocation.

Dependencies and integration points: dependencies include two DT MMIO resources, MVEBU core callbacks, and OF compatibles. Integrated functions include PCIe/PCI, GPIO, boot NAND/NAND, SATA presence/activity LEDs, GE, and UART1 on variant-specific high pins.

Risks and test signals: the high-register path computes shift from `pid % 8`, so pins 16-19 occupy low nibbles in the high register. Static MMIO globals assume a single instance. Variant filtering is essential because GPIO on MPP16-19 is 88F5182-only. Test with all compatibles, verify both resources are required, read/write muxes below and above pin 16, and confirm GPIO range differences.
