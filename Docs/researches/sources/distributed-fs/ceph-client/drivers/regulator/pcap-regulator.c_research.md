# sources/distributed-fs/ceph-client/drivers/regulator/pcap-regulator.c

Purpose: implements the Motorola/EZX PCAP2 regulator platform driver, exposing legacy PCAP voltage rails through regulator descriptors and PCAP MFD bit operations.

Important APIs/types/functions: voltage tables define V1-V10, VAUX1-4, VSIM/VSIM2, VVIB, and SW1/SW2 selector mappings. `struct pcap_regulator` maps each regulator ID to a PCAP register, enable bit, selector bit index, standby bit, and low-power bit. `pcap_regulator_ops` provides table voltage listing, custom selector get/set, and custom enable/disable/is_enabled callbacks using `ezx_pcap_read()` and `ezx_pcap_set_bits()`.

Control flow: the platform driver is registered at `subsys_initcall`. Probe gets the parent PCAP handle, uses `pdev->id` to select one descriptor from `pcap_regulators[]`, passes platform init data as regulator constraints, and registers exactly that rail. Runtime voltage writes reject fixed one-voltage rails and otherwise update selector bits in the mapped PCAP register; enable operations reject rails with `NA` enable bits.

State and persistence: regulator state is entirely in PCAP hardware registers. The standby and low-power bit metadata is present but unused by this driver. No runtime cache or remove-time restoration exists.

Dependencies and integration: depends on the EZX PCAP MFD, platform devices with IDs matching regulator IDs, board/platform init data, and regulator core. It is a non-DT legacy style driver.

Risks and test signals: there is no bounds check on `pdev->id`, so bad platform data can index past `pcap_regulators[]` or `vreg_table[]`. `ezx_pcap_read()` return values are ignored in get/is_enabled paths. Selector masks assume the number of voltages is a power-of-two minus one mask; duplicated voltage table entries may be intentional hardware encodings. Test every valid platform ID, invalid ID handling at platform layer, fixed rails V10/VSIM2, rails with `NA` enable bits, selector read/write masks, and PCAP read/write error propagation.
