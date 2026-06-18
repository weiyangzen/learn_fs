# sources/distributed-fs/ceph-client/drivers/soc/ti/pruss.c

## Purpose
This file implements the PRU-ICSS/ICSSG subsystem platform driver. It exposes PRUSS handles and memory-region management to PRU remoteproc clients, maps PRUSS memories and CFG registers, registers clock mux providers, and populates PRU child devices.

## Important APIs, Types, And Functions
Exported APIs are `pruss_get`, `pruss_put`, `pruss_request_mem_region`, `pruss_release_mem_region`, `pruss_cfg_get_gpmux`, `pruss_cfg_set_gpmux`, `pruss_cfg_gpimode`, `pruss_cfg_miirt_enable`, and `pruss_cfg_xfr_enable`. Internal setup functions include `pruss_of_setup_memories`, `pruss_cfg_of_init`, `pruss_clk_init`, and `pruss_clk_mux_setup`. Match data controls absent shared RAM and core clock mux availability.

## Control Flow
Probe sets a 32-bit coherent DMA mask, allocates `struct pruss`, maps DRAM0/DRAM1/shared RAM from the `memories` child, enables runtime PM, maps `cfg`, creates a regmap, registers IEP and optional core clock mux providers from `cfg/clocks`, and populates child devices. `pruss_get` starts from a PRU `rproc`, verifies the parent is a PRU remoteproc, gets the PRUSS platform device data, and increments the PRUSS device refcount. Memory request/release serializes ownership with `pruss->lock`.

## State And Persistence
State is held per PRUSS platform device: memory region metadata, in-use pointers, CFG regmap/base, device pointer, lock, and optional clock muxes managed by devm actions. Hardware CFG changes persist in PRUSS registers until changed or reset.

## Dependencies And Integration Points
It depends on OF child layout `memories`, `cfg`, and `cfg/clocks`, regmap MMIO, runtime PM, remoteproc PRU devices, `linux/pruss_driver.h`, and `pruss.h`. It supports AM335x, AM437x, AM57xx, K2G, AM65x/J721E/AM64x/AM62x compatible strings.

## Risks And Test Signals
Risks include strict DT layout failures, memory ownership leaks if clients fail to release, clock provider cleanup ordering, and invalid mux/mode arguments. Test signals include child PRU devices populated, `pruss_get` from PRU rproc succeeding, memory request returning correct physical/virtual ranges, CFG bit updates visible in registers, and runtime PM transitions.
