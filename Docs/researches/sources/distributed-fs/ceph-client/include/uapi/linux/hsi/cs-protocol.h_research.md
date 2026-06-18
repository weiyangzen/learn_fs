<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsi/cs-protocol.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hsi/cs-protocol.h

## Purpose
`cs-protocol.h` defines message, command, and control constants for the cellular modem control protocol carried over HSI character devices.

## Important APIs, types, and functions
The header defines `CS_DEV_FILE_NAME`, `CS_IF_VERSION`, command-domain bit packing helpers (`CS_CMD_SHIFT`, `CS_DOMAIN_SHIFT`, `CS_CMD_MASK`, `CS_PARAM_MASK`, `CS_CMD()`), indications `CS_ERROR`, `CS_RX_DATA_RECEIVED`, `CS_TX_DATA_READY`, and `CS_TX_DATA_SENT`, error parameter `CS_ERR_PEER_RESET`, buffer feature flags `CS_FEAT_TSTAMP_RX_CTRL` and `CS_FEAT_ROLLING_RX_COUNTER`, states `CS_STATE_CLOSED`, `CS_STATE_OPENED`, and `CS_STATE_CONFIGURED`, `CS_MAX_BUFFERS`, `struct cs_buffer_config`, `struct cs_timestamp`, `struct cs_mmap_config_block`, and ioctls `CS_GET_STATE`, `CS_SET_WAKELINE`, `CS_GET_IF_VERSION`, and `CS_CONFIG_BUFS`.

## Control flow
User space opens `/dev/cmt_speech`, queries the interface version and state, configures mmap buffer counts/sizes/features, controls the wake line, and receives command indications for RX data availability, TX readiness, TX completion, or peer reset. The shared mmap config block tells applications where RX/TX buffers and counters live.

## State and persistence behavior
Protocol state is transient device state: closed/opened/configured state, wake-line state, configured RX/TX buffer rings, optional RX-control timestamp, RX pointer boundary, and rolling counters. No persistent storage is described in the header.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<linux/ioctl.h>`. It integrates with the Nokia CMT speech character driver, lower-level HSI transport, modem firmware, and userspace telephony/audio daemons using mmap rings.

## Risks and test signals
Risks include command-number drift with firmware, wrong mmap offset handling, buffer count/size validation bugs, wake-line races, timestamp feature mismatches, and unsupported interface versions. Test signals include version/state ioctls, buffer config boundary tests up to `CS_MAX_BUFFERS`, mmap ring RX/TX flow, peer-reset indication handling, wake-line toggling, and ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsi/cs-protocol.h -->
