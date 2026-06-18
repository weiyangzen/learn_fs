# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/osdef1st.h

## Purpose
`osdef1st.h` supplies Linux-specific definitions that must be visible before the generic SysKonnect headers: endian selection, feature macros, descriptor counts, SMT buffer counts, OS-specific descriptor payloads, panic logging, and byte-order conversion shims.

## Important APIs, Types, And Functions
Important macros include `LITTLE_ENDIAN`/`BIG_ENDIAN`, `USE_CAN_ADDR`, `MB_OUTSIDE_SMC`, `SYNC`, `ESS`, `SMT_PANIC`, `NUM_RECEIVE_BUFFERS`, `NUM_TRANSMIT_BUFFERS`, `NUM_SMT_BUF`, `HWM_ASYNC_TXD_COUNT`, `HWM_SYNC_TXD_COUNT`, `SMT_R1_RXD_COUNT`, `SMT_R2_RXD_COUNT`, `AIX_REVERSE`, and `MDR_REVERSE`. It defines `struct s_txd_os` and `struct s_rxd_os` with `sk_buff *` and `dma_addr_t`.

## Control Flow
The header gates compile-time behavior. Enabling `ESS` brings in ESS code and MIB fields; disabling `SBA` excludes allocator source; descriptor counts determine FIFO split and ring initialization behavior.

## State And Persistence
Descriptor OS extensions hold per-buffer Linux skb and DMA mapping addresses for runtime unmap/free operations. No state is persisted beyond driver lifetime.

## Dependencies And Integration Points
It depends on Linux byteorder, `sk_buff`, DMA address types, and kernel logging. It is pulled in by `smc.h` when `PCI` requires `OSDEF`.

## Risks And Edge Cases
Structure-size rules in comments are important for descriptor alignment. Changing RX/TX buffer counts affects hardware ring sizing and the ASIC workaround extra RXD. `SMT_PANIC` only logs at info level here, so fatal generic-driver paths may not stop execution by themselves.

## Test Signals
Build on little- and big-endian configurations if supported, descriptor size/alignment checks, DMA map/unmap paths using `s_txd_os`/`s_rxd_os`, ESS-enabled compilation, and RX/TX ring count validation.
