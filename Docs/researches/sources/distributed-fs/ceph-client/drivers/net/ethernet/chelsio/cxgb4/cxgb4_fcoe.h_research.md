# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_fcoe.h

## Purpose

`cxgb4_fcoe.h` declares the optional FCoE offload state and helpers for the Chelsio `cxgb4` driver. Its contents are only present when `CONFIG_CHELSIO_T4_FCOE` is enabled.

## Important APIs, Types, And Constants

- `CXGB_FCOE_TXPKT_CSUM_START` and `CXGB_FCOE_TXPKT_CSUM_END` define checksum offset constants used by FCoE transmit packet handling elsewhere in the driver.
- `CXGB_FCOE_ENABLED` is the bit stored in `struct cxgb_fcoe::flags` to indicate runtime enablement.
- `struct cxgb_fcoe` currently contains an 8-bit `flags` field.
- `cxgb_fcoe_enable()` and `cxgb_fcoe_disable()` toggle FCoE offload features on a netdev.
- `cxgb_fcoe_sof_eof_supported()` validates FCoE SOF/EOF markers for an skb.

## Control Flow

When FCoE support is enabled in the kernel configuration, `struct port_info` can embed or reference `struct cxgb_fcoe` and other driver paths can call the declared helpers. When support is disabled, the header contributes no state or function prototypes, so all call sites must be configuration-guarded.

## State And Persistence

The only state defined here is `struct cxgb_fcoe::flags`. It is runtime-only and currently uses `CXGB_FCOE_ENABLED` to track whether netdev FCoE offload features have been enabled.

The checksum constants are compile-time protocol/layout constants, not runtime state.

## Dependencies And Integration Points

- Controlled by `CONFIG_CHELSIO_T4_FCOE`.
- Uses `struct net_device`, `struct adapter`, and `struct sk_buff` types from the broader driver/kernel include context.
- Implemented by `cxgb4_fcoe.c`.
- Integrates with netdev feature flags and FCoE skb processing paths elsewhere in `cxgb4`.

## Risks And Edge Cases

- Because the disabled configuration does not provide stubs, unguarded callers will fail to compile when FCoE is off.
- `flags` is a `u8`; future additions should remain within byte-width flags or change the type deliberately.
- The checksum offset constants must stay aligned with the hardware transmit descriptor/FCoE header layout expected by other source files.

## Test Signals

- Compile-test with `CONFIG_CHELSIO_T4_FCOE=y` and `n`.
- Static search for unguarded FCoE helper calls in non-FCoE builds.
- Runtime enable/disable tests should observe `CXGB_FCOE_ENABLED` and netdev feature bits changing together.
