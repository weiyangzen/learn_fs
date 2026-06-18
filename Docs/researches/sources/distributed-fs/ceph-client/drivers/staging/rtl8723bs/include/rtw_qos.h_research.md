<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_qos.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_qos.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_qos.h` defines the small WMM/QoS private state carried by MLME code. The source was reviewed as a complete 19-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct qos_priv` with QoS option and AC parameter fields.

## Control Flow

MLME IE parsing and association setup populate QoS/WMM state; transmit queue selection and beacon/association IE generation consume it.

## State and Persistence Behavior

`qos_priv` persists per adapter within `mlme_priv`.

## Dependencies and Integration Points

Used by `rtw_mlme.h`, AP beacon code, and xmit queue selection. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Incorrect WMM state can map traffic to wrong access categories or advertise bad AP parameters.

## Test Signals

Association with WMM APs, AP beacon WMM IE generation, and traffic queue mapping checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_qos.h -->
