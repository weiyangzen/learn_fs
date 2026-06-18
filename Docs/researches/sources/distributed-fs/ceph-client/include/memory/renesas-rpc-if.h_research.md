# sources/distributed-fs/ceph-client/include/memory/renesas-rpc-if.h

Purpose: This header defines the Renesas RPC-IF core interface used by flash or xSPI front-end drivers to describe command/address/dummy/option/data phases and execute direct-map or manual transfers.

Important APIs, types, and functions: `enum rpcif_data_dir` identifies no-data, input, and output transfers. `struct rpcif_op` describes command and optional command phases, address phase, dummy cycles, option phase, and data phase including bus width, byte counts, DDR flags, values, direction, and in/out buffers. `enum rpcif_type` identifies supported controller families. `struct rpcif` stores device pointer, direct-map I/O base, size, and xSPI mode. Functions include `rpcif_sw_init()`, `rpcif_hw_init()`, `rpcif_prepare()`, `rpcif_manual_xfer()`, `rpcif_dirmap_read()`, and `xspi_dirmap_write()`.

Control flow: A front-end driver initializes software and hardware state, constructs an `rpcif_op` for a memory operation, calls `rpcif_prepare()` to configure controller state and compute direct-map offset/length, then either triggers `rpcif_manual_xfer()` or uses direct-map read/write helpers for memory-window operations.

State and persistence behavior: Controller runtime state lives in `struct rpcif` and the associated device driver. Operation descriptors are transient. Runtime power management is included by dependency, so implementation is expected to coordinate device power around transfers.

Dependencies and integration points: It depends on Linux device and PM-runtime infrastructure and integrates with Renesas R-Car/RZ RPC-IF and xSPI controller drivers, SPI-NOR/HyperFlash style memory clients, and memory-mapped I/O.

Risks: Incorrect bus widths, DDR flags, dummy cycles, or phase byte counts can corrupt flash transactions. Direct-map offset and length must be bounded by `rpcif.size`. Direction and buffer union must agree. Power state must be active during register and direct-map access.

Test signals: Probe both RPCIF and xSPI variants, execute read and write commands with single/dual/quad widths as supported, verify dummy-cycle handling, manual transfer error paths, direct-map boundary reads/writes, runtime PM suspend/resume, and HyperFlash initialization mode.
