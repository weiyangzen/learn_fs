# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ipd.h

## Purpose
`cvmx-ipd.h` provides the C helper interface for configuring, enabling, disabling, and draining the Octeon Input Packet Data unit. It builds on the IPD CSR definitions and includes inline routines used by packet I/O initialization and FPA shutdown.

## Important APIs, Types, And Functions
`enum cvmx_ipd_mode` selects cache placement for packet blocks: all DRAM, all L2, first block L2, or first two blocks L2. `cvmx_ipd_config()` writes buffer skip sizes, packet buffer size, first/second back pointers, WQE FPA pool, cache mode, and port backpressure enable. `cvmx_ipd_enable()` and `cvmx_ipd_disable()` toggle IPD. `cvmx_ipd_free_ptr()` drains prefetched WQE and packet pointers and resets IPD/PIP.

## Control Flow
Configuration writes each layout CSR, then updates `IPD_CTL_STATUS` for cache mode and backpressure. Enable reads control status, warns if already enabled, optionally sets `len_m8`, then writes `ipd_en`. Disable clears that bit. `cvmx_ipd_free_ptr()` skips early CN38XX revisions that cannot expose pointers, detects `NO_WPTR`, reads pointer counts, drains prefetched WQE, WQE FIFO, prefetched packet, per-port packet FIFO, holding FIFO, and packet FIFO using FIFO-control `cena/raddr` sequences, frees each pointer to the proper FPA pool, then resets IPD and PIP.

## State And Persistence
The functions directly mutate IPD/PIP hardware and FPA pool state. `cvmx_ipd_free_ptr()` returns prefetched buffers to FPA pools and clears receive hardware state by reset. There is no heap or filesystem persistence.

## Dependencies And Integration Points
It depends on `octeon-feature.h`, `cvmx-ipd-defs.h`, `cvmx-pip-defs.h`, model macros, `cvmx_read_csr`, `cvmx_write_csr`, `cvmx_fpa_free`, and `cvmx_phys_to_ptr`. It is integrated with global packet I/O setup, receive shutdown, and FPA pool teardown.

## Risks
The drain logic is hardware-specific and easy to break: wrong pool selection in `NO_WPTR`, wrong FIFO address arithmetic, or running while traffic is active can free live buffers or leak prefetched buffers. Resetting IPD/PIP is disruptive. `CVMX_ENABLE_LEN_M8_FIX` changes receive length behavior except on CN38XX pass2.

## Test Signals
Tests should verify IPD enable/disable status, packet receive layout for configured skip/back/size values, warning on double enable, no FPA leaks after `cvmx_ipd_free_ptr()`, correct `NO_WPTR` pool handling, and successful receive reinitialization after IPD/PIP reset.
